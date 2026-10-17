export default function AccountPage({ onAccessCloud }) {
  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">ACCOUNT</div>
          <h1>Your VEIL account</h1>
          <p>VEIL Guard works locally; a VEIL Cloud account is optional.</p>
        </div>
      </div>
      <section className="surface-card account-cloud-card">
        <span className="account-cloud-icon" aria-hidden="true">VC</span>
        <div className="account-cloud-copy">
          <h2>Access VEIL Cloud</h2>
          <p>Sign in or create an account to manage your profile, program catalog, and feedback.</p>
          <button className="button button-primary" onClick={onAccessCloud} type="button">
            Access VEIL Cloud <span aria-hidden="true">→</span>
          </button>
        </div>
      </section>
      <section className="surface-card account-boundary">
        <span className="boundary-icon">i</span>
        <div>
          <strong>Cloud access is optional</strong>
          <p>Local protection and setup remain available without signing in. This build does not activate protection.</p>
        </div>
      </section>
    </>
  )
}
