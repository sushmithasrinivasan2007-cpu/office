"""
WebSocket Service - Real-time Notifications
Using Flask-SocketIO for live updates
"""
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
from utils.supabase_client import supabase
import json

socketio = SocketIO(async_mode='eventlet', cors_allowed_origins='*')

connected_users = {}  # user_id -> socket_id mapping

@socketio.on('connect')
def handle_connect():
    user_id = request.args.get('user_id')
    if user_id:
        connected_users[user_id] = request.sid
        join_room(f'user_{user_id}')
        emit('connected', {'message': 'Connected to real-time notifications'})

@socketio.on('disconnect')
def handle_disconnect():
    user_id = request.args.get('user_id')
    if user_id and user_id in connected_users:
        del connected_users[user_id]

def send_notification(user_id, notification_data):
    """Send real-time notification to specific user"""
    room = f'user_{user_id}'
    socketio.emit('notification', notification_data, room=room)

def broadcast_to_company(company_id, notification_data):
    """Broadcast to all users in a company"""
    socketio.emit('notification', notification_data, room=f'company_{company_id}')

def notify_task_assigned(task_id, assignee_id, company_id):
    """Real-time notification for task assignment"""
    send_notification(assignee_id, {
        'type': 'task_assigned',
        'title': 'New Task Assigned',
        'message': f'You have been assigned a new task (ID: {task_id})',
        'task_id': task_id,
        'action_url': f'/tasks/{task_id}'
    })

def notify_task_completed(task_id, reviewer_id, company_id):
    """Notify manager when task is completed and needs review"""
    broadcast_to_company(company_id, {
        'type': 'approval_required',
        'title': 'Task Completed - Awaiting Approval',
        'message': f'Task {task_id} has been completed and needs your approval',
        'task_id': task_id,
        'action_url': f'/tasks/{task_id}'
    })

def notify_payment_received(payment_id, user_id, amount):
    """Notify employee of payment"""
    send_notification(user_id, {
        'type': 'payment_received',
        'title': 'Payment Received',
        'message': f'₹{amount} has been credited to your account',
        'payment_id': payment_id
    })

def notify_risk_alert(task_id, user_id, risk_score):
    """Alert about high-risk task"""
    send_notification(user_id, {
        'type': 'risk_alert',
        'title': 'Task Risk Alert',
        'message': f'Task may be delayed. Risk score: {risk_score}%',
        'task_id': task_id,
        'priority': 'high'
    })