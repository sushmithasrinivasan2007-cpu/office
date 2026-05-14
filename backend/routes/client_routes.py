"""
Client Routes - CRM Module
Client management with full CRUD
"""
from flask import Blueprint, request, jsonify
from utils.supabase_client import supabase
from datetime import datetime

# This would be imported from a service layer
client_bp = Blueprint('client_bp', __name__)

@client_bp.route('/', methods=['GET'])
def get_clients():
    try:
        company_id = request.args.get('company_id')
        res = supabase.table('clients').select('*').eq('company_id', company_id).execute()
        return jsonify({'clients': res.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@client_bp.route('/', methods=['POST'])
def create_client():
    try:
        data = request.json
        client_data = {
            'company_id': data.get('company_id'),
            'name': data.get('name'),
            'email': data.get('email'),
            'phone': data.get('phone'),
            'address': data.get('address'),
            'gstin': data.get('gstin'),
            'pan': data.get('pan'),
            'contact_person': data.get('contact_person'),
            'notes': data.get('notes'),
            'tags': data.get('tags', []),
            'created_by': data.get('created_by'),
            'created_at': datetime.now().isoformat()
        }
        res = supabase.table('clients').insert(client_data).execute()
        
        if not res.data:
            return jsonify({'message': 'Client created successfully', 'id': 'new'}), 201
            
        return jsonify({'client': res.data[0]}), 201
    except Exception as e:
        print(f"Error creating client: {str(e)}")
        return jsonify({"error": str(e)}), 500

@client_bp.route('/<client_id>', methods=['PUT'])
def update_client(client_id):
    try:
        data = request.json
        allowed = ['name', 'email', 'phone', 'address', 'gstin', 'pan', 'contact_person', 'notes', 'tags']
        update_data = {k: v for k, v in data.items() if k in allowed}
        supabase.table('clients').update(update_data).eq('id', client_id).execute()
        return jsonify({"message": "Client updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@client_bp.route('/<client_id>', methods=['DELETE'])
def delete_client(client_id):
    try:
        supabase.table('clients').delete().eq('id', client_id).execute()
        return jsonify({"message": "Client deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@client_bp.route('/<client_id>/tasks', methods=['GET'])
def get_client_tasks(client_id):
    try:
        res = supabase.table('tasks').select('*').eq('client_id', client_id).execute()
        return jsonify({'tasks': res.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500