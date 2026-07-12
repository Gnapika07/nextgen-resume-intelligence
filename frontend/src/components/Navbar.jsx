import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav style={{
      background: 'white',
      borderBottom: '1px solid #e2e8f0',
      padding: '16px 24px',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{
          background: '#2563eb',
          borderRadius: 10,
          width: 36, height: 36,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: 'white', fontWeight: 'bold', fontSize: 16
        }}>AI</div>
        <span style={{ fontSize: 18, fontWeight: 700, color: '#1e293b' }}>
          NextGen Resume AI
        </span>
      </div>

      {user && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <span style={{ fontSize: 14, color: '#64748b' }}>
            {user.full_name}
            <span style={{
              marginLeft: 8,
              padding: '2px 10px',
              borderRadius: 999,
              fontSize: 11,
              fontWeight: 600,
              background: user.role === 'hr' ? '#dbeafe' : '#dcfce7',
              color: user.role === 'hr' ? '#1d4ed8' : '#15803d'
            }}>
              {user.role === 'hr' ? 'HR' : 'Student'}
            </span>
          </span>
          <button
            onClick={logout}
            style={{
              background: 'none', border: '1px solid #e2e8f0',
              borderRadius: 8, padding: '6px 14px',
              fontSize: 13, color: '#64748b', cursor: 'pointer'
            }}
          >
            Logout
          </button>
        </div>
      )}
    </nav>
  );
}