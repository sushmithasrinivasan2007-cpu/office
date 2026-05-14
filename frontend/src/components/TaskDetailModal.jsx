import React, { useState, useEffect } from 'react';
import { X, Calendar, MapPin, Clock, User, DollarSign, FileText, Edit, CheckCircle, Bot, AlertTriangle } from 'lucide-react';
import { API_BASE_URL } from '../api/config';

function TaskDetailModal({ task, user, onClose, onUpdate }) {
  const [note, setNote] = useState('');
  const [loading, setLoading] = useState(false);

  const canEdit = user.role === 'admin' || user.role === 'manager' || task.assigned_to === user.id;

  const handleComplete = async () => {
    setLoading(true);
    
    // 1. Get real GPS location
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser');
      setLoading(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(async (position) => {
      const { latitude, longitude } = position.coords;
      
      try {
        const token = localStorage.getItem('smartos_token');
        
        // 2. Call backend to verify location and complete task
        const response = await fetch(`${API_BASE_URL}/api/tasks/${task.id}/complete`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            user_id: user.id,
            completion_notes: note,
            user_lat: latitude,
            user_lng: longitude,
            geo_verified: true // Backend will still verify these coords
          })
        });

        if (response.ok) {
          onUpdate();
        } else {
          const data = await response.json();
          alert(data.error || 'Failed to complete task');
        }
      } catch (error) {
        console.error('Complete error:', error);
        alert('Error connecting to server');
      } finally {
        setLoading(false);
      }
    }, (error) => {
      console.error('Geolocation error:', error);
      alert('Please enable location access to complete this task.');
      setLoading(false);
    });
  };

  const handleEdit = () => {
    // Open edit modal (to be implemented)
    alert('Edit functionality coming soon');
  };

  const getPriorityColor = (p) => {
    switch (p) {
      case 'critical': return 'badge-error';
      case 'high': return 'badge-warning';
      case 'medium': return 'badge-info';
      default: return 'badge-gray';
    }
  };

  const getStatusColor = (s) => {
    switch (s) {
      case 'completed':
      case 'verified': return 'badge-success';
      case 'in_progress': return 'badge-info';
      case 'overdue': return 'badge-error';
      default: return 'badge-gray';
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Task Details</h2>
          <button className="modal-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          {/* Header */}
          <div className="mb-4">
            <div className="flex justify-between items-start mb-2">
              <h3>{task.title}</h3>
              <div className="flex gap-1">
                <span className={`badge ${getPriorityColor(task.priority)}`}>{task.priority}</span>
                <span className={`badge ${getStatusColor(task.status)}`}>{task.status}</span>
              </div>
            </div>

            {task.ai_risk_score && task.ai_risk_score > 0.5 && (
              <div className="alert alert-warning mb-2">
                <AlertTriangle size={16} />
                <span>
                  AI Risk Score: {(task.ai_risk_score * 100).toFixed(0)}% - May be delayed
                </span>
              </div>
            )}

            <p className="text-gray">{task.description || 'No description provided.'}</p>
          </div>

          {/* Details Grid */}
          <div className="grid-2 mb-4">
            <div className="card">
              <h4 className="text-sm font-semibold text-gray mb-2">Deadline</h4>
              <div className="flex items-center gap-2">
                <Calendar size={16} className="text-gray" />
                <span>{task.deadline ? new Date(task.deadline).toLocaleString() : 'Not set'}</span>
              </div>
            </div>

            <div className="card">
              <h4 className="text-sm font-semibold text-gray mb-2">Payment</h4>
              <div className="flex items-center gap-2">
                <DollarSign size={16} className="text-gray" />
                <span className="font-bold">₹{task.payment_amount || 0}</span>
              </div>
            </div>

            {task.location_lat && (
              <div className="card">
                <h4 className="text-sm font-semibold text-gray mb-2">Location</h4>
                <div className="flex items-center gap-2">
                  <MapPin size={16} className="text-gray" />
                  <span>{task.location_address || `${task.location_lat}, ${task.location_lng}`}</span>
                </div>
              </div>
            )}

            {task.assigned_to && (
              <div className="card">
                <h4 className="text-sm font-semibold text-gray mb-2">Assigned To</h4>
                <div className="flex items-center gap-2">
                  <User size={16} className="text-gray" />
                  <span>{task.assigned_to_name || 'Team Member'}</span>
                </div>
              </div>
            )}
          </div>

          {/* Completion Notes */}
          {task.status !== 'completed' && canEdit && (
            <div className="form-group">
              <label className="form-label">Completion Notes (optional)</label>
              <textarea
                className="form-input"
                rows={2}
                value={note}
                onChange={e => setNote(e.target.value)}
                placeholder="Add notes about task completion..."
              />
            </div>
          )}

          {/* Actions */}
          {canEdit && task.status === 'pending' && (
            <div className="flex flex-col gap-2">
              <button
                className="btn btn-success"
                onClick={handleComplete}
                disabled={loading}
              >
                <CheckCircle size={16} /> Mark as Complete
              </button>
              <button className="btn btn-secondary" onClick={handleEdit}>
                <Edit size={16} /> Edit Task
              </button>
            </div>
          )}

          {/* Payment Approval Removed */}
        </div>

        <div className="modal-footer">
          <small className="text-gray">
            Created: {new Date(task.created_at).toLocaleString()}
            {task.completed_at && ` • Completed: ${new Date(task.completed_at).toLocaleString()}`}
          </small>
        </div>
      </div>
    </div>
  );
}

export default TaskDetailModal;