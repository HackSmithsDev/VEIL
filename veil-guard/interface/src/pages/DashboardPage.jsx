import { useEffect, useState } from 'react'

function formatDate(value) {
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(new Date(value))
}

export default function DashboardPage({ user, request, onNavigate }) {
  const [programs, setPrograms] = useState([])
  const [feedback, setFeedback] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    Promise.all([request('/programs'), request('/feedback')])
      .then(([programData, feedbackData]) => {
        if (active) {
          setPrograms(programData)
          setFeedback(feedbackData)
        }
      })
      .catch((requestError) => { if (active) setError(requestError.message) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [request])

  return (
    <>
      <section className="welcome-panel">
        <div className="welcome-copy">
          <div className="eyebrow">YOUR VEIL WORKSPACE</div>
          <h1>Good to see you, {user.full_name.split(' ')[0]}.</h1>
          <p>Keep your program details organized while we prepare the next step in your upgrade journey.</p>
          <button className="button button-light" type="button" onClick={() => onNavigate('programs')}>
            View my programs <span aria-hidden="true">→</span>
          </button>
        </div>
        <div className="welcome-art" aria-hidden="true">
          <div className="art-orbit orbit-one" />
          <div className="art-orbit orbit-two" />
          <div className="art-core"><span>V</span></div>
          <span className="art-spark spark-one" />
          <span className="art-spark spark-two" />
        </div>
        <div className="welcome-caption"><span /> Your workspace is ready</div>
      </section>

      {error && <div className="alert alert-error page-alert" role="alert">{error}</div>}

      <section className="stat-grid" aria-label="Workspace summary">
        <article className="stat-card">
          <div className="stat-label"><span className="stat-icon indigo">PR</span> Tracked programs</div>
          <div className="stat-value">{loading ? '—' : programs.length}</div>
          <div className="stat-note">Program metadata in your workspace</div>
        </article>
        <article className="stat-card">
          <div className="stat-label"><span className="stat-icon mint">FB</span> Feedback shared</div>
          <div className="stat-value">{loading ? '—' : feedback.length}</div>
          <div className="stat-note">Ideas and notes sent to the VEIL team</div>
        </article>
        <article className="stat-card privacy-stat">
          <div className="stat-label"><span className="stat-icon gold">✓</span> Data boundary</div>
          <div className="privacy-value">Metadata only</div>
          <div className="stat-note">No source code is stored in this workspace</div>
        </article>
      </section>

      <section className="dashboard-lower">
        <article className="surface-card">
          <div className="section-heading">
            <div><div className="eyebrow">GET STARTED</div><h2>Your programs</h2></div>
            <button className="text-button" type="button" onClick={() => onNavigate('programs')}>Manage programs <span>→</span></button>
          </div>
          {loading ? <div className="loading-row">Loading your workspace…</div> : programs.length ? (
            <div className="mini-list">
              {programs.slice(0, 3).map((program) => (
                <div className="mini-row" key={program.id}>
                  <span className="program-monogram">{program.name.slice(0, 2).toUpperCase()}</span>
                  <span className="mini-main"><strong>{program.name}</strong><small>{program.platform} · v{program.version}</small></span>
                  <span className="mini-date">{formatDate(program.updated_at)}</span>
                </div>
              ))}
            </div>
          ) : <div className="empty-inline"><span className="empty-icon">+</span><strong>Nothing here yet</strong><p>Add a program to keep its basic details in one place.</p><button className="button button-secondary" type="button" onClick={() => onNavigate('programs')}>Add a program</button></div>}
        </article>

        <aside className="next-step-card">
          <div className="eyebrow">WHAT’S NEXT</div>
          <h2>A thoughtful upgrade starts with the basics.</h2>
          <p>Keep your program name, version, and platform current. AI-assisted upgrade workflows will come in a later release.</p>
          <div className="next-step-divider" />
          <div className="next-step-foot"><span className="small-shield">V</span><span>Designed for privacy<br /><small>Metadata now. Protected workflows later.</small></span></div>
        </aside>
      </section>
    </>
  )
}
