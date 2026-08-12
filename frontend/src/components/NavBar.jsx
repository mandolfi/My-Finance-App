import { Link, useLocation } from 'react-router-dom'

function NavBar() {
  const location = useLocation()

  const linkStyle = (path) => ({
    padding: '10px 16px',
    textDecoration: 'none',
    color: location.pathname === path ? '#1B3A36' : '#888',
    fontWeight: location.pathname === path ? 600 : 400,
    borderBottom: location.pathname === path ? '2px solid #1B3A36' : '2px solid transparent',
  })

  return (
    <nav style={{ display: 'flex', gap: '8px', borderBottom: '1px solid #ddd', marginBottom: '24px' }}>
      <Link to="/" style={linkStyle('/')}>Cockpit</Link>
      <Link to="/mensile" style={linkStyle('/mensile')}>Report Mensile</Link>
      <Link to="/annuale" style={linkStyle('/annuale')}>Report Annuale</Link>
      <Link to="/storico" style={linkStyle('/storico')}>Storico</Link>
    </nav>
  )
}

export default NavBar