import '../styles/Recovery_history.css'
import { useEffect, useState } from 'react';

function RecoveryHistory() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function getRecoveredTransactions() {
    try {
      const response = await fetch(
        'http://localhost:8000/recovered-transactions'
      );

      if (!response.ok) {
        throw new Error('Failed to fetch recovery history');
      }

      const data = await response.json();
      setTransactions(data);
    } catch (error) {
      console.error(error);
      setError('Unable to load recovery history.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    getRecoveredTransactions();
  }, []);

  function formatAmount(amount, currency) {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency || 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  }

  function formatDate(date) {
    return new Date(date).toLocaleString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  function formatFailureReason(reason) {
    if (!reason) return 'Unknown';

    return reason
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (char) => char.toUpperCase());
  }

  function formatRecoveryMethod(method) {
    if (!method) return 'Unknown';

    return method
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (char) => char.toUpperCase());
  }

  return (
    <div className="recovery-page">

      {/* Navbar */}
      <header className="navbar">
        <div className="brand">
          <div className="brand-icon">AI</div>
          <span>AI-Recovery Agent</span>
        </div>

        <nav className="nav-links">
          <a href="/">Home</a>
          <a href="/recovery-history" className="active">
            Recovery History
          </a>
          <a href="/recovery-actions">Currently Working On</a>
          <a href="#">Analytics</a>
        </nav>
      </header>

      {/* Page Content */}
      <main className="history-container">

        <div className="history-header">
          <div>
            <p className="eyebrow">RECOVERY</p>
            <h1>Recovery History</h1>
            <p className="subtitle">
              View all transactions successfully recovered by the AI agent.
            </p>
          </div>

          <div className="transaction-count">
            {transactions.length} recovered
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div className="state-card">
            <div className="loader"></div>
            <p>Loading recovery history...</p>
          </div>
        )}

        {/* Error */}
        {!loading && error && (
          <div className="state-card error-state">
            <p>{error}</p>
            <button onClick={getRecoveredTransactions}>
              Try Again
            </button>
          </div>
        )}

        {/* Empty */}
        {!loading && !error && transactions.length === 0 && (
          <div className="state-card">
            <div className="empty-icon">✓</div>
            <h3>No recovered transactions</h3>
            <p>
              Recovered transactions will appear here once the agent
              successfully recovers a payment.
            </p>
          </div>
        )}

        {/* Table */}
        {!loading && !error && transactions.length > 0 && (
          <div className="table-card">

            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Transaction</th>
                    <th>Amount</th>
                    <th>Failure Reason</th>
                    <th>Recovery Method</th>
                    <th>Recovered At</th>
                    <th>Razorpay ID</th>
                    <th>Status</th>
                  </tr>
                </thead>

                <tbody>
                  {transactions.map((transaction) => (
                    <tr key={transaction.id}>

                      <td>
                        <div className="transaction-info">
                          <span className="transaction-dot">✓</span>
                          <div>
                            <strong>
                              {transaction.razorpay_reference_id}
                            </strong>
                            <small>
                              {transaction.id.slice(0, 8)}...
                            </small>
                          </div>
                        </div>
                      </td>

                      <td>
                        <strong className="amount">
                          {formatAmount(
                            transaction.amount,
                            transaction.currency
                          )}
                        </strong>
                      </td>

                      <td>
                        <span className="reason">
                          {formatFailureReason(
                            transaction.original_failure_reason
                          )}
                        </span>
                      </td>

                      <td>
                        <span className="method">
                          {formatRecoveryMethod(
                            transaction.recovery_method
                          )}
                        </span>
                      </td>

                      <td>
                        <span className="date">
                          {formatDate(transaction.recovered_at)}
                        </span>
                      </td>

                      <td>
                        <span className="payment-id">
                          {transaction.razorpay_payment_id}
                        </span>
                      </td>

                      <td>
                        <span className="success-badge">
                          <span></span>
                          Recovered
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

export default RecoveryHistory;