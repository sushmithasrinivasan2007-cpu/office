"""
Analytics Routes - Performance Reports & Metrics
Dashboard data, employee reports, benchmarks
"""
from flask import Blueprint, request, jsonify
from services.analytics_service import analytics_service
from utils.supabase_client import supabase
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics_bp', __name__)

@analytics_bp.route('/dashboard/<company_id>', methods=['GET'])
def company_dashboard(company_id):
    """Get company-level dashboard metrics"""
    try:
        if not company_id or company_id == 'undefined' or company_id == 'null':
            return jsonify({"error": "Invalid company ID"}), 400
        days = int(request.args.get('days', 30))
        result, status = analytics_service.get_company_dashboard(company_id, days)
        return jsonify(result), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/employee/<employee_id>', methods=['GET'])
def employee_report(employee_id):
    """Get detailed report for single employee"""
    try:
        days = int(request.args.get('days', 30))
        result, status = analytics_service.get_employee_report(employee_id, days)
        return jsonify(result), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/benchmark/<company_id>', methods=['GET'])
def team_benchmark(company_id):
    """Compare employees against team average"""
    try:
        if not company_id or company_id == 'undefined' or company_id == 'null':
            return jsonify({"error": "Invalid company ID"}), 400
        result, status = analytics_service.get_team_benchmark(company_id)
        return jsonify(result), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/at-risk-tasks/<company_id>', methods=['GET'])
def at_risk_tasks(company_id):
    """Get tasks predicted to be delayed"""
    try:
        result, status = analytics_service.predict_delayed_tasks(company_id)
        return jsonify(result), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/productivity-trend', methods=['GET'])
def productivity_trend():
    """Daily productivity trend for last 30 days"""
    try:
        company_id = request.args.get('company_id')
        if not company_id or company_id == 'undefined' or company_id == 'null':
            return jsonify({"trend": []}), 200
        days = int(request.args.get('days', 30))

        tasks_res = supabase.table('tasks').select('*').eq('company_id', company_id).gte(
            'created_at', (datetime.now() - timedelta(days=days)).isoformat()
        ).execute()

        tasks = tasks_res.data or []
        trend = {}

        for task in tasks:
            date = task['created_at'][:10]
            if date not in trend:
                trend[date] = {'created': 0, 'completed': 0}
            trend[date]['created'] += 1
            if task['status'] == 'completed':
                trend[date]['completed'] += 1

        # Sort by date
        sorted_trend = [{'date': k, **v} for k, v in sorted(trend.items())]

        return jsonify({'trend': sorted_trend}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/employee-workload', methods=['GET'])
def employee_workload():
    """Current active task count per employee"""
    try:
        company_id = request.args.get('company_id')

        users_res = supabase.table('users').select('id,name').eq('company_id', company_id).in_('role', ['employee', 'manager']).execute()
        users = users_res.data or []

        workload = []
        for user in users:
            count_res = supabase.table('tasks').select('id').eq('assigned_to', user['id']).in_('status', ['pending', 'in_progress']).execute()
            task_count = len(count_res.data) if count_res.data else 0
            workload.append({
                'employee_id': user['id'],
                'name': user['name'],
                'active_tasks': task_count
            })

        workload.sort(key=lambda x: x['active_tasks'], reverse=True)
        return jsonify({'workload': workload}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500