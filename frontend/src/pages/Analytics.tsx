import React, { useEffect, useState } from 'react';
import { getTopBlocked, getRecentQueries } from '../api/client';
import type { TopBlockedDomain, DNSQuery } from '../types';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export const Analytics: React.FC = () => {
  const [topBlocked, setTopBlocked] = useState<TopBlockedDomain[]>([]);
  const [queries, setQueries] = useState<DNSQuery[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterVerdict, setFilterVerdict] = useState<string>('ALL');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const top = await getTopBlocked(10);
        setTopBlocked(top);
        const q = await getRecentQueries({ limit: 100 });
        setQueries(q);
      } catch (e) {
        console.error('Failed to fetch analytics', e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const COLORS = ['#10b981', '#ef4444', '#f59e0b', '#8b5cf6', '#3b82f6'];
  const pieData = [
    { name: 'Allowed', value: queries.filter(q => q.verdict === 'ALLOWED').length },
    { name: 'Threat Intel', value: queries.filter(q => q.verdict !== 'ALLOWED' && q.block_reason === 'threat_intel').length },
    { name: 'ML Blocked', value: queries.filter(q => q.verdict !== 'ALLOWED' && q.block_reason === 'ml_detected').length },
    { name: 'Tunneling', value: queries.filter(q => q.verdict !== 'ALLOWED' && q.block_reason === 'tunneling').length },
    { name: 'Manual Block', value: queries.filter(q => q.verdict !== 'ALLOWED' && q.block_reason === 'manual_block').length },
  ].filter(d => d.value > 0);

  const filteredQueries = filterVerdict === 'ALL' ? queries : queries.filter(q => q.verdict === filterVerdict);

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Analytics & Logs</h1>
        <a 
          href="/api/v1/queries/export"
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm font-medium transition-colors shadow-sm"
          download
        >
          Export CSV Report
        </a>
      </div>
      
      {loading ? (
        <div className="text-gray-500">Loading data...</div>
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 h-80">
              <h3 className="text-lg font-semibold mb-4 text-gray-800">Top Blocked Domains</h3>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={topBlocked} layout="vertical" margin={{ top: 0, right: 30, left: 40, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
                  <XAxis type="number" />
                  <YAxis type="category" dataKey="domain" width={150} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#ef4444" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 h-80">
              <h3 className="text-lg font-semibold mb-4 text-gray-800">Query Distribution (Last 100)</h3>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={5} dataKey="value">
                    {pieData.map((_entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-100 flex flex-col">
            <div className="p-4 border-b flex justify-between items-center bg-gray-50">
              <h3 className="text-lg font-semibold text-gray-800">Historic DNS Query Logs</h3>
              <select 
                className="border rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={filterVerdict}
                onChange={(e) => setFilterVerdict(e.target.value)}
              >
                <option value="ALL">All Verdicts</option>
                <option value="ALLOWED">Allowed</option>
                <option value="BLOCKED">Blocked</option>
                <option value="SINKHOLED">Sinkholed</option>
              </select>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm whitespace-nowrap">
                <thead className="bg-white border-b text-gray-600">
                  <tr>
                    <th className="px-6 py-3 font-medium">Timestamp</th>
                    <th className="px-6 py-3 font-medium">Domain</th>
                    <th className="px-6 py-3 font-medium">Type</th>
                    <th className="px-6 py-3 font-medium">Client IP</th>
                    <th className="px-6 py-3 font-medium">Verdict</th>
                    <th className="px-6 py-3 font-medium">Reason</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {filteredQueries.map((q) => (
                    <tr key={q.id} className="hover:bg-gray-50">
                      <td className="px-6 py-3 text-gray-500">{new Date(q.queried_at).toLocaleString()}</td>
                      <td className="px-6 py-3 font-medium text-gray-900">{q.domain}</td>
                      <td className="px-6 py-3 text-gray-500">{q.query_type}</td>
                      <td className="px-6 py-3 text-gray-500">{q.client_ip}</td>
                      <td className="px-6 py-3">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full 
                          ${q.verdict === 'ALLOWED' ? 'bg-green-100 text-green-700' : 
                            q.verdict === 'BLOCKED' ? 'bg-red-100 text-red-700' : 
                            'bg-purple-100 text-purple-700'}`}>
                          {q.verdict}
                        </span>
                      </td>
                      <td className="px-6 py-3 text-gray-500 text-xs truncate max-w-xs" title={q.block_reason}>{q.block_reason || '-'}</td>
                    </tr>
                  ))}
                  {filteredQueries.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-6 py-8 text-center text-gray-500">No queries found.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
