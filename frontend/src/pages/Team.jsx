import React, { useState, useEffect } from 'react';
import { UserPlus, Search, Mail, MoreVertical, TrendingUp, Clock, CheckCircle, AlertTriangle, X, Users, Briefcase } from 'lucide-react';
import CreateTaskModal from '../components/CreateTaskModal';
import { API_BASE_URL } from '../api/config';

function Team({ user }) {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showInvite, setShowInvite] = useState(false);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [selectedAssignee, setSelectedAssignee] = useState(null);

  useEffect(() => {
    fetchTeam();
  }, [user]);

  const fetchTeam = async () => {
    if (!user.company_id || user.company_id === 'undefined') {
      setLoading(false);
      return;
    }
    
    try {
      const token = localStorage.getItem('smartos_token');
      const res = await fetch(`${API_BASE_URL}/api/company/${user.company_id}/team`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      setMembers(data.team || []);
      setLoading(false);
    } catch (error) {
      console.error('Fetch team error:', error);
      setLoading(false);
    }
  };

  const openAssignModal = (member) => {
    setSelectedAssignee(member);
    setShowAssignModal(true);
  };

  const handleInvite = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('smartos_token');
      const formData = new FormData(e.target);
      const res = await fetch(`${API_BASE_URL}/api/company/${user.company_id}/invite`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email: formData.get('email'),
          name: formData.get('name'),
          role: formData.get('role'),
          invited_by: user.id
        })
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || 'Failed to send invitation');
      }

      await fetchTeam(); // Refresh the list
      setShowInvite(false);
      e.target.reset();
      alert('Invitation sent!');
    } catch (error) {
      alert(error.message || 'Failed to send invitation');
    }
  };

  const filteredMembers = members.filter(m =>
    m.name?.toLowerCase().includes(search.toLowerCase()) ||
    m.email?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="team-page">
      <div className="page-header flex justify-between items-center">
        <div>
          <h1 className="page-title">Team</h1>
          <p className="page-subtitle">Manage your company's team members</p>
        </div>
        {(user.role === 'admin' || user.role === 'super_admin') && (
          <button className="btn btn-primary" onClick={() => setShowInvite(true)}>
            <UserPlus size={18} /> Invite Member
          </button>
        )}
      </div>

      {/* Search */}
      <div className="card mb-4">
        <div className="form-group mb-0">
          <div className="relative">
            <Search size={18} className="absolute-icon" style={{ left: '12px', top: '12px', color: '#9ca3af' }} />
            <input
              type="text"
              className="form-input pl-10"
              placeholder="Search team members by name or email..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Team Grid */}
      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Fetching your team...</p>
        </div>
      ) : filteredMembers.length === 0 ? (
        <div className="empty-state">
          <Users size={48} className="empty-state-icon" />
          <h3>No team members found</h3>
          <p>Invite your first team member to get started.</p>
          <p className="text-xs text-gray mt-2">Company ID: {user.company_id || 'Not found'}</p>
        </div>
      ) : (
        <div className="grid-2">
          {filteredMembers.map(member => (
            <div key={member.id} className="employee-card">
              <div className="employee-avatar">
                {member.name?.charAt(0).toUpperCase() || 'U'}
              </div>
              <div className="employee-info flex-1">
                <h4>{member.name}</h4>
                <p className="employee-role">{member.role}</p>
                <p className="text-sm text-gray">{member.email}</p>
                {member.is_pending ? (
                  <span className="badge badge-warning" style={{ background: '#fff7ed', color: '#c2410c', border: '1px solid #ffedd5', marginTop: '0.5rem' }}>Pending</span>
                ) : !member.is_active && (
                  <span className="badge badge-gray" style={{ marginTop: '0.5rem' }}>Inactive</span>
                )}
              </div>
              <div className="flex gap-2">
                {(user.role === 'admin' || user.role === 'super_admin') && (
                  <button 
                    className="btn btn-secondary btn-sm"
                    onClick={() => openAssignModal(member)}
                    title="Assign Task"
                  >
                    <Briefcase size={16} />
                  </button>
                )}
                <button className="btn btn-secondary btn-sm">
                  <MoreVertical size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Assign Task Modal */}
      {showAssignModal && (
        <CreateTaskModal
          user={user}
          initialAssignee={selectedAssignee?.id}
          onClose={() => setShowAssignModal(false)}
          onCreated={() => {
            setShowAssignModal(false);
            alert(`Task assigned to ${selectedAssignee?.name}`);
          }}
        />
      )}

      {/* Invite Modal */}
      {showInvite && (
        <div className="modal-overlay" onClick={() => setShowInvite(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Invite Team Member</h2>
              <button className="modal-close" onClick={() => setShowInvite(false)}>
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleInvite}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Email Address *</label>
                  <input type="email" name="email" className="form-input" required placeholder="colleague@company.com" />
                </div>
                <div className="form-group">
                  <label className="form-label">Full Name *</label>
                  <input type="text" name="name" className="form-input" required placeholder="John Doe" />
                </div>
                <div className="form-group">
                  <label className="form-label">Role</label>
                  <select name="role" className="form-input form-select">
                    <option value="employee">Employee</option>
                    <option value="manager">Manager</option>
                    {(user.role === 'admin' || user.role === 'super_admin') && (
                      <option value="admin">Admin</option>
                    )}
                  </select>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowInvite(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Send Invite
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Team;