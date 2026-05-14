"""
Analytics Service - Performance Metrics & Insights
Generates reports, tracks KPIs, identifies trends
"""
from datetime import datetime, timedelta
from collections import defaultdict
from utils.supabase_client import supabase
import json

class AnalyticsService:
    def get_company_dashboard(self, company_id, days=30):
        """High-level dashboard metrics for a company"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Tasks metrics (core - always present)
            tasks_res = supabase.table('tasks').select('*').eq('company_id', company_id).execute()
            tasks = tasks_res.data or []

            total_tasks = len(tasks)
            completed = len([t for t in tasks if t['status'] == 'completed'])
            in_progress = len([t for t in tasks if t['status'] == 'in_progress'])
            overdue = 0
            for t in tasks:
                try:
                    if t.get('deadline') and t['status'] not in ['completed', 'cancelled']:
                        dl = datetime.fromisoformat(t['deadline'].replace('Z', '').replace('+00:00', ''))
                        if dl < end_date:
                            overdue += 1
                except Exception:
                    pass

            completion_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0

            # Payments - optional table, skip if missing
            total_payments = 0
            pending_payments = 0
            try:
                payments_res = supabase.table('payments').select('amount,status').eq('company_id', company_id).execute()
                payments = payments_res.data or []
                total_payments = sum(p.get('amount', 0) for p in payments if p.get('status') == 'completed')
                pending_payments = len([p for p in payments if p.get('status') == 'pending'])
            except Exception:
                pass

            # Employee performance - skip views if missing
            top_performers = []
            risk_employees = []
            try:
                employees_res = supabase.table('users').select('id,name,role').eq('company_id', company_id).execute()
                employees = employees_res.data or []
            except Exception:
                employees = []

            # Attendance - optional
            present_days = 0
            try:
                attendance_res = supabase.table('attendance').select('checkin_time').gte(
                    'checkin_time', start_date.isoformat()
                ).execute()
                attendance = attendance_res.data or []
                present_days = len(set(a['checkin_time'][:10] for a in attendance if a.get('checkin_time')))
            except Exception:
                pass

            return {
                'period': f'{days} days',
                'tasks': {
                    'total': total_tasks,
                    'completed': completed,
                    'in_progress': in_progress,
                    'overdue': overdue,
                    'completion_rate': round(completion_rate, 1)
                },
                'payments': {
                    'total_disbursed': float(total_payments),
                    'pending': pending_payments
                },
                'employees': {
                    'total_count': len(employees),
                    'top_performers': top_performers,
                    'at_risk': risk_employees
                },
                'attendance': {
                    'unique_days': present_days
                }
            }, 200

        except Exception as e:
            return {"error": str(e)}, 500

    def get_employee_report(self, employee_id, days=30):
        """Detailed performance for a single employee"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Tasks
            tasks_res = supabase.table('tasks').select('*').eq('assigned_to', employee_id).gte('created_at', start_date.isoformat()).execute()
            tasks = tasks_res.data or []

            metrics = {
                'total_tasks': len(tasks),
                'completed': len([t for t in tasks if t['status'] == 'completed']),
                'on_time': 0,
                'delayed': 0,
                'earnings': 0
            }

            for task in tasks:
                if task['status'] == 'completed':
                    # Check if on time
                    if task.get('deadline') and task.get('completed_at'):
                        deadline = datetime.fromisoformat(task['deadline'].replace('Z', '+00:00'))
                        completed = datetime.fromisoformat(task['completed_at'].replace('Z', '+00:00'))
                        if completed <= deadline:
                            metrics['on_time'] += 1
                        else:
                            metrics['delayed'] += 1

                    # Sum payments
                    pay_res = supabase.table('payments').select('amount,status').eq('task_id', task['id']).execute()
                    if pay_res.data:
                        metrics['earnings'] += sum(p['amount'] for p in pay_res.data if p['status'] == 'completed')

            metrics['completion_rate'] = (metrics['completed'] / max(metrics['total_tasks'], 1)) * 100
            metrics['on_time_rate'] = (metrics['on_time'] / max(metrics['completed'], 1)) * 100

            # Recent activities
            act_res = supabase.table('activity_logs').select('*').eq('user_id', employee_id).limit(20).execute()
            metrics['recent_activity'] = act_res.data if act_res.data else []

            return metrics, 200

        except Exception as e:
            return {"error": str(e)}, 500

    def get_team_benchmark(self, company_id):
        """Compare employee performance against team average"""
        try:
            # Get company averages
            tasks_res = supabase.table('tasks').select('*').eq('company_id', company_id).execute()
            tasks = tasks_res.data or []

            avg_completion_time = 0
            if tasks:
                completed_tasks = [t for t in tasks if t.get('completed_at')]
                if completed_tasks:
                    durations = []
                    for t in completed_tasks:
                        created = datetime.fromisoformat(t['created_at'].replace('Z', '+00:00'))
                        completed = datetime.fromisoformat(t['completed_at'].replace('Z', '+00:00'))
                        durations.append((completed - created).total_seconds() / 3600)
                    avg_completion_time = sum(durations) / len(durations)

            # Per-employee breakdown
            users_res = supabase.table('users').select('id,name').eq('company_id', company_id).execute()
            users = users_res.data or []

            benchmark = []
            for user in users:
                    try:
                        perf_res = supabase.table('employee_performance').select('*').eq('employee_id', user['id']).execute()
                        if perf_res.data:
                            p = perf_res.data[0]
                            benchmark.append({
                                'name': user['name'],
                                'tasks_completed': p['tasks_completed'],
                                'completion_rate': (p['tasks_completed'] / max(p['total_tasks_assigned'], 1)) * 100,
                                'vs_average': 'above' if (p['tasks_completed'] / max(p['total_tasks_assigned'], 1)) > 0.7 else 'below'
                            })
                    except Exception:
                        pass # Skip if view is missing

            return {
                'avg_completion_time_hours': round(avg_completion_time, 1),
                'employee_benchmark': sorted(benchmark, key=lambda x: x['completion_rate'], reverse=True)
            }, 200

        except Exception as e:
            return {"error": str(e)}, 500

    def predict_delayed_tasks(self, company_id):
        """Get all tasks predicted to be delayed"""
        try:
            preds_res = supabase.table('predictions').select('*').eq('company_id', company_id).gte('delay_risk', 0.6).execute()
            predictions = preds_res.data or []

            delayed_tasks = []
            for pred in predictions:
                task_res = supabase.table('tasks').select('*').eq('id', pred['task_id']).execute()
                if task_res.data:
                    task = task_res.data[0]
                    delayed_tasks.append({
                        'task': {k: v for k, v in task.items() if k != 'ai_risk_score'},
                        'risk_score': pred['delay_risk'],
                        'risk_factors': pred['risk_factors'],
                        'suggested_deadline': pred['suggested_deadline']
                    })

            return {'at_risk_tasks': delayed_tasks}, 200

        except Exception as e:
            print(f"[ERROR] Analytics prediction failed: {e}")
            return {'at_risk_tasks': []}, 200

analytics_service = AnalyticsService()