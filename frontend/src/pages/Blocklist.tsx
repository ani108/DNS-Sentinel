import React, { useEffect, useState } from 'react';
import { getBlocklist, addToBlocklist, deleteFromBlocklist, getWhitelist, addToWhitelist, deleteFromWhitelist } from '../api/client';
import type { BlocklistEntry, WhitelistEntry } from '../types';
import { Trash2, Plus } from 'lucide-react';

export const Blocklist: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'blocklist' | 'whitelist'>('blocklist');
  const [blocklist, setBlocklist] = useState<BlocklistEntry[]>([]);
  const [whitelist, setWhitelist] = useState<WhitelistEntry[]>([]);
  const [domainsInput, setDomainsInput] = useState('');
  const [reasonInput, setReasonInput] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchLists = async () => {
    try {
      const [bl, wl] = await Promise.all([getBlocklist(), getWhitelist()]);
      setBlocklist(bl);
      setWhitelist(wl);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchLists();
  }, []);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const domains = domainsInput.split(/[\n,]+/).map(d => d.trim()).filter(Boolean);
    try {
      if (activeTab === 'blocklist') {
        await addToBlocklist(domains, reasonInput || 'Manually added');
      } else {
        await addToWhitelist(domains, reasonInput || 'Manually added');
      }
      setDomainsInput('');
      setReasonInput('');
      await fetchLists();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      if (activeTab === 'blocklist') await deleteFromBlocklist(id);
      else await deleteFromWhitelist(id);
      await fetchLists();
    } catch (e) {
      console.error(e);
    }
  };

  const activeData = activeTab === 'blocklist' ? blocklist : whitelist;

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      <h1 className="text-2xl font-bold text-gray-900">Access Control</h1>

      <div className="flex gap-4 border-b border-gray-200">
        <button
          className={`pb-2 px-1 font-medium ${activeTab === 'blocklist' ? 'text-red-600 border-b-2 border-red-600' : 'text-gray-500 hover:text-gray-700'}`}
          onClick={() => setActiveTab('blocklist')}
        >
          Custom Blocklist
        </button>
        <button
          className={`pb-2 px-1 font-medium ${activeTab === 'whitelist' ? 'text-green-600 border-b-2 border-green-600' : 'text-gray-500 hover:text-gray-700'}`}
          onClick={() => setActiveTab('whitelist')}
        >
          Whitelist
        </button>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 mb-6">
        <h3 className="text-lg font-medium mb-4">Add to {activeTab === 'blocklist' ? 'Blocklist' : 'Whitelist'}</h3>
        <form onSubmit={handleAdd} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Domains (comma or newline separated)</label>
            <textarea
              className="w-full border rounded-md p-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              rows={3}
              value={domainsInput}
              onChange={(e) => setDomainsInput(e.target.value)}
              placeholder="example.com, badsite.org"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Reason (Optional)</label>
            <input
              type="text"
              className="w-full border rounded-md p-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              value={reasonInput}
              onChange={(e) => setReasonInput(e.target.value)}
              placeholder="Phishing campaign detected"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !domainsInput.trim()}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            <Plus size={18} /> Add Rules
          </button>
        </form>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-left text-sm whitespace-nowrap">
          <thead className="bg-gray-50 border-b text-gray-600">
            <tr>
              <th className="px-6 py-3 font-medium">Domain</th>
              <th className="px-6 py-3 font-medium">Reason</th>
              <th className="px-6 py-3 font-medium">Added By</th>
              <th className="px-6 py-3 font-medium">Date</th>
              <th className="px-6 py-3 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {activeData.map((entry) => (
              <tr key={entry.id} className="hover:bg-gray-50">
                <td className="px-6 py-3 font-medium text-gray-900">{entry.domain}</td>
                <td className="px-6 py-3 text-gray-500">{entry.reason}</td>
                <td className="px-6 py-3 text-gray-500">{entry.added_by}</td>
                <td className="px-6 py-3 text-gray-500">{new Date(entry.created_at).toLocaleDateString()}</td>
                <td className="px-6 py-3 text-right">
                  <button onClick={() => handleDelete(entry.id)} className="text-red-500 hover:text-red-700">
                    <Trash2 size={18} />
                  </button>
                </td>
              </tr>
            ))}
            {activeData.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-gray-500">No entries found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
