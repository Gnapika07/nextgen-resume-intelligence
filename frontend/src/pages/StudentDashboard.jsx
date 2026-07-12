import { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import api from '../services/api';
import {
  RadarChart, Radar, PolarGrid,
  PolarAngleAxis, ResponsiveContainer, Tooltip
} from 'recharts';

const s = {
  page: { minHeight: '100vh', background: '#f8fafc' },
  container: { maxWidth: 1100, margin: '0 auto', padding: '24px 16px' },
  card: {
    background: 'white', borderRadius: 16,
    border: '1px solid #e2e8f0',
    boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
    padding: 20, marginBottom: 16
  },
  input: {
    width: '100%', padding: '10px 14px',
    border: '1.5px solid #e2e8f0', borderRadius: 10,
    fontSize: 14, outline: 'none',
    boxSizing: 'border-box', marginBottom: 10
  },
  tag: (bg, color) => ({
    background: bg, color,
    fontSize: 12, padding: '4px 10px',
    borderRadius: 999, fontWeight: 500,
    border: `1px solid ${color}30`
  })
};

export default function StudentDashboard() {
  const [resume, setResume] = useState(null);
  const [result, setResult] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [msg, setMsg] = useState('');
  const [jdForm, setJdForm] = useState({
    title: '', description_text: '',
    required_skills: '', required_experience: ''
  });

  useEffect(() => { loadResume(); }, []);

  const loadResume = async () => {
    try {
      const res = await api.get('/student/my-resume');
      setResume(res.data);
    } catch (e) {}
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setMsg('');
    try {
      const fd = new FormData();
      fd.append('file', file);
      const res = await api.post('/student/upload-resume', fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResume(res.data);
      setMsg('✅ Resume uploaded!');
    } catch (e) {
      setMsg('❌ ' + (e.response?.data?.detail || e.message));
    } finally { setUploading(false); }
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!resume) { setMsg('❌ Upload resume first'); return; }
    setAnalyzing(true);
    setMsg('');
    try {
      const skills = jdForm.required_skills.split(',').map(s => s.trim()).filter(Boolean);
      const res = await api.post('/student/analyze', {
        ...jdForm, required_skills: skills
      });
      setResult(res.data);
      setMsg('✅ Analysis complete!');
    } catch (e) {
      setMsg('❌ ' + (e.response?.data?.detail || e.message));
    } finally { setAnalyzing(false); }
  };

  const scoreColor = (score) =>
    score >= 80 ? '#059669' : score >= 60 ? '#2563eb' : score >= 40 ? '#d97706' : '#dc2626';

  const scoreBg = (score) =>
    score >= 80 ? '#f0fdf4' : score >= 60 ? '#eff6ff' : score >= 40 ? '#fffbeb' : '#fef2f2';

  const radarData = result ? [
    { subject: 'Skills', score: result.skills_score },
    { subject: 'Experience', score: result.experience_score },
    { subject: 'Keywords', score: result.keyword_score },
    { subject: 'Overall', score: result.overall_score },
  ] : [];

  return (
    <div style={s.page}>
      <Navbar />
      <div style={s.container}>

        {msg && (
          <div style={{
            padding: '12px 16px', borderRadius: 10, marginBottom: 16,
            background: msg.startsWith('✅') ? '#f0fdf4' : '#fef2f2',
            color: msg.startsWith('✅') ? '#15803d' : '#dc2626',
            fontSize: 14, border: `1px solid ${msg.startsWith('✅') ? '#bbf7d0' : '#fecaca'}`
          }}>{msg}</div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: '340px 1fr', gap: 20 }}>

          {/* LEFT PANEL */}
          <div>
            {/* Resume Upload */}
            <div style={s.card}>
              <p style={{ fontWeight: 700, fontSize: 15, color: '#1e293b', marginBottom: 16 }}>
                📄 Your Resume
              </p>

              {resume && (
                <div style={{
                  background: '#f0fdf4', border: '1px solid #bbf7d0',
                  borderRadius: 12, padding: 12, marginBottom: 12
                }}>
                  <p style={{ fontWeight: 600, fontSize: 14, color: '#15803d' }}>
                    ✅ {resume.candidate_name || resume.filename}
                  </p>
                  <p style={{ fontSize: 12, color: '#16a34a', marginTop: 4 }}>
                    {resume.skills?.length} skills · {resume.experience_years}y exp
                  </p>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 8 }}>
                    {resume.skills?.slice(0, 6).map(sk => (
                      <span key={sk} style={s.tag('#dcfce7', '#15803d')}>{sk}</span>
                    ))}
                  </div>
                </div>
              )}

              <label style={{
                display: 'block', width: '100%', textAlign: 'center',
                padding: '10px', background: '#2563eb', color: 'white',
                borderRadius: 10, fontWeight: 600, fontSize: 14,
                cursor: 'pointer', boxSizing: 'border-box'
              }}>
                {uploading ? 'Uploading...' : resume ? '🔄 Replace Resume' : '📤 Upload Resume'}
                <input
                  type="file" accept=".pdf,.docx"
                  onChange={handleUpload} style={{ display: 'none' }}
                />
              </label>
            </div>

            {/* JD Form */}
            <div style={s.card}>
              <p style={{ fontWeight: 700, fontSize: 15, color: '#1e293b', marginBottom: 16 }}>
                🎯 Analyze Against Job
              </p>
              <form onSubmit={handleAnalyze}>
                <input
                  style={s.input} placeholder="Job Title *"
                  value={jdForm.title}
                  onChange={e => setJdForm({...jdForm, title: e.target.value})}
                  required
                  onFocus={e => e.target.style.borderColor = '#3b82f6'}
                  onBlur={e => e.target.style.borderColor = '#e2e8f0'}
                />
                <textarea
                  style={{ ...s.input, height: 120, resize: 'none' }}
                  placeholder="Paste job description here... *"
                  value={jdForm.description_text}
                  onChange={e => setJdForm({...jdForm, description_text: e.target.value})}
                  required
                  onFocus={e => e.target.style.borderColor = '#3b82f6'}
                  onBlur={e => e.target.style.borderColor = '#e2e8f0'}
                />
                <input
                  style={s.input}
                  placeholder="Required Skills (Python, SQL)"
                  value={jdForm.required_skills}
                  onChange={e => setJdForm({...jdForm, required_skills: e.target.value})}
                  onFocus={e => e.target.style.borderColor = '#3b82f6'}
                  onBlur={e => e.target.style.borderColor = '#e2e8f0'}
                />
                <input
                  style={s.input}
                  placeholder="Experience (e.g. 1-3 years)"
                  value={jdForm.required_experience}
                  onChange={e => setJdForm({...jdForm, required_experience: e.target.value})}
                  onFocus={e => e.target.style.borderColor = '#3b82f6'}
                  onBlur={e => e.target.style.borderColor = '#e2e8f0'}
                />
                <button
                  type="submit"
                  disabled={analyzing || !resume}
                  style={{
                    width: '100%', padding: 12,
                    background: analyzing || !resume ? '#93c5fd' : '#2563eb',
                    color: 'white', border: 'none', borderRadius: 10,
                    fontWeight: 700, fontSize: 14,
                    cursor: analyzing || !resume ? 'not-allowed' : 'pointer'
                  }}
                >
                  {analyzing ? '⏳ Analyzing...' : '🔍 Analyze My Resume'}
                </button>
              </form>
            </div>
          </div>

          {/* RIGHT PANEL */}
          <div>
            {result ? (
              <>
                {/* Score Hero */}
                <div style={{
                  ...s.card,
                  background: scoreBg(result.overall_score),
                  border: `1px solid ${scoreColor(result.overall_score)}30`
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <p style={{ fontSize: 22, fontWeight: 800, color: '#1e293b' }}>
                        {result.job_title}
                      </p>
                      <p style={{ fontSize: 13, color: '#64748b', marginTop: 4 }}>
                        ATS Resume Match Analysis
                      </p>
                      <span style={{
                        display: 'inline-block', marginTop: 12,
                        padding: '6px 16px', borderRadius: 999,
                        fontWeight: 700, fontSize: 13,
                        background: scoreColor(result.overall_score),
                        color: 'white'
                      }}>
                        {result.score_label}
                      </span>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                      <p style={{
                        fontSize: 64, fontWeight: 900,
                        color: scoreColor(result.overall_score),
                        lineHeight: 1
                      }}>
                        {result.overall_score?.toFixed(0)}
                      </p>
                      <p style={{ fontSize: 12, color: '#94a3b8' }}>out of 100</p>
                    </div>
                  </div>
                  <p style={{
                    marginTop: 16, fontSize: 13,
                    color: '#475569', fontStyle: 'italic',
                    background: 'rgba(255,255,255,0.6)',
                    padding: '10px 14px', borderRadius: 10
                  }}>
                    💡 {result.ats_tip}
                  </p>
                </div>

                {/* Score Breakdown + Radar */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
                  <div style={s.card}>
                    <p style={{ fontWeight: 700, fontSize: 14, color: '#1e293b', marginBottom: 16 }}>
                      Score Breakdown
                    </p>
                    {[
                      { label: 'Skills Match (40%)', score: result.skills_score, color: '#3b82f6' },
                      { label: 'Experience (25%)', score: result.experience_score, color: '#10b981' },
                      { label: 'Keywords (20%)', score: result.keyword_score, color: '#8b5cf6' },
                    ].map(item => (
                      <div key={item.label} style={{ marginBottom: 14 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: '#64748b', marginBottom: 4 }}>
                          <span>{item.label}</span>
                          <span style={{ fontWeight: 700, color: item.color }}>
                            {item.score?.toFixed(1)}
                          </span>
                        </div>
                        <div style={{ height: 8, background: '#f1f5f9', borderRadius: 4 }}>
                          <div style={{
                            height: '100%', borderRadius: 4,
                            background: item.color,
                            width: `${Math.min(item.score, 100)}%`,
                            transition: 'width 0.8s ease'
                          }} />
                        </div>
                      </div>
                    ))}
                  </div>

                  <div style={s.card}>
                    <p style={{ fontWeight: 700, fontSize: 14, color: '#1e293b', marginBottom: 8 }}>
                      Skill Radar Chart
                    </p>
                    <ResponsiveContainer width="100%" height={160}>
                      <RadarChart data={radarData}>
                        <PolarGrid />
                        <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11 }} />
                        <Radar
                          dataKey="score" stroke="#3b82f6"
                          fill="#3b82f6" fillOpacity={0.25}
                        />
                        <Tooltip />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Skills Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
                  <div style={s.card}>
                    <p style={{ fontWeight: 700, fontSize: 14, color: '#1e293b', marginBottom: 12 }}>
                      ✅ Matched Skills
                    </p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                      {result.matched_skills?.length > 0
                        ? result.matched_skills.map(sk => (
                            <span key={sk} style={s.tag('#dcfce7', '#15803d')}>✓ {sk}</span>
                          ))
                        : <p style={{ fontSize: 13, color: '#94a3b8' }}>No exact matches</p>
                      }
                    </div>
                  </div>

                  <div style={s.card}>
                    <p style={{ fontWeight: 700, fontSize: 14, color: '#1e293b', marginBottom: 12 }}>
                      ❌ Missing Skills
                    </p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                      {result.missing_skills?.length > 0
                        ? result.missing_skills.map(sk => (
                            <span key={sk} style={s.tag('#fee2e2', '#dc2626')}>✗ {sk}</span>
                          ))
                        : <p style={{ fontSize: 13, color: '#15803d', fontWeight: 600 }}>
                            🎉 All skills matched!
                          </p>
                      }
                    </div>
                  </div>
                </div>

                {/* Suggestions */}
                <div style={s.card}>
                  <p style={{ fontWeight: 700, fontSize: 14, color: '#1e293b', marginBottom: 12 }}>
                    💡 Improvement Suggestions
                  </p>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {result.suggestions?.map((sg, i) => (
                      <div key={i} style={{
                        display: 'flex', gap: 10,
                        background: '#f8fafc', borderRadius: 10,
                        padding: '10px 14px', fontSize: 13, color: '#374151'
                      }}>
                        <span style={{ color: '#3b82f6', fontWeight: 700 }}>→</span>
                        {sg}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recommended Roles */}
                {result.recommended_roles?.length > 0 && (
                  <div style={s.card}>
                    <p style={{ fontWeight: 700, fontSize: 14, color: '#1e293b', marginBottom: 12 }}>
                      🚀 Recommended Job Roles For You
                    </p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                      {result.recommended_roles.map(role => (
                        <span key={role} style={s.tag('#ede9fe', '#7c3aed')}>
                          {role}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div style={{
                ...s.card,
                display: 'flex', flexDirection: 'column',
                alignItems: 'center', justifyContent: 'center',
                minHeight: 400, color: '#94a3b8', textAlign: 'center'
              }}>
                <div style={{ fontSize: 80, marginBottom: 16 }}>🎯</div>
                <p style={{ fontWeight: 700, fontSize: 16, color: '#64748b' }}>
                  No analysis yet
                </p>
                <p style={{ fontSize: 13, marginTop: 8, maxWidth: 300 }}>
                  Upload your resume and paste a job description on the left to get your ATS score
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}