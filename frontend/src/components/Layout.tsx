import { Outlet, NavLink } from 'react-router-dom';
import { Shield, BarChart2, List, Activity, Settings as SettingsIcon } from 'lucide-react';

export default function Layout() {
  const navItems = [
    { to: '/', icon: Shield, label: 'Dashboard' },
    { to: '/analytics', icon: BarChart2, label: 'Analytics' },
    { to: '/blocklist', icon: List, label: 'Rules & Lists' },
    { to: '/tunneling', icon: Activity, label: 'Tunnel Monitor' },
    { to: '/settings', icon: SettingsIcon, label: 'Settings' },
  ];

  return (
    <div className="flex h-screen bg-gray-50 text-gray-900 font-sans">
      <aside className="w-64 bg-slate-900 text-slate-100 flex flex-col">
        <div className="p-4 flex items-center gap-3 border-b border-slate-800">
          <Shield className="w-8 h-8 text-blue-400" />
          <h1 className="text-xl font-bold tracking-tight">DNS Sentinel</h1>
        </div>
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${
                  isActive ? 'bg-blue-600 text-white' : 'hover:bg-slate-800 hover:text-white'
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-slate-800">
          <button 
            onClick={() => {
              localStorage.removeItem('admin_token');
              window.location.reload();
            }}
            className="flex items-center gap-3 px-3 py-2 w-full rounded-md transition-colors hover:bg-slate-800 hover:text-white text-left"
          >
            <Shield className="w-5 h-5 opacity-50" />
            <span>Logout</span>
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-y-auto p-8">
        <Outlet />
      </main>
    </div>
  );
}
