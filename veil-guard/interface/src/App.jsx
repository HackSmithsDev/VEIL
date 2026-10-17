import { useState } from 'react'
import './App.css'
import AppShell from './components/layout/AppShell'
import { useCloudSession } from './hooks/useCloudSession'
import AuthPage from './pages/AuthPage'
import DashboardPage from './pages/DashboardPage'
import FeedbackPage from './pages/FeedbackPage'
import ProfilePage from './pages/ProfilePage'
import ProgramsPage from './pages/ProgramsPage'

export default function App() {
  const [page, setPage] = useState('dashboard')
  const session = useCloudSession()

  if (!session.isAuthenticated) {
    return <AuthPage onLogin={session.login} onRegister={session.register} />
  }

  const pageContent = {
    dashboard: <DashboardPage user={session.user} request={session.request} onNavigate={setPage} />,
    programs: <ProgramsPage request={session.request} />,
    profile: <ProfilePage user={session.user} request={session.request} onUserUpdated={session.updateUser} />,
    feedback: <FeedbackPage request={session.request} />,
  }[page]

  return (
    <AppShell page={page} onNavigate={setPage} onLogout={session.logout} user={session.user}>
      {pageContent}
    </AppShell>
  )
}
