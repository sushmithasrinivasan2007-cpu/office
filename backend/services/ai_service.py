"""
AI Service - Intelligent Assistant
Handles task parsing, summarization, document extraction, risk prediction
"""
import os
import openai
import anthropic
import json
import re
from datetime import datetime, timedelta
from utils.supabase_client import supabase
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY')) if os.getenv('OPENAI_API_KEY') else None
        self.anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY')) if os.getenv('ANTHROPIC_API_KEY') else None
        self.provider = os.getenv('AI_PROVIDER', 'openai')  # openai or anthropic

    def parse_task(self, text, user_id, company_id):
        """
        Convert natural language into structured task
        Example: "Call client tomorrow at 2pm about project X"
        """
        try:
            prompt = f"""
            Parse the following task description and extract structured information.
            Return JSON with: title, description (expanded), deadline (YYYY-MM-DD), priority (low/medium/high/critical),
            task_type, required_skills (as list), estimated_duration_minutes, location_required (boolean),
            payment_suggested (boolean), client_name (if mentioned).

            Task: "{text}"

            Current date: {datetime.now().strftime('%Y-%m-%d')}

            Return only valid JSON, nothing else.
            """

            if self.provider == 'openai' and self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                parsed = json.loads(response.choices[0].message.content)
            elif self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-opus-20240229",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000
                )
                parsed = json.loads(response.content[0].text)
            else:
                # Fallback simple parser
                parsed = self._simple_parse(text)

            # Log AI interaction
            self._log_ai_interaction('parse_task', text, parsed, user_id, company_id)

            return parsed, 200

        except Exception as e:
            return {"error": str(e)}, 500

    def summarize_project(self, tasks_data, user_id, company_id):
        """
        Generate executive summary from task list
        """
        try:
            tasks_json = json.dumps(tasks_data, indent=2)
            prompt = f"""
            Analyze these project tasks and generate a concise executive summary:

            {tasks_json}

            Provide:
            1. Overall status (on-track/at-risk/delayed)
            2. Key achievements
            3. Blockers and risks
            4. Resource utilization
            5. Next steps recommendation

            Keep it professional and actionable. Max 200 words.
            """

            if self.provider == 'openai' and self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5
                )
                summary = response.choices[0].message.content
            elif self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-opus-20240229",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500
                )
                summary = response.content[0].text
            else:
                summary = "AI analysis: Project is on track with most tasks pending. (AI Provider not configured for detailed summary)"

            self._log_ai_interaction('summarize', tasks_json, {'summary': summary}, user_id, company_id)

            return {'summary': summary}, 200

        except Exception as e:
            return {"error": str(e)}, 500

    def extract_info_from_document(self, document_text, user_id, company_id, document_type=None):
        """
        Extract key info from documents (invoices, contracts, proposals)
        """
        try:
            extraction_prompt = f"""
            Extract structured information from this document text:

            {document_text[:5000]}  # Limit to first 5k chars

            Return JSON with relevant fields based on document type: {document_type or 'general'}
            Possible fields: client_name, invoice_number, amount, dates, services, terms,
            contact_info, total, tax, items (list).
            """

            if self.provider == 'openai' and self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": extraction_prompt}],
                    temperature=0.2
                )
                extracted = json.loads(response.choices[0].message.content)
            elif self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-opus-20240229",
                    messages=[{"role": "user", "content": extraction_prompt}],
                    max_tokens=1000
                )
                # Try to parse JSON from Claude's response
                extracted = self._extract_json_from_text(response.content[0].text)
            else:
                extracted = {"error": "AI Provider not configured", "message": "Manual entry required"}

            self._log_ai_interaction('extract', document_text[:500], extracted, user_id, company_id)

            return extracted, 200

        except Exception as e:
            return {"error": str(e)}, 500

    def predict_task_risk(self, task_data, user_data, company_id):
        """
        Predict risk of delay for a task
        Returns: delay_probability (0-1), risk_factors list, suggested_deadline
        """
        try:
            # Analyze task complexity, employee workload, historical data
            risk_score = 0.0
            risk_factors = []

            # Check employee's current workload
            active_tasks = supabase.table('tasks').select('id').eq('assigned_to', user_data['id']).in_(
                'status', ['pending', 'in_progress']
            ).execute()

            workload_count = len(active_tasks.data) if active_tasks.data else 0
            if workload_count > 5:
                risk_score += 0.2
                risk_factors.append('High current workload')

            # Check deadline proximity
            if task_data.get('deadline'):
                deadline = datetime.fromisoformat(task_data['deadline'].replace('Z', '+00:00'))
                days_until = (deadline - datetime.now(deadline.tzinfo)).days
                if days_until < 2:
                    risk_score += 0.3
                    risk_factors.append('Tight deadline')
                elif days_until < 0:
                    risk_score += 0.5
                    risk_factors.append('Already overdue')

            # Check employee performance history
            perf_res = supabase.table('employee_performance').select('*').eq('employee_id', user_data['id']).execute()
            if perf_res.data:
                perf = perf_res.data[0]
                completion_rate = perf['tasks_completed'] / max(perf['total_tasks_assigned'], 1)
                if completion_rate < 0.7:
                    risk_score += 0.2
                    risk_factors.append('Lower than average completion rate')

            # Check if task is high priority
            if task_data.get('priority') in ['high', 'critical']:
                risk_score += 0.1

            # AI enhancement if available
            if self.openai_client or self.anthropic_client:
                ai_insights = self._get_ai_risk_insights(task_data, user_data)
                if ai_insights:
                    risk_score = min(1.0, risk_score + ai_insights.get('additional_risk', 0))
                    risk_factors.extend(ai_insights.get('factors', []))

            # Calculate suggested deadline
            days_needed = task_data.get('estimated_duration_minutes', 60) / 480  # 8-hour workday
            suggested_deadline = (datetime.now() + timedelta(days=max(1, days_needed + 1))).isoformat()

            prediction = {
                'delay_risk': round(risk_score, 2),
                'risk_factors': list(set(risk_factors)),  # deduplicate
                'suggested_deadline': suggested_deadline,
                'confidence': 0.85 if self.openai_client else 0.75
            }

            # Store prediction
            supabase.table('predictions').insert({
                'task_id': task_data['id'],
                'company_id': company_id,
                'delay_risk': prediction['delay_risk'],
                'workload_score': workload_count * 10,
                'suggested_deadline': prediction['suggested_deadline'],
                'risk_factors': prediction['risk_factors']
            }).execute()

            return prediction, 200

        except Exception as e:
            return {"error": str(e)}, 500

    def get_smart_plan(self, user_id, date):
        """
        Generate "Today's Smart Plan" - prioritized task list
        """
        try:
            # Skip if it's a mock user ID or not a valid UUID
            import re
            uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)
            if not user_id or 'mock' in str(user_id).lower() or not uuid_pattern.match(str(user_id)):
                return {
                    'date': date,
                    'tasks': [],
                    'focus_areas': [],
                    'estimated_completion': '0 hours',
                    'risk_alerts': [],
                    'message': 'Log in with a real account to see your smart plan.'
                }, 200

            # Get all pending/in-progress tasks for user
            tasks_res = supabase.table('tasks').select('*').eq('assigned_to', user_id).in_(
                'status', ['pending', 'in_progress']
            ).execute()

            tasks = tasks_res.data or []

            # Score each task for smart ordering
            scored_tasks = []
            for task in tasks:
                score = self._calculate_task_priority_score(task)
                scored_tasks.append({**task, 'priority_score': score})

            # Sort by score descending
            scored_tasks.sort(key=lambda x: x['priority_score'], reverse=True)

            plan = {
                'date': date,
                'tasks': scored_tasks[:10],
                'focus_areas': self._identify_focus_areas(scored_tasks),
                'estimated_completion': self._estimate_completion_time(scored_tasks),
                'risk_alerts': [t for t in scored_tasks if t.get('ai_risk_score', 0) > 0.6]
            }

            return plan, 200

        except Exception as e:
            return {"error": str(e)}, 500

    def answer_query(self, query, user_id, company_id, context_data=None):
        """
        Answer project-related queries with context awareness
        """
        try:
            # Gather context safely
            context = {}
            try:
                context = self._build_context(user_id, company_id, context_data)
            except Exception as context_err:
                print(f"AI Context building error: {context_err}")
                context = {'error': 'Could not gather full context'}

            prompt = f"""
            You are an intelligent office assistant for a task management system.
            Answer the user's question based on the provided context.

            Context:
            {json.dumps(context, indent=2)}

            Question: {query}

            Provide a concise, helpful answer. If the answer requires data not in context,
            say so politely. Format clearly with bullet points when listing items.
            """

            answer = ""
            def is_valid_key(key_name):
                key = os.getenv(key_name, '')
                return "sk-" in key and "your-" not in key.lower() and "placeholder" not in key.lower()

            if self.provider == 'openai' and self.openai_client and is_valid_key('OPENAI_API_KEY'):
                try:
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7
                    )
                    answer = response.choices[0].message.content
                except Exception as ai_err:
                    answer = f"I encountered an error with my OpenAI brain: {str(ai_err)}"
            elif self.anthropic_client and is_valid_key('ANTHROPIC_API_KEY'):
                try:
                    response = self.anthropic_client.messages.create(
                        model="claude-3-opus-20240229",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=1000
                    )
                    answer = response.content[0].text
                except Exception as ai_err:
                    answer = f"I encountered an error with my Anthropic brain: {str(ai_err)}"
            else:
                # SMART-MOCK ENGINE: Provide real insights from local data
                tasks = context.get('tasks', [])
                team = context.get('team', [])
                
                low_query = query.lower()
                if any(w in low_query for w in ['task', 'doing', 'list']):
                    pending = [t for t in tasks if t.get('status') != 'completed']
                    if pending:
                        answer = f"You have {len(pending)} pending tasks. The most urgent ones are:\n"
                        for t in pending[:3]:
                            answer += f"• **{t['title']}** (Priority: {t['priority']})\n"
                    else:
                        answer = "Great news! You don't have any pending tasks at the moment."
                elif any(w in low_query for w in ['team', 'member', 'employee']):
                    answer = f"Your team currently has {len(team)} members:\n"
                    for m in team[:5]:
                        answer += f"• {m['name']} ({m['role']})\n"
                elif any(w in low_query for w in ['summary', 'report', 'status']):
                    completed = len([t for t in tasks if t.get('status') == 'completed'])
                    total = len(tasks)
                    answer = f"**Project Summary:**\n• Total Tasks: {total}\n• Completion Rate: {round((completed/total*100) if total > 0 else 0)}%\n• Active Team: {len(team)} members\n\nI recommend focusing on the pending high-priority items first."
                else:
                    answer = "I'm in Local Intelligence mode. I can see your tasks and team data! Ask me for a 'summary' or to 'list my tasks' to see what I can do."

            # Log interaction safely
            try:
                self._log_ai_interaction('answer_query', query, {'answer': answer}, user_id, company_id)
            except:
                pass

            return {'answer': answer}, 200

        except Exception as e:
            return {"answer": f"I'm sorry, I encountered a technical error: {str(e)}"}, 200 # Return as 200 to show in chat

    # Private helper methods
    def _simple_parse(self, text):
        """Fallback simple parser without AI"""
        words = text.lower().split()
        has_tomorrow = 'tomorrow' in words
        has_today = 'today' in words
        has_urgent = any(w in words for w in ['urgent', 'asap', 'immediately', 'critical'])

        deadline = None
        if has_tomorrow:
            deadline = (datetime.now() + timedelta(days=1)).replace(hour=17, minute=0).strftime('%Y-%m-%dT%H:%M')
        elif has_today:
            deadline = (datetime.now() + timedelta(hours=4)).strftime('%Y-%m-%dT%H:%M')

        return {
            'title': text[:100],
            'description': text,
            'deadline': deadline,
            'priority': 'critical' if has_urgent else 'medium',
            'estimated_duration_minutes': 60
        }

    def _extract_json_from_text(self, text):
        """Extract JSON blob from text"""
        try:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
            return {}
        except:
            return {}

    def _log_ai_interaction(self, action, input_text, output_data, user_id, company_id):
        """Store AI interaction for analytics - non-critical"""
        try:
            supabase.table('ai_logs').insert({
                'user_id': user_id,
                'company_id': company_id,
                'action': action,
                'input_text': str(input_text)[:2000],
                'output_data': output_data,
                'created_at': datetime.now().isoformat()
            }).execute()
        except Exception:
            pass  # AI logs are non-critical

    def _get_ai_risk_insights(self, task_data, user_data):
        """Get risk insights from LLM"""
        try:
            prompt = f"""
            Task: {task_data.get('title')}
            Description: {task_data.get('description')}
            Employee avg completion rate: {user_data.get('completion_rate', 'unknown')}
            Employee current workload: {user_data.get('active_tasks', 0)} tasks

            Rate risk of delay (0-1) and list 1-2 key risk factors as JSON.
            Example: {{"additional_risk": 0.15, "factors": ["Complex dependency", "New skill required"]}}
            Return only JSON.
            """
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return self._extract_json_from_text(response.choices[0].message.content)
        except:
            return {}

    def _calculate_task_priority_score(self, task):
        """Calculate smart priority score for sorting"""
        score = 0

        # Priority weight
        priority_weights = {'low': 10, 'medium': 30, 'high': 60, 'critical': 100}
        score += priority_weights.get(task.get('priority', 'medium'), 30)

        # Deadline proximity (sooner = higher)
        if task.get('deadline'):
            deadline = datetime.fromisoformat(task['deadline'].replace('Z', '+00:00'))
            days_left = max(0, (deadline - datetime.now(deadline.tzinfo)).days)
            proximity_score = max(0, 100 - (days_left * 10))
            score += proximity_score

        # Risk penalty
        ai_risk = task.get('ai_risk_score', 0)
        if ai_risk > 0.6:
            score -= 20  # High risk tasks get prioritized to mitigate risk

        return score

    def _identify_focus_areas(self, tasks):
        """Identify main focus areas from task list"""
        types = [t.get('task_type', 'general') for t in tasks]
        from collections import Counter
        counts = Counter(types)
        return [{'type': k, 'count': v} for k, v in counts.most_common(3)]

    def _estimate_completion_time(self, tasks):
        """Estimate total time to complete all tasks"""
        total_minutes = sum(t.get('estimated_duration_minutes', 60) for t in tasks)
        hours = total_minutes / 60
        if hours < 8:
            return f"{round(hours, 1)} hours"
        return f"{round(hours/8, 1)} days"

    def _build_context(self, user_id, company_id, extra):
        """Build context for AI queries from DB"""
        import re
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)
        context = {'user_id': user_id, 'company_id': company_id}

        # Get user's tasks (only if valid UUID)
        try:
            if user_id and uuid_pattern.match(str(user_id)):
                tasks_res = supabase.table('tasks').select('*').eq('assigned_to', user_id).limit(20).execute()
                context['tasks'] = tasks_res.data if tasks_res.data else []
            else:
                context['tasks'] = []
        except Exception:
            context['tasks'] = []

        # Get team info (only if valid UUID)
        try:
            if company_id and uuid_pattern.match(str(company_id)):
                team_res = supabase.table('users').select('id,name,role').eq('company_id', company_id).execute()
                context['team'] = team_res.data if team_res.data else []
            else:
                context['team'] = []
        except Exception:
            context['team'] = []

        return context

ai_service = AIService()