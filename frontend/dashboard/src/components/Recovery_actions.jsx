import '../styles/RecoveryActions.css';
import { useEffect, useState } from 'react';

function RecoveryActions() {
  const [actions, setActions] = useState([]);

  const [summary, setSummary] = useState({
    all: 0,
    completed: 0,
    pending: 0,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function getRecoveryActions() {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        'http://localhost:8000/recovery-actions'
      );

      if (!response.ok) {
        throw new Error('Failed to fetch recovery actions');
      }

      const data = await response.json();

      console.log('Recovery actions response:', data);
      console.log('First action:', data.all?.[0]);
      console.log('Attempts:', data.all?.[0]?.attempts);
      console.log('Attempt limit:', data.all?.[0]?.attempt_limit);

      const allActions = data.all || [];

      setActions(allActions);

      setSummary({
        all: allActions.length,
        completed: data.completed?.length || 0,
        pending: data.pending?.length || 0,
      });

    } catch (error) {
      console.error(error);
      setError('Unable to load recovery actions.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    getRecoveryActions();
  }, []);

  function formatDate(date) {
    if (!date) return '--';

    return new Date(date).toLocaleString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  function formatText(value) {
    if (!value) return '--';

    return value
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (char) => char.toUpperCase());
  }

  function formatProbability(value) {
    if (value === null || value === undefined) {
      return '--';
    }

    return `${(Number(value) * 100).toFixed(1)}%`;
  }

  function getStatusClass(status) {
    if (!status) return 'status-pending';

    switch (status.toLowerCase()) {
      case 'completed':
        return 'status-completed';

      case 'executed':
        return 'status-executed';

      case 'failed':
        return 'status-failed';

      case 'pending':
        return 'status-pending';

      default:
        return 'status-pending';
    }
  }

  return (
    <div className="recovery-actions-page">

      {/* Navbar */}
      <header className="navbar">

        <div className="brand">
          <div className="brand-icon">AI</div>
          <span>AI-Recovery Agent</span>
        </div>

        <nav className="nav-links">

          <a href="/">
            Home
          </a>

          <a href="/recovery-history">
            Recovery History
          </a>

          <a
            href="/recovery-actions"
            className="active"
          >
            Currently Working On
          </a>

          <a href="#">
            Analytics
          </a>

        </nav>

      </header>


      {/* Page */}
      <main className="actions-container">

        <div className="actions-header">

          <div>
            <p className="eyebrow">
              AI OPERATIONS
            </p>

            <h1>
              Recovery Actions
            </h1>

            <p className="subtitle">
              Monitor decisions made by the AI recovery agent.
            </p>
          </div>

          <div className="actions-count">
            {summary.all} actions
          </div>

        </div>


        {/* Small summary cards */}
        <div className="action-summary">

          <div className="summary-card">
            <span>Total Actions</span>
            <strong>{summary.all}</strong>
          </div>

          <div className="summary-card">
            <span>Pending</span>
            <strong>
              {
                summary.pending
              }
            </strong>
          </div>

          <div className="summary-card">
            <span>Completed</span>
            <strong>
              {
                summary.completed
              }
            </strong>
          </div>

          <div className="summary-card">
            <span>Executed</span>
            <strong>
              {
                summary.all
              }
            </strong>
          </div>

        </div>


        {/* Loading */}
        {loading && (
          <div className="state-card">

            <div className="loader"></div>

            <p>
              Loading recovery actions...
            </p>

          </div>
        )}


        {/* Error */}
        {!loading && error && (
          <div className="state-card error-state">

            <p>
              {error}
            </p>

            <button onClick={getRecoveryActions}>
              Try Again
            </button>

          </div>
        )}


        {/* Empty */}
        {!loading &&
          !error &&
          actions.length === 0 && (
            <div className="state-card">

              <div className="empty-icon">
                AI
              </div>

              <h3>
                No recovery actions yet
              </h3>

              <p>
                AI recovery decisions will appear here
                when the agent starts processing failed
                transactions.
              </p>

            </div>
          )}


        {/* Actions Table */}
        {!loading &&
          !error &&
          actions.length > 0 && (

            <div className="actions-table-card">

              <div className="table-wrapper">

                <table>

                  <thead>

                    <tr>
                      <th>Action</th>
                      <th>Transaction</th>
                      <th>Recovery Probability</th>
                      <th>Confidence</th>
                      <th>Status</th>
                      <th>Decision Reason</th>
                      <th>Attempts</th>
                      <th>Limit</th>
                      <th>Created</th>
                      <th>Reference</th>
                    </tr>

                  </thead>


                  <tbody>

                    {actions.map((action) => (

                      <tr key={action.id}>

                        {/* Action */}
                        <td>

                          <div className="action-info">

                            <div className="action-icon">
                              AI
                            </div>

                            <div>

                              <strong>
                                {formatText(action.action_type)}
                              </strong>

                              <small>
                                {action.id.slice(0, 8)}...
                              </small>

                            </div>

                          </div>

                        </td>


                        {/* Transaction */}
                        <td>

                          <span className="transaction-id">
                            {action.failed_transaction_id
                              ? `${action.failed_transaction_id.slice(
                                  0,
                                  8
                                )}...`
                              : '--'}
                          </span>

                        </td>


                        {/* Probability */}
                        <td>

                          <div className="metric">

                            <div className="metric-value">
                              {formatProbability(
                                action.recovery_probability
                              )}
                            </div>

                            <div className="metric-bar">

                              <div
                                className="metric-fill"
                                style={{
                                  width: `${Math.min(
                                    Number(
                                      action.recovery_probability || 0
                                    ) * 100,
                                    100
                                  )}%`,
                                }}
                              ></div>

                            </div>

                          </div>

                        </td>


                        {/* Confidence */}
                        <td>

                          <span className="confidence">
                            {formatProbability(
                              action.confidence
                            )}
                          </span>

                        </td>


                        {/* Status */}
                        <td>

                          <span
                            className={`action-status ${getStatusClass(
                              action.status
                            )}`}
                          >

                            <span className="status-dot-small"></span>

                            {formatText(action.status)}

                          </span>

                        </td>


                        {/* Reason */}
                        <td>

                          <div className="decision-reason">

                            {action.decision_reason
                              ? action.decision_reason
                              : '--'}

                          </div>

                        </td>
                        {/* Attempts */}
                            <td>
                            <span className="attempts-count">
                                {action.attempts }
                            </span>
                            </td>

                            {/* Attempt Limit */}
                            <td>
                            <span className="attempt-limit">
                                {action.attempt_limit ?? 5}
                            </span>
                            </td>


                        {/* Created */}
                        <td>

                          <span className="created-date">
                            {formatDate(action.created_at)}
                          </span>

                        </td>


                        {/* Reference */}
                        <td>

                          <span className="reference-id">

                            {action.razorpay_reference_id ||
                              '--'}

                          </span>

                        </td>

                      </tr>

                    ))}

                  </tbody>

                </table>

              </div>

            </div>

          )}

      </main>

    </div>
  );
}

export default RecoveryActions;