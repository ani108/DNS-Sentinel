import React, { useEffect, useState } from 'react';
import { DomainTester } from '../components/DomainTester';
import { useTrafficStream } from '../hooks/useTrafficStream';
import { getStatsSummary, getHourlyStats } from '../api/client';
import type { StatsSummary, HourlyStat } from '../types';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ShieldAlert, Activity, Database, AlertCircle } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { queries, isConnected } = useTrafficStream();
  const [stats, setStats] = useState<StatsSummary | null>(null);
  const [chartData, setChartData] = useState<HourlyStat[]>([]);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [summaryRes, hourlyRes] = await Promise.all([
          getStatsSummary(),
          getHourlyStats()
        ]);
        setStats(summaryRes);
        setChartData(hourlyRes);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
      }
    };
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <div className="flex items-center gap-2">
          <span className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></span>
          <span className="text-sm text-gray-600">{isConnected ? 'Live Stream Connected' : 'Stream Disconnected'}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="p-3 bg-blue-100 text-blue-600 rounded-full"><Activity size={24} /></div>
          <div>
            <p className="text-sm text-gray-500 font-medium">Total Queries</p>
            <p className="text-2xl font-bold text-gray-900">{stats?.total_queries.toLocaleString() ?? '-'}</p>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="p-3 bg-red-100 text-red-600 rounded-full"><ShieldAlert size={24} /></div>
          <div>
            <p className="text-sm text-gray-500 font-medium">Threats Blocked</p>
            <p className="text-2xl font-bold text-gray-900">{stats?.blocked_queries.toLocaleString() ?? '-'}</p>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="p-3 bg-purple-100 text-purple-600 rounded-full"><AlertCircle size={24} /></div>
          <div>
            <p className="text-sm text-gray-500 font-medium">Tunneling Detections</p>
            <p className="text-2xl font-bold text-gray-900">{stats?.tunneling_detected.toLocaleString() ?? '-'}</p>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="p-3 bg-green-100 text-green-600 rounded-full"><Database size={24} /></div>
          <div>
            <p className="text-sm text-gray-500 font-medium">Active Threat Feeds</p>
            <p className="text-2xl font-bold text-gray-900">{stats?.active_feeds ?? '-'}</p>
          </div>
        </div>
      </div>

      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 h-80">
        <h3 className="text-lg font-semibold mb-4 text-gray-800">24-hour Activity</h3>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="hour" tickFormatter={(tick) => {
              const parts = String(tick).split('-');
              return parts.length === 4 ? `${parts[3]}:00` : tick;
            }} />
            <YAxis />
            <Tooltip labelFormatter={(label) => {
              const parts = String(label).split('-');
              return parts.length === 4 ? `${parts[0]}-${parts[1]}-${parts[2]} ${parts[3]}:00` : label;
            }} />
            <Area type="monotone" dataKey="allowed" stackId="1" stroke="#10b981" fill="#10b981" fillOpacity={0.2} name="Allowed" />
            <Area type="monotone" dataKey="blocked" stackId="2" stroke="#ef4444" fill="#ef4444" fillOpacity={0.2} name="Blocked" />
            <Area type="monotone" dataKey="tunneling" stackId="3" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.2} name="Tunneling" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <DomainTester />
        </div>
        <div className="lg:col-span-2 bg-white rounded-lg shadow-sm border border-gray-100 flex flex-col">
          <div className="p-4 border-b flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-800">Live Query Feed</h3>
            <span className="text-xs text-gray-500 font-medium uppercase px-2 py-1 bg-gray-100 rounded">Latest 50</span>
          </div>
          <div className="overflow-auto flex-1 h-[400px]">
            <table className="w-full text-left text-sm whitespace-nowrap">
              <thead className="bg-gray-50 sticky top-0 text-gray-600">
                <tr>
                  <th className="px-4 py-3 font-medium">Time</th>
                  <th className="px-4 py-3 font-medium">Domain</th>
                  <th className="px-4 py-3 font-medium">Type</th>
                  <th className="px-4 py-3 font-medium">Client IP</th>
                  <th className="px-4 py-3 font-medium">Verdict</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {queries.map((q) => (
                  <tr key={q.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-2 text-gray-500">{new Date(q.queried_at).toLocaleTimeString()}</td>
                    <td className="px-4 py-2 font-medium text-gray-900 truncate max-w-[200px]" title={q.domain}>{q.domain}</td>
                    <td className="px-4 py-2 text-gray-500">{q.query_type}</td>
                    <td className="px-4 py-2 text-gray-500">{q.client_ip}</td>
                    <td className="px-4 py-2">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full 
                        ${q.verdict === 'ALLOWED' ? 'bg-green-100 text-green-700' : 
                          q.verdict === 'BLOCKED' ? 'bg-red-100 text-red-700' : 
                          'bg-purple-100 text-purple-700'}`}>
                        {q.verdict}
                      </span>
                    </td>
                  </tr>
                ))}
                {queries.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-gray-500">Waiting for queries...</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
