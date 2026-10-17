const navigation = [
  { id: 'dashboard', label: 'Overview', icon: 'OV' },
  { id: 'programs', label: 'My programs', icon: 'PR' },
  { id: 'profile', label: 'Profile', icon: 'ME' },
  { id: 'feedback', label: 'Feedback', icon: 'FB' },
]

export default function AppShell({ page, onNavigate, onLogout, user, children }) {
  const initials = user.full_name
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase()

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#" onClick={(event) => { event.preventDefault(); onNavigate('dashboard') }}>
          <span className="brand-mark">V</span>
          <span className="brand-name">VEIL<span>GUARD</span></span>
        </a>

        <div className="workspace-label">WORKSPACE</div>
        <nav className="main-nav" aria-label="Main navigation">
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
              {page === item.id && <span className="nav-indicator" />}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="connection-card">
            <span className="connection-dot" />
            <div>
              <strong>Signed-in account</strong>
              <small>VEIL Cloud profile loaded</small>
            </div>
          </div>
          <div className="user-card">
            <span className="avatar">{initials || 'VG'}</span>
            <span className="user-card-copy">
              <strong>{user.full_name}</strong>
              <small>{user.email}</small>
            </span>
            <button className="icon-button" type="button" onClick={onLogout} aria-label="Sign out" title="Sign out">
              ↗
            </button>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb"><span>VEIL Guard</span><b>/</b>{navigation.find((item) => item.id === page)?.label}</div>
          <div className="topbar-right">
            <span className="local-badge"><span />Desktop workspace</span>
            <span className="topbar-avatar">{initials || 'VG'}</span>
          </div>
        </header>
        <div className="page-content">{children}</div>
        <footer className="app-footer">
          <span>VEIL Guard <span className="footer-version">v0.1 · Early access</span></span>
          <span>Program details only · No source code stored</span>
        </footer>
      </main>
    </div>
  )
}
