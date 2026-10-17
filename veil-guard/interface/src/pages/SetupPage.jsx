function detectPlatform() {
  const platform = navigator.userAgentData?.platform || navigator.platform || ''
  if (/win/i.test(platform)) return 'Windows'
  if (/mac|darwin/i.test(platform)) return 'macOS'
  if (/linux/i.test(platform)) return 'Linux'
  return 'Unknown platform'
}

const setupSteps = [
  {
    number: '01',
    title: 'VEIL Engine service',
    description: 'The background Engine and local IPC are not connected in this build, so requests are not inspected and credential leaks are not blocked.',
    status: 'Not included in this build',
    state: 'blocked',
  },
  {
    number: '02',
    title: 'Optional local processing',
    description: 'Ollama and model integration are not available yet. This app does not install Ollama or download a model.',
    status: 'Optional · not implemented',
    state: 'pending',
  },
  {
    number: '03',
    title: 'Supported-app connectors',
    description: 'No AI app connectors or permission controls are available yet. VEIL Guard is not monitoring other apps.',
    status: 'No connectors in this build',
    state: 'pending',
  },
]

export default function SetupPage({ onNavigate }) {
  return (
    <>
      <div className="page-heading setup-page-heading">
        <div>
          <div className="eyebrow">PROTECTION SETUP</div>
          <h1>Setup readiness</h1>
          <p>The installer installs VEIL Guard; this page shows what is needed before protection is available.</p>
        </div>
        <span className="platform-chip">{detectPlatform()} device</span>
      </div>

      <section className="setup-status-card" aria-labelledby="setup-status-title">
        <div className="setup-status-icon" aria-hidden="true">!</div>
        <div>
          <div className="eyebrow">CURRENT STATUS</div>
          <h2 id="setup-status-title">Protection is off</h2>
          <p>The Engine service is not bundled or connected in this build. VEIL Guard is not inspecting AI requests or blocking credential leaks.</p>
        </div>
      </section>

      <section className="setup-card" aria-label="Setup readiness">
        <div className="setup-card-heading">
          <div><div className="eyebrow">READINESS</div><h2>What is available right now</h2></div>
          <span className="setup-progress-label">Protection off</span>
        </div>
        <ol className="setup-steps">
          {setupSteps.map((step) => (
            <li className={`setup-step setup-step-${step.state}`} key={step.number}>
              <span className="setup-step-number">{step.number}</span>
              <div className="setup-step-copy">
                <h3>{step.title}</h3>
                <p>{step.description}</p>
                <span className="setup-step-status">{step.status}</span>
              </div>
            </li>
          ))}
        </ol>
        <div className="setup-consent-note">
          <span aria-hidden="true">i</span>
          <p>Local protection will remain account-free. Any future optional model download or platform permission request must be shown clearly and require your confirmation.</p>
        </div>
        <button className="button button-secondary setup-install-button" type="button" onClick={() => onNavigate('settings')}>
          Configure local model preferences
        </button>
      </section>
    </>
  )
}
