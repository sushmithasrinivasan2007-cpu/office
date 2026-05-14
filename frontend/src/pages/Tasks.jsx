import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  Plus, Calendar, MapPin, Clock, User, DollarSign, Edit, Trash2,
  CheckCircle, AlertTriangle, Bot, Zap, ArrowLeft, FileText, MessageSquare,
  Briefcase
} from 'lucide-react';
import CreateTaskModal from '../components/CreateTaskModal';
import TaskDetailModal from '../components/TaskDetailModal';
import { API_BASE_URL } from '../api/config';

function Tasks({ user }) {
  const { id } = useParams();
  const [tasks, setTasks] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);

  useEffect(() => {
    fetchTasks();
  }, [user, filter]);

  const fetchTasks = async () => {
    if (!user.company_id || user.company_id === 'undefined') {
      setLoading(false);
      return;
    }
    
    try {
      const token = localStorage.getItem('smartos_token');
      let url = `${API_BASE_URL}/api/tasks/?company_id=${user.company_id}`;

      if (filter === 'assigned') {
        url += `&user_id=${user.id}`;
      } else if (filter === 'pending') {
        url += '&status=pending';
      } else if (filter === 'completed') {
        url += '&status=completed';
      }

      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const data = await res.json();
      setTasks(data.tasks || []);
      setLoading(false);

      // If navigating to specific task detail
      if (id) {
        const task = (data.tasks || []).find(t => t.id === id);
        if (task) setSelectedTask(task);
      }
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
      setLoading(false);
    }
  };

  const handleComplete = async (taskId) => {
    try {
      const token = localStorage.getItem('smartos_token');
      await fetch(`${API_BASE_URL}/api/tasks/${taskId}/complete`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: user.id })
      });
      fetchTasks();
    } catch (error) {
      console.error('Failed to complete task:', error);
      alert('Failed to complete task');
    }
  };

  const handleDelete = async (taskId) => {
    if (!confirm('Delete this task?')) return;
    try {
      const token = localStorage.getItem('smartos_token');
      await fetch(`${API_BASE_URL}/api/tasks/${taskId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchTasks();
    } catch (error) {
      console.error('Failed to delete task:', error);
    }
  };

  const getRiskLevel = (task) => {
    if (task.ai_risk_score > 0.7) return 'high';
    if (task.ai_risk_score > 0.4) return 'medium';
    return 'low';
  };

  const renderTaskCard = (task) => (
    <div
      key={task.id}
      className={`task-card ${task.status === 'completed' ? 'completed' : ''}`}
      onClick={() => setSelectedTask(task)}
    >
      <div className="task-card-header">
        <div className="task-title-section">
          <h3 className="task-title">{task.title}</h3>
          <div className="flex gap-1 mt-1">
            <span className={`badge badge-${getPriorityColor(task.priority)}`}>{task.priority}</span>
            <span className={`badge badge-${getStatusColor(task.status)}`}>{task.status}</span>
          </div>
        </div>
        <div className="flex gap-1">
          {task.ai_risk_score > 0.5 && (
            <span className="badge badge-error">High Risk</span>
          )}
        </div>
      </div>

      <p className="text-sm text-gray mt-1 line-clamp-2">
        {task.description || 'No description provided.'}
      </p>

      {/* Task Meta */}
      <div className="task-meta">
        {task.deadline && (
          <span className="task-meta-item">
            <Calendar size={14} />
            {formatDate(task.deadline)}
            {isOverdue(task.deadline, task.status) && <AlertTriangle size={14} className="text-error" />}
          </span>
        )}
        {task.location_lat && (
          <span className="task-meta-item">
            <MapPin size={14} />
            {task.location_address || 'Location set'}
          </span>
        )}

        {task.assigned_to && (
          <span className="task-meta-item">
            <User size={14} />
            {task.assigned_to_name || 'Assigned'}
          </span>
        )}
      </div>

      {/* Actions */}
      {task.assigned_to === user.id && task.status === 'pending' && (
        <div className="task-actions mt-2" onClick={e => e.stopPropagation()}>
          <button
            className="btn btn-success btn-sm"
            onClick={() => handleComplete(task.id)}
          >
            <CheckCircle size={14} /> Complete
          </button>
        </div>
      )}

      {/* Payment Approval Removed */}
    </div>
  );

  return (
    <div className="tasks-page">
      <div className="page-header">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="page-title">Tasks</h1>
            <p className="page-subtitle">Manage and track all tasks across your team</p>
          </div>
          {(user.role === 'admin' || user.role === 'super_admin') && (
            <div className="flex gap-2">
              <button className="btn btn-secondary" onClick={() => setShowCreateModal(true)}>
                <Plus size={18} /> Create with AI
              </button>
              <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
                <Plus size={18} /> New Task
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="tabs mb-4">
        {['all', 'assigned', 'pending', 'completed', 'overdue'].map(f => (
          <button
            key={f}
            className={`tab ${filter === f ? 'active' : ''}`}
            onClick={() => setFilter(f)}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {/* Task Grid / Kanban */}
      {user.role === 'admin' || user.role === 'manager' ? (
        <div className="kanban-board">
          {/* For demo, show as grid */}
          <div className="grid-3">
            {loading ? (
              <div className="col-span-full text-center">Loading tasks...</div>
            ) : tasks.length === 0 ? (
              <div className="col-span-full">
                <div className="empty-state">
                  <Briefcase size={48} className="empty-state-icon" />
                  <h3>No tasks found</h3>
                  <p>Create your first task to get started.</p>
                  <button className="btn btn-primary mt-3" onClick={() => setShowCreateModal(true)}>
                    <Plus size={18} /> Create Task
                  </button>
                </div>
              </div>
            ) : (
              tasks.map(renderTaskCard)
            )}
          </div>
        </div>
      ) : (
        <div className="grid-2">
          {!loading && tasks.map(renderTaskCard)}
        </div>
      )}

      {/* Create Task Modal */}
      {showCreateModal && (
        <CreateTaskModal
          user={user}
          onClose={() => setShowCreateModal(false)}
          onCreated={() => { fetchTasks(); setShowCreateModal(false); }}
        />
      )}

      {/* Task Detail Modal */}
      {selectedTask && (
        <TaskDetailModal
          task={selectedTask}
          user={user}
          onClose={() => {
            setSelectedTask(null);
            if (id) window.history.pushState({}, '', '/tasks');
          }}
          onUpdate={() => { fetchTasks(); setSelectedTask(null); }}
        />
      )}
    </div>
  );
}

function getPriorityColor(priority) {
  switch (priority) {
    case 'critical': return 'error';
    case 'high': return 'warning';
    case 'medium': return 'info';
    case 'low': return 'gray';
    default: return 'info';
  }
}

function getStatusColor(status) {
  switch (status) {
    case 'completed':
    case 'verified': return 'success';
    case 'in_progress': return 'info';
    case 'overdue': return 'error';
    default: return 'gray';
  }
}

function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function isOverdue(deadline, status) {
  if (!deadline || status === 'completed') return false;
  return new Date(deadline) < new Date();
}

export default Tasks;