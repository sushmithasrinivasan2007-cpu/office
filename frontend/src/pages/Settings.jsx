import React, { useState, useEffect } from 'react';
import { Settings, Bell, Mail, Shield, Globe, Database } from 'lucide-react';
import { Link } from 'react-router-dom';
import { API_BASE_URL } from '../api/config';

function SettingsPage({ user }) {
  const [activeTab, setActiveTab] = useState('general');
  const [settings, setSettings] = useState({
    email_notifications: true,
    daily_summary: true,
    weekly_report: true,
    overdue_alerts: true,
    geo_verification_radius: 100,
    working_hours_start: '09:00',
    working_hours_end: '18:00',
    timezone: 'UTC'
  });
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      const token = localStorage.getItem('smartos_token');
      await fetch(`${API_BASE_URL}/api/company/${user.company_id}/settings`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
      });
      alert('Settings saved!');
      setSaving(false);
    } catch (error) {
      alert('Failed to save settings');
      setSaving(false);
    }
  };

  return (
    <div className="settings-page">
      <div className="page-header">
        <h1 className="page-title">Settings</h1>
        <p className="page-subtitle">Manage your account and company preferences</p>
      </div>

      <div className="grid-3 mb-4">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Email Notifications</h2>
          </div>
          <div className="card-body">
            <div className="flex items-center justify-between mb-3">
              <div>
                <p className="font-medium">Daily Summary</p>
                <p className="text-sm text-gray">Receive daily task digest</p>
              </div>
              <ToggleSwitch
                checked={settings.daily_summary}
                onChange={v => setSettings({ ...settings, daily_summary: v })}
              />
            </div>
            <div className="flex items-center justify-between mb-3">
              <div>
                <p className="font-medium">Weekly Report</p>
                <p className="text-sm text-gray">Performance report every Monday</p>
              </div>
              <ToggleSwitch
                checked={settings.weekly_report}
                onChange={v => setSettings({ ...settings, weekly_report: v })}
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Overdue Alerts</p>
                <p className="text-sm text-gray">Get notified about overdue tasks</p>
              </div>
              <ToggleSwitch
                checked={settings.overdue_alerts}
                onChange={v => setSettings({ ...settings, overdue_alerts: v })}
              />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Geo Verification</h2>
          </div>
          <div className="card-body">
            <div className="form-group">
              <label className="form-label">Allowed radius for task completion</label>
              <input
                type="range"
                min="50"
                max="500"
                step="50"
                value={settings.geo_verification_radius}
                onChange={e => setSettings({ ...settings, geo_verification_radius: parseInt(e.target.value) })}
                className="w-full"
              />
              <p className="text-sm text-gray mt-1">Current: {settings.geo_verification_radius} meters</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Working Hours</h2>
          </div>
          <div className="card-body">
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Start</label>
                <input
                  type="time"
                  className="form-input"
                  value={settings.working_hours_start}
                  onChange={e => setSettings({ ...settings, working_hours_start: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">End</label>
                <input
                  type="time"
                  className="form-input"
                  value={settings.working_hours_end}
                  onChange={e => setSettings({ ...settings, working_hours_end: e.target.value })}
                />
              </div>
            </div>
            <div className="form-group mt-3">
              <label className="form-label">Timezone</label>
              <select
                className="form-input form-select"
                value={settings.timezone}
                onChange={e => setSettings({ ...settings, timezone: e.target.value })}
              >
                <option value="UTC">UTC</option>
                <option value="Asia/Kolkata">India (IST)</option>
                <option value="America/New_York">Eastern Time</option>
                <option value="America/Los_Angeles">Pacific Time</option>
                <option value="Europe/London">London (GMT)</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Security</h2>
        </div>
        <div className="card-body">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="font-medium">Two-Factor Authentication</p>
              <p className="text-sm text-gray">Add extra security to your account</p>
            </div>
            <Link to="/profile?tab=security" className="btn btn-secondary">
              {user.two_factor_enabled ? 'Manage 2FA' : 'Enable 2FA'}
            </Link>
          </div>
        </div>
      </div>

      <div className="mt-4 text-right">
        <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
          {saving ? 'Saving...' : 'Save Settings'}
        </button>
      </div>
    </div>
  );
}

function ToggleSwitch({ checked, onChange }) {
  return (
    <button
      className={`toggle-switch ${checked ? 'checked' : ''}`}
      onClick={() => onChange(!checked)}
    >
      <span className="toggle-thumb"></span>
    </button>
  );
}

export default SettingsPage;