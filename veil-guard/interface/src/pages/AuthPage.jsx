import { useState } from 'react'

export default function AuthPage({
  onLogin,
  onRegister,
  onRequestPasswordReset,
  onConfirmPasswordReset,
}) {
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({ full_name: '', email: '', password: '' })
  const [resetToken, setResetToken] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const isRegister = mode === 'register'
  const isForgotPassword = mode === 'forgot'
  const isConfirmingReset = mode === 'reset'

  async function submit(event) {
    event.preventDefault()
    setError('')
    setNotice('')
    setIsSubmitting(true)
    try {
      if (isRegister) {
        await onRegister(form)
      } else if (isForgotPassword) {
        const result = await onRequestPasswordReset({ email: form.email })
        setNotice(result.message)
        setMode('reset')
      } else if (isConfirmingReset) {
        const result = await onConfirmPasswordReset({
          email: form.email,
          reset_token: resetToken,
          new_password: newPassword,
        })
        setForm({ ...form, password: '' })
        setResetToken('')
        setNewPassword('')
        setMode('login')
        setNotice(result.message)
      } else {
        await onLogin({ email: form.email, password: form.password })
      }
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  async function resendResetCode() {
    setError('')
    setNotice('')
    setIsSubmitting(true)
    setMode('forgot')
    try {
      const result = await onRequestPasswordReset({ email: form.email })
      setMode('reset')
      setNotice(result.message)
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="auth-card">
        <div className="auth-eyebrow"><span /> VEIL CLOUD</div>
        <h1 id="cloud-access-title">
          {isForgotPassword
            ? 'Forgot your password?'
            : isConfirmingReset
              ? 'Enter your reset code'
              : isRegister
                ? 'Create your account'
                : 'Welcome back'}
        </h1>
        {isForgotPassword || isConfirmingReset ? (
          <>
            <p className="auth-subtitle">{isForgotPassword
              ? 'Enter your email and we’ll send a one-time reset code if an account exists.'
              : `Enter the one-time code sent to ${form.email} and choose a new password.`}</p>
            <form className="form-stack" onSubmit={submit}>
              {isForgotPassword ? (
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
              ) : (
                <>
                  <label className="field">
                    <span>One-time reset code</span>
                    <input
                      autoComplete="one-time-code"
                      maxLength={128}
                      required
                      value={resetToken}
                      onChange={(event) => setResetToken(event.target.value)}
                      placeholder="Paste the code from your email"
                    />
                  </label>
                  <label className="field">
                    <span>New password</span>
                    <input
                      autoComplete="new-password"
                      type="password"
                      minLength={12}
                      maxLength={128}
                      required
                      value={newPassword}
                      onChange={(event) => setNewPassword(event.target.value)}
                      placeholder="At least 12 characters"
                    />
                    <small>Use at least 12 characters.</small>
                  </label>
                </>
              )}
              {error && <div className="alert alert-error" role="alert">{error}</div>}
              {notice && <div className="alert alert-success" role="status">{notice}</div>}
              <button className="button button-primary button-full" type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Please wait…' : isConfirmingReset ? 'Reset password' : 'Send reset code'}
                {!isSubmitting && <span aria-hidden="true">→</span>}
              </button>
              {isConfirmingReset && (
                <button
                  className="auth-forgot-button"
                  disabled={isSubmitting}
                  onClick={resendResetCode}
                  type="button"
                >
                  {isSubmitting ? 'Sending…' : 'Send a new code'}
                </button>
              )}
            </form>
            <button
              className="auth-forgot-button"
              onClick={() => { setMode('login'); setError(''); setNotice('') }}
              type="button"
            >
              Back to sign in
            </button>
          </>
        ) : (
          <>
            <p className="auth-subtitle">
              {isRegister
                ? 'Create an account for your VEIL Cloud profile, program metadata, and feedback.'
                : 'Sign in to access your VEIL Cloud profile, program metadata, and feedback.'}
            </p>
            {notice && <div className="alert alert-success" role="status">{notice}</div>}
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
            {!isRegister && (
              <button
                className="auth-forgot-button"
                onClick={() => { setMode('forgot'); setError(''); setNotice('') }}
                type="button"
              >
                Forgot password?
              </button>
            )}
            <div className="auth-switch">
              {isRegister ? 'Already have an account?' : 'New to VEIL Guard?'}
              <button
                type="button"
                onClick={() => { setMode(isRegister ? 'login' : 'register'); setError(''); setNotice('') }}
              >
                {isRegister ? 'Sign in' : 'Create an account'}
              </button>
            </div>
          </>
        )}
        <p className="auth-footnote">
          Signing in is optional. Local protection setup does not require a VEIL Cloud account.
        </p>
      </section>
  )
}
