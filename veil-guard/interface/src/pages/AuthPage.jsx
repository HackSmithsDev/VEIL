import { useState } from 'react'
import { getApiBaseUrl } from '../api/cloud/client'

export default function AuthPage({ onLogin, onRegister }) {
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({ full_name: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const isRegister = mode === 'register'

  async function submit(event) {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)
    try {
      if (isRegister) {
        await onRegister(form)
      } else {
        await onLogin({ email: form.email, password: form.password })
      }
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="auth-page">
      <div className="auth-decoration auth-decoration-one" />
      <div className="auth-decoration auth-decoration-two" />
      <header className="auth-brand">
        <span className="brand-mark">V</span>
        <span className="brand-name">VEIL<span>GUARD</span></span>
      </header>
      <section className="auth-card">
        <div className="auth-eyebrow"><span /> PRIVATE WORKSPACE</div>
        <h1>{isRegister ? 'Create your account' : 'Welcome back'}</h1>
        <p className="auth-subtitle">
          {isRegister
            ? 'Set up your VEIL Guard account to manage your program details.'
            : 'Sign in to continue to your VEIL Guard workspace.'}
        </p>
        <form className="form-stack" onSubmit={submit}>
          {isRegister && (
            <label className="field">
              <span>Your name</span>
              <input
                autoComplete="name"
                maxLength={120}
                required
                value={form.full_name}
                onChange={(event) => setForm({ ...form, full_name: event.target.value })}
                placeholder="e.g. Alex Morgan"
              />
            </label>
          )}
          <label className="field">
            <span>Email address</span>
            <input
              autoComplete="email"
              type="email"
              required
              value={form.email}
              onChange={(event) => setForm({ ...form, email: event.target.value })}
              placeholder="you@example.com"
            />
          </label>
          <label className="field">
            <span>Password</span>
            <input
              autoComplete={isRegister ? 'new-password' : 'current-password'}
              type="password"
              minLength={isRegister ? 12 : 1}
              maxLength={128}
              required
              value={form.password}
              onChange={(event) => setForm({ ...form, password: event.target.value })}
              placeholder={isRegister ? 'At least 12 characters' : 'Enter your password'}
            />
            {isRegister && <small>Use at least 12 characters.</small>}
          </label>
          {error && <div className="alert alert-error" role="alert">{error}</div>}
          <button className="button button-primary button-full" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Please wait…' : isRegister ? 'Create account' : 'Sign in'}
            {!isSubmitting && <span aria-hidden="true">→</span>}
          </button>
        </form>
        <div className="auth-switch">
          {isRegister ? 'Already have an account?' : 'New to VEIL Guard?'}
          <button
            type="button"
            onClick={() => { setMode(isRegister ? 'login' : 'register'); setError('') }}
          >
            {isRegister ? 'Sign in' : 'Create an account'}
          </button>
        </div>
      </section>
      <p className="auth-footnote">
        Your program records contain metadata only. Do not upload source code,
        credentials, or confidential AI prompts.
      </p>
      <small className="auth-api">API: {getApiBaseUrl()}</small>
    </main>
  )
}
