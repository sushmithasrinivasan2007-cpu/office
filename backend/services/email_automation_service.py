"""
Email Automation Service - SMTP Integration
Sends daily summaries, reminders, weekly reports
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from jinja2 import Template
from utils.supabase_client import supabase, supabase_admin
from utils.email_service import send_email as basic_send_email
import os
from collections import defaultdict

class EmailAutomationService:
    def __init__(self):
        self.smtp_configured = bool(os.getenv('SMTP_USERNAME') and os.getenv('SMTP_PASSWORD'))

    def send_daily_summary(self, user_id):
        """
        Send daily task summary to employee or manager
        """
        try:
            user_res = supabase.table('users').select('*').eq('id', user_id).execute()
            if not user_res.data:
                return {"error": "User not found"}, 404

            user = user_res.data[0]
            company_id = user['company_id']

            # Get today's tasks
            today = datetime.now().strftime('%Y-%m-%d')
            tasks_res = supabase.table('tasks').select('*').eq('assigned_to', user_id).gte('deadline', today).execute()
            tasks = tasks_res.data or []

            pending = [t for t in tasks if t['status'] in ['pending', 'in_progress']]
            completed = [t for t in tasks if t['status'] == 'completed']

            # Attendance check
            att_res = supabase.table('attendance').select('*').eq('user_id', user_id).gte('checkin_time', today).execute()
            checked_in = len(att_res.data) > 0

            # Render HTML email
            html_template = """
            <!DOCTYPE html>
            <html>
            <head><title>Daily Summary - SmartOS</title></head>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px;">
                <h2>Good morning, {{name}}!</h2>
                <p>Here's your productivity update for <strong>{{date}}</strong></p>

                <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3>Today's Focus</h3>
                    {% if pending %}
                        <ul>
                        {% for task in pending %}
                            <li>
                                <strong>{{task.title}}</strong> - {{task.priority}} priority
                                {% if task.deadline %}
                                    <br><small>Due: {{task.deadline}}</small>
                                {% endif %}
                            </li>
                        {% endfor %}
                        </ul>
                    {% else %}
                        <p>No pending tasks! Great work.</p>
                    {% endif %}
                </div>

                <div style="display: flex; justify-content: space-between; margin: 20px 0;">
                    <div style="text-align: center; padding: 15px; background: #e8f5e9; border-radius: 8px; flex: 1; margin: 0 5px;">
                        <h4 style="color: #2e7d32;">{{completed_count}}</h4>
                        <p>Completed Today</p>
                    </div>
                    <div style="text-align: center; padding: 15px; background: #fff3e0; border-radius: 8px; flex: 1; margin: 0 5px;">
                        <h4 style="color: #ef6c00;">{{pending_count}}</h4>
                        <p>In Progress</p>
                    </div>
                    <div style="text-align: center; padding: 15px; background: #e3f2fd; border-radius: 8px; flex: 1; margin: 0 5px;">
                        <h4 style="color: #1565c0;">{{'✅' if checked_in else '⚠️'}}</h4>
                        <p>Checked In</p>
                    </div>
                </div>

                <p style="margin-top: 30px; color: #666;">
                    <a href="https://yourapp.com/tasks" style="background: #1976d2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">Open Dashboard</a>
                </p>
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                <p style="color: #999; font-size: 12px;">
                    Smart Office OS • You received this email because you're registered.
                    <br><a href="{{unsubscribe_link}}" style="color: #999;">Manage notifications</a>
                </p>
            </body>
            </html>
            """

            template = Template(html_template)
            html_body = template.render(
                name=user['name'],
                date=today,
                pending=pending,
                completed=completed,
                completed_count=len(completed),
                pending_count=len(pending),
                checked_in=checked_in,
                unsubscribe_link=f"https://yourapp.com/notifications/unsubscribe?user={user_id}"
            )

            subject = f"Daily Summary - {today}"
            if not self.smtp_configured:
                print(f"[DEV MODE] Email to: {user.get('email', 'N/A')} | Subject: {subject}")
                return {"message": "Email simulated (SMTP not configured)"}, 200

            success = basic_send_email(user['email'], subject, html_body)
            return {"sent": success, "recipient": user['email']}, 200 if success else 500

        except Exception as e:
            return {"error": str(e)}, 500

    def send_overdue_reminder(self, task_id):
        """Remind employee about overdue task"""
        try:
            task_res = supabase.table('tasks').select('*').eq('id', task_id).execute()
            if not task_res.data:
                return {"error": "Task not found"}, 404

            task = task_res.data[0]
            emp_res = supabase.table('users').select('email,name').eq('id', task['assigned_to']).execute()
            if not emp_res.data:
                return {"error": "Employee not found"}, 404

            emp = emp_res.data[0]

            subject = f"⚠️ Overdue Task: {task['title']}"
            html_body = f"""
            <h2>Task Overdue</h2>
            <p>Hi {emp['name']},</p>
            <p>The following task is overdue:</p>
            <div style="background: #ffebee; padding: 15px; border-left: 4px solid #c62828;">
                <strong>{task['title']}</strong><br>
                Due: {task['deadline']}<br>
                {task.get('description', '')[:200]}...
            </div>
            <p>Please update the status or contact your manager.</p>
            <p><a href="https://yourapp.com/tasks/{task['id']}">View Task</a></p>
            """

            if not self.smtp_configured:
                print(f"[DEV MODE] Overdue reminder to {emp['email']} for task {task['title']}")
                return {"message": "Reminder simulated"}, 200

            success = basic_send_email(emp['email'], subject, html_body)
            return {"sent": success}, 200 if success else 500

        except Exception as e:
            return {"error": str(e)}, 500

    def send_weekly_report(self, company_id, manager_id):
        """Send comprehensive weekly performance report to manager"""
        try:
            # Get company data for past week
            week_ago = datetime.now() - timedelta(days=7)

            tasks_res = supabase.table('tasks').select('*').eq('company_id', company_id).gte('created_at', week_ago.isoformat()).execute()
            tasks = tasks_res.data or []

            completed_this_week = [t for t in tasks if t['status'] == 'completed' and t.get('completed_at')]
            total_completed = len(completed_this_week)
            total_value = sum(t.get('payment_amount', 0) for t in completed_this_week)

            # Top performers
            emp_stats = defaultdict(lambda: {'completed': 0, 'value': 0})
            for task in completed_this_week:
                if task.get('assigned_to'):
                    emp_stats[task['assigned_to']]['completed'] += 1
                    emp_stats[task['assigned_to']]['value'] += task.get('payment_amount', 0)

            top_emp = sorted(emp_stats.items(), key=lambda x: x[1]['completed'], reverse=True)[:3]
            top_names = []
            for emp_id, stats in top_emp:
                emp_res = supabase.table('users').select('name').eq('id', emp_id).execute()
                if emp_res.data:
                    top_names.append(f"{emp_res.data[0]['name']} - {stats['completed']} tasks")

            # Manager email
            mgr_res = supabase.table('users').select('email,name').eq('id', manager_id).execute()
            if not mgr_res.data:
                return {"error": "Manager not found"}, 404

            manager = mgr_res.data[0]

            subject = f"Weekly Performance Report - {datetime.now().strftime('%b %d, %Y')}"
            html_body = f"""
            <h1>Weekly Report</h1>
            <p>Dear {manager['name']},</p>
            <p>Here's your team's performance for the past week:</p>

            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr style="background: #f5f5f5;">
                    <th style="padding: 10px; text-align: left;">Metric</th>
                    <th style="padding: 10px; text-align: right;">Value</th>
                </tr>
                <tr><td style="padding: 10px; border-bottom: 1px solid #eee;">Tasks Completed</td><td style="padding: 10px; text-align: right;"><strong>{total_completed}</strong></td></tr>
                <tr><td style="padding: 10px; border-bottom: 1px solid #eee;">Total Value</td><td style="padding: 10px; text-align: right;"><strong>₹{total_value:,.2f}</strong></td></tr>
                <tr><td style="padding: 10px; border-bottom: 1px solid #eee;">New Tasks Created</td><td style="padding: 10px; text-align: right;">{len(tasks)}</td></tr>
            </table>

            <h3>Top Performers</h3>
            <ul>
                {"".join(f'<li>{n}</li>' for n in top_names) if top_names else '<li>No tasks completed this week</li>'}
            </ul>

            <p><a href="https://yourapp.com/reports/weekly">View Full Report</a></p>
            """

            if not self.smtp_configured:
                print(f"[DEV MODE] Weekly report to {manager['email']}")
                return {"message": "Report simulated"}, 200

            success = basic_send_email(manager['email'], subject, html_body)
            return {"sent": success}, 200 if success else 500

        except Exception as e:
            return {"error": str(e)}, 500

    def send_task_assignment_notification(self, task_id):
        """Notify employee of new task assignment"""
        try:
            task_res = supabase.table('tasks').select('*').eq('id', task_id).execute()
            if not task_res.data:
                return {"error": "Task not found"}, 404

            task = task_res.data[0]
            emp_res = supabase.table('users').select('email,name').eq('id', task['assigned_to']).execute()
            if not emp_res.data:
                return {"error": "Employee not found"}, 404

            emp = emp_res.data[0]

            subject = f"New Task Assigned: {task['title']}"
            html_body = f"""
            <h2>New Task Assigned</h2>
            <p>Hi {emp['name']},</p>
            <p>You've been assigned a new task:</p>
            <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 15px 0;">
                <h3>{task['title']}</h3>
                <p>{task.get('description', '')[:300]}</p>
                <p><strong>Priority:</strong> {task['priority']}</p>
                <p><strong>Deadline:</strong> {task.get('deadline', 'Not set')}</p>
            </div>
            <p><a href="https://yourapp.com/tasks/{task['id']}">Start Working</a></p>
            """

            if not self.smtp_configured:
                print(f"[DEV MODE] Task assignment to {emp['email']}")
                return {"message": "Notification simulated"}, 200

            success = basic_send_email(emp['email'], subject, html_body)
            return {"sent": success}, 200 if success else 500

        except Exception as e:
            return {"error": str(e)}, 500

    def send_invite_email(self, email, name, company_id):
        """Send invitation email to join company"""
        try:
            # Get company info using ADMIN client
            comp_res = supabase_admin.table('companies').select('name').eq('id', company_id).execute()
            company_name = comp_res.data[0]['name'] if comp_res.data else "SmartOS"

            subject = f"You're invited to join {company_name} on SmartOS"
            
            html_template = """
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px;">
                <h2 style="color: #2563eb;">Welcome to SmartOS!</h2>
                <p>Hi {{name}},</p>
                <p>You have been invited to join <strong>{{company_name}}</strong> as a team member.</p>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center;">
                    <p>Click the link below to accept your invitation and set up your account:</p>
                    <a href="{{invite_link}}" style="background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">Join the Team</a>
                </div>
                <p>If you didn't expect this invitation, you can safely ignore this email.</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #999; font-size: 12px;">Smart Office OS • Automated Notification</p>
            </body>
            </html>
            """
            
            template = Template(html_template)
            html_body = template.render(
                name=name or email,
                company_name=company_name,
                invite_link=f"http://localhost:5173/register?company_id={company_id}&email={email}"
            )

            if not self.smtp_configured:
                print(f"[DEV MODE] Invite email to: {email} | Company: {company_name}")
                return {"message": "Invite simulated"}, 200

            success = basic_send_email(email, subject, html_body)
            if not success:
                return {"error": "SMTP delivery failed. Check server logs."}, 500
            return {"sent": True}, 200

        except Exception as e:
            return {"error": str(e)}, 500

email_service = EmailAutomationService()