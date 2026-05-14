import React, { useState, useEffect } from 'react';
import { FileText, Plus, Search, Download, Send } from 'lucide-react';
import { API_BASE_URL } from '../api/config';

function Invoices({ user }) {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInvoices();
  }, []);

  const fetchInvoices = async () => {
    try {
      const token = localStorage.getItem('smartos_token');
      const res = await fetch(`${API_BASE_URL}/api/invoices?company_id=${user.company_id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      setInvoices(data.invoices || []);
      setLoading(false);
    } catch (error) {
      console.error('Fetch invoices error:', error);
      setLoading(false);
    }
  };

  const handleSend = async (id) => {
    try {
      const token = localStorage.getItem('smartos_token');
      await fetch(`${API_BASE_URL}/api/invoices/${id}/send`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Invoice sent!');
      fetchInvoices();
    } catch (error) {
      alert('Failed to send invoice');
    }
  };

  return (
    <div className="invoices-page">
      <div className="page-header flex justify-between items-center">
        <div>
          <h1 className="page-title">Invoices</h1>
          <p className="page-subtitle">Create and manage client invoices</p>
        </div>
        <button className="btn btn-primary">
          <Plus size={18} /> Create Invoice
        </button>
      </div>

      {loading ? (
        <div>Loading invoices...</div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Invoice #</th>
                <th>Client</th>
                <th>Items</th>
                <th>Amount</th>
                <th>Issue Date</th>
                <th>Due Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {invoices.length === 0 ? (
                <tr>
                  <td colSpan="8" className="text-center p-4">
                    <div className="empty-state">
                      <FileText size={48} className="empty-state-icon" />
                      <p>No invoices created yet</p>
                    </div>
                  </td>
                </tr>
              ) : (
                invoices.map(inv => (
                  <tr key={inv.id}>
                    <td className="font-mono font-medium">{inv.invoice_number}</td>
                    <td>{inv.client_name || 'Unknown'}</td>
                    <td>{(inv.items?.length || 0)} items</td>
                    <td className="font-mono font-semibold">₹{inv.total_amount?.toLocaleString()}</td>
                    <td>{inv.issue_date}</td>
                    <td>{inv.due_date}</td>
                    <td>
                      <span className={`badge badge-${getStatusColor(inv.status)}`}>
                        {inv.status}
                      </span>
                    </td>
                    <td>
                      <div className="flex gap-1">
                        <button className="btn btn-secondary btn-sm" title="Download PDF" onClick={() => handleDownload(inv.id)}>
                          <Download size={14} />
                        </button>
                        {(inv.status === 'draft' || inv.status === 'sent') && (
                          <button className="btn btn-primary btn-sm" title="Send" onClick={() => handleSend(inv.id)}>
                            <Send size={14} />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function getStatusColor(status) {
  switch (status) {
    case 'paid': return 'success';
    case 'sent': return 'info';
    case 'draft': return 'gray';
    case 'overdue': return 'error';
    default: return 'warning';
  }
}

export default Invoices;