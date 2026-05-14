"""
Integration Service - Third-party API Connections
Slack, Zoom, Google Drive, GitHub
"""
import requests
import json
from datetime import datetime, timedelta
from utils.supabase_client import supabase
import os

class IntegrationService:
    def __init__(self):
        self.base_urls = {
            'slack': 'https://slack.com/api',
            'zoom': 'https://api.zoom.us/v2',
            'google_drive': 'https://www.googleapis.com/drive/v3',
            'github': 'https://api.github.com'
        }

    def send_slack_notification(self, company_id, channel, message, task_id=None):
        """Send message to Slack channel"""
        try:
            integration = self._get_active_integration(company_id, 'slack')
            if not integration:
                return {"error": "Slack integration not configured"}, 400

            headers = {'Authorization': f"Bearer {integration['access_token']}"}
            payload = {
                'channel': channel,
                'text': message,
                'blocks': [
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": message}
                    }
                ]
            }

            if task_id:
                payload['blocks'].append({
                    "type": "actions",
                    "elements": [{
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View Task"},
                        "url": f"https://yourapp.com/tasks/{task_id}"
                    }]
                })

            response = requests.post(f"{self.base_urls['slack']}/chat.postMessage", json=payload, headers=headers)
            return response.json(), 200

        except Exception as e:
            return {"error": str(e)}, 500

    def create_zoom_meeting(self, company_id, topic, duration=60, start_time=None):
        """Create a Zoom meeting"""
        try:
            integration = self._get_active_integration(company_id, 'zoom')
            if not integration:
                return {"error": "Zoom integration not configured"}, 400

            headers = {
                'Authorization': f"Bearer {integration['access_token']}",
                'Content-Type': 'application/json'
            }

            meeting_data = {
                'topic': topic,
                'type': 2,  # Scheduled meeting
                'duration': duration,
                'timezone': 'UTC',
                'settings': {
                    'host_video': True,
                    'participant_video': True,
                    'join_before_host': True
                }
            }

            if start_time:
                meeting_data['start_time'] = start_time

            response = requests.post(f"{self.base_urls['zoom']}/users/me/meetings", json=meeting_data, headers=headers)
            return response.json(), 200

        except Exception as e:
            return {"error": str(e)}, 500

    def upload_to_drive(self, company_id, file_path, file_name, mime_type, task_id=None):
        """Upload file to Google Drive"""
        try:
            integration = self._get_active_integration(company_id, 'google_drive')
            if not integration:
                return {"error": "Google Drive integration not configured"}, 400

            headers = {'Authorization': f"Bearer {integration['access_token']}"}
            metadata = {'name': file_name}
            if task_id:
                metadata['parents'] = [self._get_task_folder_id(task_id, integration['access_token'])]

            # Upload file (simplified - would need google-auth library in production)
            # This is a placeholder - implement with google-api-python-client
            return {"message": "Upload simulated - implement with googleapiclient", "file_name": file_name}, 200

        except Exception as e:
            return {"error": str(e)}, 500

    def link_github_issue(self, company_id, task_id, github_repo, github_issue_number):
        """Link a GitHub issue to a task"""
        try:
            integration = self._get_active_integration(company_id, 'github')
            if not integration:
                return {"error": "GitHub integration not configured"}, 400

            headers = {
                'Authorization': f"token {integration['access_token']}",
                'Accept': 'application/vnd.github.v3+json'
            }

            # Add SmartOS webhook comment to issue
            comment = {
                'body': f":robot: This task is tracked in SmartOS.\nTask ID: `{task_id}`\n[View in SmartOS](https://yourapp.com/tasks/{task_id})"
            }

            response = requests.post(
                f"https://api.github.com/repos/{github_repo}/issues/{github_issue_number}/comments",
                json=comment,
                headers=headers
            )

            if response.status_code == 201:
                # Store link in task metadata
                supabase.table('tasks').update({
                    'metadata': supabase.raw(f"jsonb_set(metadata, '{{github_issue}}', '{github_repo}#{github_issue_number}')")
                }).eq('id', task_id).execute()

            return response.json(), response.status_code

        except Exception as e:
            return {"error": str(e)}, 500

    def sync_calendar(self, company_id, user_id):
        """Sync tasks with Google Calendar (placeholder)"""
        # Implement with Google Calendar API
        return {"message": "Calendar sync not implemented yet"}, 501

    def _get_active_integration(self, company_id, service):
        """Fetch active integration credentials"""
        res = supabase.table('integrations').select('*').eq('company_id', company_id).eq('service', service).eq('is_active', True).limit(1).execute()
        return res.data[0] if res.data else None

    def _get_task_folder_id(self, task_id, access_token):
        """Get or create Google Drive folder for task"""
        # Placeholder - implement properly
        return None

    def log_activity(self, user_id, company_id, action, resource_type, resource_id, metadata=None):
        """Log integration activity"""
        try:
            supabase.table('activity_logs').insert({
                'user_id': user_id,
                'company_id': company_id,
                'action': action,
                'resource_type': resource_type,
                'resource_id': resource_id,
                'metadata': metadata or {}
            }).execute()
        except:
            pass

integration_service = IntegrationService()