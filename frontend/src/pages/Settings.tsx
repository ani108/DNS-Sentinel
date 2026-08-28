import React, { useEffect, useState } from 'react';
import { getSettings, updateSettings, changePassword } from '../api/client';
import { Save, Server, Shield, Brain, Lock } from 'lucide-react';

export const Settings: React.FC = () => {
  const [settings, setSettings] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState('');
  
  const [passwordData, setPasswordData] = useState({ current: '', new: '' });
  const [changingPwd, setChangingPwd] = useState(false);

  const handlePasswordChange = async () => {
    setChangingPwd(true);
    try {
      await changePassword({ current_password: passwordData.current, new_password: passwordData.new });
      setToast('Password updated successfully!');
      setPasswordData({ current: '', new: '' });
      setTimeout(() => setToast(''), 3000);
    } catch (e: any) {
      setToast('Failed to update password. Check current password.');
      setTimeout(() => setToast(''), 3000);
    } finally {
      setChangingPwd(false);
    }
  };

  useEffect(() => {
    const fetchSet = async () => {
      try {
        const res = await getSettings();
        setSettings(res);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchSet();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateSettings(settings);
      setToast('Settings saved successfully!');
      setTimeout(() => setToast(''), 3000);
    } catch (e) {
      console.error(e);
      setToast('Error saving settings');
      setTimeout(() => setToast(''), 3000);
    } finally {
      setSaving(false);
    }
  };

  const updateField = (field: string, value: any) => {
    setSettings((prev: any) => ({
      ...prev,
      [field]: value
    }));
  };

  if (loading || !settings) return <div className="p-6">Loading settings...</div>;

  return (
    <div className="p-6 max-w-4xl space-y-6 bg-gray-50 min-h-screen relative">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">System Settings</h1>
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          <Save size={18} /> {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      {toast && (
        <div className="absolute top-4 right-4 bg-gray-900 text-white px-4 py-2 rounded-md shadow-lg transition-opacity">
          {toast}
        </div>
      )}

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
        <div className="flex items-center gap-2 mb-4 text-lg font-semibold text-gray-800">
          <Server size={20} className="text-blue-500" />
          <h3>Upstream DNS Resolver</h3>
        </div>
        <div className="space-y-4 max-w-md">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Primary Resolver</label>
            <select
              className="w-full border rounded-md p-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              value={settings.upstream_dns}
              onChange={(e) => updateField('upstream_dns', e.target.value)}
            >
              <option value="1.1.1.1">Cloudflare (1.1.1.1)</option>
              <option value="8.8.8.8">Google (8.8.8.8)</option>
              <option value="9.9.9.9">Quad9 (9.9.9.9)</option>
            </select>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
        <div className="flex items-center gap-2 mb-4 text-lg font-semibold text-gray-800">
          <Brain size={20} className="text-purple-500" />
          <h3>Machine Learning Detection</h3>
        </div>
        <div className="max-w-md">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Detection Sensitivity (Threshold: {settings.ml_threshold})
          </label>
          <input
            type="range"
            min="0.1"
            max="0.9"
            step="0.05"
            className="w-full"
            value={settings.ml_threshold}
            onChange={(e) => updateField('ml_threshold', parseFloat(e.target.value))}
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>High Precision (Fewer False Positives)</span>
            <span>High Recall (Catch More Threats)</span>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
        <div className="flex items-center gap-2 mb-4 text-lg font-semibold text-gray-800">
          <Shield size={20} className="text-red-500" />
          <h3>Threat Intelligence Feeds</h3>
        </div>
        <div className="space-y-4 max-w-md">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Sync Interval (Minutes)</label>
            <input
              type="number"
              min="10"
              max="1440"
              className="w-full border rounded-md p-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              value={settings.feed_sync_interval_minutes}
              onChange={(e) => updateField('feed_sync_interval_minutes', parseInt(e.target.value))}
            />
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
        <div className="flex items-center gap-2 mb-4 text-lg font-semibold text-gray-800">
          <Lock size={20} className="text-gray-600" />
          <h3>Admin Password</h3>
        </div>
        <div className="space-y-4 max-w-md">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Current Password</label>
            <input
              type="password"
              className="w-full border rounded-md p-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              value={passwordData.current}
              onChange={(e) => setPasswordData(prev => ({ ...prev, current: e.target.value }))}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">New Password</label>
            <input
              type="password"
              className="w-full border rounded-md p-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              value={passwordData.new}
              onChange={(e) => setPasswordData(prev => ({ ...prev, new: e.target.value }))}
            />
          </div>
          <div>
            <button
              onClick={handlePasswordChange}
              disabled={changingPwd || !passwordData.current || !passwordData.new}
              className="px-4 py-2 bg-gray-800 text-white rounded-md hover:bg-gray-900 disabled:opacity-50"
            >
              {changingPwd ? 'Updating...' : 'Change Password'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
