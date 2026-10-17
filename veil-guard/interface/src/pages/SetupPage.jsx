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
    title: 'Install VEIL Guard',
    description: 'A separate platform installer will install the utility and background Engine without requiring a VEIL Cloud account.',
    status: 'Installer package not available in this build',
    state: 'blocked',
  },
  {
    number: '02',
    title: 'Add local processing',
    description: 'Ollama and model downloads will be optional, with download size and storage requirements shown before consent.',
    status: 'Optional · not available yet',
    state: 'pending',
  },
  {
    number: '03',
    title: 'Connect supported apps',
    description: 'Enable explicitly supported AI apps one at a time. VEIL Guard will not monitor every app or intercept unrelated traffic.',
    status: 'Not available yet',
    state: 'pending',
  },
]

export default function SetupPage() {
  return (
    <>
      <div className="page-heading setup-page-heading">
        <div>
          <div className="eyebrow">PROTECTION SETUP</div>
          <h1>Set up VEIL Guard</h1>
          <p>Review each step before enabling local prompt protection.</p>
        </div>
        <span className="platform-chip">{detectPlatform()} device</span>
      </div>

      <section className="setup-status-card" aria-labelledby="setup-status-title">
        <div className="setup-status-icon" aria-hidden="true">!</div>
        <div>
          <div className="eyebrow">CURRENT STATUS</div>
          <h2 id="setup-status-title">Protection is off</h2>
          <p>The separate platform installer and Engine service are not available in this build. VEIL Guard is not inspecting AI requests or blocking credential leaks.</p>
        </div>
      </section>

      <section className="setup-card" aria-label="Setup steps">
        <div className="setup-card-heading">
          <div><div className="eyebrow">INSTALLATION</div><h2>Three steps to get started</h2></div>
          <span className="setup-progress-label">0 of 3 complete</span>
        </div>
        <div className="setup-progress-track" role="progressbar" aria-label="Setup progress" aria-valuemin="0" aria-valuemax="3" aria-valuenow="0">
          <span />
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
          <p>When installers are available, VEIL Guard will request administrator approval only for platform steps that require it. Ollama and model downloads will be optional and require your confirmation.</p>
        </div>
        <button className="button button-primary setup-install-button" type="button" disabled title="Platform installer package is not available in this build">
          Installer package not available
        </button>
      </section>
    </>
  )
}
