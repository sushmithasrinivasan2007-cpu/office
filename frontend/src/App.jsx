import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom';
import { MapPin, Briefcase, Users, LayoutDashboard, CreditCard, FileText, BarChart3, Settings as SettingsIcon, Bot, Calendar, Bell, LogOut, User, Menu, X, Building2, Bot as BotIcon, Zap, CheckCircle } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Tasks from './pages/Tasks';
import Team from './pages/Team';
import Billing from './pages/Billing';
import Invoices from './pages/Invoices';
import Analytics from './pages/Analytics';
import CRM from './pages/CRM';
import HR from './pages/HR';
import Settings from './pages/Settings';
import AIChat from './pages/AIChat';
import Profile from './pages/Profile';
import Login from './pages/Login';
import Register from './pages/Register';
import EmployeeSidePanel from './components/EmployeeSidePanel';
import AdminSidePanel from './components/AdminSidePanel';


function App() {
  const [user, setUser] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check local storage for auth token
    const token = localStorage.getItem('smartos_token');
    const userData = localStorage.getItem('smartos_user');

    if (token && userData) {
      try {
        const parsed = JSON.parse(userData);
        // Detect stale mock sessions — real UUIDs match this pattern
        const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
        const isMockId = !parsed.id || !uuidPattern.test(parsed.id);

        if (isMockId) {
          // Clear the invalid session and force a fresh login
          localStorage.removeItem('smartos_token');
          localStorage.removeItem('smartos_user');
          console.warn('[SmartOS] Cleared stale mock session. Please log in again.');
        } else {
          setUser(parsed);
        }
      } catch (e) {
        localStorage.removeItem('smartos_token');
        localStorage.removeItem('smartos_user');
      }
    }
    setLoading(false);
  }, []);

  const handleLogin = (userData, portal = 'admin') => {
    localStorage.setItem('smartos_token', userData.token);
    const userWithPortal = { ...userData.user, portal };
    localStorage.setItem('smartos_user', JSON.stringify(userWithPortal));
    setUser(userWithPortal);
  };

  const handleLogout = () => {
    localStorage.removeItem('smartos_token');
    localStorage.removeItem('smartos_user');
    setUser(null);
  };

  if (loading) {
    return (
      <Router>
        <div className="loading-screen">
          <div className="spinner"></div>
          <p>Loading NeuroOps...</p>
        </div>
      </Router>
    );
  }

  return (
    <Router>
      {!user ? (
        <Routes>
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          <Route path="/register" element={<Register onLogin={handleLogin} />} />
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      ) : (
        <>
          <div className="app-container">
            <Sidebar 
              user={user} 
              isOpen={sidebarOpen} 
              onToggle={() => setSidebarOpen(!sidebarOpen)} 
              onLogout={handleLogout} 
              role={user.portal === 'employee' ? 'employee' : (user.role || 'employee')} 
            />

            <main className={`main-content ${sidebarOpen ? 'sidebar-open' : ''}`}>
              <Routes>
                <Route path="/" element={<Dashboard user={user} />} />
                <Route path="/tasks" element={<Tasks user={user} />} />
                <Route path="/tasks/:id" element={<Tasks user={user} />} />
                <Route path="/team" element={<Team user={user} />} />
                <Route path="/analytics" element={<Analytics user={user} />} />
                <Route path="/crm" element={<CRM user={user} />} />
                <Route path="/hr" element={<HR user={user} />} />
                <Route path="/settings" element={<Settings user={user} />} />
                <Route path="/ai" element={<AIChat user={user} />} />
                <Route path="/profile" element={<Profile user={user} />} />
                <Route path="*" element={<Navigate to="/" />} />
              </Routes>
            </main>
            {(user.role === 'employee' || user.role === 'manager') && <EmployeeSidePanel user={user} />}
            {(user.role === 'admin' || user.role === 'super_admin') && <AdminSidePanel user={user} />}
          </div>
        </>
      )}
    </Router>
  );
}

function Sidebar({ user, isOpen, onToggle, onLogout, role }) {
  const location = useLocation();
  const navItems = getNavItems(role);

  const isActive = (path) => location.pathname === path;

  return (
    <aside className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
      <div className="sidebar-header">
        <div className="logo">
          <img src="/logo.png" alt="NeuroOps" style={{ width: '32px', height: '32px', objectFit: 'contain' }} />
          <span>Neuro<span>Ops</span></span>
        </div>
        <button className="sidebar-toggle" onClick={onToggle}>
          {isOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-group">
          {isOpen && <span className="nav-group-label">Core</span>}
          {navItems.filter(i => ['Dashboard', 'Tasks', 'Team', 'Analytics', 'AI Assistant'].includes(i.label)).map((item, idx) => (
            <Link
              key={idx}
              to={item.path}
              className={`nav-item ${isActive(item.path) ? 'active' : ''}`}
              title={item.label}
            >
              <item.icon size={20} />
              {isOpen && <span>{item.label}</span>}
            </Link>
          ))}
        </div>

        {(role === 'admin' || role === 'super_admin') && (
          <div className="nav-group mt-4">
            {isOpen && <span className="nav-group-label">Management</span>}
            {navItems.filter(i => ['CRM', 'Billing', 'Invoices', 'HR'].includes(i.label)).map((item, idx) => (
              <Link
                key={idx}
                to={item.path}
                className={`nav-item ${isActive(item.path) ? 'active' : ''}`}
                title={item.label}
              >
                <item.icon size={20} />
                {isOpen && <span>{item.label}</span>}
              </Link>
            ))}
          </div>
        )}

        <div className="nav-group mt-auto">
          {isOpen && <span className="nav-group-label">Account</span>}
          {navItems.filter(i => ['Settings', 'Profile'].includes(i.label)).map((item, idx) => (
            <Link
              key={idx}
              to={item.path}
              className={`nav-item ${isActive(item.path) ? 'active' : ''}`}
              title={item.label}
            >
              <item.icon size={20} />
              {isOpen && <span>{item.label}</span>}
            </Link>
          ))}
        </div>
      </nav>

      <div className="sidebar-footer">
        {isOpen && (
          <div className="user-info">
            <div className="avatar">{user.name?.charAt(0).toUpperCase()}</div>
            <div className="user-details">
              <span className="user-name">{user.name}</span>
              <span className="user-role">{role}</span>
            </div>
          </div>
        )}
        <button onClick={onLogout} className="logout-btn" title="Logout">
          <LogOut size={20} />
        </button>
      </div>
    </aside>
  );
}

function getNavItems(role) {
  const base = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
    { icon: Briefcase, label: 'Tasks', path: '/tasks' },
    { icon: Users, label: 'Team', path: '/team' },
    { icon: BarChart3, label: 'Analytics', path: '/analytics' },
  ];

  if (role === 'admin' || role === 'super_admin') {
    base.push(
      { icon: Building2, label: 'CRM', path: '/crm' },
      { icon: User, label: 'HR', path: '/hr' }
    );
  }

  base.push(
    { icon: BotIcon, label: 'AI Assistant', path: '/ai' },
    { icon: SettingsIcon, label: 'Settings', path: '/settings' },
    { icon: User, label: 'Profile', path: '/profile' }
  );

  return base;
}

export default App;