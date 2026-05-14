import React, { useState, useEffect } from 'react';
import { 
  Clock, CheckCircle, Zap, MessageSquare, 
  Calendar, Coffee, ArrowRight, Play, Pause, Loader2 
} from 'lucide-react';
import { API_BASE_URL } from '../api/config';

function EmployeeSidePanel({ user }) {
  const [time, setTime] = useState(new Date());
  const [isActive, setIsActive] = useState(false);
  const [timer, setTimer] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const clockInterval = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(clockInterval);
  }, []);

  useEffect(() => {
    let interval;
    if (isActive) {
      interval = setInterval(() => setTimer(t => t + 1), 1000);
    }
    return () => clearInterval(interval);
  }, [isActive]);

  const formatTime = (seconds) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const handleToggleClock = async () => {
    if (!navigator.geolocation) {
      alert('Geolocation not supported');
      return;
    }

    setLoading(true);
    navigator.geolocation.getCurrentPosition(async (position) => {
      const { latitude, longitude } = position.coords;
      const endpoint = isActive ? '/api/users/checkout' : '/api/users/checkin';
      const payload = {
        user_id: user.id,
        company_id: user.company_id,
        latitude,
        longitude
      };

      try {
        const token = localStorage.getItem('smartos_token');
        const res = await fetch(`${API_BASE_URL}${endpoint}`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (res.ok) {
          setIsActive(!isActive);
          if (!isActive) {
            setTimer(0);
          }
          alert(data.message);
        } else {
          alert(data.error || 'Failed to update attendance');
        }
      } catch (error) {
        console.error('Attendance error:', error);
        alert('Server connection error');
      } finally {
        setLoading(false);
      }
    }, (error) => {
      console.error('GPS Error:', error);
      alert('Please enable location to clock in/out.');
      setLoading(false);
    });
  };

  return (
    <aside className="right-panel">
      {/* Time & Attendance */}
      <section className="panel-section">
        <div className="panel-section-title">
          <span>Attendance</span>
          <span className={`badge ${isActive ? 'badge-blue' : 'badge-gray'}`}>
            {isActive ? 'Active' : 'Offline'}
          </span>
        </div>
        <div className="status-card">
          <div style={{ fontSize: '0.875rem', color: 'var(--gray-500)' }}>
            {time.toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' })}
          </div>
          <div className="attendance-timer">
            {time.toLocaleTimeString(undefined, { hour12: false })}
          </div>
          <div className="flex gap-2 mt-4">
            <button 
              className={`btn ${isActive ? 'btn-danger' : 'btn-primary pulse-primary'} flex-1`}
              onClick={handleToggleClock}
              disabled={loading}
            >
              {loading ? <Loader2 className="animate-spin" size={16} /> : (isActive ? <Pause size={16} /> : <Play size={16} />)}
              {isActive ? 'Clock Out' : 'Clock In'}
            </button>
          </div>
        </div>
      </section>

      {/* Progress Section */}
      <section className="panel-section">
        <div className="panel-section-title">
          <span>Daily Goal</span>
          <span style={{ color: 'var(--primary-500)' }}>75%</span>
        </div>
        <div className="progress-circle-container">
          <div className="circular-progress">
            <svg width="120" height="120">
              <circle className="bg" cx="60" cy="60" r="50" />
              <circle className="fg" cx="60" cy="60" r="50" />
            </svg>
            <div className="progress-value">6/8h</div>
          </div>
          <p className="text-center text-sm text-gray">
            You're 2 hours away from your daily target.
          </p>
        </div>
      </section>

      {/* Active Task */}
      <section className="panel-section">
        <div className="panel-section-title">
          <span>Focusing On</span>
        </div>
        <div className="active-task-mini">
          <div className="flex items-center gap-2 mb-2">
            <Zap size={14} className="text-primary-500" />
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--primary-600)' }}>CURRENT TASK</span>
          </div>
          <h4 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '0.5rem' }}>Update UI Components</h4>
          <p style={{ fontSize: '0.8rem', color: 'var(--gray-600)', marginBottom: '1rem' }}>
            Refactor the sidebar and dashboard for the new light theme.
          </p>
          <div className="flex justify-between items-center">
            <span className="badge badge-sm badge-info">In Progress</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--gray-500)' }}>{formatTime(timer)}</span>
          </div>
        </div>
      </section>

      {/* Quick Actions */}
      <section className="panel-section">
        <div className="panel-section-title">
          <span>Quick Actions</span>
        </div>
        <div className="quick-action-list">
          <div className="action-item">
            <div className="action-icon"><Coffee size={16} /></div>
            <span>Take a Break</span>
          </div>
          <div className="action-item">
            <div className="action-icon"><MessageSquare size={16} /></div>
            <span>AI Assistant</span>
          </div>
          <div className="action-item">
            <div className="action-icon"><Calendar size={16} /></div>
            <span>Request Leave</span>
          </div>
        </div>
      </section>

      {/* Motivation Tip */}
      <div style={{ marginTop: 'auto', padding: '1rem', background: 'var(--gray-50)', borderRadius: 'var(--radius)', fontSize: '0.8rem', color: 'var(--gray-500)', fontStyle: 'italic' }}>
        "Success is the sum of small efforts, repeated day in and day out."
      </div>
    </aside>
  );
}

export default EmployeeSidePanel;
