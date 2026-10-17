import { useCallback, useEffect, useState } from 'react'

const emptyProgram = { name: '', version: '', platform: '', purpose: '' }

export default function ProgramsPage({ request }) {
  const [programs, setPrograms] = useState([])
  const [query, setQuery] = useState('')
  const [editing, setEditing] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [form, setForm] = useState(emptyProgram)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  const loadPrograms = useCallback(async () => {
    try {
      setPrograms(await request('/programs'))
      setError('')
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }, [request])

  useEffect(() => {
    let active = true
    request('/programs')
      .then((result) => { if (active) setPrograms(result) })
      .catch((requestError) => { if (active) setError(requestError.message) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [request])

  function openForm(program = null) {
    setEditing(program)
    setIsModalOpen(true)
    setForm(program ? {
      name: program.name,
      version: program.version,
      platform: program.platform,
      purpose: program.purpose || '',
    } : emptyProgram)
    setError('')
  }

  async function saveProgram(event) {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      await request(editing ? `/programs/${editing.id}` : '/programs', {
        method: editing ? 'PUT' : 'POST',
        body: { ...form, purpose: form.purpose || null },
      })
      setIsModalOpen(false)
      await loadPrograms()
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setSaving(false)
    }
  }

  async function deleteProgram(program) {
    if (!window.confirm(`Remove ${program.name} from your program list?`)) return
    setError('')
    try {
      await request(`/programs/${program.id}`, { method: 'DELETE' })
      await loadPrograms()
    } catch (requestError) {
      setError(requestError.message)
    }
  }

  const filteredPrograms = programs.filter((program) =>
    `${program.name} ${program.version} ${program.platform}`.toLowerCase().includes(query.toLowerCase()),
  )

  return (
    <>
      <div className="page-heading">
        <div><div className="eyebrow">VEIL CLOUD CATALOG</div><h1>Program metadata</h1><p>Keep basic program details together. This catalog is not a list of connected or protected apps.</p></div>
        <button className="button button-primary" type="button" onClick={() => openForm()}><span>＋</span> Add program</button>
      </div>
      <div className="privacy-note"><span className="privacy-note-icon">i</span><span><strong>Metadata only.</strong> Add the name, version, and platform. This is not a source-code upload or upgrade request.</span></div>
      {error && <div className="alert alert-error page-alert" role="alert">{error}</div>}
      <section className="surface-card programs-card">
        <div className="list-toolbar">
          <div className="list-count">{programs.length} {programs.length === 1 ? 'program' : 'programs'}</div>
          <label className="search-field"><span aria-hidden="true">⌕</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search programs" aria-label="Search programs" /></label>
        </div>
        {loading ? <div className="loading-row">Loading your programs…</div> : filteredPrograms.length ? (
          <div className="program-list">
            {filteredPrograms.map((program) => (
              <article className="program-row" key={program.id}>
                <span className="program-monogram">{program.name.slice(0, 2).toUpperCase()}</span>
                <div className="program-description"><strong>{program.name}</strong><span>{program.purpose || 'No description added'}</span></div>
                <div className="program-meta"><span>{program.platform}</span><small>Version {program.version}</small></div>
                <div className="program-actions">
                  <button className="subtle-button" type="button" onClick={() => openForm(program)}>Edit</button>
                  <button className="subtle-button danger-text" type="button" onClick={() => deleteProgram(program)}>Remove</button>
                </div>
              </article>
            ))}
          </div>
        ) : <div className="empty-state"><span className="empty-icon">PR</span><h2>{query ? 'No matching programs' : 'Your list is ready for its first program'}</h2><p>{query ? 'Try a different search.' : 'Add a few basic details to start building your catalog.'}</p>{!query && <button className="button button-secondary" type="button" onClick={() => openForm()}>Add your first program</button>}</div>}
      </section>

      {isModalOpen && (
        <div className="modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setIsModalOpen(false) }}>
          <section className="modal-card" role="dialog" aria-modal="true" aria-labelledby="program-modal-title">
            <div className="modal-heading"><div><div className="eyebrow">{editing ? 'UPDATE DETAILS' : 'NEW ENTRY'}</div><h2 id="program-modal-title">{editing ? 'Edit program' : 'Add a program'}</h2></div><button className="icon-button modal-close" type="button" onClick={() => setIsModalOpen(false)} aria-label="Close">×</button></div>
            <form className="form-stack" onSubmit={saveProgram}>
              <label className="field"><span>Program name</span><input required maxLength={120} value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} placeholder="e.g. Customer portal" /></label>
              <div className="form-grid">
                <label className="field"><span>Current version</span><input required maxLength={60} value={form.version} onChange={(event) => setForm({ ...form, version: event.target.value })} placeholder="e.g. 2.4.1" /></label>
                <label className="field"><span>Platform</span><input required maxLength={80} value={form.platform} onChange={(event) => setForm({ ...form, platform: event.target.value })} placeholder="e.g. Windows, web" /></label>
              </div>
              <label className="field"><span>Short description <small>Optional</small></span><textarea maxLength={1000} rows={3} value={form.purpose} onChange={(event) => setForm({ ...form, purpose: event.target.value })} placeholder="What does this program do?" /></label>
              {error && <div className="alert alert-error" role="alert">{error}</div>}
              <div className="modal-actions"><button className="button button-quiet" type="button" onClick={() => setIsModalOpen(false)}>Cancel</button><button className="button button-primary" disabled={saving} type="submit">{saving ? 'Saving…' : editing ? 'Save changes' : 'Add program'}</button></div>
            </form>
          </section>
        </div>
      )}
    </>
  )
}
