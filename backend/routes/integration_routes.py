"""
Integration Routes - Third-party Connections
Slack, Zoom, Google Drive, GitHub, etc.
"""
from flask import Blueprint, request, jsonify
from services.integration_service import integration_service
from utils.supabase_client import supabase
import json

integration_bp = Blueprint('integration_bp', __name__)

@integration_bp.route('/connect', methods=['POST'])
def connect_integration():
    """Store OAuth credentials for integration"""
    try:
        data = request.json
        company_id = data.get('company_id')
        service = data.get('service')
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        config = data.get('config', {})

        if not all([company_id, service, access_token]):
            return jsonify({"error": "Missing required fields"}), 400

        # Upsert integration
        existing = supabase.table('integrations').select('id').eq('company_id', company_id).eq('service', service).execute()

        payload = {
            'company_id': company_id,
            'service': service,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'config': config,
            'is_active': True,
            'updated_at': json.dumps({'updated_at': 'now()'}, default=str)
        }

        if existing.data:
            supabase.table('integrations').update(payload).eq('id', existing.data[0]['id']).execute()
            msg = "Integration updated"
        else:
            supabase.table('integrations').insert(payload).execute()
            msg = "Integration connected"

        return jsonify({"message": msg}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@integration_bp.route('/<service>/test', methods=['POST'])
def test_integration(service):
    """Test connection to service"""
    try:
        data = request.json
        company_id = data.get('company_id')

        if service == 'slack':
            channel = data.get('channel', '#general')
            msg = data.get('message', 'Test message from SmartOS')
            result, status = integration_service.send_slack_notification(company_id, channel, msg)
            return jsonify(result), status
        elif service == 'zoom':
            result, status = integration_service.create_zoom_meeting(company_id, "Test Meeting", 30)
            return jsonify(result), status
        else:
            return jsonify({"error": f"Test not implemented for {service}"}), 501

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@integration_bp.route('/slack/task-notification', methods=['POST'])
def slack_task_notification():
    """Send task assignment to Slack"""
    try:
        data = request.json
        result, status = integration_service.send_slack_notification(
            data['company_id'],
            data.get('channel', '#tasks'),
            data.get('message', 'New task assigned!'),
            data.get('task_id')
        )
        return jsonify(result), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@integration_bp.route('/zoom/create-meeting', methods=['POST'])
def create_zoom_meeting_endpoint():
    """Create Zoom meeting for task discussion"""
    try:
        data = request.json
        result, status = integration_service.create_zoom_meeting(
            data['company_id'],
            data['topic'],
            data.get('duration', 60),
            data.get('start_time')
        )
        return jsonify(result), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@integration_bp.route('/github/link', methods=['POST'])
def link_github_issue_endpoint():
    """Link GitHub issue to task"""
    try:
        data = request.json
        result, status = integration_service.link_github_issue(
            data['company_id'],
            data['task_id'],
            data['repo'],
            data['issue_number']
        )
        return jsonify(result), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@integration_bp.route('/list/<company_id>', methods=['GET'])
def list_integrations(company_id):
    """List all integrations for company"""
    try:
        res = supabase.table('integrations').select('*').eq('company_id', company_id).execute()
        return jsonify({'integrations': res.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@integration_bp.route('/disable/<integration_id>', methods=['POST'])
def disable_integration(integration_id):
    """Disable an integration"""
    try:
        supabase.table('integrations').update({'is_active': False}).eq('id', integration_id).execute()
        return jsonify({"message": "Integration disabled"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500