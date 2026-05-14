import React from 'react';
import { Users, UserPlus, Building2, Mail, Phone, MapPin } from 'lucide-react';
import { API_BASE_URL } from '../api/config';

function CRM({ user }) {
  const [clients, setClients] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [showAdd, setShowAdd] = React.useState(false);

  React.useEffect(() => {
    fetchClients();
  }, []);

  const fetchClients = async () => {
    try {
      const token = localStorage.getItem('smartos_token');
      const res = await fetch(`${API_BASE_URL}/api/clients?company_id=${user.company_id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (!res.ok) throw new Error('Failed to fetch clients');
      
      const data = await res.json();
      setClients(data.clients || []);
      setLoading(false);
    } catch (error) {
      console.error('Fetch clients error:', error);
      setLoading(false);
    }
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('smartos_token');
      const formData = new FormData(e.target);
      const res = await fetch(`${API_BASE_URL}/api/clients`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: formData.get('name'),
          email: formData.get('email'),
          phone: formData.get('phone'),
          company_id: user.company_id,
          created_by: user.id
        })
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || 'Failed to add client');
      }

      setShowAdd(false);
      fetchClients();
    } catch (error) {
      console.error('Add client error:', error);
      alert(error.message || 'Failed to add client');
    }
  };

  return (
    <div className="crm-page">
      <div className="page-header flex justify-between items-center">
        <div>
          <h1 className="page-title">CRM</h1>
          <p className="page-subtitle">Client management & relationships</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowAdd(true)}>
          <UserPlus size={18} /> Add Client
        </button>
      </div>

      {loading ? (
        <div>Loading clients...</div>
      ) : (
        <div className="grid-2">
          {clients.length === 0 ? (
            <div className="col-span-full">
              <div className="empty-state">
                <Building2 size={48} className="empty-state-icon" />
                <h3>No clients yet</h3>
                <p>Add your first client to get started.</p>
              </div>
            </div>
          ) : (
            clients.map(client => (
              <div key={client.id} className="card">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h3 className="font-semibold">{client.name}</h3>
                    <p className="text-sm text-gray">{client.email}</p>
                  </div>
                  <Building2 size={20} className="text-gray" />
                </div>
                {client.phone && <p className="text-sm mb-1">📞 {client.phone}</p>}
                {client.address && <p className="text-sm text-gray mb-2">📍 {client.address}</p>}
                <div className="flex gap-2 mt-3">
                  <a href={`mailto:${client.email}`} className="btn btn-secondary btn-sm">
                    <Mail size={14} /> Email
                  </a>
                  <button className="btn btn-primary btn-sm">View Details</button>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Add Client Modal */}
      {showAdd && (
        <div className="modal-overlay" onClick={() => setShowAdd(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Add New Client</h2>
              <button className="modal-close" onClick={() => setShowAdd(false)}>
                ✕
              </button>
            </div>
            <form onSubmit={handleAdd}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Client Name *</label>
                  <input type="text" name="name" className="form-input" required />
                </div>
                <div className="form-group">
                  <label className="form-label">Email</label>
                  <input type="email" name="email" className="form-input" />
                </div>
                <div className="form-group">
                  <label className="form-label">Phone</label>
                  <input type="tel" name="phone" className="form-input" />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowAdd(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Add Client</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default CRM;