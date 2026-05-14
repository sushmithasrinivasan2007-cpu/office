import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff, Building2, User2 } from 'lucide-react';

import { API_BASE_URL } from '../api/config';

function Login({ onLogin }) {
  const [form, setForm] = useState({ email: '', password: '' });
  const [loginMode, setLoginMode] = useState('admin'); // 'admin' or 'employee'
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      });

      const data = await res.json();

      if (res.ok) {
        onLogin(data, loginMode);
        navigate('/');
      } else {
        setError(data.error || 'Invalid credentials');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError(err.message === 'Failed to fetch' 
        ? 'Network error: Cannot connect to the server. Please ensure the backend is running.' 
        : `Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`login-page mode-${loginMode}`}>
      <div className="login-container">
        <div className="login-header text-center">
          <div className="logo mb-4">
            <img src="/logo.png" alt="NeuroOps" />
            <span>Neuro<span>Ops</span></span>
          </div>
          <h1>{loginMode === 'admin' ? 'Management Portal' : 'Employee Workspace'}</h1>
          <p className="text-gray">
            {loginMode === 'admin' 
              ? 'Access company analytics and team management' 
              : 'Clock in and manage your daily productivity'}
          </p>
        </div>

        <div className="login-tabs mb-6">
          <button 
            type="button"
            className={`login-tab ${loginMode === 'admin' ? 'active' : ''}`}
            onClick={() => setLoginMode('admin')}
          >
            <Building2 size={18} />
            Management
          </button>
          <button 
            type="button"
            className={`login-tab ${loginMode === 'employee' ? 'active' : ''}`}
            onClick={() => setLoginMode('employee')}
          >
            <User2 size={18} />
            Employee
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          {error && <div className="alert alert-error mb-4">{error}</div>}

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
                placeholder="Enter your email"
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
                placeholder="Enter your password"
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

          <button
            type="submit"
            className={`btn ${loginMode === 'admin' ? 'btn-primary' : 'btn-success'} btn-lg w-full`}
            disabled={loading}
          >
            {loading ? 'Authenticating...' : `Sign in to ${loginMode === 'admin' ? 'Management' : 'Workspace'}`}
          </button>
        </form>

        <div className="text-center mt-6">
          <p className="text-gray">
            Don't have an account?{' '}
            <Link to="/register" className="text-primary font-medium">Create one</Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Login;