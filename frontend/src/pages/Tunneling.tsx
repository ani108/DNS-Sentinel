import React, { useEffect, useState } from 'react';
import { getTunnelIncidents, updateTunnelIncident } from '../api/client';
import type { TunnelIncident } from '../types';
import { ShieldAlert, CheckCircle, XCircle } from 'lucide-react';

export const Tunneling: React.FC = () => {
  const [incidents, setIncidents] = useState<TunnelIncident[]>([]);
  const [, setLoading] = useState(true);

  const fetchIncidents = async () => {
    setLoading(true);
    try {
      const data = await getTunnelIncidents();
      setIncidents(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, []);

  const handleStatusChange = async (id: number, status: string) => {
    try {
      await updateTunnelIncident(id, status);
      await fetchIncidents();
    } catch (e) {
      console.error(e);
    }
  };

  const activeIncidents = incidents.filter(i => i.status.toLowerCase() === 'active');
  const pastIncidents = incidents.filter(i => i.status.toLowerCase() !== 'active');

  const SeverityBadge = ({ sev }: { sev: string }) => {
    const colors = {
      HIGH: 'bg-red-100 text-red-800 border-red-200',
      MEDIUM: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      LOW: 'bg-blue-100 text-blue-800 border-blue-200',
    } as any;
    const key = sev ? sev.toUpperCase() : 'MEDIUM';
    return <span className={`px-2 py-1 rounded text-xs font-semibold border ${colors[key]}`}>{key}</span>;
  };

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      <div className="flex items-center gap-3">
        <ShieldAlert size={28} className="text-purple-600" />
        <h1 className="text-2xl font-bold text-gray-900">DNS Tunneling Monitor</h1>
      </div>

      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-800">Active Incidents</h2>
        {activeIncidents.length === 0 ? (
          <p className="text-gray-500 bg-white p-6 rounded-lg border border-gray-100 text-center">No active tunneling incidents detected.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {activeIncidents.map(inc => (
              <div key={inc.id} className="bg-white p-5 rounded-lg shadow-sm border-l-4 border-l-red-500 border-y border-r border-gray-100">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="font-bold text-gray-900 text-lg">{inc.base_domain}</h3>
                    <p className="text-sm text-gray-500">Client IP: {inc.client_ip}</p>
                  </div>
                  <SeverityBadge sev={inc.severity} />
                </div>
                
                <div className="grid grid-cols-2 gap-4 mb-4 text-sm bg-gray-50 p-3 rounded">
                  <div>
                    <p className="text-gray-500">Unique Subdomains</p>
                    <p className="font-semibold text-gray-800">{inc.unique_subdomains}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Avg Entropy</p>
                    <p className="font-semibold text-gray-800">{inc.avg_entropy.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Avg Length</p>
                    <p className="font-semibold text-gray-800">{inc.avg_subdomain_length.toFixed(1)} chars</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Detected</p>
                    <p className="font-semibold text-gray-800">{new Date(inc.detected_at).toLocaleTimeString()}</p>
                  </div>
                </div>

                <div className="flex gap-2">
                  <button onClick={() => handleStatusChange(inc.id, 'resolved')} className="flex items-center gap-1 px-3 py-1.5 bg-green-50 text-green-700 hover:bg-green-100 rounded text-sm font-medium transition">
                    <CheckCircle size={16} /> Mark Resolved
                  </button>
                  <button onClick={() => handleStatusChange(inc.id, 'false_positive')} className="flex items-center gap-1 px-3 py-1.5 bg-gray-100 text-gray-700 hover:bg-gray-200 rounded text-sm font-medium transition">
                    <XCircle size={16} /> False Positive
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="space-y-4 pt-6 border-t border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800">Incident History</h2>
        <div className="bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-gray-50 border-b text-gray-600">
              <tr>
                <th className="px-6 py-3 font-medium">Base Domain</th>
                <th className="px-6 py-3 font-medium">Severity</th>
                <th className="px-6 py-3 font-medium">Detected</th>
                <th className="px-6 py-3 font-medium">Status</th>
                <th className="px-6 py-3 font-medium">Resolved At</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {pastIncidents.map((inc) => (
                <tr key={inc.id} className="hover:bg-gray-50">
                  <td className="px-6 py-3 font-medium text-gray-900">{inc.base_domain}</td>
                  <td className="px-6 py-3"><SeverityBadge sev={inc.severity} /></td>
                  <td className="px-6 py-3 text-gray-500">{new Date(inc.detected_at).toLocaleString()}</td>
                  <td className="px-6 py-3">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${inc.status.toLowerCase() === 'resolved' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                      {inc.status.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-3 text-gray-500">{inc.resolved_at ? new Date(inc.resolved_at).toLocaleString() : '-'}</td>
                </tr>
              ))}
              {pastIncidents.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-500">No past incidents.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
