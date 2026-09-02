import './App.css';
import { useEffect, useState } from 'react';
import RecoveryHistory from './components/Recovery_history';
import RecoveryActions from './components/Recovery_actions';
function App() {
  const [info, setInfo] = useState(null);
   


  async function get_info() {
    try {
      const response = await fetch('http://localhost:8000/fetch-info');

      if (!response.ok) {
        throw new Error('Failed to fetch dashboard info');
      }

      const data = await response.json();
      setInfo(data);
    } catch (error) {
      console.error(error);
    }
  }

  useEffect(() => {
    get_info();
  }, []);
  if (window.location.pathname === '/recovery-history') {
    return <RecoveryHistory />;
  }
  if (window.location.pathname === '/recovery-actions') {
  return <RecoveryActions />;
}
  return (
    <div className="app">
      {/* Top Navigation */}
      <header className="navbar">
        <div className="brand">
          <div className="brand-icon">AI</div>
          <span>AI-Recovery Agent</span>
        </div>

        <nav className="nav-links">
          <a href="#">Home</a>
          <a href="/recovery-history">Recovery History</a>
          <a href="/recovery-actions">Currently Working On</a>
          <a href="#">Analytics</a>
        </nav>
      </header>

      {/* Dashboard */}
      <main className="dashboard">
        <div className="dashboard-header">
          <div>
            <p className="eyebrow">OVERVIEW</p>
            <h1>Recovery Dashboard</h1>
            <p className="subtitle">
              Monitor failed payments and recovered revenue.
            </p>
          </div>

          <div className="status">
            <span className="status-dot"></span>
            Agent Active
          </div>
        </div>

        {/* KPI Cards */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-top">
              <span>Failed Transactions</span>
              <span className="stat-icon">↘</span>
            </div>
            <h2>{info ? info.failed_transactions : '--'}</h2>
            <p className="muted">Transactions requiring recovery</p>
          </div>

          <div className="stat-card warning">
            <div className="stat-top">
              <span>Revenue at Risk</span>
              <span className="stat-icon">₹</span>
            </div>
            <h2>
              {info ? `₹${Number(info.failed_amount).toLocaleString()}` : '--'}
            </h2>
            <p className="muted">Potentially recoverable revenue</p>
          </div>

          <div className="stat-card success">
            <div className="stat-top">
              <span>Recovered Transactions</span>
              <span className="stat-icon">✓</span>
            </div>
            <h2>{info ? info.recovered_transactions : '--'}</h2>
            <p className="muted">Successfully recovered</p>
          </div>

          <div className="stat-card success">
            <div className="stat-top">
              <span>Revenue Recovered</span>
              <span className="stat-icon">↑</span>
            </div>
            <h2>
              {info
                ? `₹${Number(info.recovered_amount).toLocaleString()}`
                : '--'}
            </h2>
            <p className="muted">Revenue brought back</p>
          </div>
        </div>

        {/* Recovery Overview */}
        <section className="overview-card">
          <div className="overview-header">
            <div>
              <p className="eyebrow">RECOVERY PERFORMANCE</p>
              <h2>Recovery Rate</h2>
            </div>

            <div className="recovery-rate">
              {info ? `${info.recovery_rate}%` : '--'}
            </div>
          </div>

          <div className="progress-container">
            <div
              className="progress-bar"
              style={{
                width: `${info ? Math.min(info.recovery_rate, 100) : 0}%`,
              }}
            ></div>
          </div>

          <div className="progress-labels">
            <span>Failed payments</span>
            <span>Recovered payments</span>
          </div>
        </section>

        {/* Agent Activity */}
        <section className="activity-card">
          <div>
            <p className="eyebrow">AI AGENT</p>
            <h2>Recovery Agent Status</h2>
            <p>
              The AI agent is monitoring failed transactions and working on
              recovery opportunities.
            </p>
          </div>

          <div className="agent-status">
            <span className="pulse"></span>
            <span>Working</span>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;