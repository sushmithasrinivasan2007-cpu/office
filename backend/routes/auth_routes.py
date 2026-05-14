from flask import Blueprint, request, jsonify
from utils.supabase_client import supabase, supabase_admin
import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        role = data.get('role', 'employee')
        company_id = data.get('company_id')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        # Validate company_id if provided
        if company_id:
            import re
            uuid_re = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)
            if not uuid_re.match(str(company_id)):
                return jsonify({"error": "The Company ID you entered is invalid. It must be a valid ID (e.g., 35083752-...). If you are trying to start a new company, use the 'Management' tab."}), 400

        # Check if user already exists in our 'users' table
        existing_user_res = supabase_admin.table('users').select('*').eq('email', email).execute()
        existing_user = existing_user_res.data[0] if existing_user_res.data else None

        if existing_user:
            # If they are already active, they should just login
            if existing_user.get('is_active'):
                return jsonify({"error": "An account with this email already exists. Please sign in."}), 400
            
            # If they are invited (inactive), we "complete" their registration
            print(f"[DEBUG] Completing registration for invited user: {email}")
            
            # Update their password in Supabase Auth
            try:
                supabase_admin.auth.admin.update_user_by_id(
                    existing_user['id'],
                    {"password": password, "user_metadata": {"name": name or existing_user.get('name')}}
                )
            except Exception as auth_err:
                print(f"[ERROR] Failed to update auth password: {auth_err}")
                # If they are not in Auth for some reason, we'll try sign_up below
                pass
            
            # Activate their profile
            supabase_admin.table('users').update({
                "is_active": True,
                "name": name or existing_user.get('name'),
                "role": role or existing_user.get('role')
            }).eq('id', existing_user['id']).execute()

            # Sign them in to get a token
            login_res = supabase.auth.sign_in_with_password({"email": email, "password": password})

            # Return success with token
            return jsonify({
                "message": "Registration completed successfully.",
                "user": {
                    "id": existing_user['id'],
                    "email": email,
                    "name": name or existing_user.get('name'),
                    "role": role or existing_user.get('role'),
                    "company_id": existing_user.get('company_id')
                },
                "token": login_res.session.access_token if login_res.session else None
            }), 201

        # NORMAL FLOW: Create user via ADMIN to bypass Supabase's strict email limits
        print(f"[DEBUG] Creating new user via Admin API: {email}")
        
        try:
            # Create the user and confirm their email immediately
            res = supabase_admin.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {"name": name}
            })
            
            if not res or not res.user:
                return jsonify({"error": "Failed to create user account"}), 400

            # Create user profile in 'users' table
            supabase_admin.table('users').upsert({
                "id": res.user.id,
                "email": email,
                "name": name or email,
                "role": role,
                "company_id": company_id,
                "is_active": True
            }).execute()

            # Sign them in to get a session/token for the frontend
            login_res = supabase.auth.sign_in_with_password({"email": email, "password": password})

            # Send a welcome email using OUR SMTP (not Supabase's)
            try:
                from backend.services.email_automation_service import email_service
                email_service.send_email(email, f"Welcome to NeuroOps, {name}!", 
                    f"<h1>Welcome to the team!</h1><p>Your account for {email} has been created successfully.</p>")
            except:
                pass # Don't block registration if welcome email fails

            return jsonify({
                "message": "User registered successfully",
                "user": {
                    "id": res.user.id,
                    "email": email,
                    "name": name,
                    "role": role,
                    "company_id": company_id
                },
                "token": login_res.session.access_token if login_res.session else None
            }), 201

        except Exception as admin_err:
            error_msg = str(admin_err)
            print(f"[ERROR] Admin registration failed: {error_msg}")
            
            # Friendly error for invalid UUID
            if "invalid input syntax for type uuid" in error_msg.lower():
                return jsonify({"error": "The Company ID you entered is invalid. Please ensure it is a valid ID (e.g., 35083752-...) "}), 400
                
            return jsonify({"error": f"Registration failed: {error_msg}"}), 400
    except Exception as e:
        print(f"[ERROR] Registration crash: {str(e)}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Missing request body"}), 400
            
        email = data.get('email')
        password = data.get('password')
        twofa_code = data.get('twofa_code')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        try:
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        except Exception as auth_err:
            print(f"[ERROR] Auth sign-in failed: {auth_err}")
            return jsonify({"error": str(auth_err)}), 401

        if res.session:
            try:
                user_res = supabase.table('users').select('*').eq('id', res.user.id).execute()
                user = user_res.data[0] if (user_res.data and len(user_res.data) > 0) else {}
                
                # AUTO-ELEVATION: Ensure sushmithatumkur2127 has admin access
                # AUTO-ELEVATION: Ensure specific admins have access
                admin_emails = ["sushmithatumkur2127", "sushmithasush2703"]
                is_admin_user = any(x in str(user.get('name', '')).lower() or x in str(user.get('email', '')).lower() for x in admin_emails)
                
                if user and is_admin_user:
                    if user.get('role') != 'super_admin':
                        print(f"[SECURITY] Auto-elevating {user.get('email')} to super_admin")
                        supabase_admin.table('users').update({'role': 'super_admin'}).eq('id', user['id']).execute()
                        user['role'] = 'super_admin'

                # If user profile is missing, try to create it or at least provide basic info
                if not user:
                    print(f"[WARNING] User profile missing in 'users' table for ID: {res.user.id}")
                    # Check if this missing user should be elevated anyway
                    is_special = "sushmithatumkur2127" in email.lower()
                    user = {
                        "id": res.user.id,
                        "email": email,
                        "role": "super_admin" if is_special else "employee",
                        "name": email.split('@')[0]
                    }
                    if is_special:
                        print(f"[SECURITY] Creating missing special admin profile for: {email}")
                        supabase_admin.table('users').upsert(user).execute()

                # Check 2FA
                if user.get('two_factor_enabled'):
                    if not twofa_code:
                        return jsonify({
                            "requires_2fa": True,
                            "temp_token": res.session.access_token,
                            "message": "2FA code required"
                        }), 202

                    secret = user.get('two_factor_secret')
                    if secret:
                        totp = pyotp.TOTP(secret)
                        if not totp.verify(twofa_code):
                            return jsonify({"error": "Invalid 2FA code"}), 401

                # Update last login (don't block login if this fails)
                try:
                    supabase.table('users').update({
                        'last_login': datetime.now().isoformat()
                    }).eq('id', res.user.id).execute()
                except Exception as update_err:
                    print(f"[WARNING] Failed to update last_login: {update_err}")

                return jsonify({
                    "message": "Login successful",
                    "token": res.session.access_token,
                    "refresh_token": res.session.refresh_token,
                    "user": user
                }), 200
            except Exception as db_err:
                print(f"[ERROR] Database operation failed during login: {db_err}")
                return jsonify({"error": f"Database error: {str(db_err)}"}), 500

        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    try:
        refresh_token = request.json.get('refresh_token')
        res = supabase.auth.refresh_session(refresh_token)
        return jsonify({"token": res.session.access_token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        supabase.auth.sign_out()
        return jsonify({"message": "Logged out"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/2fa/enable', methods=['POST'])
def enable_2fa():
    try:
        user_id = request.json.get('user_id')
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        qr_uri = totp.provisioning_uri(name=user_id, issuer_name="SmartOS")

        supabase.table('users').update({'two_factor_secret': secret}).eq('id', user_id).execute()

        return jsonify({"qr_uri": qr_uri, "secret": secret}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/2fa/verify', methods=['POST'])
def verify_2fa():
    try:
        user_id = request.json.get('user_id')
        code = request.json.get('code')

        user_res = supabase.table('users').select('two_factor_secret').eq('id', user_id).execute()
        if user_res.data:
            secret = user_res.data[0]['two_factor_secret']
            totp = pyotp.TOTP(secret)
            if totp.verify(code):
                supabase.table('users').update({'two_factor_enabled': True}).eq('id', user_id).execute()
                return jsonify({"message": "2FA enabled"}), 200

        return jsonify({"error": "Invalid code"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
