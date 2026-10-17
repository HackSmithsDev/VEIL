import { useCallback, useState } from 'react'
import './App.css'
import AppShell from './components/layout/AppShell'
import CloudAccessModal from './components/CloudAccessModal'
import { useCloudSession } from './hooks/useCloudSession'
import AccountPage from './pages/AccountPage'
import AuthPage from './pages/AuthPage'
import DashboardPage from './pages/DashboardPage'
import FeedbackPage from './pages/FeedbackPage'
import ProfilePage from './pages/ProfilePage'
import ProgramsPage from './pages/ProgramsPage'
import SettingsPage from './pages/SettingsPage'
import SetupPage from './pages/SetupPage'

export default function App() {
  const [page, setPage] = useState('protection')
  const [afterAuthentication, setAfterAuthentication] = useState('account')
  const [isCloudAccessOpen, setIsCloudAccessOpen] = useState(false)
  const session = useCloudSession()

  const closeCloudAccess = useCallback(() => setIsCloudAccessOpen(false), [])

  function openCloudAccess(returnPage = 'account') {
    setAfterAuthentication(returnPage)
    setPage('account')
    setIsCloudAccessOpen(true)
  }

  function navigate(target) {
    if (
      !session.isAuthenticated &&
      ['programs', 'feedback'].includes(target)
    ) {
      setAfterAuthentication(target)
    }
    setIsCloudAccessOpen(false)
    setPage(target)
  }

  function authenticate(action) {
    return async (details) => {
      await action(details)
      setPage(afterAuthentication)
      setIsCloudAccessOpen(false)
    }
  }

  function signOut() {
    session.logout()
    setAfterAuthentication('account')
    closeCloudAccess()
    setPage('account')
  }

  const pageContent = {
    protection: <DashboardPage onNavigate={navigate} />,
    setup: <SetupPage onNavigate={navigate} />,
    settings: <SettingsPage />,
    account: session.isAuthenticated
      ? <ProfilePage user={session.user} request={session.request} onUserUpdated={session.updateUser} />
      : <AccountPage onAccessCloud={() => openCloudAccess()} />,
    programs: session.isAuthenticated
      ? <ProgramsPage request={session.request} />
      : <CloudAccountGate
          feature="program catalog"
          onSignIn={() => openCloudAccess('programs')}
        />,
    feedback: session.isAuthenticated
      ? <FeedbackPage request={session.request} />
      : <CloudAccountGate
          feature="feedback"
          onSignIn={() => openCloudAccess('feedback')}
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
      {isCloudAccessOpen && (
        <CloudAccessModal onClose={closeCloudAccess}>
          <AuthPage
            onLogin={authenticate(session.login)}
            onRegister={authenticate(session.register)}
            onRequestPasswordReset={session.requestPasswordReset}
            onConfirmPasswordReset={session.confirmPasswordReset}
          />
        </CloudAccessModal>
      )}
    </AppShell>
  )
}

function CloudAccountGate({ feature, onSignIn }) {
  return (
    <section className="cloud-account-gate">
      <span className="setup-status-icon" aria-hidden="true">↗</span>
      <div>
        <div className="eyebrow">OPTIONAL VEIL CLOUD</div>
        <h1>Sign in for {feature}</h1>
        <p>This feature uses VEIL Cloud. Signing in is optional; local protection and setup remain available without an account.</p>
        <button className="button button-primary" type="button" onClick={onSignIn}>Sign in or create account</button>
      </div>
    </section>
  )
}
