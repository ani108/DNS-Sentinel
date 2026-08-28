import React, { useState } from 'react';
import { analyzeDomain } from '../api/client';
import type { DomainAnalyzeResult } from '../types';
import { Search, ShieldAlert, ShieldCheck, AlertTriangle } from 'lucide-react';

export const DomainTester: React.FC = () => {
  const [domain, setDomain] = useState('');
  const [result, setResult] = useState<DomainAnalyzeResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [showFeatures, setShowFeatures] = useState(false);

  const testSamples = [
    'google.com',
    'paypal-security-update.xyz',
    'x89qzvb103.top',
    'exfil.data.tunnel-demo.com'
  ];

  const handleAnalyze = async (d: string) => {
    setLoading(true);
    try {
      const res = await analyzeDomain(d);
      setResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
      <h3 className="text-lg font-semibold mb-4 text-gray-800">Domain Tester</h3>
      
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          className="flex-1 px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter domain to analyze..."
          value={domain}
          onChange={(e) => setDomain(e.target.value)}
        />
        <button
          onClick={() => handleAnalyze(domain)}
          disabled={loading || !domain}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
        >
          <Search size={18} /> Analyze with AI
        </button>
      </div>

      <div className="flex flex-wrap gap-2 mb-6">
        {testSamples.map(sample => (
          <button
            key={sample}
            onClick={() => { setDomain(sample); handleAnalyze(sample); }}
            className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-full"
          >
            {sample}
          </button>
        ))}
      </div>

      {result && (
        <div className="mt-6 border-t pt-4">
          <div className="flex justify-between items-center mb-4">
            <span className="font-medium text-gray-700">{result.domain}</span>
            {result.verdict === 'CLEAN' && <span className="flex items-center gap-1 text-green-600 bg-green-50 px-2 py-1 rounded text-sm"><ShieldCheck size={16} /> Clean</span>}
            {result.verdict === 'BLOCKED' && <span className="flex items-center gap-1 text-red-600 bg-red-50 px-2 py-1 rounded text-sm"><ShieldAlert size={16} /> Blocked</span>}
            {result.verdict === 'SUSPICIOUS' && <span className="flex items-center gap-1 text-yellow-600 bg-yellow-50 px-2 py-1 rounded text-sm"><AlertTriangle size={16} /> Suspicious</span>}
          </div>

          <div className="mb-4">
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">ML Risk Score</span>
              <span className="font-medium">{Math.round(result.ml_score * 100)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${result.ml_score > 0.7 ? 'bg-red-500' : result.ml_score > 0.4 ? 'bg-yellow-500' : 'bg-green-500'}`}
                style={{ width: `${Math.round(result.ml_score * 100)}%` }}
              ></div>
            </div>
          </div>

          {result.threat_intel_match && (
            <div className="mb-4 p-3 bg-red-50 text-red-700 text-sm rounded-md border border-red-100 flex items-start gap-2">
              <ShieldAlert size={18} className="mt-0.5" />
              <div>
                <strong>Threat Intel Match:</strong> {result.threat_intel_source} ({result.threat_category})
              </div>
            </div>
          )}

          <p className="text-sm text-gray-600 mb-4">{result.explanation}</p>

          <div>
            <button
              onClick={() => setShowFeatures(!showFeatures)}
              className="text-sm text-blue-600 hover:underline focus:outline-none"
            >
              {showFeatures ? 'Hide Feature Breakdown' : 'Show Feature Breakdown'}
            </button>
            {showFeatures && (
              <div className="mt-2 text-xs border rounded-md overflow-hidden">
                <table className="w-full text-left bg-white">
                  <tbody className="divide-y divide-gray-100">
                    {Object.entries(result.features).map(([key, val]) => (
                      <tr key={key}>
                        <td className="px-3 py-2 font-medium text-gray-600 bg-gray-50 w-1/2">{key}</td>
                        <td className="px-3 py-2 text-gray-800">{String(val)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
