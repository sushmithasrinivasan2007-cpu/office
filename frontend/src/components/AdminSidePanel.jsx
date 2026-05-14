import React from 'react';
import { 
  Users, UserPlus, Search, Circle, 
  Activity, Shield, Star, MoreHorizontal, CheckSquare 
} from 'lucide-react';
import { API_BASE_URL } from '../api/config';

function AdminSidePanel({ user }) {
  const [members, setMembers] = React.useState([]);
  const [tasks, setTasks] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [search, setSearch] = React.useState('');

  React.useEffect(() => {
    fetchData();
  }, [user]);

  const fetchData = async () => {
    setLoading(true);
    await Promise.all([fetchTeam(), fetchTasks()]);
    setLoading(false);
  };

  const fetchTeam = async () => {
    try {
      const token = localStorage.getItem('smartos_token');
      const res = await fetch(`${API_BASE_URL}/api/company/${user.company_id}/team`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      setMembers(data.team || []);
    } catch (error) {
      console.error('Fetch team error:', error);
    }
  };

  const fetchTasks = async () => {
    try {
      const token = localStorage.getItem('smartos_token');
      const res = await fetch(`${API_BASE_URL}/api/tasks/?company_id=${user.company_id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      setTasks(data.tasks || []);
    } catch (error) {
      console.error('Fetch tasks error:', error);
    }
  };

  const filteredMembers = members.filter(m =>
    m.name?.toLowerCase().includes(search.toLowerCase()) ||
    m.email?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <aside className="right-panel">
      {/* Admin Identity */}
      <section className="panel-section">
        <div className="panel-section-title">
          <span>Admin Controls</span>
          <span className="badge badge-error">Root</span>
        </div>
        <div className="card bg-gray-900 text-white border-none p-4" style={{ borderRadius: '16px' }}>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/10 rounded-lg text-primary-400">
              <Shield size={20} />
            </div>
            <div>
              <h4 className="font-bold text-sm">Workspace Admin</h4>
              <p className="text-xs text-gray-400">Company ID: {user.company_id?.substring(0, 8)}...</p>
            </div>
          </div>
        </div>
      </section>

      {/* Team Overview */}
      <section className="panel-section flex-1 overflow-hidden flex flex-col">
        <div className="panel-section-title">
          <span>Team Status</span>
          <span className="badge badge-info">{members.length} Total</span>
        </div>
        
        <div className="relative mb-3">
          <Search size={14} className="absolute-icon" style={{ left: '10px' }} />
          <input 
            type="text" 
            className="form-input text-xs pl-8" 
            placeholder="Search members..." 
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{ padding: '0.4rem 0.4rem 0.4rem 2rem' }}
          />
        </div>

        <div className="flex-1 overflow-y-auto pr-1">
          {loading ? (
            <p className="text-center text-xs text-gray py-4">Loading team...</p>
          ) : filteredMembers.length > 0 ? (
            <div className="space-y-2">
              {filteredMembers.map(member => (
                <div key={member.id} className="flex items-center gap-3 p-2 hover:bg-gray-50 rounded-lg border border-transparent hover:border-gray-100 transition-all cursor-pointer">
                  <div className="relative">
                    <div className="avatar sm" style={{ background: member.role === 'admin' ? 'var(--primary-500)' : 'var(--gray-200)', color: member.role === 'admin' ? 'white' : 'var(--gray-600)' }}>
                      {member.name?.charAt(0).toUpperCase()}
                    </div>
                    <Circle size={10} fill={member.is_active ? '#10b981' : '#94a3b8'} stroke="none" className="absolute" style={{ bottom: '-1px', right: '-1px', border: '2px solid white', borderRadius: '50%' }} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h5 className="text-xs font-bold text-gray-900 truncate">{member.name}</h5>
                    <div className="flex items-center gap-1">
                      <p className="text-[10px] text-gray-500 capitalize">{member.role}</p>
                      <Circle size={4} fill="currentColor" className="text-gray-300" />
                      <span className="text-[10px] text-gray-400">
                        {tasks.filter(t => t.assigned_to === member.id).length} tasks
                      </span>
                    </div>
                    
                    {/* Tasks List */}
                    <div className="mt-1 space-y-0.5">
                      {tasks
                        .filter(t => t.assigned_to === member.id && t.status !== 'completed')
                        .slice(0, 2)
                        .map(task => (
                          <div key={task.id} className="flex items-center gap-1 text-[9px] text-primary-600 bg-primary-50 px-1.5 py-0.5 rounded truncate">
                            <CheckSquare size={8} />
                            <span className="truncate">{task.title}</span>
                          </div>
                        ))
                      }
                      {tasks.filter(t => t.assigned_to === member.id && t.status !== 'completed').length > 2 && (
                        <p className="text-[8px] text-gray-400 pl-1">
                          +{tasks.filter(t => t.assigned_to === member.id && t.status !== 'completed').length - 2} more...
                        </p>
                      )}
                    </div>
                  </div>
                  {member.role === 'admin' && <Star size={12} className="text-warning-500" />}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-xs text-gray py-4">No members found</p>
          )}
        </div>
      </section>

      {/* System Health */}
      <section className="panel-section mt-4">
        <div className="panel-section-title">
          <span>System Health</span>
        </div>
        <div className="space-y-3">
          <div className="flex justify-between items-center text-xs">
            <div className="flex items-center gap-2 text-gray-600">
              <Activity size={14} />
              <span>API Status</span>
            </div>
            <span className="text-success-500 font-bold">Optimal</span>
          </div>
          <div className="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden">
            <div className="h-full bg-success-500 rounded-full" style={{ width: '98%' }}></div>
          </div>
        </div>
      </section>

      {/* Quick Admin Actions */}
      <section className="panel-section mt-4">
        <button className="btn btn-primary btn-sm w-full gap-2">
          <UserPlus size={14} />
          Bulk Invite
        </button>
      </section>
    </aside>
  );
}

export default AdminSidePanel;
