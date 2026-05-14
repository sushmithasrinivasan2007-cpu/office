import React from 'react';
import { Zap, Bot, TrendingUp, CheckCircle, Clock, AlertTriangle } from 'lucide-react';

function AISummary({ tasks, insight }) {
  if (!insight || (!tasks && !insight)) return null;

  return (
    <div className="ai-insight mb-4">
      <div className="ai-insight-header">
        <Bot size={20} />
        <h3>AI Insights</h3>
      </div>
      <div className="ai-insight-content">
        {insight.summary ? (
          <p>{insight.summary}</p>
        ) : (
          <>
            <p><strong>Focus areas:</strong> {insight.focus_areas?.map(f => f.type).join(', ') || 'General productivity'}</p>
            <p><strong>Estimated completion:</strong> {insight.estimated_completion || 'Unknown'}</p>

            {insight.risk_alerts && insight.risk_alerts.length > 0 && (
              <div className="mt-2">
                <p><strong>⚠️ At Risk:</strong></p>
                <ul style={{ paddingLeft: '1.5rem' }}>
                  {insight.risk_alerts.map((task, i) => (
                    <li key={i}>{task.title}</li>
                  ))}
                </ul>
                <p className="mt-2 text-sm opacity-75">
                  Consider reassigning or extending deadlines for these tasks.
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default AISummary;