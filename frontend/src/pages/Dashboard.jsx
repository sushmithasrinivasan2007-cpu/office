import React from 'react';
import { Link } from 'react-router-dom';
import {
  LayoutDashboard, Briefcase, CheckCircle, Clock, AlertTriangle, Users,
  TrendingUp, DollarSign, Zap, Calendar, Bot, ArrowRight
} from 'lucide-react';
import TaskCard from '../components/TaskCard';
import AISummary from '../components/AISummary';
import PerformanceChart from '../components/PerformanceChart';
import { API_BASE_URL } from '../api/config';

function Dashboard({ user }) {
  const [stats, setStats] = React.useState({
    totalTasks: 0,
    completedToday: 0,
    overdue: 0,
    pending: 0,
    pendingPayments: 0,
    teamSize: 0,
    personalCompleted: 0
  });
  const [recentTasks, setRecentTasks] = React.useState([]);
  const [insight, setInsight] = React.useState(null);
  const [loading, setLoading] = React.useState(true);

  const isAdmin = user.role === 'admin' || user.role === 'manager' || user.role === 'super_admin';

  React.useEffect(() => {
    fetchDashboardData();
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('smartos_token');
      const companyId = user.company_id;

      // Fetch tasks
      let tasks = [];
      if (companyId && companyId !== 'undefined') {
        const tasksRes = await fetch(`${API_BASE_URL}/api/tasks/?company_id=${companyId}&limit=20`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const tasksData = await tasksRes.json();
        tasks = tasksData.tasks || [];
      }

      // Fetch analytics (if admin)
      let analyticsData = {};
      if (isAdmin && companyId && companyId !== 'undefined') {
        const analyticsRes = await fetch(`${API_BASE_URL}/api/analytics/dashboard/${companyId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        analyticsData = await analyticsRes.json();
      }

      // Fetch AI suggestion
      let aiData = {};
      if (user && user.id) {
        const aiRes = await fetch(`${API_BASE_URL}/api/ai/smart-plan?user_id=${user.id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        aiData = await aiRes.json();
      }

      const userTasks = tasks.filter(t => t.assigned_to === user.id);

      setStats({
        totalTasks: isAdmin ? tasks.length : userTasks.length,
        completedToday: tasks.filter(t => t.status === 'completed' && isToday(t.completed_at)).length,
        overdue: (isAdmin ? tasks : userTasks).filter(t => isOverdue(t.deadline, t.status)).length,
        pending: (isAdmin ? tasks : userTasks).filter(t => t.status === 'pending').length,
        pendingPayments: analyticsData.payments?.pending || 0,
        teamSize: analyticsData.employees?.total_count || 0,
        personalCompleted: userTasks.filter(t => t.status === 'completed').length
      });

      setRecentTasks(isAdmin ? tasks.slice(0, 5) : userTasks.slice(0, 5));
      setInsight(aiData);
      setLoading(false);
    } catch (error) {
      console.error('Dashboard fetch error:', error);
      setLoading(false);
    }
  };

  const isToday = (dateStr) => {
    if (!dateStr) return false;
    const date = new Date(dateStr);
    return date.toDateString() === new Date().toDateString();
  };

  const isOverdue = (deadline, status) => {
    if (!deadline || status === 'completed') return false;
    return new Date(deadline) < new Date();
  };

  const getTimeGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Morning';
    if (hour < 17) return 'Afternoon';
    return 'Evening';
  };

  if (loading) {
    return (
      <div className="loading-state">
        <div className="spinner"></div>
        <p>Loading your {isAdmin ? 'Admin' : 'Personal'} Panel...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="page-header">
        <div className="flex justify-between items-center w-full">
          <div>
            <h1 className="page-title">
              {isAdmin ? 'Management Console' : `Good ${getTimeGreeting()}, ${(user.name || 'User').split(' ')[0]}!`}
            </h1>
            <p className="page-subtitle">
              {isAdmin 
                ? "Here's what's happening across your company today." 
                : "Ready to crush your goals? Here is your workspace summary."}
            </p>
          </div>
          <div className={`badge ${isAdmin ? 'badge-blue' : 'badge-success'}`} style={{ padding: '0.5rem 1rem' }}>
            <div className="flex items-center gap-2">
              <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'currentColor', animation: 'pulse 2s infinite' }}></div>
              {isAdmin ? 'Admin Mode' : 'Employee Workspace'}
            </div>
          </div>
        </div>
      </div>

      {/* AI Insight Panel */}
      {insight && insight.risk_alerts && insight.risk_alerts.length > 0 && (
        <div className="ai-insight mb-4">
          <div className="ai-insight-header">
            <Bot size={24} />
            <h3>AI Productivity Insight</h3>
          </div>
          <div className="ai-insight-content">
            <p>You have {insight.risk_alerts.length} tasks that may need urgent attention. Focus on these for maximum impact:</p>
            <ul style={{ marginTop: '0.8rem', paddingLeft: '1.5rem' }}>
              {insight.risk_alerts.map((task, i) => (
                <li key={i}>{task.title}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid-4 mb-4">
        <div className="stat-card">
          <div className="stat-icon blue">
            <Briefcase size={24} />
          </div>
          <div className="stat-content">
            <h3>{isAdmin ? 'Total Projects' : 'Assigned Tasks'}</h3>
            <p className="stat-value">{stats.totalTasks}</p>
            <span className="stat-change up">
              {stats.pending} pending
            </span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon green">
            <CheckCircle size={24} />
          </div>
          <div className="stat-content">
            <h3>Completed Today</h3>
            <p className="stat-value">{stats.completedToday}</p>
            <span className="stat-change up">Excellent progress!</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon red">
            <AlertTriangle size={24} />
          </div>
          <div className="stat-content">
            <h3>Overdue</h3>
            <p className="stat-value">{stats.overdue}</p>
            <span className="stat-change down">Action required</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon purple">
            {isAdmin ? <Users size={24} /> : <Zap size={24} />}
          </div>
          <div className="stat-content">
            <h3>{isAdmin ? 'Team Members' : 'Productivity'}</h3>
            <p className="stat-value">{isAdmin ? stats.teamSize : 'High'}</p>
            <span className="stat-change">
              {isAdmin ? 'Active currently' : 'Based on last 7 days'}
            </span>
          </div>
        </div>
      </div>

      {/* Conditional Layouts */}
      <div className="grid-2 mb-4">
        {/* Recent Activity */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">{isAdmin ? 'Recent Team Activity' : 'My Recent Tasks'}</h2>
            <Link to="/tasks" className="btn btn-secondary btn-sm">View All</Link>
          </div>
          <div className="card-body">
            {recentTasks.length > 0 ? (
              <div className="space-y-3">
                {recentTasks.map(task => (
                  <div key={task.id} className="task-item-mini p-3 border rounded-lg hover:bg-gray-50 flex justify-between items-center cursor-pointer">
                    <div>
                      <h4 className="font-medium text-sm">{task.title}</h4>
                      <p className="text-xs text-gray">{task.status}</p>
                    </div>
                    <span className={`badge badge-sm ${task.priority === 'critical' ? 'badge-error' : 'badge-info'}`}>
                      {task.priority}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state py-8">
                <p>No activity to show</p>
              </div>
            )}
          </div>
        </div>

        {/* Dynamic Widget */}
        <div className="widget">
          <div className="widget-title">
            <Zap size={18} />
            <span>{isAdmin ? 'Team Suggestions' : 'Quick Actions'}</span>
          </div>
          <div className="card-body">
            {isAdmin ? (
              <div className="space-y-2">
                <p className="text-sm">Based on current workload, you should reassign 3 tasks from Rahul to Sushmitha.</p>
                <button className="btn btn-primary btn-sm w-full">Optimize Workflow</button>
              </div>
            ) : (
              <div className="grid-2 gap-2">
                {(user.role === 'admin' || user.role === 'super_admin') && (
                  <Link to="/tasks" className="btn btn-secondary btn-sm text-center">New Task</Link>
                )}
                <Link to="/ai" className="btn btn-secondary btn-sm text-center">Ask AI</Link>
                <Link to="/attendance" className="btn btn-secondary btn-sm text-center">Check In</Link>
                <Link to="/profile" className="btn btn-secondary btn-sm text-center">Profile</Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Performance Chart (Manager/Admin only) */}
      {isAdmin && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Team Performance Trend</h2>
          </div>
          <div className="card-body">
            <PerformanceChart companyId={user.company_id} />
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;