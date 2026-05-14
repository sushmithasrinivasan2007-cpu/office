"""
AI Routes - Native AI Assistant Endpoints
parse-task, summarize, extract, predict-risk, smart-plan, ask
"""
from flask import Blueprint, request, jsonify
from services.ai_service import ai_service
from utils.supabase_client import supabase
from datetime import datetime
from services.email_automation_service import email_service

ai_bp = Blueprint('ai_bp', __name__)

@ai_bp.route('/parse-task', methods=['POST'])
def parse_task():
    """Convert natural language to structured task"""
    try:
        data = request.json
        text = data.get('text')
        user_id = data.get('user_id')
        company_id = data.get('company_id')

        if not text:
            return jsonify({"error": "Text is required"}), 400

        result, status = ai_service.parse_task(text, user_id, company_id)
        return jsonify(result), status

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ai_bp.route('/summarize', methods=['POST'])
def summarize():
    """Generate executive summary of tasks/project"""
    try:
        data = request.json
        tasks = data.get('tasks', [])
        user_id = data.get('user_id')
        company_id = data.get('company_id')

        result, status = ai_service.summarize_project(tasks, user_id, company_id)
        return jsonify(result), status

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ai_bp.route('/extract', methods=['POST'])
def extract():
    """Extract structured data from document/text"""
    try:
        data = request.json
        document_text = data.get('text')
        document_type = data.get('type')
        user_id = data.get('user_id')
        company_id = data.get('company_id')

        if not document_text:
            return jsonify({"error": "Document text is required"}), 400

        result, status = ai_service.extract_info_from_document(document_text, user_id, company_id, document_type)
        return jsonify(result), status

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ai_bp.route('/predict-risk/<task_id>', methods=['GET'])
def predict_risk(task_id):
    """Predict delay risk for a task"""
    try:
        user_id = request.args.get('user_id')
        company_id = request.args.get('company_id')

        # Get task data
        task_res = supabase.table('tasks').select('*').eq('id', task_id).execute()
        if not task_res.data:
            return jsonify({"error": "Task not found"}), 404

        task = task_res.data[0]

        # Get user data
        user_res = supabase.table('users').select('*').eq('id', task['assigned_to']).execute()
        if not user_res.data:
            return jsonify({"error": "Assigned user not found"}), 404

        user = user_res.data[0]

        result, status = ai_service.predict_task_risk(task, user, company_id or task['company_id'])
        return jsonify(result), status

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ai_bp.route('/smart-plan', methods=['GET'])
def get_smart_plan():
    """Get AI-generated task plan for employee"""
    try:
        user_id = request.args.get('user_id')
        date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))

        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        result, status = ai_service.get_smart_plan(user_id, date)
        return jsonify(result), status

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ai_bp.route('/ask', methods=['POST'])
def ask_assistant():
    """Ask AI assistant a question about the project"""
    try:
        data = request.json
        query = data.get('query')
        user_id = data.get('user_id')
        company_id = data.get('company_id')

        if not query:
            return jsonify({"error": "Query is required"}), 400

        result, status = ai_service.answer_query(query, user_id, company_id)
        return jsonify(result), status

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ai_bp.route('/auto-assign/<task_id>', methods=['POST'])
def auto_assign_task(task_id):
    """Automatically find best employee for task using AI routing"""
    try:
        from services.task_routing_service import task_routing_service

        task_res = supabase.table('tasks').select('*').eq('id', task_id).execute()
        if not task_res.data:
            return jsonify({"error": "Task not found"}), 404

        task = task_res.data[0]
        result, status = task_routing_service.find_best_assignee(task, task['company_id'])

        if status == 200 and result.get('best_assignee'):
            # Auto-assign
            supabase.table('tasks').update({
                'assigned_to': result['best_assignee']['id'],
                'ai_suggested_priority': result['best_assignee'].get('ai_suggested_priority')
            }).eq('id', task_id).execute()

            # Send notification
            email_service.send_task_assignment_notification(task_id)

            return jsonify({"message": "Task auto-assigned", "assignee": result['best_assignee'], "score": result['score']}), 200

        return jsonify({"error": "No suitable assignee found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500