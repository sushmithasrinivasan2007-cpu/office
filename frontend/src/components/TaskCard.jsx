import React from 'react';
import { MapPin, Calendar, DollarSign, Clock } from 'lucide-react';

function TaskCard({ task }) {
  const priorityColors = {
    critical: '#ef4444',
    high: '#f59e0b',
    medium: '#3b82f6',
    low: '#6b7280'
  };

  const statusColors = {
    completed: '#10b981',
    verified: '#059669',
    'in_progress': '#3b82f6',
    pending: '#6b7280',
    overdue: '#ef4444',
    cancelled: '#9ca3af'
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Not set';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const isOverdue = (deadline, status) => {
    return deadline && status !== 'completed' && new Date(deadline) < new Date();
  };

  return (
    <div className="task-card">
      <div className="flex justify-between items-start mb-3">
        <h4 className="task-title text-base font-semibold text-gray-900 line-clamp-2">
          {task.title}
        </h4>
        <div className="flex gap-1">
          <span
            className="badge"
            style={{
              backgroundColor: `${priorityColors[task.priority]}15`,
              color: priorityColors[task.priority],
              border: `1px solid ${priorityColors[task.priority]}30`
            }}
          >
            {task.priority}
          </span>
        </div>
      </div>

      <p className="text-sm text-gray-600 mb-3 line-clamp-2">
        {task.description || 'No description provided'}
      </p>

      {/* Meta */}
      <div className="grid-2 gap-2 text-xs text-gray-500">
        {task.deadline && (
          <div className="flex items-center gap-1">
            <Calendar size={12} />
            <span className={isOverdue(task.deadline, task.status) ? 'text-error font-medium' : ''}>
              {formatDate(task.deadline)}
              {isOverdue(task.deadline, task.status) && ' (Overdue)'}
            </span>
          </div>
        )}
        {task.location_lat && (
          <div className="flex items-center gap-1">
            <MapPin size={12} />
            <span>Geo-tagged</span>
          </div>
        )}
        {task.payment_amount > 0 && (
          <div className="flex items-center gap-1">
            <DollarSign size={12} />
            <span>₹{task.payment_amount}</span>
          </div>
        )}
        {task.estimated_duration_minutes && (
          <div className="flex items-center gap-1">
            <Clock size={12} />
            <span>{Math.round(task.estimated_duration_minutes / 60)}h</span>
          </div>
        )}
      </div>

      {/* Status Badge */}
      <div className="mt-3 flex items-center justify-between">
        <span
          className="badge"
          style={{
            backgroundColor: `${statusColors[task.status]}15`,
            color: statusColors[task.status],
            border: `1px solid ${statusColors[task.status]}30`
          }}
        >
          {task.status.replace('_', ' ')}
        </span>

        {task.completed_at && (
          <span className="text-xs text-gray-400">
            {new Date(task.completed_at).toLocaleDateString()}
          </span>
        )}
      </div>
    </div>
  );
}

export default TaskCard;