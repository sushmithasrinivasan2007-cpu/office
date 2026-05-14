import React, { useState, useEffect } from 'react';
import { TrendingUp, DollarSign, BarChart3, PieChart, Users, Calendar } from 'lucide-react';
import PerformanceChart from '../components/PerformanceChart';
import { API_BASE_URL } from '../api/config';

function Analytics({ user }) {
  const [dashboard, setDashboard] = useState(null);
  const [benchmark, setBenchmark] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, [user]);

  const fetchAnalytics = async () => {
    if (!user.company_id || user.company_id === 'undefined') {
      setLoading(false);
      return;
    }

    try {
      const token = localStorage.getItem('smartos_token');
      const [dashRes, benchRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/analytics/dashboard/${user.company_id}`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${API_BASE_URL}/api/analytics/benchmark/${user.company_id}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);

      const dash = await dashRes.json();
      const bench = await benchRes.json();

      setDashboard(dash);
      setBenchmark(bench);
      setLoading(false);
    } catch (error) {
      console.error('Analytics fetch error:', error);
      setLoading(false);
    }
  };

  const getPerformanceLabel = (completionRate) => {
    if (completionRate >= 90) return { text: 'Excellent', class: 'badge-success' };
    if (completionRate >= 70) return { text: 'Good', class: 'badge-info' };
    if (completionRate >= 50) return { text: 'Average', class: 'badge-warning' };
    return { text: 'Needs Improvement', class: 'badge-error' };
  };

  if (loading) return <div>Loading analytics...</div>;

  return (
    <div className="analytics-page">
      <div className="page-header">
        <h1 className="page-title">Analytics</h1>
        <p className="page-subtitle">Performance metrics and insights</p>
      </div>

      {/* Top Stats */}
      <div className="grid-4 mb-4">
        <div className="stat-card">
          <div className="stat-icon blue">
            <BarChart3 size={24} />
          </div>
          <div className="stat-content">
            <h3>Completion Rate</h3>
            <p className="stat-value">{dashboard?.tasks?.completion_rate?.toFixed(1) || 0}%</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon green">
            <DollarSign size={24} />
          </div>
          <div className="stat-content">
            <h3>Total Revenue</h3>
            <p className="stat-value">₹{dashboard?.payments?.total_disbursed?.toLocaleString() || 0}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon yellow">
            <Users size={24} />
          </div>
          <div className="stat-content">
            <h3>Active Employees</h3>
            <p className="stat-value">{dashboard?.employees?.total_count || 0}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon purple">
            <TrendingUp size={24} />
          </div>
          <div className="stat-content">
            <h3>Tasks Completed</h3>
            <p className="stat-value">{dashboard?.tasks?.completed || 0}</p>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid-2 mb-4">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Task Status</h2>
          </div>
          <div className="card-body">
            <div className="chart-placeholder">
              <PieChart size={32} style={{ marginRight: '0.5rem' }} />
              Status distribution chart (integrate Chart.js)
            </div>
            <div className="mt-3 grid-2">
              <StatItem label="Completed" value={dashboard?.tasks?.completed || 0} color="text-success" />
              <StatItem label="In Progress" value={dashboard?.tasks?.in_progress || 0} color="text-primary" />
              <StatItem label="Pending" value={dashboard?.tasks?.pending || 0} color="text-warning" />
              <StatItem label="Overdue" value={dashboard?.tasks?.overdue || 0} color="text-error" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Productivity Trend</h2>
          </div>
          <div className="card-body">
            <PerformanceChart companyId={user.company_id} />
          </div>
        </div>
      </div>

      {/* Performance Table */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Team Performance</h2>
        </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Employee</th>
                <th>Total Tasks</th>
                <th>Completed</th>
                <th>Completion %</th>
                <th>Earnings</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {benchmark?.employee_benchmark?.map((emp, idx) => (
                <tr key={idx}>
                  <td className="font-medium">{emp.name}</td>
                  <td>{emp.tasks_completed + Math.round(emp.tasks_completed / (emp.completion_rate / 100) - emp.tasks_completed)}</td>
                  <td>{emp.tasks_completed}</td>
                  <td>
                    <span className={`badge ${getPerformanceClass(emp.completion_rate)}`}>
                      {emp.completion_rate.toFixed(0)}%
                    </span>
                  </td>
                  <td>
                    <span className="font-mono">₹{emp.total_earnings?.toLocaleString() || 0}</span>
                  </td>
                  <td>
                    {emp.vs_average === 'above' ? (
                      <span className="badge badge-success">Above Average</span>
                    ) : (
                      <span className="badge badge-warning">Below Average</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function StatItem({ label, value, color }) {
  return (
    <div className="text-center">
      <p className={`stat-value ${color}`}>{value}</p>
      <p className="text-sm text-gray">{label}</p>
    </div>
  );
}

function getPerformanceClass(rate) {
  if (rate >= 80) return 'badge-success';
  if (rate >= 60) return 'badge-info';
  if (rate >= 40) return 'badge-warning';
  return 'badge-error';
}


export default Analytics;