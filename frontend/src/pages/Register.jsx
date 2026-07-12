import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Register() {
  const [form, setForm] = useState({ email: '', fullName: '', password: '', role: 'student' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register(form.email, form.fullName, form.password, form.role);
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = {
    width: '100%', padding: '10px 14px',
    border: '1.5px solid #e2e8f0', borderRadius: 10,
    fontSize: 14, outline: 'none', boxSizing: 'border-box'
  };

  const labelStyle = {
    fontSize: 13, fontWeight: 600,
    color: '#374151', display: 'block', marginBottom: 6
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #eff6ff 0%, #e0e7ff 100%)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 16
    }}>
      <div style={{
        background: 'white', borderRadius: 20,
        boxShadow: '0 20px 60px rgba(0,0,0,0.1)',
        width: '100%', maxWidth: 420, padding: 40
      }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div style={{
            background: '#2563eb', borderRadius: 16,
            width: 60, height: 60, margin: '0 auto 16px',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 24, color: 'white', fontWeight: 'bold'
          }}>AI</div>
          <h1 style={{ fontSize: 24, fontWeight: 700, color: '#1e293b' }}>Create Account</h1>
          <p style={{ color: '#94a3b8', fontSize: 14, marginTop: 4 }}>Join NextGen Resume AI</p>
        </div>

        {error && (
          <div style={{
            background: '#fef2f2', border: '1px solid #fecaca',
            borderRadius: 10, padding: '12px 16px',
            color: '#dc2626', fontSize: 14, marginBottom: 20
          }}>{error}</div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 16 }}>
            <label style={labelStyle}>Full Name</label>
            <input
              type="text"
              value={form.fullName}
              onChange={e => setForm({...form, fullName: e.target.value})}
              placeholder="Your full name"
              required
              style={inputStyle}
              onFocus={e => e.target.style.borderColor = '#3b82f6'}
              onBlur={e => e.target.style.borderColor = '#e2e8f0'}
            />
          </div>

          <div style={{ marginBottom: 16 }}>
            <label style={labelStyle}>Email</label>
            <input
              type="email"
              value={form.email}
              onChange={e => setForm({...form, email: e.target.value})}
              placeholder="you@example.com"
              required
              style={inputStyle}
              onFocus={e => e.target.style.borderColor = '#3b82f6'}
              onBlur={e => e.target.style.borderColor = '#e2e8f0'}
            />
          </div>

          <div style={{ marginBottom: 16 }}>
            <label style={labelStyle}>Password</label>
            <input
              type="password"
              value={form.password}
              onChange={e => setForm({...form, password: e.target.value})}
              placeholder="••••••••"
              required
              style={inputStyle}
              onFocus={e => e.target.style.borderColor = '#3b82f6'}
              onBlur={e => e.target.style.borderColor = '#e2e8f0'}
            />
          </div>

          <div style={{ marginBottom: 24 }}>
            <label style={labelStyle}>I am a...</label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              {['student', 'hr'].map(r => (
                <button
                  key={r}
                  type="button"
                  onClick={() => setForm({...form, role: r})}
                  style={{
                    padding: '12px',
                    border: `2px solid ${form.role === r ? '#2563eb' : '#e2e8f0'}`,
                    borderRadius: 10,
                    background: form.role === r ? '#eff6ff' : 'white',
                    color: form.role === r ? '#1d4ed8' : '#64748b',
                    fontSize: 14, fontWeight: 600, cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  {r === 'student' ? '🎓 Student' : '👔 HR Recruiter'}
                </button>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%', padding: 12,
              background: loading ? '#93c5fd' : '#2563eb',
              color: 'white', border: 'none', borderRadius: 10,
              fontSize: 15, fontWeight: 600,
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? 'Creating...' : 'Create Account'}
          </button>
        </form>

        <p style={{ textAlign: 'center', fontSize: 14, color: '#94a3b8', marginTop: 24 }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: '#2563eb', fontWeight: 600, textDecoration: 'none' }}>
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}