import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import { Activity, Network, ShieldAlert, Users, Search, BarChart3, LayoutDashboard, UserX, Loader2, AlertTriangle, TrendingUp, Shield } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, Cell, PieChart, Pie, Legend, ScatterChart, Scatter, ZAxis } from 'recharts';
import ForceGraph2D from 'react-force-graph-2d';
import {
  getDashboardSummary, getUserBehavior, getGraphThreats, getUserExplanation,
  getUsers, searchUsers, getAnalyticsOverview, getAnalyticsTimeline,
  getUserActivityGraph
} from './api';

// ─── Loading Spinner ─────────────────────────────
const LoadingSpinner = ({ message = 'Loading...' }) => (
  <div className="flex flex-col items-center justify-center h-64 text-slate-400 gap-3">
    <Loader2 className="animate-spin" size={32} />
    <span>{message}</span>
  </div>
);

// ─── Risk Helpers ────────────────────────────────
const getRiskLevel = (error) => {
  if (error > 5.28) return { label: 'CRITICAL', color: 'red' };
  if (error > 2.14) return { label: 'HIGH', color: 'orange' };
  if (error > 1.55) return { label: 'MEDIUM', color: 'yellow' };
  return { label: 'LOW', color: 'green' };
};

const RiskBadge = ({ error }) => {
  const risk = getRiskLevel(error);
  const colorMap = {
    red: 'bg-red-500/20 text-red-400 border-red-500/30',
    orange: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    yellow: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    green: 'bg-green-500/20 text-green-400 border-green-500/30',
  };
  return (
    <span className={`px-3 py-1 ${colorMap[risk.color]} rounded-full text-xs border`}>
      {risk.label}
    </span>
  );
};

// ─── Sidebar ─────────────────────────────────────
const SidebarItem = ({ to, icon: Icon, label, isActive }) => (
  <Link
    to={to}
    className={`flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-all duration-200 ${isActive
      ? 'bg-primary-500/10 text-primary-400 border border-primary-500/20'
      : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
      }`}
  >
    <Icon size={20} />
    <span className="font-medium">{label}</span>
  </Link>
);

const Sidebar = () => {
  const location = useLocation();
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    getDashboardSummary().then(setSummary).catch(() => { });
  }, []);

  const threatCount = summary?.confirmed_threats || 0;

  return (
    <aside className="w-64 glass-panel border-r border-y-0 border-l-0 rounded-none h-screen fixed left-0 top-0 flex flex-col pt-6 z-50">
      <div className="px-6 mb-8 flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-tr from-primary-500 to-accent-500 flex items-center justify-center shadow-lg">
          <ShieldAlert size={24} className="text-white" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Dual<span className="text-primary-400">Scope</span></h1>
          <p className="text-xs text-slate-400">Insider Threat Platform</p>
        </div>
      </div>

      <nav className="flex-1 px-4">
        <div className="mb-4">
          <p className="px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Overview</p>
          <SidebarItem to="/" icon={LayoutDashboard} label="Dashboard Hub" isActive={location.pathname === '/'} />
        </div>

        <div className="mb-4">
          <p className="px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Core Analysis (Dual Mode)</p>
          <SidebarItem to="/digital-twin" icon={Activity} label="Digital Twin" isActive={location.pathname === '/digital-twin'} />
          <SidebarItem to="/graph-analysis" icon={Network} label="Graph Analysis" isActive={location.pathname === '/graph-analysis'} />
        </div>

        <div className="mb-4">
          <p className="px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Investigations</p>
          <SidebarItem to="/insiders" icon={UserX} label="Insiders / Threats" isActive={location.pathname === '/insiders'} />
          <SidebarItem to="/search-user" icon={Search} label="Search User" isActive={location.pathname === '/search-user'} />
          <SidebarItem to="/analytics" icon={BarChart3} label="Analytics" isActive={location.pathname === '/analytics'} />
        </div>

        <div className="mb-4">
          <p className="px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Visualizations</p>
          <SidebarItem to="/visualizations" icon={BarChart3} label="Graphs & Charts" isActive={location.pathname === '/visualizations'} />
        </div>
      </nav>

      <div className="p-4 border-t border-white/5">
        <div className={`flex items-center gap-3 px-4 py-3 rounded-lg bg-dark-700/50 border ${threatCount > 0 ? 'border-red-500/20 glow-red' : 'border-white/10'}`}>
          <div className={`w-2 h-2 rounded-full ${threatCount > 0 ? 'bg-red-500 animate-pulse' : 'bg-green-500'}`}></div>
          <div>
            <p className={`text-sm font-medium ${threatCount > 0 ? 'text-red-400' : 'text-green-400'}`}>
              {threatCount} Active Threat{threatCount !== 1 ? 's' : ''}
            </p>
            <p className="text-xs text-slate-400">
              {threatCount > 0 ? 'Require Analyst Review' : 'System Secure'}
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
};


// ─── Dashboard Hub ───────────────────────────────
const DashboardHub = () => {
  const [summary, setSummary] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getDashboardSummary(), getAnalyticsTimeline()])
      .then(([s, t]) => {
        setSummary(s);
        setTimeline(t.map(item => ({
          label: `${item.year}-W${item.week}`,
          count: item.count,
          avg_error: item.avg_error
        })));
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner message="Loading dashboard..." />;

  return (
    <div className="p-8">
      <header className="mb-8">
        <h2 className="text-3xl font-bold text-white mb-2">Security Dashboard</h2>
        <p className="text-slate-400">High-level overview of system health and active threats — powered by real CERT r4.2 dataset.</p>
      </header>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="glass-card p-6 border-l-4 border-l-blue-500">
          <div className="flex items-center gap-2 mb-2"><Users size={16} className="text-blue-400" /><h3 className="text-slate-400 text-sm font-medium">Monitored Users</h3></div>
          <p className="text-4xl font-bold text-white">{summary?.total_users?.toLocaleString()}</p>
        </div>
        <div className="glass-card p-6 border-l-4 border-l-purple-500">
          <div className="flex items-center gap-2 mb-2"><Activity size={16} className="text-purple-400" /><h3 className="text-slate-400 text-sm font-medium">Total Events</h3></div>
          <p className="text-4xl font-bold text-white">{summary?.total_events?.toLocaleString()}</p>
        </div>
        <div className="glass-card p-6 border-l-4 border-l-orange-500">
          <div className="flex items-center gap-2 mb-2"><AlertTriangle size={16} className="text-orange-400" /><h3 className="text-slate-400 text-sm font-medium">Suspicious Users</h3></div>
          <p className="text-4xl font-bold text-orange-400">{summary?.suspicious_users}</p>
        </div>
        <div className="glass-card p-6 border-l-4 border-l-red-500 glow-red">
          <div className="flex items-center gap-2 mb-2"><ShieldAlert size={16} className="text-red-400" /><h3 className="text-slate-400 text-sm font-medium">Confirmed Threats</h3></div>
          <p className="text-4xl font-bold text-red-400">{summary?.confirmed_threats}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="glass-card p-6 border-l-4 border-l-cyan-500">
          <h3 className="text-slate-400 text-sm font-medium">Anomalous Weeks Detected</h3>
          <p className="text-3xl font-bold text-white mt-2">{summary?.total_anomalous_weeks}</p>
        </div>
        <div className="glass-card p-6 col-span-2">
          <h3 className="text-slate-400 text-sm font-medium mb-1">Threat User IDs</h3>
          <div className="flex flex-wrap gap-2 mt-2">
            {summary?.threat_user_ids?.map(uid => (
              <Link key={uid} to={`/digital-twin?user=${uid}`}>
                <span className="px-3 py-1 bg-red-500/20 text-red-400 rounded-full text-xs border border-red-500/30 hover:bg-red-500/30 transition-colors cursor-pointer">
                  {uid}
                </span>
              </Link>
            ))}
          </div>
        </div>
      </div>

      <div className="glass-card p-6 h-96 flex flex-col">
        <h3 className="text-white font-semibold mb-4">Weekly Anomaly Trend</h3>
        <div className="flex-1 w-full">
          {timeline.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={timeline}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                <XAxis dataKey="label" stroke="#ffffff50" tick={{ fontSize: 10 }} interval={Math.floor(timeline.length / 15)} />
                <YAxis stroke="#ffffff50" />
                <RechartsTooltip contentStyle={{ backgroundColor: '#13131a', borderColor: '#ffffff20', borderRadius: '8px' }} />
                <Bar dataKey="count" name="Anomalies" radius={[4, 4, 0, 0]}>
                  {timeline.map((entry, index) => (
                    <Cell key={index} fill={entry.count > 5 ? '#ef4444' : entry.count > 2 ? '#f97316' : '#3b82f6'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-full text-slate-500">No timeline data available</div>
          )}
        </div>
      </div>
    </div>
  );
};


// ─── Digital Twin Mode ───────────────────────────
const DigitalTwinMode = () => {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const initialUser = params.get('user') || '';

  const [userId, setUserId] = useState(initialUser);
  const [inputValue, setInputValue] = useState(initialUser);
  const [weeklyData, setWeeklyData] = useState([]);
  const [shapData, setShapData] = useState([]);
  const [explainData, setExplainData] = useState(null);
  const [psychometric, setPsychometric] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchUserData = useCallback(async (uid) => {
    if (!uid) return;
    setLoading(true);
    setError(null);
    try {
      const [behavior, explanation] = await Promise.all([
        getUserBehavior(uid),
        getUserExplanation(uid)
      ]);

      if (!behavior.features || behavior.features.length === 0) {
        setError(`No data found for user "${uid}"`);
        setWeeklyData([]);
        setShapData([]);
        setExplainData(null);
        setPsychometric(null);
        setAnomalies([]);
        return;
      }

      // Build weekly timeline
      const anomalySet = new Set(
        (behavior.anomalies || []).map(a => `${a.year}-${a.week}`)
      );

      const timeline = behavior.features.map(f => ({
        label: `${f.year}-W${f.week}`,
        logon_count: f.logon_count,
        after_hours_logons: f.after_hours_logons,
        file_events: f.file_events,
        usb_events: f.usb_events,
        email_events: f.email_events,
        is_anomaly: anomalySet.has(`${f.year}-${f.week}`) ? 1 : 0,
      }));

      setWeeklyData(timeline);
      setAnomalies(behavior.anomalies || []);
      setPsychometric(behavior.psychometric || null);

      // Enhanced explanation
      if (explanation?.contributions) {
        setExplainData(explanation);
        setShapData(explanation.contributions.map(e => ({
          name: e.label || e.feature.replace(/_/g, ' '),
          value: e.score,
          user_value: e.user_value,
          global_avg: e.global_avg,
          direction: e.direction
        })));
      } else if (explanation?.explanation) {
        // Fallback for old format
        setExplainData(null);
        setShapData(explanation.explanation.map(e => ({
          name: e.feature.replace(/_/g, ' '),
          value: Math.round(e.contribution * 100) / 100,
          user_value: e.user_value,
          global_avg: e.global_avg
        })));
      }
    } catch (e) {
      console.error(e);
      setError(`Failed to load data for "${uid}"`);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (initialUser) fetchUserData(initialUser);
  }, [initialUser, fetchUserData]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (inputValue.trim()) {
      setUserId(inputValue.trim());
      fetchUserData(inputValue.trim());
    }
  };

  const riskColorMap = {
    CRITICAL: { bg: 'bg-red-500/15', border: 'border-red-500/30', text: 'text-red-400', bar: 'bg-red-500' },
    HIGH: { bg: 'bg-orange-500/15', border: 'border-orange-500/30', text: 'text-orange-400', bar: 'bg-orange-500' },
    MEDIUM: { bg: 'bg-yellow-500/15', border: 'border-yellow-500/30', text: 'text-yellow-400', bar: 'bg-yellow-500' },
    LOW: { bg: 'bg-green-500/15', border: 'border-green-500/30', text: 'text-green-400', bar: 'bg-green-500' },
  };

  return (
    <div className="p-8">
      <header className="mb-6">
        <h2 className="text-3xl font-bold text-white mb-2">Digital Twin Behavioral Analysis</h2>
        <p className="text-slate-400">Personalized autoencoder baselines with XAI explanations — using real CERT dataset.</p>
      </header>

      {/* User Search */}
      <form onSubmit={handleSearch} className="mb-6">
        <div className="glass-card p-4 flex items-center gap-4">
          <Search className="text-slate-400" size={20} />
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Enter User ID (e.g. CKB0427, LRR0148, MOH0273)"
            className="flex-1 bg-transparent border-none text-white placeholder-slate-500 focus:outline-none"
          />
          <button type="submit" className="bg-primary-500 hover:bg-primary-400 text-white px-6 py-2 rounded-lg text-sm transition-colors">
            Analyze
          </button>
        </div>
      </form>

      {loading && <LoadingSpinner message={`Analyzing user ${userId}...`} />}
      {error && (
        <div className="glass-card p-6 border border-red-500/20 text-red-400 text-center">{error}</div>
      )}

      {!loading && !error && weeklyData.length > 0 && (
        <div className="space-y-6">
          {/* Summary cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="glass-card p-4">
              <p className="text-xs text-slate-400">User</p>
              <p className="text-lg font-bold text-white">{userId}</p>
            </div>
            <div className="glass-card p-4">
              <p className="text-xs text-slate-400">Total Weeks</p>
              <p className="text-lg font-bold text-white">{weeklyData.length}</p>
            </div>
            <div className="glass-card p-4">
              <p className="text-xs text-slate-400">Anomalous Weeks</p>
              <p className="text-lg font-bold text-red-400">{anomalies.length}</p>
            </div>
            <div className="glass-card p-4">
              <p className="text-xs text-slate-400">Personality (OCEAN)</p>
              {psychometric ? (
                <p className="text-sm text-white mt-1">
                  O:{psychometric.O?.toFixed(1)} C:{psychometric.C?.toFixed(1)} E:{psychometric.E?.toFixed(1)} A:{psychometric.A?.toFixed(1)} N:{psychometric.N?.toFixed(1)}
                </p>
              ) : <p className="text-sm text-slate-500">N/A</p>}
            </div>
          </div>

          {/* XAI Natural Language Explanation */}
          {explainData && (
            <div className={`glass-card p-6 border ${riskColorMap[explainData.risk_level]?.border || 'border-white/10'}`}>
              <div className="flex items-center gap-3 mb-4">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${riskColorMap[explainData.risk_level]?.bg || 'bg-white/10'}`}>
                  <ShieldAlert size={20} className={riskColorMap[explainData.risk_level]?.text || 'text-white'} />
                </div>
                <div>
                  <h3 className="font-semibold text-white flex items-center gap-2">
                    Explainable AI — Why Was This User Flagged?
                    <span className={`px-3 py-1 rounded-full text-xs font-bold border ${riskColorMap[explainData.risk_level]?.bg || ''} ${riskColorMap[explainData.risk_level]?.border || ''} ${riskColorMap[explainData.risk_level]?.text || ''}`}>
                      {explainData.risk_level}
                    </span>
                  </h3>
                  <p className="text-xs text-slate-500">
                    Risk Score: {explainData.risk_score} · Anomaly Rate: {explainData.anomaly_rate}% ({explainData.anomalous_weeks}/{explainData.total_weeks} weeks)
                  </p>
                </div>
              </div>
              <p className="text-sm text-slate-300 leading-relaxed bg-white/5 rounded-lg p-4 border border-white/5">
                {explainData.summary}
              </p>
            </div>
          )}

          {/* Risk Factor Breakdown Panel */}
          {explainData && (
            <div className="glass-card p-6">
              <h3 className="font-semibold text-white mb-5 flex items-center gap-2">
                <TrendingUp size={18} className="text-primary-400" />
                Risk Factor Breakdown
                <span className="text-xs text-slate-500 font-normal ml-2">Contribution Score (1–100)</span>
              </h3>
              <div className="space-y-3">
                {shapData.map((item, i) => {
                  const barColor = item.value >= 70 ? 'bg-red-500' : item.value >= 40 ? 'bg-orange-500' : item.value >= 20 ? 'bg-yellow-500' : 'bg-blue-500';
                  const textColor = item.value >= 70 ? 'text-red-400' : item.value >= 40 ? 'text-orange-400' : item.value >= 20 ? 'text-yellow-400' : 'text-blue-400';
                  return (
                    <div key={i} className="group">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm text-slate-300 font-medium">{item.name}</span>
                        <div className="flex items-center gap-3">
                          <span className="text-xs text-slate-500">
                            User: {item.user_value} vs Avg: {item.global_avg}
                            {item.direction && <span className={item.direction === 'above' ? ' text-red-400' : ' text-blue-400'}> ({item.direction} avg)</span>}
                          </span>
                          <span className={`text-sm font-bold ${textColor} w-8 text-right`}>{item.value}</span>
                        </div>
                      </div>
                      <div className="w-full h-2.5 bg-white/5 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${barColor} rounded-full transition-all duration-700`}
                          style={{ width: `${item.value}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* OCEAN Personality Section */}
              {explainData.psychometric && (
                <div className="mt-6 pt-5 border-t border-white/10">
                  <h4 className="text-sm font-semibold text-slate-400 mb-3">OCEAN Personality Profile</h4>
                  <div className="grid grid-cols-5 gap-3">
                    {[
                      { key: 'O', label: 'Openness', color: 'bg-purple-500' },
                      { key: 'C', label: 'Conscientiousness', color: 'bg-blue-500' },
                      { key: 'E', label: 'Extraversion', color: 'bg-green-500' },
                      { key: 'A', label: 'Agreeableness', color: 'bg-yellow-500' },
                      { key: 'N', label: 'Neuroticism', color: 'bg-red-500' },
                    ].map(trait => {
                      const val = explainData.psychometric[trait.key] || 0;
                      const pct = Math.min(100, Math.max(0, val / 7 * 100));
                      return (
                        <div key={trait.key} className="text-center">
                          <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden mb-1">
                            <div className={`h-full ${trait.color} rounded-full`} style={{ width: `${pct}%` }} />
                          </div>
                          <p className="text-xs text-white font-bold">{val.toFixed(1)}</p>
                          <p className="text-xs text-slate-500 truncate" title={trait.label}>{trait.label}</p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Timeline Chart */}
            <div className="glass-card p-6 h-80 flex flex-col col-span-1 md:col-span-2">
              <h3 className="font-semibold text-white mb-4">Weekly Activity Timeline (User: {userId})</h3>
              <div className="flex-1 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={weeklyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                    <XAxis dataKey="label" stroke="#ffffff50" tick={{ fontSize: 10 }} interval={Math.max(1, Math.floor(weeklyData.length / 12))} />
                    <YAxis stroke="#ffffff50" />
                    <RechartsTooltip contentStyle={{ backgroundColor: '#13131a', borderColor: '#ffffff20', borderRadius: '8px' }} />
                    <Line type="monotone" dataKey="logon_count" stroke="#3b82f6" strokeWidth={2} name="Logons" dot={false} />
                    <Line type="monotone" dataKey="after_hours_logons" stroke="#ef4444" strokeWidth={2} name="After-hours" dot={false} />
                    <Line type="monotone" dataKey="file_events" stroke="#f97316" strokeWidth={2} name="File Events" dot={false} />
                    <Line type="monotone" dataKey="usb_events" stroke="#10b981" strokeWidth={2} name="USB Events" dot={false} />
                    <Legend />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Feature Importance Chart (scaled 1-100) */}
            <div className="glass-card p-6 h-80 flex flex-col">
              <h3 className="font-semibold text-white mb-4">XAI Contribution Score</h3>
              <div className="flex-1 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart layout="vertical" data={shapData} margin={{ top: 0, right: 0, bottom: 0, left: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" horizontal={false} />
                    <XAxis type="number" stroke="#ffffff50" domain={[0, 100]} />
                    <YAxis dataKey="name" type="category" stroke="#ffffff80" width={120} tick={{ fontSize: 11 }} />
                    <RechartsTooltip
                      contentStyle={{ backgroundColor: '#13131a', borderColor: '#ffffff20', borderRadius: '8px' }}
                      cursor={{ fill: '#ffffff05' }}
                      formatter={(value, name, props) => [`${value}/100`, `Score`]}
                    />
                    <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                      {shapData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.value >= 70 ? '#ef4444' : entry.value >= 40 ? '#f97316' : '#8b5cf6'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Anomalous weeks table */}
          {anomalies.length > 0 && (
            <div className="glass-card p-6">
              <h3 className="font-semibold text-white mb-4">Flagged Anomalous Weeks</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="bg-white/5 border-b border-white/10 text-slate-300">
                    <tr>
                      <th className="p-3">Year</th>
                      <th className="p-3">Week</th>
                      <th className="p-3">Reconstruction Error</th>
                      <th className="p-3">Risk</th>
                    </tr>
                  </thead>
                  <tbody className="text-slate-300">
                    {anomalies.map((a, i) => (
                      <tr key={i} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                        <td className="p-3">{a.year}</td>
                        <td className="p-3">W{a.week}</td>
                        <td className="p-3 font-mono">{a.reconstruction_error?.toFixed(6)}</td>
                        <td className="p-3"><RiskBadge error={a.reconstruction_error} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {!loading && !error && weeklyData.length === 0 && !userId && (
        <div className="glass-card p-12 text-center text-slate-500">
          <Activity size={48} className="mx-auto mb-4 opacity-50" />
          <p className="text-lg">Search for a user ID to view their Digital Twin behavioral analysis</p>
          <p className="text-sm mt-2">Try: CKB0427, LRR0148, MOH0273, NGF0157</p>
        </div>
      )}
    </div>
  );
};


// ─── Graph Mode ──────────────────────────────────
const RISK_COLORS = { high: '#ef4444', medium: '#f97316', low: '#22c55e', info: '#60a5fa' };
const TYPE_ICONS = { LOGON: '🔑', EMAIL: '📧', FILE: '📄', USB: '🔌' };

const GraphMode = () => {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const initialUser = params.get('user') || '';

  const [userId, setUserId] = useState(initialUser);
  const [inputValue, setInputValue] = useState(initialUser);
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [summary, setSummary] = useState(null);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchGraph = useCallback(async (uid) => {
    if (!uid) return;
    setLoading(true);
    setError(null);
    setHoveredNode(null);
    try {
      const data = await getUserActivityGraph(uid);
      if (!data || !data.nodes || data.nodes.length === 0) {
        setError(`No activity data found for "${uid}"`);
        setGraphData({ nodes: [], links: [] });
        setSummary(null);
        return;
      }

      // Format nodes with colors and sizes
      const formatted = data.nodes.map(n => {
        let color, size;
        if (n.type === 'user') {
          color = '#60a5fa'; size = 18;
        } else if (n.type === 'activity_type') {
          color = '#a78bfa'; size = 12;
        } else {
          color = RISK_COLORS[n.risk_level] || '#22c55e';
          size = n.risk_level === 'high' ? 8 : n.risk_level === 'medium' ? 6 : 4;
        }
        return { ...n, color, val: size };
      });

      setGraphData({ nodes: formatted, links: data.links });
      setSummary(data.summary);
    } catch (e) {
      console.error(e);
      setError(`Failed to load graph for "${uid}". User may not exist.`);
      setGraphData({ nodes: [], links: [] });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (initialUser) fetchGraph(initialUser);
  }, [initialUser, fetchGraph]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (inputValue.trim()) {
      setUserId(inputValue.trim());
      fetchGraph(inputValue.trim());
    }
  };

  // Custom node renderer
  const drawNode = useCallback((node, ctx, globalScale) => {
    const r = node.val || 4;
    const fontSize = Math.max(10 / globalScale, 2);

    // Glow effect for anomalous nodes
    if (node.risk_level === 'high' || node.risk_level === 'medium') {
      ctx.shadowColor = node.color;
      ctx.shadowBlur = node.risk_level === 'high' ? 15 : 8;
    }

    // Draw node circle
    ctx.beginPath();
    ctx.arc(node.x, node.y, r, 0, 2 * Math.PI);
    ctx.fillStyle = node.color;
    ctx.fill();
    ctx.shadowBlur = 0;

    // Border for user and type nodes
    if (node.type === 'user' || node.type === 'activity_type') {
      ctx.strokeStyle = 'rgba(255,255,255,0.6)';
      ctx.lineWidth = node.type === 'user' ? 2 : 1;
      ctx.stroke();
    }

    // Label
    if (globalScale > 0.5 || node.type === 'user' || node.type === 'activity_type') {
      const label = node.type === 'activity_type' ? `${TYPE_ICONS[node.label] || '📊'} ${node.label}` : node.label;
      ctx.font = `${node.type === 'user' ? 'bold ' : ''}${fontSize}px Inter, sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#ffffffcc';
      ctx.fillText(label, node.x, node.y + r + fontSize + 1);
    }
  }, []);

  // Link color based on risk
  const getLinkColor = useCallback((link) => {
    if (link.risk_level === 'high') return 'rgba(239,68,68,0.5)';
    if (link.risk_level === 'medium') return 'rgba(249,115,22,0.4)';
    return 'rgba(255,255,255,0.15)';
  }, []);

  // Tooltip generator for node hover
  const getNodeTooltip = useCallback((node) => {
    if (!node) return '';
    if (node.type === 'user') {
      const psy = node.psychometric;
      return `<div style="background:#13131aee;border:1px solid #ffffff20;border-radius:8px;padding:12px;min-width:220px;font-family:Inter,sans-serif;color:#e2e8f0;font-size:12px">
        <div style="font-size:16px;font-weight:700;color:#60a5fa;margin-bottom:6px">👤 ${node.label}</div>
        <div style="color:#94a3b8">Risk Score: <strong style="color:${node.risk_score > 1 ? '#ef4444' : '#f97316'}">${node.risk_score}</strong></div>
        <div style="color:#94a3b8">Anomalous Weeks: <strong style="color:#ef4444">${node.total_anomalous_weeks}</strong></div>
        ${psy ? `<div style="margin-top:6px;padding-top:6px;border-top:1px solid #ffffff15;color:#94a3b8">OCEAN: O:${psy.O} C:${psy.C} E:${psy.E} A:${psy.A} N:${psy.N}</div>` : ''}
      </div>`;
    }
    if (node.type === 'activity_type') {
      return `<div style="background:#13131aee;border:1px solid #ffffff20;border-radius:8px;padding:12px;min-width:180px;font-family:Inter,sans-serif;color:#e2e8f0;font-size:12px">
        <div style="font-size:14px;font-weight:700;color:#a78bfa;margin-bottom:4px">${TYPE_ICONS[node.label] || '📊'} ${node.label}</div>
        <div style="color:#94a3b8">Total Events: <strong>${node.total_events?.toLocaleString()}</strong></div>
      </div>`;
    }
    // Activity node
    const riskColor = RISK_COLORS[node.risk_level];
    const ctx = node.weekly_context;
    return `<div style="background:#13131aee;border:1px solid ${riskColor}40;border-radius:8px;padding:12px;min-width:240px;font-family:Inter,sans-serif;color:#e2e8f0;font-size:12px">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
        <span style="font-size:14px;font-weight:700;color:${riskColor}">${TYPE_ICONS[node.event_type] || ''} ${node.event_type} — W${node.week}'${String(node.year).slice(-2)}</span>
        <span style="padding:2px 8px;border-radius:12px;font-size:10px;font-weight:600;background:${riskColor}22;color:${riskColor};border:1px solid ${riskColor}44">${node.risk_level?.toUpperCase()}</span>
      </div>
      <div style="color:#94a3b8">Events: <strong>${node.count?.toLocaleString()}</strong></div>
      <div style="color:#94a3b8">After-Hours: <strong style="color:${node.after_hours_pct > 30 ? '#ef4444' : '#94a3b8'}">${node.after_hours_count} (${node.after_hours_pct}%)</strong></div>
      <div style="color:#94a3b8">Weekend: <strong>${node.weekend_count}</strong></div>
      ${node.pcs?.length ? `<div style="color:#94a3b8">PCs: ${node.pcs.join(', ')}</div>` : ''}
      ${node.is_anomalous ? `<div style="margin-top:6px;padding-top:6px;border-top:1px solid #ffffff15;color:#ef4444;font-weight:600">⚠ ANOMALOUS — Error: ${node.reconstruction_error}</div>` : ''}
      ${ctx ? `<div style="margin-top:4px;color:#64748b;font-size:11px">Week total: Logons:${ctx.logon_count || 0} Files:${ctx.file_events || 0} USB:${ctx.usb_events || 0} Email:${ctx.email_events || 0}</div>` : ''}
    </div>`;
  }, []);

  return (
    <div className="p-8 h-full flex flex-col space-y-6">
      <header>
        <h2 className="text-3xl font-bold text-white mb-2">Graph-Based Structural Analysis</h2>
        <p className="text-slate-400">Per-user activity graph — search for a user to visualize their behavioral patterns with risk-colored activity nodes.</p>
      </header>

      {/* Search Bar */}
      <form onSubmit={handleSearch}>
        <div className="glass-card p-4 flex items-center gap-4">
          <Network className="text-slate-400" size={20} />
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Enter User ID to visualize activity graph (e.g. DLM0051, AJF0370, HSB0196)"
            className="flex-1 bg-transparent border-none text-white placeholder-slate-500 focus:outline-none"
          />
          <button type="submit" className="bg-primary-500 hover:bg-primary-400 text-white px-6 py-2 rounded-lg text-sm transition-colors font-medium">
            Build Graph
          </button>
        </div>
      </form>

      {loading && <LoadingSpinner message={`Building activity graph for ${userId}...`} />}
      {error && (
        <div className="glass-card p-6 border border-red-500/20 text-red-400 text-center">{error}</div>
      )}

      {/* Summary cards when graph is loaded */}
      {!loading && !error && summary && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="glass-card p-4 text-center">
            <p className="text-xs text-slate-400">User</p>
            <p className="text-lg font-bold text-blue-400">{userId}</p>
          </div>
          <div className="glass-card p-4 text-center">
            <p className="text-xs text-slate-400">Total Events</p>
            <p className="text-lg font-bold text-white">{summary.total_events?.toLocaleString()}</p>
          </div>
          <div className="glass-card p-4 text-center">
            <p className="text-xs text-slate-400">Active Weeks</p>
            <p className="text-lg font-bold text-white">{summary.total_weeks}</p>
          </div>
          <div className="glass-card p-4 text-center">
            <p className="text-xs text-slate-400">Anomalous Weeks</p>
            <p className="text-lg font-bold text-red-400">{summary.anomalous_weeks}</p>
          </div>
          <div className="glass-card p-4 text-center">
            <p className="text-xs text-slate-400">Risk Score</p>
            <p className={`text-lg font-bold ${summary.risk_score > 1 ? 'text-red-400' : summary.risk_score > 0.1 ? 'text-orange-400' : 'text-green-400'}`}>
              {summary.risk_score}
            </p>
          </div>
        </div>
      )}

      {/* Graph + Legend */}
      {!loading && !error && graphData.nodes.length > 0 && (
        <div className="glass-card flex-1 w-full rounded-xl overflow-hidden relative" style={{ minHeight: '600px' }}>
          {/* Legend */}
          <div className="absolute top-4 left-4 bg-dark-800/90 backdrop-blur border border-white/10 p-4 rounded-lg z-10 w-60 shadow-2xl">
            <h3 className="font-semibold text-white mb-3 tracking-wide text-sm">Node Legend</h3>
            <div className="space-y-2 text-xs text-slate-300">
              <div className="flex items-center gap-2"><div className="w-4 h-4 rounded-full bg-blue-400 shadow-[0_0_8px_rgba(96,165,250,0.6)]"></div> User (Central)</div>
              <div className="flex items-center gap-2"><div className="w-4 h-4 rounded-full bg-purple-400 shadow-[0_0_8px_rgba(167,139,250,0.6)]"></div> Activity Type</div>
              <div className="flex items-center gap-2 pt-1 border-t border-white/10 mt-1"><div className="w-3 h-3 rounded-full bg-green-500"></div> Low Risk (Normal)</div>
              <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-orange-500"></div> Medium Risk (Suspicious)</div>
              <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-red-500 glow-red"></div> High Risk (Anomalous)</div>
            </div>
            <div className="mt-3 pt-3 border-t border-white/10 text-xs text-slate-400">
              {graphData.nodes.length} nodes · {graphData.links.length} edges
            </div>
            {summary?.event_types && (
              <div className="mt-2 pt-2 border-t border-white/10 text-xs text-slate-400 space-y-1">
                {Object.entries(summary.event_types).map(([t, c]) => (
                  <div key={t} className="flex justify-between">
                    <span>{TYPE_ICONS[t]} {t}</span>
                    <span className="text-white font-medium">{c.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Interactive graph */}
          <div style={{ width: '100%', height: '100%', position: 'absolute', inset: 0 }}>
            <ForceGraph2D
              graphData={graphData}
              nodeCanvasObject={drawNode}
              nodePointerAreaPaint={(node, color, ctx) => {
                ctx.beginPath();
                ctx.arc(node.x, node.y, node.val || 4, 0, 2 * Math.PI);
                ctx.fillStyle = color;
                ctx.fill();
              }}
              nodeLabel={getNodeTooltip}
              linkColor={getLinkColor}
              linkWidth={link => link.value || 1}
              linkLineDash={link => link.risk_level === 'high' ? [4, 2] : null}
              backgroundColor="#0a0a0f"
              cooldownTicks={100}
              d3AlphaDecay={0.02}
              d3VelocityDecay={0.3}
              onNodeDragEnd={node => { node.fx = node.x; node.fy = node.y; }}
              onNodeClick={(node) => setHoveredNode(node)}
            />
          </div>

          {/* Detail panel on click */}
          {hoveredNode && hoveredNode.type === 'activity' && (
            <div className="absolute top-4 right-4 bg-dark-800/95 backdrop-blur border border-white/10 p-5 rounded-lg z-10 w-72 shadow-2xl">
              <div className="flex justify-between items-start mb-3">
                <h4 className="font-semibold text-white">{TYPE_ICONS[hoveredNode.event_type]} {hoveredNode.event_type}</h4>
                <span className={`px-2 py-0.5 rounded-full text-xs font-semibold border ${hoveredNode.risk_level === 'high' ? 'bg-red-500/20 text-red-400 border-red-500/30' : hoveredNode.risk_level === 'medium' ? 'bg-orange-500/20 text-orange-400 border-orange-500/30' : 'bg-green-500/20 text-green-400 border-green-500/30'}`}>
                  {hoveredNode.risk_level?.toUpperCase()}
                </span>
              </div>
              <div className="space-y-2 text-sm text-slate-300">
                <div className="flex justify-between"><span>Period</span><strong className="text-white">Year {hoveredNode.year}, Week {hoveredNode.week}</strong></div>
                <div className="flex justify-between"><span>Event Count</span><strong className="text-white">{hoveredNode.count?.toLocaleString()}</strong></div>
                <div className="flex justify-between"><span>After-Hours</span><strong className={hoveredNode.after_hours_pct > 30 ? 'text-red-400' : 'text-white'}>{hoveredNode.after_hours_count} ({hoveredNode.after_hours_pct}%)</strong></div>
                <div className="flex justify-between"><span>Weekend</span><strong className="text-white">{hoveredNode.weekend_count}</strong></div>
                {hoveredNode.pcs?.length > 0 && (
                  <div><span className="text-slate-400">PCs:</span> <span className="text-white text-xs">{hoveredNode.pcs.join(', ')}</span></div>
                )}
                {hoveredNode.is_anomalous && (
                  <div className="mt-2 pt-2 border-t border-red-500/20 text-red-400 text-xs font-semibold flex items-center gap-1">
                    <AlertTriangle size={14} /> ANOMALOUS — Reconstruction Error: {hoveredNode.reconstruction_error}
                  </div>
                )}
              </div>
              <button onClick={() => setHoveredNode(null)} className="mt-3 text-xs text-slate-500 hover:text-slate-300 transition-colors">✕ Close</button>
            </div>
          )}
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && graphData.nodes.length === 0 && !userId && (
        <div className="glass-card p-16 text-center text-slate-500 flex-1 flex flex-col items-center justify-center">
          <Network size={56} className="mx-auto mb-4 opacity-50" />
          <p className="text-lg mb-2">Search for a user to build their activity graph</p>
          <p className="text-sm">Each user's activities (logins, files, USB, email) are rendered as connected nodes,</p>
          <p className="text-sm">color-coded by risk: <span className="text-green-400">Green</span> = Normal, <span className="text-orange-400">Orange</span> = Suspicious, <span className="text-red-400">Red</span> = Anomalous</p>
          <p className="text-xs mt-3 text-slate-600">Try: DLM0051, AJF0370, HSB0196, LBH0942, MOH0273</p>
        </div>
      )}
    </div>
  );
};


// ─── Insiders List ───────────────────────────────
const InsidersList = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getUsers(50, 0)
      .then(setUsers)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner message="Loading threat data..." />;

  return (
    <div className="p-8">
      <header className="mb-8">
        <h2 className="text-3xl font-bold text-white mb-2">High-Risk Insiders</h2>
        <p className="text-slate-400">Users flagged for anomalous activity, ranked by autoencoder reconstruction error.</p>
      </header>
      <div className="glass-card overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-white/5 border-b border-white/10 text-slate-300 text-sm">
            <tr>
              <th className="p-4">User ID</th>
              <th className="p-4">Risk Level</th>
              <th className="p-4">Reconstruction Error</th>
              <th className="p-4">Anomalous Weeks</th>
              <th className="p-4">OCEAN Profile</th>
              <th className="p-4">Action</th>
            </tr>
          </thead>
          <tbody className="text-slate-300">
            {users.map((u, i) => (
              <tr key={u.user_id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                <td className="p-4 font-medium text-white">{u.user_id}</td>
                <td className="p-4"><RiskBadge error={u.reconstruction_error} /></td>
                <td className="p-4 font-mono text-sm">{u.reconstruction_error?.toFixed(6)}</td>
                <td className="p-4">
                  <span className={u.anomalous_weeks > 0 ? 'text-red-400 font-semibold' : ''}>
                    {u.anomalous_weeks}
                  </span>
                </td>
                <td className="p-4 text-xs">
                  {u.O != null ? `O:${u.O?.toFixed(1)} C:${u.C?.toFixed(1)} E:${u.E?.toFixed(1)}` : 'N/A'}
                </td>
                <td className="p-4">
                  <Link to={`/digital-twin?user=${u.user_id}`} className="text-primary-400 text-sm hover:text-primary-300">
                    Investigate
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};


// ─── Search User ─────────────────────────────────
const SearchUser = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const navigate = useNavigate();

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setSearched(true);
    try {
      const data = await searchUsers(query.trim());
      setResults(data);
    } catch (err) {
      console.error(err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      <header className="mb-8">
        <h2 className="text-3xl font-bold text-white mb-2">Search User</h2>
        <p className="text-slate-400">Find a specific user to view their Digital Twin profile and activity history.</p>
      </header>
      <form onSubmit={handleSearch}>
        <div className="glass-card p-6 flex flex-col items-center justify-center">
          <div className="w-full max-w-lg relative">
            <Search className="absolute left-4 top-3 text-slate-400" size={20} />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter User ID (e.g. CKB0427, MOH, LRR)"
              className="w-full bg-dark-800 border border-white/10 text-white rounded-lg py-3 pl-12 pr-24 focus:outline-none focus:border-primary-500 transition-colors"
            />
            <button type="submit" className="absolute right-2 top-2 bg-primary-500 hover:bg-primary-400 text-white px-4 py-1.5 rounded-md text-sm transition-colors">
              Search
            </button>
          </div>
        </div>
      </form>

      {loading && <LoadingSpinner message="Searching..." />}

      {!loading && searched && results.length === 0 && (
        <div className="glass-card p-6 mt-6 text-center text-slate-500">No users found matching "{query}"</div>
      )}

      {!loading && results.length > 0 && (
        <div className="glass-card mt-6 overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-white/5 border-b border-white/10 text-slate-300 text-sm">
              <tr>
                <th className="p-4">User ID</th>
                <th className="p-4">Risk Level</th>
                <th className="p-4">Reconstruction Error</th>
                <th className="p-4">Anomalous Weeks</th>
                <th className="p-4">Action</th>
              </tr>
            </thead>
            <tbody className="text-slate-300">
              {results.map((u) => (
                <tr key={u.user_id} className="border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer" onClick={() => navigate(`/digital-twin?user=${u.user_id}`)}>
                  <td className="p-4 font-medium text-white">{u.user_id}</td>
                  <td className="p-4"><RiskBadge error={u.reconstruction_error} /></td>
                  <td className="p-4 font-mono text-sm">{u.reconstruction_error?.toFixed(6)}</td>
                  <td className="p-4">{u.anomalous_weeks}</td>
                  <td className="p-4">
                    <Link to={`/digital-twin?user=${u.user_id}`} className="text-primary-400 text-sm hover:text-primary-300">
                      Investigate
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};


// ─── Analytics ───────────────────────────────────
const Analytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAnalyticsOverview()
      .then(setAnalytics)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner message="Loading analytics..." />;

  const psyData = analytics?.psychometric_correlation || [];
  const activityData = analytics?.activity_distribution || [];
  const topUsers = analytics?.top_risky_users || [];

  // Colors for OCEAN traits scatter
  const traitColors = { O: '#3b82f6', C: '#10b981', E: '#f97316', A: '#8b5cf6', N: '#ef4444' };

  return (
    <div className="p-8">
      <header className="mb-8">
        <h2 className="text-3xl font-bold text-white mb-2">Deep Analytics</h2>
        <p className="text-slate-400">Correlate psychometric profiles with anomaly risk — real OCEAN data from CERT r4.2.</p>
      </header>

      {/* Top row: Activity + Risk */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="glass-card p-6 h-80 flex flex-col">
          <h3 className="font-semibold text-white mb-2">Event Type Breakdown</h3>
          <div className="flex-1 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={activityData} margin={{ top: 10, right: 10, bottom: 0, left: -10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                <XAxis dataKey="event_type" stroke="#ffffff50" />
                <YAxis stroke="#ffffff50" tickFormatter={v => v >= 1000000 ? `${(v / 1000000).toFixed(1)}M` : v >= 1000 ? `${(v / 1000).toFixed(0)}K` : v} />
                <RechartsTooltip contentStyle={{ backgroundColor: '#13131a', borderColor: '#ffffff20', borderRadius: '8px' }} formatter={v => v.toLocaleString()} />
                <Bar dataKey="count" name="Events" radius={[4, 4, 0, 0]}>
                  {activityData.map((entry, index) => {
                    const colors = { LOGON: '#3b82f6', EMAIL: '#8b5cf6', FILE: '#f97316', USB: '#10b981' };
                    return <Cell key={index} fill={colors[entry.event_type] || '#64748b'} />;
                  })}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-card p-6 h-80 flex flex-col">
          <h3 className="font-semibold text-white mb-2">Top 10 Riskiest Users</h3>
          <div className="flex-1 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart layout="vertical" data={topUsers.map(u => ({ user: u.user_id, error: Math.round(u.reconstruction_error * 10000) / 100 }))} margin={{ top: 0, right: 10, bottom: 0, left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" horizontal={false} />
                <XAxis type="number" stroke="#ffffff50" />
                <YAxis dataKey="user" type="category" stroke="#ffffff80" width={70} tick={{ fontSize: 11 }} />
                <RechartsTooltip contentStyle={{ backgroundColor: '#13131a', borderColor: '#ffffff20', borderRadius: '8px' }} cursor={{ fill: '#ffffff05' }} />
                <Bar dataKey="error" name="Risk Score" radius={[0, 4, 4, 0]}>
                  {topUsers.map((_, index) => (
                    <Cell key={index} fill={index < 3 ? '#ef4444' : index < 5 ? '#f97316' : '#8b5cf6'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Psychometric correlation table */}
      <div className="glass-card p-6">
        <h3 className="font-semibold text-white mb-4">Psychometric Profile vs Risk (Top 100 Users)</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-white/5 border-b border-white/10 text-slate-300">
              <tr>
                <th className="p-3">User ID</th>
                <th className="p-3">Risk Score</th>
                <th className="p-3 text-blue-400">Openness</th>
                <th className="p-3 text-green-400">Conscientiousness</th>
                <th className="p-3 text-orange-400">Extraversion</th>
                <th className="p-3 text-purple-400">Agreeableness</th>
                <th className="p-3 text-red-400">Neuroticism</th>
              </tr>
            </thead>
            <tbody className="text-slate-300">
              {psyData.slice(0, 20).map((u) => (
                <tr key={u.user_id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                  <td className="p-3 font-medium text-white">
                    <Link to={`/digital-twin?user=${u.user_id}`} className="hover:text-primary-400">{u.user_id}</Link>
                  </td>
                  <td className="p-3 font-mono">{u.reconstruction_error}</td>
                  <td className="p-3">{u.O?.toFixed(2)}</td>
                  <td className="p-3">{u.C?.toFixed(2)}</td>
                  <td className="p-3">{u.E?.toFixed(2)}</td>
                  <td className="p-3">{u.A?.toFixed(2)}</td>
                  <td className="p-3">{u.N?.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};


// ─── Visualizations ──────────────────────────────
const Visualizations = () => {
  const [analytics, setAnalytics] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getAnalyticsOverview(), getAnalyticsTimeline()])
      .then(([a, t]) => {
        setAnalytics(a);
        setTimeline(t.map(item => ({
          label: `${item.year}-W${item.week}`,
          count: item.count,
          avg_error: item.avg_error
        })));
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner message="Loading visualizations..." />;

  const actData = analytics?.activity_distribution || [];
  const totalEvents = actData.reduce((s, a) => s + a.count, 0);
  const pieColors = { LOGON: '#3b82f6', EMAIL: '#8b5cf6', FILE: '#f97316', USB: '#10b981' };
  const pieData = actData.map(a => ({
    name: a.event_type,
    value: a.count,
    color: pieColors[a.event_type] || '#64748b'
  }));

  const topUsers = (analytics?.top_risky_users || []).slice(0, 8).map(u => ({
    entity: u.user_id,
    risk: Math.round(u.reconstruction_error * 10000) / 100
  }));

  return (
    <div className="p-8 h-full flex flex-col space-y-6">
      <header>
        <h2 className="text-3xl font-bold text-white mb-2">Global Visualizations</h2>
        <p className="text-slate-400">System-wide charts from real CERT r4.2 dataset — {totalEvents.toLocaleString()} events analyzed.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-72">
        <div className="glass-card p-6 flex flex-col">
          <h3 className="font-semibold text-white mb-2">Event Distribution</h3>
          <div className="flex-1 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip contentStyle={{ backgroundColor: '#13131a', borderColor: '#ffffff20', borderRadius: '8px' }} formatter={v => v.toLocaleString()} />
                <Legend verticalAlign="bottom" height={36} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-card p-6 flex flex-col">
          <h3 className="font-semibold text-white mb-2">Highest Risk Users</h3>
          <div className="flex-1 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topUsers} margin={{ top: 10, right: 10, bottom: 0, left: -20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                <XAxis dataKey="entity" stroke="#ffffff50" tick={{ fontSize: 10 }} />
                <YAxis stroke="#ffffff50" tick={{ fontSize: 12 }} />
                <RechartsTooltip contentStyle={{ backgroundColor: '#13131a', borderColor: '#ffffff20', borderRadius: '8px' }} cursor={{ fill: '#ffffff05' }} />
                <Bar dataKey="risk" name="Risk Score" radius={[4, 4, 0, 0]}>
                  {topUsers.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={index < 3 ? '#ef4444' : '#f97316'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 h-72">
        <div className="glass-card p-6 flex flex-col">
          <h3 className="font-semibold text-white mb-2">Anomaly Timeline (System-Wide)</h3>
          <div className="flex-1 w-full">
            {timeline.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={timeline}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                  <XAxis dataKey="label" stroke="#ffffff50" tick={{ fontSize: 10 }} interval={Math.floor(timeline.length / 12)} />
                  <YAxis stroke="#ffffff50" />
                  <RechartsTooltip contentStyle={{ backgroundColor: '#13131a', borderColor: '#ffffff20', borderRadius: '8px' }} />
                  <Line type="monotone" dataKey="count" stroke="#10b981" strokeWidth={3} name="Anomaly Count" dot={{ r: 3, fill: '#10b981' }} activeDot={{ r: 6, fill: '#ef4444' }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-slate-500">No timeline data</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};


// ─── App ─────────────────────────────────────────
const App = () => {
  return (
    <Router>
      <div className="flex bg-dark-900 min-h-screen">
        <Sidebar />
        <main className="flex-1 ml-64 p-2 transition-all duration-300">
          <Routes>
            <Route path="/" element={<DashboardHub />} />
            <Route path="/digital-twin" element={<DigitalTwinMode />} />
            <Route path="/graph-analysis" element={<GraphMode />} />
            <Route path="/insiders" element={<InsidersList />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/search-user" element={<SearchUser />} />
            <Route path="/visualizations" element={<Visualizations />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;
