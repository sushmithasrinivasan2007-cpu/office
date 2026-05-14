import React, { useState, useEffect } from 'react';
import { UserCheck, Calendar, Clock, AlertTriangle, CheckCircle } from 'lucide-react';
import { API_BASE_URL } from '../api/config';

function HR({ user }) {
  const [leaveRequests, setLeaveRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('smartos_token');
      const res = await fetch(`${API_BASE_URL}/api/hr/leave-requests?company_id=${user.company_id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      setLeaveRequests(data.requests || []);
      setLoading(false);
    } catch (error) {
      console.error('HR fetch error:', error);
      setLoading(false);
    }
  };

  return (
    <div className="hr-page">
      <div className="page-header">
        <h1 className="page-title">Human Resources</h1>
        <p className="page-subtitle">Employee management and leave tracking</p>
      </div>

      <div className="grid-2 mb-4">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Attendance Summary</h2>
          </div>
          <div className="card-body">
            <p className="text-sm text-gray">Today's check-ins</p>
            <p className="stat-value text-primary">12 / 15</p>
            <div className="progress-bar mt-2">
              <div className="progress-fill" style={{ width: '80%' }}></div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Leave Requests</h2>
          </div>
          <div className="card-body">
            <p>Pending approvals: <span className="badge badge-warning">3</span></p>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Recent Leave Requests</h2>
        </div>
        {loading ? (
          <p>Loading...</p>
        ) : leaveRequests.length === 0 ? (
          <div className="empty-state">
            <Calendar size={48} className="empty-state-icon" />
            <p>No leave requests</p>
          </div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Employee</th>
                <th>Type</th>
                <th>Dates</th>
                <th>Days</th>
                <th>Reason</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {leaveRequests.map(req => (
                <tr key={req.id}>
                  <td>{req.employee_name}</td>
                  <td><span className="badge badge-info">{req.leave_type}</span></td>
                  <td>{req.start_date} - {req.end_date}</td>
                  <td>{req.total_days}</td>
                  <td className="max-w-xs truncate">{req.reason}</td>
                  <td>
                    <span className={`badge badge-${getStatusColor(req.status)}`}>
                      {req.status}
                    </span>
                  </td>
                  <td>
                    {req.status === 'pending' && (
                      <div className="flex gap-1">
                        <button className="btn btn-success btn-sm" onClick={() => handleApprove(req.id)}>
                          <CheckCircle size={14} />
                        </button>
                        <button className="btn btn-danger btn-sm" onClick={() => handleReject(req.id)}>
                          <AlertTriangle size={14} />
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function getStatusColor(status) {
  switch (status) {
    case 'approved': return 'success';
    case 'rejected': return 'error';
    case 'pending': return 'warning';
    default: return 'gray';
  }
}

export default HR;