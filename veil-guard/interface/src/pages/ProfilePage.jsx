import { useState } from 'react'

export default function ProfilePage({ user, request, onUserUpdated }) {
  const [fullName, setFullName] = useState(user.full_name)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  async function saveProfile(event) {
    event.preventDefault()
    setSaving(true)
    setMessage('')
    setError('')
    try {
      const updatedUser = await request('/profile', {
        method: 'PATCH',
        body: { full_name: fullName },
      })
      onUserUpdated(updatedUser)
      setMessage('Your profile has been updated.')
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <div className="page-heading"><div><div className="eyebrow">ACCOUNT SETTINGS</div><h1>Your profile</h1><p>Manage the basic details associated with your VEIL Guard account.</p></div></div>
      <section className="surface-card profile-card">
        <div className="profile-card-heading"><span className="profile-avatar">{user.full_name.split(/\s+/).map((part) => part[0]).slice(0, 2).join('').toUpperCase()}</span><div><h2>Personal details</h2><p>Only you can view and update this information.</p></div></div>
        <form className="profile-form" onSubmit={saveProfile}>
          <label className="field"><span>Full name</span><input required maxLength={120} value={fullName} onChange={(event) => setFullName(event.target.value)} /></label>
          <label className="field"><span>Email address</span><input value={user.email} readOnly disabled /><small>Email changes are not available yet.</small></label>
          {message && <div className="alert alert-success" role="status">{message}</div>}
          {error && <div className="alert alert-error" role="alert">{error}</div>}
          <div className="profile-actions"><button className="button button-primary" disabled={saving || fullName.trim() === user.full_name} type="submit">{saving ? 'Saving…' : 'Save profile'}</button></div>
        </form>
      </section>
      <section className="surface-card account-boundary"><span className="boundary-icon">i</span><div><strong>Your account data</strong><p>Your profile and program metadata are stored in VEIL Cloud. Do not add passwords, source code, confidential prompts, or other secrets to descriptions or feedback.</p></div></section>
    </>
  )
}
