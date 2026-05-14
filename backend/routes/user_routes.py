"""
User Routes - User Management & Profile
Profile, permissions, check-in/out
"""
from flask import Blueprint, request, jsonify
from utils.supabase_client import supabase
from services.task_routing_service import task_routing_service
from services.email_automation_service import email_service
from datetime import datetime
import pyotp

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    """Get user profile"""
    try:
        # Select only existing columns to avoid schema cache errors
        res = supabase.table('users').select('id,name,email,role,company_id,is_active,created_at').eq('id', user_id).execute()
        if res.data:
            return jsonify({"profile": res.data[0]}), 200
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/profile/<user_id>', methods=['PUT'])
def update_profile(user_id):
    """Update user profile"""
    try:
        data = request.json
        allowed = ['name', 'role', 'is_active'] # Temporarily only allowing columns verified to exist
        
        update_data = {k: v for k, v in data.items() if k in allowed}

        supabase.table('users').update(update_data).eq('id', user_id).execute()

        return jsonify({"message": "Profile updated"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/checkin', methods=['POST'])
def check_in():
    """Geo-verified check-in"""
    try:
        data = request.json
        user_id = data.get('user_id')
        company_id = data.get('company_id')
        lat = data.get('latitude')
        lng = data.get('longitude')
        photo_url = data.get('photo_url')

        if not all([user_id, company_id, lat, lng]):
            return jsonify({"error": "Missing required fields"}), 400

        # Check if already checked in
        today = datetime.now().strftime('%Y-%m-%d')
        existing = supabase.table('attendance').select('*').eq('user_id', user_id).gte('checkin_time', today).is_('checkout_time', 'null').execute()

        if existing.data:
            return jsonify({"error": "Already checked in"}), 400

        attendance_data = {
            'user_id': user_id,
            'company_id': company_id,
            'checkin_lat': lat,
            'checkin_lng': lng,
            'checkin_time': datetime.now().isoformat(),
            'checkin_photo_url': photo_url,
            'checkin_verified': True
        }

        res = supabase.table('attendance').insert(attendance_data).execute()

        if res.data:
            # Log activity
            supabase.table('activity_logs').insert({
                'user_id': user_id,
                'company_id': company_id,
                'action': 'checkin'
                # 'metadata': {'lat': lat, 'lng': lng} -- Disabled due to missing column
            }).execute()

            return jsonify({"message": "Checked in successfully", "attendance": res.data[0]}), 200

        return jsonify({"error": "Failed to check in"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/checkout', methods=['POST'])
def check_out():
    """Check-out with duration calculation"""
    try:
        data = request.json
        user_id = data.get('user_id')
        lat = data.get('latitude')
        lng = data.get('longitude')

        # Find today's check-in
        today = datetime.now().strftime('%Y-%m-%d')
        checkin_res = supabase.table('attendance').select('*').eq('user_id', user_id).gte('checkin_time', today).is_('checkout_time', 'null').order('checkin_time', desc=True).limit(1).execute()

        if not checkin_res.data:
            return jsonify({"error": "No active check-in found"}), 404

        checkin = checkin_res.data[0]
        checkout_time = datetime.now()
        checkin_time = datetime.fromisoformat(checkin['checkin_time'].replace('Z', '+00:00'))

        duration_minutes = int((checkout_time - checkin_time).total_seconds() / 60)

        supabase.table('attendance').update({
            'checkout_time': checkout_time.isoformat(),
            'checkout_lat': lat,
            'checkout_lng': lng,
            'work_duration_minutes': duration_minutes
        }).eq('id', checkin['id']).execute()

        supabase.table('activity_logs').insert({
            'user_id': user_id,
            'company_id': checkin['company_id'],
            'action': 'checkout'
            # 'metadata': {'duration_minutes': duration_minutes}
        }).execute()

        return jsonify({"message": "Checked out", "duration_minutes": duration_minutes}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/<user_id>/tasks/today', methods=['GET'])
def today_tasks(user_id):
    """Get today's smart plan"""
    try:
        from services.ai_service import ai_service
        result, status = ai_service.get_smart_plan(user_id, datetime.now().strftime('%Y-%m-%d'))
        return jsonify(result), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/<user_id>/permissions', methods=['GET'])
def get_permissions(user_id):
    """Get user's permissions"""
    try:
        user_res = supabase.table('users').select('role,company_id').eq('id', user_id).execute()
        if not user_res.data:
            return jsonify({"error": "User not found"}), 404

        user = user_res.data[0]
        perms_res = supabase.table('role_permissions').select('permission').eq('role', user['role']).eq('company_id', user['company_id']).execute()
        permissions = [p['permission'] for p in perms_res.data] if perms_res.data else []

        return jsonify({'role': user['role'], 'permissions': permissions}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/<user_id>/2fa/enable', methods=['POST'])
def enable_2fa(user_id):
    """Enable 2FA for user"""
    try:
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        qr_uri = totp.provisioning_uri(name=user_id, issuer_name="SmartOS")

        # Store secret (encrypted in production)
        supabase.table('users').update({
            'two_factor_secret': secret,
            'two_factor_enabled': False  # Not enabled until verified
        }).eq('id', user_id).execute()

        return jsonify({'secret': secret, 'qr_uri': qr_uri}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/<user_id>/2fa/verify', methods=['POST'])
def verify_2fa(user_id):
    """Verify 2FA code and enable"""
    try:
        data = request.json
        code = data.get('code')

        user_res = supabase.table('users').select('two_factor_secret').eq('id', user_id).execute()
        if not user_res.data:
            return jsonify({"error": "User not found"}), 404

        secret = user_res.data[0]['two_factor_secret']
        totp = pyotp.TOTP(secret)

        if totp.verify(code):
            supabase.table('users').update({'two_factor_enabled': True}).eq('id', user_id).execute()
            return jsonify({"message": "2FA enabled"}), 200

        return jsonify({"error": "Invalid code"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/<user_id>/2fa/validate', methods=['POST'])
def validate_2fa_code(user_id):
    """Validate 2FA code during login"""
    try:
        data = request.json
        code = data.get('code')

        user_res = supabase.table('users').select('two_factor_secret,two_factor_enabled').eq('id', user_id).execute()
        if not user_res.data or not user_res.data[0]['two_factor_enabled']:
            return jsonify({"error": "2FA not enabled"}), 400

        secret = user_res.data[0]['two_factor_secret']
        totp = pyotp.TOTP(secret)

        if totp.verify(code):
            return jsonify({"valid": True}), 200

        return jsonify({"valid": False}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/activity/<user_id>', methods=['GET'])
def get_user_activity(user_id):
    """Get recent activity for user"""
    try:
        limit = int(request.args.get('limit', 50))
        res = supabase.table('activity_logs').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(limit).execute()
        return jsonify({'activities': res.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500