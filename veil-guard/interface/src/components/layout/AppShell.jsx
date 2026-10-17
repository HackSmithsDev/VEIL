const navigation = [
  { id: 'protection', label: 'Protection', icon: 'PR' },
  { id: 'setup', label: 'Setup', icon: 'ST' },
  { id: 'programs', label: 'Program Catalog', icon: 'PC' },
  { id: 'account', label: 'Account', icon: 'AC' },
  { id: 'settings', label: 'Settings', icon: 'CF' },
  { id: 'feedback', label: 'Feedback', icon: 'FB' },
]

export default function AppShell({ page, onNavigate, onLogout, user, children }) {
  const initials = user?.full_name
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase()

  return (
    <div className="app-shell">
      <header className="utility-header">
        <a className="brand" href="#" onClick={(event) => { event.preventDefault(); onNavigate('protection') }}>
          <span className="brand-mark">V</span>
          <span className="brand-name">VEIL<span>GUARD</span></span>
        </a>
        <div className="utility-account">
          {user ? (
            <>
              <span className="avatar">{initials || 'VG'}</span>
              <span className="utility-account-copy">{user.full_name}</span>
              <button className="icon-button" type="button" onClick={onLogout} aria-label="Sign out" title="Sign out">↗</button>
            </>
          ) : <span className="local-mode-label">Local mode</span>}
        </div>
      </header>
      <nav className="utility-nav" aria-label="Main navigation">
          {navigation.map((item) => (
            <button
              className={`nav-item ${page === item.id ? 'active' : ''}`}
              key={item.id}
              type="button"
              onClick={() => onNavigate(item.id)}
              aria-current={page === item.id ? 'page' : undefined}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
      </nav>

      <main className="main-content">
        <div className="page-content">{children}</div>
        <footer className="app-footer">
          <span className="engine-state"><span /> Protection off</span>
          <span>VEIL Guard</span>
        </footer>
      </main>
    </div>
  )
}
