import { useCallback, useEffect, useState } from 'react'

const categories = [
  { value: 'idea', label: 'An idea' },
  { value: 'issue', label: 'Something is not working' },
  { value: 'experience', label: 'General experience' },
  { value: 'other', label: 'Other' },
]

function formatDate(value) {
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(new Date(value))
}

export default function FeedbackPage({ request }) {
  const [category, setCategory] = useState('idea')
  const [message, setMessage] = useState('')
  const [feedback, setFeedback] = useState([])
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)

  const loadFeedback = useCallback(async () => {
    try {
      setFeedback(await request('/feedback'))
      setError('')
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }, [request])

  useEffect(() => {
    let active = true
    request('/feedback')
      .then((result) => { if (active) setFeedback(result) })
      .catch((requestError) => { if (active) setError(requestError.message) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [request])

  async function submit(event) {
    event.preventDefault()
    setError('')
    setNotice('')
    setSending(true)
    try {
      await request('/feedback', { method: 'POST', body: { category, message } })
      setMessage('')
      setNotice('Thanks — your feedback was sent.')
      await loadFeedback()
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setSending(false)
    }
  }

  return (
    <>
      <div className="page-heading"><div><div className="eyebrow">HELP US IMPROVE</div><h1>Share feedback</h1><p>Your input helps us make VEIL Guard more useful and easier to trust.</p></div></div>
      <div className="feedback-layout">
        <section className="surface-card feedback-form-card">
          <div className="card-title"><span className="feedback-title-icon">FB</span><div><h2>Send a note</h2><p>Tell us what’s on your mind.</p></div></div>
          <form className="form-stack" onSubmit={submit}>
            <label className="field"><span>What is this about?</span><select value={category} onChange={(event) => setCategory(event.target.value)}>{categories.map((item) => <option value={item.value} key={item.value}>{item.label}</option>)}</select></label>
            <label className="field"><span>Your message</span><textarea rows={6} minLength={10} maxLength={2000} required value={message} onChange={(event) => setMessage(event.target.value)} placeholder="Share an idea, a rough edge, or something that worked well…" /><small className="character-count">{message.length}/2000 characters</small></label>
            <div className="privacy-warning"><span>!</span><p>Please don’t include passwords, source code, confidential prompts, or other sensitive information.</p></div>
            {notice && <div className="alert alert-success" role="status">{notice}</div>}
            {error && <div className="alert alert-error" role="alert">{error}</div>}
            <button className="button button-primary" disabled={sending || message.trim().length < 10} type="submit">{sending ? 'Sending…' : 'Send feedback'} <span aria-hidden="true">→</span></button>
          </form>
        </section>
        <aside className="feedback-aside">
          <div className="feedback-promise"><span className="promise-icon">V</span><h2>Small details make a difference.</h2><p>Your feedback is attached to your account so you can keep track of what you’ve shared.</p><div className="promise-foot"><span className="connection-dot" /> Associated with your account</div></div>
          <section className="feedback-history">
            <div className="section-heading"><div><div className="eyebrow">YOUR NOTES</div><h2>Recent feedback</h2></div></div>
            {loading ? <div className="loading-row">Loading…</div> : feedback.length ? feedback.slice(0, 3).map((item) => (
              <article className="feedback-item" key={item.id}><span className="feedback-category">{categories.find((option) => option.value === item.category)?.label || item.category}</span><p>{item.message}</p><small>{formatDate(item.created_at)}</small></article>
            )) : <p className="muted-copy">You haven’t sent feedback yet.</p>}
          </section>
        </aside>
      </div>
    </>
  )
}
