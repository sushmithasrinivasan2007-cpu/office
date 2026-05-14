import React, { useState, useEffect } from 'react';
import { CreditCard, FileText, DollarSign, Send, Plus, Calendar, TrendingUp } from 'lucide-react';
import { API_BASE_URL } from '../api/config';

function Billing({ user }) {
  const [invoices, setInvoices] = useState([]);
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('invoices');

  useEffect(() => {
    fetchData();
  }, [user]);

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('smartos_token');
      const [invRes, payRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/invoices?company_id=${user.company_id}`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${API_BASE_URL}/api/payments/company/${user.company_id}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);

      const invData = await invRes.json();
      const payData = await payRes.json();

      setInvoices(invData.invoices || []);
      setPayments(payData.payments || []);
      setLoading(false);
    } catch (error) {
      console.error('Fetch error:', error);
      setLoading(false);
    }
  };

  const totalRevenue = invoices.reduce((sum, inv) => sum + (inv.total_amount || 0), 0);
  const pendingInvoices = invoices.filter(i => i.status === 'sent' || i.status === 'draft').length;
  const paidInvoices = invoices.filter(i => i.status === 'paid').length;

  return (
    <div className="billing-page">
      <div className="page-header flex justify-between items-center">
        <div>
          <h1 className="page-title">Billing</h1>
          <p className="page-subtitle">Manage invoices and payments</p>
        </div>
        <button className="btn btn-primary">
          <Plus size={18} /> New Invoice
        </button>
      </div>

      {/* Stats */}
      <div className="grid-3 mb-4">
        <div className="stat-card">
          <div className="stat-icon green">
            <DollarSign size={24} />
          </div>
          <div className="stat-content">
            <h3>Total Revenue</h3>
            <p className="stat-value">₹{totalRevenue.toLocaleString()}</p>
            <span className="stat-change up">+12% this month</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon blue">
            <FileText size={24} />
          </div>
          <div className="stat-content">
            <h3>Invoices</h3>
            <p className="stat-value">{invoices.length}</p>
            <span className="text-gray text-sm">{pendingInvoices} pending</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon yellow">
            <TrendingUp size={24} />
          </div>
          <div className="stat-content">
            <h3>Paid</h3>
            <p className="stat-value">{paidInvoices}</p>
            <span className="text-gray text-sm">Completion rate: {((paidInvoices / (invoices.length || 1)) * 100).toFixed(0)}%</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs mb-4">
        <button className={`tab ${activeTab === 'invoices' ? 'active' : ''}`} onClick={() => setActiveTab('invoices')}>
          Invoices
        </button>
        <button className={`tab ${activeTab === 'payments' ? 'active' : ''}`} onClick={() => setActiveTab('payments')}>
          Payment History
        </button>
      </div>

      {/* Content */}
      {loading ? (
        <div>Loading...</div>
      ) : activeTab === 'invoices' ? (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Invoice #</th>
                <th>Client</th>
                <th>Amount</th>
                <th>Issue Date</th>
                <th>Due Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {invoices.length === 0 ? (
                <tr><td colSpan="7" className="text-center p-4">No invoices yet</td></tr>
              ) : (
                invoices.map(inv => (
                  <tr key={inv.id}>
                    <td className="font-mono font-medium">{inv.invoice_number}</td>
                    <td>{inv.client_name || 'N/A'}</td>
                    <td className="font-mono">₹{inv.total_amount?.toLocaleString()}</td>
                    <td>{inv.issue_date}</td>
                    <td>{inv.due_date}</td>
                    <td>
                      <span className={`badge badge-${getStatusColor(inv.status)}`}>
                        {inv.status}
                      </span>
                    </td>
                    <td>
                      <button className="btn btn-secondary btn-sm" title="Send">
                        <Send size={14} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Task</th>
                <th>Employee</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {payments.length === 0 ? (
                <tr><td colSpan="5" className="text-center p-4">No payments yet</td></tr>
              ) : (
                payments.map(pay => (
                  <tr key={pay.id}>
                    <td>{pay.task_title || 'Task Payment'}</td>
                    <td>{pay.employee_name || 'Employee'}</td>
                    <td className="font-mono">₹{pay.amount?.toLocaleString()}</td>
                    <td>
                      <span className={`badge badge-${pay.status === 'completed' ? 'success' : 'warning'}`}>
                        {pay.status}
                      </span>
                    </td>
                    <td>{new Date(pay.created_at).toLocaleDateString()}</td>
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

export default Billing;