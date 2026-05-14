import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Zap, Mail, Lock, Eye, EyeOff, Building2, User2 } from 'lucide-react';
import { API_BASE_URL } from '../api/config';

function Register({ onLogin }) {
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const inviteCompanyId = queryParams.get('company_id');
  const inviteEmail = queryParams.get('email');

  const [regMode, setRegMode] = useState(inviteCompanyId ? 'employee' : 'admin');
  const [form, setForm] = useState({
    name: '', 
    email: inviteEmail || '', 
    password: '', 
    confirmPassword: '', 
    company_name: '',
    company_id: inviteCompanyId || ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const isInvitation = !!inviteCompanyId;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Clean up Company ID if in Employee mode
    if (regMode === 'employee' && !inviteCompanyId && form.company_id) {
      form.company_id = form.company_id.trim();
    }

    setLoading(true);

    try {
      // Step 1: Register user
      const isEmployee = regMode === 'employee';
      const registerPayload = {
        email: form.email,
        password: form.password,
        name: form.name,
        role: isEmployee ? 'employee' : 'admin'
      };

      // Use either the invite ID or the manually entered ID
      const targetCompanyId = isEmployee ? (form.company_id || inviteCompanyId) : null;
      if (targetCompanyId) {
        registerPayload.company_id = targetCompanyId;
      }

      const userRes = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(registerPayload)
      });

      const userData = await userRes.json();
      if (!userRes.ok) {
        setError(userData.error || 'Registration failed');
        setLoading(false);
        return;
      }

      // Step 2: Create company (only if Admin and NOT joining existing)
      if (regMode === 'admin') {
        const companyRes = await fetch(`${API_BASE_URL}/api/company/create`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: form.company_name,
            slug: form.company_name.toLowerCase().replace(/\s+/g, '-'),
            owner_id: userData.user.id
          })
        });
        
        const companyData = await companyRes.json();
        
        if (!companyRes.ok) {
          setError(companyData.error || 'Company creation failed');
          setLoading(false);
          return;
        }

        userData.user.company_id = companyData.company.id;
        userData.user.role = 'super_admin';
      }

      onLogin(userData, regMode);
      navigate('/');
    } catch (err) {
      console.error('Registration error:', err);
      setError(err.message === 'Failed to fetch' 
        ? 'Network error: Cannot connect to the server. Please ensure the backend is running.' 
        : `Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`login-page mode-${regMode}`}>
      <div className="login-container">
        <div className="login-header text-center">
          <div className="logo mb-4">
            <img src="/logo.png" alt="NeuroOps" style={{ width: '48px', height: '48px', objectFit: 'contain' }} />
            <span style={{ fontSize: '1.75rem', fontWeight: 700 }}>Neuro<span>Ops</span></span>
          </div>
          <h1>{regMode === 'admin' ? 'Start a New Company' : 'Join Your Team'}</h1>
          <p className="text-gray">
            {regMode === 'admin' ? 'Create a workspace for your entire team' : 'Join an existing workspace on NeuroOps'}
          </p>
        </div>

        {!isInvitation && (
          <div className="login-tabs mb-6">
            <button 
              type="button"
              className={`login-tab ${regMode === 'admin' ? 'active' : ''}`}
              onClick={() => setRegMode('admin')}
            >
              <Building2 size={18} />
              Management
            </button>
            <button 
              type="button"
              className={`login-tab ${regMode === 'employee' ? 'active' : ''}`}
              onClick={() => setRegMode('employee')}
            >
              <User2 size={18} />
              Employee
            </button>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {error && <div className="alert alert-error mb-4">{error}</div>}

          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input
              type="text"
              className="form-input"
              value={form.name}
              onChange={e => setForm({ ...form, name: e.target.value })}
              required
              placeholder="Enter your full name"
            />
          </div>

          {regMode === 'admin' && (
            <div className="form-group">
              <label className="form-label">Company Name</label>
              <div className="relative">
                <Building2 size={18} className="absolute-icon" />
                <input
                  type="text"
                  className="form-input pl-10"
                  value={form.company_name}
                  onChange={e => setForm({ ...form, company_name: e.target.value })}
                  required
                  placeholder="Your Company Inc."
                />
              </div>
            </div>
          )}

          {regMode === 'employee' && !isInvitation && (
            <div className="form-group">
              <label className="form-label">Company ID</label>
              <div className="relative">
                <Building2 size={18} className="absolute-icon" />
                <input
                  type="text"
                  className="form-input pl-10"
                  value={form.company_id}
                  onChange={e => setForm({ ...form, company_id: e.target.value })}
                  required
                  placeholder="Enter your Company ID"
                />
              </div>
              <small className="text-gray mt-1 block">Ask your admin for the Company ID</small>
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Email Address</label>
            <div className="relative">
              <Mail size={18} className="absolute-icon" />
              <input
                type="email"
                className="form-input pl-10"
                value={form.email}
                onChange={e => setForm({ ...form, email: e.target.value })}
                required
                disabled={!!inviteEmail}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <div className="relative">
              <Lock size={18} className="absolute-icon" />
              <input
                type={showPassword ? 'text' : 'password'}
                className="form-input pl-10 pr-10"
                value={form.password}
                onChange={e => setForm({ ...form, password: e.target.value })}
                required
                minLength={8}
                placeholder="Create a strong password"
              />
              <button
                type="button"
                className="absolute-icon-right"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Confirm Password</label>
            <input
              type="password"
              className="form-input"
              value={form.confirmPassword}
              onChange={e => setForm({ ...form, confirmPassword: e.target.value })}
              required
            />
          </div>

          <button
            type="submit"
            className={`btn ${regMode === 'admin' ? 'btn-primary' : 'btn-success'} btn-lg w-full`}
            disabled={loading}
          >
            {loading ? 'Processing...' : (regMode === 'admin' ? 'Create Company' : 'Join Team')}
          </button>
        </form>

        <div className="text-center mt-6">
          <p className="text-gray">
            Already have an account?{' '}
            <Link to="/login" className="text-primary font-medium">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Register;