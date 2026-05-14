"""
Email Routes - Automated Email Endpoints
Daily summaries, reminders, weekly reports
"""
from flask import Blueprint, request, jsonify
from services.email_automation_service import email_service
from utils.supabase_client import supabase
from datetime import datetime

email_bp = Blueprint('email_bp', __name__)

@email_bp.route('/daily-summary/<user_id>', methods=['POST'])
def send_daily_summary(user_id):
    """Trigger daily summary email"""
    try:
        result, status = email_service.send_daily_summary(user_id)
        return jsonify(result), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@email_bp.route('/overdue-reminder/<task_id>', methods=['POST'])
def send_overdue_reminder(task_id):
    """Send overdue task reminder"""
    try:
        result, status = email_service.send_overdue_reminder(task_id)
        return jsonify(result), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@email_bp.route('/weekly-report/<company_id>', methods=['POST'])
def send_weekly_report(company_id):
    """Send weekly performance report to all managers"""
    try:
        # Get all managers in company
        mgrs_res = supabase.table('users').select('id').eq('company_id', company_id).eq('role', 'manager').execute()
        managers = mgrs_res.data or []

        results = []
        for mgr in managers:
            result, status = email_service.send_weekly_report(company_id, mgr['id'])
            results.append({'manager_id': mgr['id'], 'sent': status == 200})

        return jsonify({'results': results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@email_bp.route('/task-assigned/<task_id>', methods=['POST'])
def notify_task_assigned(task_id):
    """Notify employee of new task"""
    try:
        result, status = email_service.send_task_assignment_notification(task_id)
        return jsonify(result), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@email_bp.route('/bulk-notify', methods=['POST'])
def bulk_notify():
    """Send notification to multiple users"""
    try:
        data = request.json
        user_ids = data.get('user_ids', [])
        subject = data.get('subject')
        body = data.get('body')

        results = []
        for uid in user_ids:
            user_res = supabase.table('users').select('email').eq('id', uid).execute()
            if user_res.data:
                # Use basic email service
                from utils.email_service import send_email
                success = send_email(user_res.data[0]['email'], subject, body)
                results.append({'user_id': uid, 'sent': success})

        return jsonify({'results': results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500