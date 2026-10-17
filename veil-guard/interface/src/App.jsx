import { useState } from 'react'
import './App.css'
import AppShell from './components/layout/AppShell'
import { useCloudSession } from './hooks/useCloudSession'
import AuthPage from './pages/AuthPage'
import DashboardPage from './pages/DashboardPage'
import FeedbackPage from './pages/FeedbackPage'
import ProfilePage from './pages/ProfilePage'
import ProgramsPage from './pages/ProgramsPage'
import SetupPage from './pages/SetupPage'

export default function App() {
  const [page, setPage] = useState('protection')
  const [afterAuthentication, setAfterAuthentication] = useState('protection')
  const session = useCloudSession()

  function navigate(target) {
    if (target === 'account' && !session.isAuthenticated) {
      setAfterAuthentication('account')
    }
    setPage(target)
  }

  function authenticate(action) {
    return async (details) => {
      await action(details)
      setPage(afterAuthentication)
    }
  }

  function signOut() {
    session.logout()
    setPage('protection')
  }

  const pageContent = {
    protection: <DashboardPage onNavigate={navigate} />,
    setup: <SetupPage />,
    programs: session.isAuthenticated
      ? <ProgramsPage request={session.request} />
      : <CloudAccountGate
          onSignIn={() => {
            setAfterAuthentication('programs')
            setPage('account')
          }}
          feature="program metadata"
        />,
    account: session.isAuthenticated
      ? <ProfilePage user={session.user} request={session.request} onUserUpdated={session.updateUser} />
      : <AuthPage
          onLogin={authenticate(session.login)}
          onRegister={authenticate(session.register)}
        />,
    feedback: session.isAuthenticated
      ? <FeedbackPage request={session.request} />
      : <CloudAccountGate
          onSignIn={() => {
            setAfterAuthentication('feedback')
            setPage('account')
          }}
          feature="feedback"
        />,
  }[page]

  return (
    <AppShell
      page={page}
      onNavigate={navigate}
      onLogout={signOut}
      user={session.user}
    >
      {pageContent}
    </AppShell>
  )
}

function CloudAccountGate({ onSignIn, feature }) {
  return (
    <section className="cloud-account-gate">
      <span className="setup-status-icon" aria-hidden="true">↗</span>
      <div>
        <div className="eyebrow">VEIL CLOUD ACCOUNT</div>
        <h1>Sign in to use {feature}</h1>
        <p>This feature uses VEIL Cloud. Signing in is optional; local protection and setup remain available without an account.</p>
        <button className="button button-primary" type="button" onClick={onSignIn}>Sign in or create account</button>
      </div>
    </section>
  )
}
