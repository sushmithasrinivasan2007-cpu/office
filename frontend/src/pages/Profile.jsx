import React, { useState, useEffect } from 'react';
import { User, Mail, Phone, MapPin, Building2, Shield, Key, X, Bot, Send, Loader2, Sparkles, BookOpen, AlertTriangle } from 'lucide-react';
import QRCode from 'qrcode';
import { API_BASE_URL } from '../api/config';

function Profile({ user }) {
  const [userData, setUserData] = useState(user || {});
  const [qrCode, setQrCode] = useState('');
  const [show2FA, setShow2FA] = useState(false);
  const [secret, setSecret] = useState('');

  useEffect(() => {
    fetchUserProfile();
  }, []);

  const fetchUserProfile = async () => {
    try {
      const token = localStorage.getItem('smartos_token');
      const res = await fetch(`${API_BASE_URL}/api/users/profile/${user.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      if (data.profile) {
        setUserData(data.profile);
      }
    } catch (error) {
      console.error('Fetch profile error:', error);
    }
  };

  const handle2FASetup = async () => {
    try {
      const token = localStorage.getItem('smartos_token');
      const res = await fetch(`${API_BASE_URL}/api/auth/2fa/enable`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: user.id })
      });
      const data = await res.json();
      setSecret(data.secret);
      QRCode.toDataURL(data.qr_uri, (err, url) => {
        if (!err) setQrCode(url);
      });
      setShow2FA(true);
    } catch (error) {
      alert('Failed to setup 2FA');
    }
  };

  const verify2FA = async (code) => {
    try {
      const token = localStorage.getItem('smartos_token');
      await fetch(`${API_BASE_URL}/api/auth/2fa/verify`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: user.id, code })
      });
      alert('2FA enabled!');
      setShow2FA(false);
      fetchUserProfile();
    } catch (error) {
      alert('Invalid code');
    }
  };

  return (
    <div className="profile-page">
      <div className="page-header">
        <h1 className="page-title">Profile</h1>
        <p className="page-subtitle">Manage your account settings</p>
      </div>

      <div className="grid-3">
        {/* Profile Card */}
        <div className="card">
          <div className="card-body text-center">
            <div className="avatar mx-auto mb-3" style={{ width: '80px', height: '80px', fontSize: '2rem' }}>
              {userData.name?.charAt(0).toUpperCase()}
            </div>
            <h2 className="text-xl font-semibold">{userData?.name || 'User'}</h2>
            <p className="text-gray">{userData?.role?.toUpperCase() || 'EMPLOYEE'}</p>
            <p className="text-sm text-gray mt-2">{userData?.email || 'No email'}</p>
            <p className="text-sm text-gray">{userData?.phone || 'No phone'}</p>
          </div>
        </div>

        {/* Details */}
        <div className="card col-span-2">
          <div className="card-header">
            <h2 className="card-title">Account Details</h2>
          </div>
          <div className="card-body">
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <input type="text" className="form-input" defaultValue={userData.name || ''} />
              </div>
              <div className="form-group">
                <label className="form-label">Email</label>
                <input type="email" className="form-input" defaultValue={userData.email || ''} readOnly />
              </div>
              <div className="form-group">
                <label className="form-label">Phone</label>
                <input type="tel" className="form-input" defaultValue={userData.phone || ''} />
              </div>
              <div className="form-group">
                <label className="form-label">Timezone</label>
                <select className="form-input form-select" defaultValue={userData.timezone || 'UTC'}>
                  <option value="UTC">UTC</option>
                  <option value="Asia/Kolkata">India (IST)</option>
                </select>
              </div>
              <div className="form-group col-span-2">
                <label className="form-label">Bio</label>
                <textarea className="form-input" rows={3} defaultValue={userData.bio || ''} placeholder="Tell us about yourself..." />
              </div>
            </div>
            <button className="btn btn-primary" onClick={() => alert('Profile update would go here!')}>
              Save Changes
            </button>
          </div>
        </div>
      </div>

      {/* Security */}
      <div className="card mt-4">
        <div className="card-header">
          <h2 className="card-title">Security</h2>
        </div>
        <div className="card-body">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Shield size={20} className="text-primary" />
              <div>
                <p className="font-medium">Two-Factor Authentication</p>
                <p className="text-sm text-gray">
                  {userData.two_factor_enabled
                    ? '2FA is enabled. Adds an extra layer of security.'
                    : '2FA is disabled. Enable for better account protection.'
                  }
                </p>
              </div>
            </div>
            {!userData.two_factor_enabled ? (
              <button className="btn btn-primary" onClick={handle2FASetup}>
                <Key size={16} /> Enable 2FA
              </button>
            ) : (
              <span className="badge badge-success">Enabled</span>
            )}
          </div>

          {/* 2FA Setup Modal */}
          {show2FA && (
            <div className="modal-overlay mt-4" onClick={() => setShow2FA(false)}>
              <div className="modal" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                  <h2 className="modal-title">Scan QR Code</h2>
                  <button className="modal-close" onClick={() => setShow2FA(false)}>
                    <X size={20} />
                  </button>
                </div>
                <div className="modal-body text-center">
                  <p className="mb-3">Scan this QR code with your authenticator app:</p>
                  {qrCode && <img src={qrCode} alt="2FA QR" className="mx-auto mb-3" />}
                  <p className="font-mono text-sm mb-3">{secret}</p>
                  <div className="form-group">
                    <label className="form-label">Enter 6-digit code</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="123456"
                      maxLength={6}
                      onBlur={e => verify2FA(e.target.value)}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Profile;