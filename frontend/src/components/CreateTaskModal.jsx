import React, { useState } from 'react';
import { X, Bot, MapPin, DollarSign, Calendar, Clock, User, FileText } from 'lucide-react';
import { API_BASE_URL } from '../api/config';

function CreateTaskModal({ user, onClose, onCreated, initialAssignee }) {
  const [mode, setMode] = useState('manual'); // 'manual' or 'ai'
  const [aiPrompt, setAiPrompt] = useState('');
  const [form, setForm] = useState({
    title: '', description: '', deadline: '', priority: 'medium',
    assigned_to: initialAssignee || '', payment_amount: 0, location_lat: '', location_lng: ''
  });
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchEmployees = async () => {
    if (!user.company_id || user.company_id === 'undefined') return;
    
    try {
      const token = localStorage.getItem('smartos_token');
      const res = await fetch(`${API_BASE_URL}/api/company/${user.company_id}/team`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      setEmployees(data.team || []);
    } catch (error) {
      console.error('Fetch employees error:', error);
    }
  };

  React.useEffect(() => {
    if (user.role === 'admin' || user.role === 'manager') {
      fetchEmployees();
    }
  }, []);

  const handleAICreate = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('smartos_token');
      const res = await fetch(`${API_BASE_URL}/api/ai/parse-task`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: aiPrompt,
          user_id: user.id,
          company_id: user.company_id
        })
      });
      const data = await res.json();
      if (data.confidence) {
        setForm({
          ...form,
          title: data.title || aiPrompt.substring(0, 50),
          description: data.description || aiPrompt,
          deadline: data.deadline || '',
          priority: data.priority || 'medium',
          estimated_duration_minutes: data.estimated_duration_minutes || 60
        });
        setMode('manual');
      } else {
        alert('Could not parse task. Try being more specific.');
      }
    } catch (error) {
      console.error('AI parse error:', error);
      alert('AI parsing failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const token = localStorage.getItem('smartos_token');
      const payload = {
        ...form,
        company_id: user.company_id,
        created_by: user.id,
        assigned_to: form.assigned_to || null
      };

      const res = await fetch(`${API_BASE_URL}/api/tasks/create-task`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        onCreated();
      } else {
        const err = await res.json();
        alert(err.error || 'Failed to create task');
      }
    } catch (error) {
      console.error('Create task error:', error);
      alert('Failed to create task');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Create New Task</h2>
          <button className="modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          {/* Mode Toggle */}
          <div className="tabs mb-3">
            <button
              className={`tab ${mode === 'manual' ? 'active' : ''}`}
              onClick={() => setMode('manual')}
            >
              Manual Entry
            </button>
            <button
              className={`tab ${mode === 'ai' ? 'active' : ''}`}
              onClick={() => setMode('ai')}
            >
              <Bot size={16} /> AI Parse
            </button>
          </div>

          {mode === 'ai' ? (
            <div>
              <label className="form-label">Describe the task</label>
              <textarea
                className="form-input mb-2"
                rows={4}
                placeholder="E.g., Call client tomorrow at 2pm about project X, high priority, ₹500 payment"
                value={aiPrompt}
                onChange={e => setAiPrompt(e.target.value)}
              />
              <button
                className="btn btn-primary"
                onClick={handleAICreate}
                disabled={!aiPrompt.trim() || loading}
              >
                {loading ? 'Parsing...' : 'Parse with AI'}
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Task Title *</label>
                <input
                  type="text"
                  className="form-input"
                  required
                  value={form.title}
                  onChange={e => setForm({ ...form, title: e.target.value })}
                  placeholder="Brief task description"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea
                  className="form-input"
                  rows={3}
                  value={form.description}
                  onChange={e => setForm({ ...form, description: e.target.value })}
                  placeholder="Detailed instructions..."
                />
              </div>

              <div className="grid-2">
                <div className="form-group">
                  <label className="form-label">Deadline</label>
                  <input
                    type="datetime-local"
                    className="form-input"
                    value={form.deadline}
                    onChange={e => setForm({ ...form, deadline: e.target.value })}
                    onClick={(e) => e.target.showPicker && e.target.showPicker()}
                    placeholder="Set deadline"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Priority</label>
                  <select
                    className="form-input form-select"
                    value={form.priority}
                    onChange={e => setForm({ ...form, priority: e.target.value })}
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
              </div>

              {(user.role === 'admin' || user.role === 'manager') && (
                <div className="form-group">
                  <label className="form-label">Assign To</label>
                  <select
                    className="form-input form-select"
                    value={form.assigned_to}
                    onChange={e => setForm({ ...form, assigned_to: e.target.value })}
                  >
                    <option value="">Unassigned</option>
                    {employees.map(emp => (
                      <option key={emp.id} value={emp.id}>{emp.name} ({emp.role})</option>
                    ))}
                  </select>
                </div>
              )}



              <div className="grid-2">
                <div className="form-group">
                  <label className="form-label">Location Latitude</label>
                  <input
                    type="number"
                    step="any"
                    className="form-input"
                    value={form.location_lat}
                    onChange={e => setForm({ ...form, location_lat: e.target.value })}
                    placeholder="Optional"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Location Longitude</label>
                  <input
                    type="number"
                    step="any"
                    className="form-input"
                    value={form.location_lng}
                    onChange={e => setForm({ ...form, location_lng: e.target.value })}
                    placeholder="Optional"
                  />
                </div>
              </div>

              <div className="modal-footer" style={{ padding: 0, marginTop: '1.5rem' }}>
                <button type="button" className="btn btn-secondary" onClick={onClose}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Creating...' : 'Create Task'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

export default CreateTaskModal;