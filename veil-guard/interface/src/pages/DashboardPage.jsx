export default function DashboardPage({ onNavigate }) {
  return (
    <>
      <div className="page-heading protection-page-heading">
        <div>
          <div className="eyebrow">VEIL GUARD</div>
          <h1>Protection status</h1>
          <p>Manage local protection independently from your VEIL Cloud account.</p>
        </div>
        <button className="button button-secondary" type="button" onClick={() => onNavigate('setup')}>Setup</button>
      </div>

      <section className="protection-status-card" aria-labelledby="protection-title">
        <span className="protection-status-indicator" aria-hidden="true">!</span>
        <div className="protection-status-copy">
          <div className="eyebrow">ENGINE STATUS</div>
          <h2 id="protection-title">Not connected</h2>
          <p>This build has no Engine service integration. VEIL Guard is not inspecting AI requests or blocking credential leaks.</p>
        </div>
      </section>

      <section className="protection-checks" aria-label="Protection components">
        <article className="protection-check">
          <span className="protection-check-icon">01</span>
          <span><strong>VEIL Engine</strong><small>Installer and IPC integration not available</small></span>
          <span className="status-pill status-pill-off">Unavailable</span>
        </article>
        <article className="protection-check">
          <span className="protection-check-icon">02</span>
          <span><strong>AI connectors</strong><small>No supported apps connected</small></span>
          <span className="status-pill status-pill-off">Not configured</span>
        </article>
        <article className="protection-check">
          <span className="protection-check-icon">03</span>
          <span><strong>Local processing</strong><small>Optional Ollama setup is not available yet</small></span>
          <span className="status-pill status-pill-pending">Not configured</span>
        </article>
      </section>

      <div className="protection-actions">
        <button className="button button-primary" type="button" onClick={() => onNavigate('setup')}>Review setup steps</button>
        <p>Your account is optional. Local protection will not require sign-in when it becomes available.</p>
      </div>
    </>
  )
}
