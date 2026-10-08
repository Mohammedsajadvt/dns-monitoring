import React from 'react';
import { useSelector } from 'react-redux';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function AnalyticsTab() {
  const { stats, isLoading } = useSelector((state) => state.analytics);

  const topDomains = stats.top_domains || [];
  const maxCount = topDomains.length > 0 ? topDomains[0].count : 1;

  // Timeline Chart Configuration
  const timelineLabels = stats.query_timeline?.map((t) => t.hour) || [];
  const timelineTotals = stats.query_timeline?.map((t) => t.total) || [];
  const timelineThreats = stats.query_timeline?.map((t) => t.threats) || [];

  const lineChartData = {
    labels: timelineLabels.length > 0 ? timelineLabels : ['00:00', '06:00', '12:00', '18:00', '23:00'],
    datasets: [
      {
        label: 'Total Queries',
        data: timelineTotals.length > 0 ? timelineTotals : [12, 45, 80, 120, 95],
        borderColor: '#06b6d4',
        backgroundColor: 'rgba(6, 182, 212, 0.12)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Threats Blocked',
        data: timelineThreats.length > 0 ? timelineThreats : [0, 1, 0, 2, 1],
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.2)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const lineChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', weight: '600' } },
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(255,255,255,0.05)' },
        ticks: { color: '#64748b' },
      },
      y: {
        grid: { color: 'rgba(255,255,255,0.05)' },
        ticks: { color: '#64748b' },
        beginAtZero: true,
      },
    },
  };

  // Category Doughnut Chart Configuration
  const categoryLabels = stats.category_distribution?.map((c) => c.category) || [];
  const categoryCounts = stats.category_distribution?.map((c) => c.count) || [];

  const doughnutData = {
    labels: categoryLabels.length > 0 ? categoryLabels : ['Developer', 'Streaming', 'Social', 'Security', 'Cloud'],
    datasets: [
      {
        data: categoryCounts.length > 0 ? categoryCounts : [45, 30, 25, 10, 15],
        backgroundColor: [
          '#06b6d4',
          '#3b82f6',
          '#a855f7',
          '#10b981',
          '#f59e0b',
          '#ef4444',
          '#64748b',
        ],
        borderWidth: 0,
      },
    ],
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
        labels: {
          color: '#94a3b8',
          font: { family: 'Plus Jakarta Sans', size: 11, weight: '600' },
        },
      },
    },
  };

  return (
    <div className="tab-pane active" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div className="analytics-grid">
        {/* Timeline Chart */}
        <div className="chart-card">
          <h3>24-Hour DNS Traffic & Threat Beacon Timeline</h3>
          <div className="chart-container">
            <Line data={lineChartData} options={lineChartOptions} />
          </div>
        </div>

        {/* Category Breakdown */}
        <div className="chart-card">
          <h3>Traffic Volume by Category</h3>
          <div className="chart-container">
            <Doughnut data={doughnutData} options={doughnutOptions} />
          </div>
        </div>
      </div>

      {/* Top Domains Leaderboard */}
      <div className="chart-card">
        <h3>Top Queried Domains & Destinations</h3>
        {topDomains.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            No domain analytics accumulated for this timeframe.
          </p>
        ) : (
          <div className="top-domains-list">
            {topDomains.map((d) => {
              const pct = Math.round((d.count / maxCount) * 100);
              return (
                <div key={d.domain} className="top-domain-row">
                  <span className="top-domain-name" title={d.domain}>
                    {d.domain}
                  </span>
                  <div className="progress-bar-wrap">
                    <div
                      className="progress-bar-fill"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <span className="tag-category">{d.category || 'General'}</span>
                  <span className="top-domain-count">
                    {d.count.toLocaleString()}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
