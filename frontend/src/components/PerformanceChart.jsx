import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../api/config';

function PerformanceChart({ companyId }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchChartData();
  }, [companyId]);

  const fetchChartData = async () => {
    if (!companyId || companyId === 'undefined') {
      setLoading(false);
      return;
    }

    try {
      const token = localStorage.getItem('smartos_token');
      const res = await fetch(`${API_BASE_URL}/api/analytics/productivity-trend?company_id=${companyId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const result = await res.json();
      setData(result.trend || []);
      setLoading(false);
    } catch (error) {
      console.error('Chart fetch error:', error);
      setLoading(false);
    }
  };

  if (loading) return <div>Loading chart...</div>;
  if (data.length === 0) return <div className="chart-placeholder">No data available yet</div>;

  const maxValue = Math.max(...data.map(d => Math.max(d.created, d.completed)));

  return (
    <div className="chart-container">
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: '8px', height: '200px' }}>
        {data.map((d, i) => (
          <div key={i} className="flex-1 flex flex-col items-center gap-1">
            <div
              style={{
                height: `${(d.created / maxValue) * 100}%`,
                width: '100%',
                background: 'linear-gradient(to top, #3b82f6, #8b5cf6)',
                borderRadius: '4px 4px 0 0',
                minHeight: '4px'
              }}
              title={`Created: ${d.created}`}
            />
            <div
              style={{
                height: `${(d.completed / maxValue) * 100}%`,
                width: '100%',
                background: '#10b981',
                borderRadius: '4px 4px 0 0',
                minHeight: '4px',
                marginTop: '2px'
              }}
              title={`Completed: ${d.completed}`}
            />
            <span style={{ fontSize: '10px', color: '#6b7280' }}>{d.date.slice(5)}</span>
          </div>
        ))}
      </div>
      <div className="flex justify-center gap-4 mt-3">
        <div className="flex items-center gap-1">
          <div style={{ width: '12px', height: '12px', background: '#3b82f6', borderRadius: '2px' }}></div>
          <span className="text-sm text-gray">Created</span>
        </div>
        <div className="flex items-center gap-1">
          <div style={{ width: '12px', height: '12px', background: '#10b981', borderRadius: '2px' }}></div>
          <span className="text-sm text-gray">Completed</span>
        </div>
      </div>
    </div>
  );
}

export default PerformanceChart;