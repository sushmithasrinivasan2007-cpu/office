"""
Task Routing Service - Smart Assignment System
Automatically assigns tasks based on workload, skills, availability
"""
from utils.supabase_client import supabase
from datetime import datetime, timedelta
import json

class TaskRoutingService:
    def find_best_assignee(self, task_data, company_id, exclusion_list=None):
        """
        Find the optimal employee for a task based on:
        - Current workload (active task count)
        - Skill match
        - Performance history
        - Availability (attendance)
        - Location proximity (if geo task)
        """
        try:
            # Get all eligible employees in company
            query = supabase.table('users').select('*').eq('company_id', company_id).in_('role', ['employee', 'manager'])
            if exclusion_list:
                query = query.not_.in_('id', exclusion_list)
            employees_res = query.execute()
            employees = employees_res.data or []

            if not employees:
                return {"error": "No eligible employees found"}, 404

            scored_candidates = []

            for emp in employees:
                score = 0
                reasons = []

                # 1. Workload Check (most important)
                active_tasks = supabase.table('tasks').select('id').eq('assigned_to', emp['id']).in_(
                    'status', ['pending', 'in_progress']
                ).execute()
                task_count = len(active_tasks.data) if active_tasks.data else 0
                workload_penalty = task_count * 10
                score -= workload_penalty
                reasons.append(f'Active tasks: {task_count}')

                # 2. Skill Match
                if task_data.get('required_skills'):
                    required_skills = set(task_data['required_skills'])
                    emp_skills = set(emp.get('metadata', {}).get('skills', []))
                    match_pct = len(required_skills & emp_skills) / len(required_skills) if required_skills else 0.5
                    skill_score = int(match_pct * 50)
                    score += skill_score
                    reasons.append(f'Skill match: {int(match_pct*100)}%')

                # 3. Performance History
                perf_res = supabase.table('employee_performance').select('tasks_completed,total_tasks_assigned').eq('employee_id', emp['id']).execute()
                if perf_res.data:
                    perf = perf_res.data[0]
                    completion_rate = perf['tasks_completed'] / max(perf['total_tasks_assigned'], 1)
                    perf_score = int(completion_rate * 30)
                    score += perf_score
                    reasons.append(f'Completion rate: {round(completion_rate*100, 1)}%')

                # 4. Availability (Today's check-in)
                today = datetime.now().strftime('%Y-%m-%d')
                att_res = supabase.table('attendance').select('*').eq('user_id', emp['id']).gte('checkin_time', today).execute()
                is_present = len(att_res.data) > 0 if att_res.data else False
                if is_present:
                    score += 20
                    reasons.append('Present today')
                else:
                    score -= 50
                    reasons.append('Not checked in')

                # 5. Geo proximity (if task has location and employee has recent location)
                if task_data.get('location_lat') and task_data.get('location_lng'):
                    # Get employee's last known location from attendance or GPS
                    last_loc_res = supabase.table('attendance').select('checkin_lat,checkin_lng').eq('user_id', emp['id']).order('checkin_time', desc=True).limit(1).execute()
                    if last_loc_res.data:
                        last_loc = last_loc_res.data[0]
                        from geopy.distance import geodesic
                        distance = geodesic(
                            (task_data['location_lat'], task_data['location_lng']),
                            (last_loc['checkin_lat'], last_loc['checkin_lng'])
                        ).meters
                        if distance < 5000:  # Within 5km
                            proximity_score = max(0, 30 - (distance / 200))
                            score += proximity_score
                            reasons.append(f'Proximity: {round(distance)}m')

                # 6. Task priority affinity (high priority tasks to high performers)
                if task_data.get('priority') in ['high', 'critical']:
                    if perf_res.data and perf_res.data[0]['tasks_completed'] > 10:
                        score += 15
                        reasons.append('High-performer for critical task')

                scored_candidates.append({
                    'employee': emp,
                    'score': round(score, 2),
                    'active_tasks': task_count,
                    'reasons': reasons
                })

            # Sort by score descending
            scored_candidates.sort(key=lambda x: x['score'], reverse=True)

            best = scored_candidates[0]
            return {
                'best_assignee': best['employee'],
                'score': best['score'],
                'alternatives': scored_candidates[1:4],
                'rationale': best['reasons']
            }, 200

        except Exception as e:
            return {"error": str(e)}, 500

    def rebalance_workload(self, company_id):
        """
        Redistribute tasks among employees to balance workload
        Called when someone is overloaded or underutilized
        """
        try:
            # Get all pending tasks
            tasks_res = supabase.table('tasks').select('*').eq('company_id', company_id).in_(
                'status', ['pending']
            ).execute()
            tasks = tasks_res.data or []

            # Get employees with their active task counts
            emp_load = {}
            for emp in supabase.table('users').select('id,name').eq('company_id', company_id).in_('role', ['employee', 'manager']).execute().data:
                count_res = supabase.table('tasks').select('id').eq('assigned_to', emp['id']).in_('status', ['pending', 'in_progress']).execute()
                emp_load[emp['id']] = {
                    'user': emp,
                    'load': len(count_res.data) if count_res.data else 0
                }

            avg_load = sum(e['load'] for e in emp_load.values()) / len(emp_load) if emp_load else 0

            reassign_candidates = []

            # Find overloaded employees (> avg + 2)
            overloaded = [e for e in emp_load.values() if e['load'] > avg_load + 2]
            for emp_data in overloaded:
                emp_tasks = [t for t in tasks if t['assigned_to'] == emp_data['user']['id']]
                for task in emp_tasks:
                    # Try to reassign
                    new_assign_res = self.find_best_assignee(task, company_id, [emp_data['user']['id']])
                    if new_assign_res[0].get('best_assignee'):
                        reassign_candidates.append({
                            'task_id': task['id'],
                            'current_assignee': emp_data['user']['name'],
                            'suggested_assignee': new_assign_res[0]['best_assignee']['name'],
                            'reason': f'Load balancing: {emp_data["load"]} tasks → target {round(avg_load, 1)} tasks'
                        })

            return {'rebalance_suggestions': reassign_candidates}, 200

        except Exception as e:
            return {"error": str(e)}, 500

task_routing_service = TaskRoutingService()