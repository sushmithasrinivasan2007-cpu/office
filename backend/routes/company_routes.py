"""
Company Routes - Multi-tenant Management
Company CRUD, settings, team management
"""
from flask import Blueprint, request, jsonify
from utils.supabase_client import supabase, supabase_admin
from services.email_automation_service import email_service
from datetime import datetime
import uuid

company_bp = Blueprint('company_bp', __name__)

@company_bp.route('/create', methods=['POST'])
def create_company():
    """Create a new company (tenant)"""
    try:
        data = request.json
        name = data.get('name')
        slug = data.get('slug')
        owner_id = data.get('owner_id')
        subscription_tier = data.get('subscription_tier', 'free')

        if not name or not slug or not owner_id:
            return jsonify({"error": "Name, slug, and owner_id are required"}), 400

        # Check for slug collision and append suffix if needed
        existing_slug = supabase_admin.table('companies').select('id').eq('slug', slug).execute()
        if existing_slug.data:
            slug = f"{slug}-{str(uuid.uuid4())[:4]}"

        # Create company
        company_data = {
            'id': str(uuid.uuid4()),
            'name': name,
            'slug': slug,
            'subscription_tier': subscription_tier,
            'created_at': datetime.now().isoformat()
        }

        # Create company using ADMIN client to bypass RLS
        supabase_admin.table('companies').insert(company_data).execute()

        # Set owner as super_admin using ADMIN client
        supabase_admin.table('users').update({
            'company_id': company_data['id'],
            'role': 'super_admin'
        }).eq('id', owner_id).execute()

        # Create default company settings (optional - table may not have all columns)
        try:
            supabase_admin.table('company_settings').insert({
                'company_id': company_data['id'],
                'created_at': datetime.now().isoformat()
            }).execute()
        except Exception:
            pass  # company_settings is optional

        return jsonify({"message": "Company created", "company": company_data}), 201

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@company_bp.route('/<company_id>', methods=['GET'])
def get_company(company_id):
    """Get company details"""
    try:
        res = supabase.table('companies').select('*').eq('id', company_id).execute()
        if res.data:
            return jsonify({"company": res.data[0]}), 200
        return jsonify({"error": "Company not found"}), 404
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@company_bp.route('/<company_id>/team', methods=['GET'])
def get_team(company_id):
    """Get all users in company"""
    try:
        print(f"[DEBUG] Fetching team for company_id: {company_id}")
        if company_id in ['null', 'undefined', '', None]:
            return jsonify({"team": []}), 200
            
        # Fetch all members linked to this company
        res = supabase_admin.table('users').select('id,name,email,role,is_active').eq('company_id', company_id).execute()
        print(f"[DEBUG] Result data: {res.data}")
        print(f"[DEBUG] Found {len(res.data) if res.data else 0} members")
        members = res.data or []
        
        # Metadata logic temporarily disabled due to missing column in DB
        # for member in members:
        #     if member.get('metadata') and member['metadata'].get('status') == 'pending':
        #         member['is_pending'] = True
                
        return jsonify({"team": members}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@company_bp.route('/<company_id>/invite', methods=['POST'])
def invite_user(company_id):
    """Invite new user to company"""
    try:
        data = request.json
        email = data.get('email')
        name = data.get('name')
        role = data.get('role', 'employee')

        if not email:
            return jsonify({"error": "Email required"}), 400

        # Verify company exists
        comp_check = supabase_admin.table('companies').select('id').eq('id', company_id).execute()
        if not comp_check.data:
            return jsonify({"error": f"Invalid company ID: {company_id}"}), 404

        # 1. Create user in Supabase Auth via Admin API
        try:
            auth_res = supabase_admin.auth.admin.create_user({
                "email": email,
                "email_confirm": True,
                "user_metadata": {"name": name},
                "password": str(uuid.uuid4())
            })
            new_user_id = auth_res.user.id
            print(f"[DEBUG] Created new auth user: {new_user_id}")
        except Exception as auth_err:
            # If user already exists, we need to find their ID to link them
            err_msg = str(auth_err).lower()
            if "already" in err_msg or "registered" in err_msg or "exists" in err_msg or "400" in err_msg:
                print(f"[DEBUG] User {email} already exists in Auth, attempting to link...")
                # Try to find user by email in our public users table first
                existing = supabase_admin.table('users').select('id, company_id').eq('email', email).execute()
                if existing.data:
                    user_data = existing.data[0]
                    if user_data.get('company_id') and user_data['company_id'] != company_id:
                        return jsonify({"error": "User is already a member of another company."}), 400
                    if user_data.get('company_id') == company_id:
                        return jsonify({"message": "User is already a member of your company.", "email": email}), 200
                    new_user_id = user_data['id']
                else:
                    # User is in Auth but not in our 'users' table.
                    # We'll try to find them in Auth to get their ID
                    try:
                        auth_users_res = supabase_admin.auth.admin.list_users()
                        # list_users() returns a list in v2.13.0
                        user_id_found = None
                        for u in auth_users_res:
                            if u.email.lower() == email.lower():
                                user_id_found = u.id
                                break
                        
                        if user_id_found:
                            new_user_id = user_id_found
                        else:
                            return jsonify({"error": "This email is registered but ID could not be retrieved."}), 400
                    except Exception as list_err:
                        print(f"[ERROR] list_users failed: {list_err}")
                        return jsonify({"error": "Could not retrieve existing user information."}), 500
            else:
                print(f"[ERROR] Auth creation failed: {auth_err}")
                raise auth_err
        
        # 2. Create or Update profile in our 'users' table
        print(f"[DEBUG] Upserting user profile for {new_user_id}")
        supabase_admin.table('users').upsert({
            'id': new_user_id,
            'email': email,
            'name': name or email,
            'role': role,
            'company_id': company_id,
            'is_active': False
        }).execute()
        
        # 3. Send invite email - Make this non-blocking/graceful
        try:
            msg, status_code = email_service.send_invite_email(email, name, company_id)
            if status_code != 200:
                print(f"[WARNING] Email failed but user was invited: {msg}")
                return jsonify({
                    "message": "User invited successfully, but invitation email could not be sent. Please share the registration link manually.",
                    "email": email,
                    "warning": "SMTP_ERROR"
                }), 201
        except Exception as e_err:
            print(f"[WARNING] Email service error: {e_err}")
            return jsonify({
                "message": "User invited successfully, but email service encountered an error.",
                "email": email,
                "warning": "EMAIL_SERVICE_ERROR"
            }), 201

        return jsonify({"message": "Invitation sent successfully", "email": email}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@company_bp.route('/<company_id>/settings', methods=['GET', 'PUT'])
def company_settings(company_id):
    """Get or update company settings"""
    try:
        if request.method == 'GET':
            res = supabase.table('company_settings').select('*').eq('company_id', company_id).execute()
            if res.data:
                return jsonify({"settings": res.data[0]}), 200
            return jsonify({"error": "Settings not found"}), 404
        else:
            data = request.json
            supabase.table('company_settings').update(data).eq('company_id', company_id).execute()
            return jsonify({"message": "Settings updated"}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@company_bp.route('/<company_id>/stats', methods=['GET'])
def company_stats(company_id):
    """Quick stats for company card"""
    try:
        from services.analytics_service import analytics_service
        result, status = analytics_service.get_company_dashboard(company_id, 7)
        return jsonify(result), status
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@company_bp.route('/<company_id>/members/<user_id>/role', methods=['PUT'])
def update_member_role(company_id, user_id):
    """Update team member's role"""
    try:
        data = request.json
        new_role = data.get('role')

        if new_role not in ['admin', 'manager', 'employee', 'client']:
            return jsonify({"error": "Invalid role"}), 400

        supabase.table('users').update({'role': new_role}).eq('id', user_id).eq('company_id', company_id).execute()

        return jsonify({"message": f"Role updated to {new_role}"}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@company_bp.route('/<company_id>/members/<user_id>/deactivate', methods=['PUT'])
def deactivate_member(company_id, user_id):
    """Deactivate a team member"""
    try:
        supabase.table('users').update({'is_active': False}).eq('id', user_id).eq('company_id', company_id).execute()
        return jsonify({"message": "Member deactivated"}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500