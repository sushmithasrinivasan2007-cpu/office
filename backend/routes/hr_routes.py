"""
HR Routes - Leave & Attendance Management
"""
from flask import Blueprint, request, jsonify
from utils.supabase_client import supabase
from services.email_automation_service import email_service
from datetime import datetime, timedelta

hr_bp = Blueprint('hr_bp', __name__)

@hr_bp.route('/leave-requests', methods=['GET'])
def get_leave_requests():
    try:
        company_id = request.args.get('company_id')
        user_id = request.args.get('user_id')
        status = request.args.get('status', 'pending')

        query = supabase.table('leave_requests').select('*').eq('status', status)

        if company_id:
            query = query.eq('company_id', company_id)
        if user_id:
            query = query.eq('user_id', user_id)

        res = query.order('created_at', desc=True).execute()
        return jsonify({'requests': res.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@hr_bp.route('/leave-requests', methods=['POST'])
def create_leave_request():
    try:
        data = request.json
        leave_data = {
            'user_id': data.get('user_id'),
            'company_id': data.get('company_id'),
            'leave_type': data.get('leave_type'),
            'start_date': data.get('start_date'),
            'end_date': data.get('end_date'),
            'total_days': data.get('total_days'),
            'reason': data.get('reason'),
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        res = supabase.table('leave_requests').insert(leave_data).execute()
        return jsonify({'request': res.data[0]}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@hr_bp.route('/leave-requests/<request_id>/approve', methods=['POST'])
def approve_leave(request_id):
    try:
        manager_id = request.json.get('manager_id')
        supabase.table('leave_requests').update({
            'status': 'approved',
            'approved_by': manager_id,
            'approved_at': datetime.now().isoformat()
        }).eq('id', request_id).execute()
        return jsonify({"message": "Leave approved"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@hr_bp.route('/leave-requests/<request_id>/reject', methods=['POST'])
def reject_leave(request_id):
    try:
        manager_id = request.json.get('manager_id')
        reason = request.json.get('reason', '')
        supabase.table('leave_requests').update({
            'status': 'rejected',
            'approved_by': manager_id,
            'approved_at': datetime.now().isoformat(),
            'rejection_reason': reason
        }).eq('id', request_id).execute()
        return jsonify({"message": "Leave rejected"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@hr_bp.route('/attendance/daily', methods=['GET'])
def daily_attendance():
    try:
        company_id = request.args.get('company_id')
        date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))

        res = supabase.table('attendance').select('*').eq('company_id', company_id).gte('checkin_time', date).lt('checkin_time', date + ' 23:59:59').execute()
        return jsonify({'attendance': res.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@hr_bp.route('/attendance/summary', methods=['GET'])
def attendance_summary():
    try:
        company_id = request.args.get('company_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        res = supabase.table('daily_attendance_summary').select('*').eq('company_id', company_id).gte('date', start_date).lte('date', end_date).execute()
        return jsonify({'summary': res.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@hr_bp.route('/employees/active', methods=['GET'])
def get_active_employees():
    try:
        company_id = request.args.get('company_id')
        res = supabase.table('users').select('id,name,email,role,last_login').eq('company_id', company_id).eq('is_active', True).execute()
        return jsonify({'employees': res.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500