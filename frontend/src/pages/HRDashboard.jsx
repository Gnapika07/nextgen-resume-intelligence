import { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import api from '../services/api';
import {
  BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';

const s = {
  page: { minHeight: '100vh', background: '#f8fafc' },
  container: { maxWidth: 1200, margin: '0 auto', padding: '24px 16px' },
  card: {
    background: 'white', borderRadius: 16,
    border: '1px solid #e2e8f0',
    boxShadow: '0 1px 3px rgba(0,0,0,0.06)'
  },
  statCard: {
    background: 'white', borderRadius: 16,
    border: '1px solid #e2e8f0', padding: 24,
    boxShadow: '0 1px 3px rgba(0,0,0,0.06)'
  },
  btn: (color = '#2563eb') => ({
    background: color, color: 'white',
    border: 'none', borderRadius: 10,
    padding: '10px 20px', fontSize: 14,
    fontWeight: 600, cursor: 'pointer'
  }),
  input: {
    width: '100%', padding: '10px 14px',
    border: '1.5px solid #e2e8f0',
    borderRadius: 10, fontSize: 14,
    outline: 'none', boxSizing: 'border-box',
    marginBottom: 12
  },
  tag: (color) => ({
    background: color + '15',
    color: color,
    fontSize: 11, padding: '3px 8px',
    borderRadius: 999, fontWeight: 500
  })
};

export default function HRDashboard() {
  const [tab, setTab] = useState('upload');
  const [resumes, setResumes] = useState([]);
  const [jds, setJds] = useState([]);
  const [results, setResults] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [msg, setMsg] = useState('');
  const [jdForm, setJdForm] = useState({
    title: '', company: '',
    description_text: '',
    required_skills: '',
    required_experience: ''
  });

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [r, j] = await Promise.all([
        api.get('/hr/resumes'),
        api.get('/hr/job-descriptions')
      ]);
      setResumes(r.data);
      setJds(j.data);
    } catch (e) {}
  };

  const handleUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (!files.length) return;
    setUploading(true);
    setMsg('');
    try {
      const fd = new FormData();
      files.forEach(f => fd.append('files', f));
      const res = await api.post('/hr/upload-resumes', fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setMsg(`✅ Uploaded ${res.data.successful} resumes! Duplicates: ${res.data.duplicates}`);
      loadData();
    } catch (e) {
      setMsg('❌ ' + (e.response?.data?.detail || e.message));
    } finally { setUploading(false); }
  };

  const handleCreateJD = async (e) => {
    e.preventDefault();
    try {
      const skills = jdForm.required_skills.split(',').map(s => s.trim()).filter(Boolean);
      await api.post('/hr/upload-jd', { ...jdForm, required_skills: skills });
      setMsg('✅ Job Description created!');
      setJdForm({ title: '', company: '', description_text: '', required_skills: '', required_experience: '' });
      loadData();
    } catch (e) {
      setMsg('❌ ' + (e.response?.data?.detail || e.message));
    }
  };

  const handleExport = async (jdId) => {
  alert("CSV button clicked");

  try {
    const token = localStorage.getItem("access_token");

    const response = await fetch(
      `http://localhost:8000/api/hr/export/${jdId}`,
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    );

    const blob = await response.blob();

    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `results_jd_${jdId}.csv`;
    a.click();

    window.URL.revokeObjectURL(url);

  } catch (error) {
    console.error(error);
  }
};

const handleAnalyze = async (jdId) => {
  setAnalyzing(true);
  setMsg('Analyzing resumes...');

  try {
    await api.post('/hr/analyze', {
      jd_id: jdId
    });

    const res = await api.get(`/hr/results/${jdId}`);

    setResults(res.data);
    setMsg('✅ Analysis complete!');
    setTab('results');

  } catch (e) {
    setMsg('❌ ' + (e.response?.data?.detail || e.message));

  } finally {
    setAnalyzing(false);
  }
};

  const tabs = [
    { id: 'upload', label: '📄 Resumes' },
    { id: 'jd', label: '📋 Job Description' },
    { id: 'results', label: '📊 Results' },
  ];

  return (
    <div style={s.page}>
      <Navbar />
      <div style={s.container}>

        {/* Stats */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 16, marginBottom: 24 }}>
          {[
            { label: 'Resumes', value: resumes.length, color: '#2563eb' },
            { label: 'Job Descriptions', value: jds.length, color: '#059669' },
            { label: 'Ranked Candidates', value: results.length, color: '#7c3aed' },
          ].map(stat => (
            <div key={stat.label} style={s.statCard}>
              <p style={{ fontSize: 13, color: '#94a3b8' }}>{stat.label}</p>
              <p style={{ fontSize: 36, fontWeight: 800, color: stat.color, marginTop: 4 }}>
                {stat.value}
              </p>
            </div>
          ))}
        </div>

        {/* Message */}
        {msg && (
          <div style={{
            padding: '12px 16px', borderRadius: 10, marginBottom: 16,
            background: msg.startsWith('✅') ? '#f0fdf4' : msg.startsWith('❌') ? '#fef2f2' : '#eff6ff',
            color: msg.startsWith('✅') ? '#15803d' : msg.startsWith('❌') ? '#dc2626' : '#1d4ed8',
            border: `1px solid ${msg.startsWith('✅') ? '#bbf7d0' : msg.startsWith('❌') ? '#fecaca' : '#bfdbfe'}`,
            fontSize: 14
          }}>{msg}</div>
        )}

        {/* Tabs */}
        <div style={s.card}>
          <div style={{ display: 'flex', borderBottom: '1px solid #f1f5f9' }}>
            {tabs.map(t => (
              <button key={t.id} onClick={() => setTab(t.id)} style={{
                padding: '16px 24px', border: 'none', background: 'none',
                fontSize: 14, fontWeight: 600, cursor: 'pointer',
                color: tab === t.id ? '#2563eb' : '#94a3b8',
                borderBottom: tab === t.id ? '2px solid #2563eb' : '2px solid transparent',
                transition: 'all 0.2s'
              }}>{t.label}</button>
            ))}
          </div>

          <div style={{ padding: 24 }}>

            {/* Upload Tab */}
            {tab === 'upload' && (
              <div>
                <div style={{
                  border: '2px dashed #e2e8f0', borderRadius: 16,
                  padding: 48, textAlign: 'center', marginBottom: 24
                }}>
                  <div style={{ fontSize: 48, marginBottom: 12 }}>📁</div>
                  <p style={{ fontWeight: 600, color: '#374151', marginBottom: 4 }}>
                    Upload Resumes (PDF / DOCX)
                  </p>
                  <p style={{ fontSize: 13, color: '#94a3b8', marginBottom: 20 }}>
                    Up to 100 files at once
                  </p>
                  <label style={{ ...s.btn(), padding: '10px 28px', borderRadius: 10, cursor: 'pointer' }}>
                    {uploading ? 'Uploading...' : 'Choose Files'}
                    <input
                      type="file" multiple accept=".pdf,.docx"
                      onChange={handleUpload} style={{ display: 'none' }}
                    />
                  </label>
                </div>

                {resumes.length > 0 && (
                  <div>
                    <p style={{ fontWeight: 600, color: '#374151', marginBottom: 12 }}>
                      Uploaded Resumes ({resumes.length})
                    </p>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                      {resumes.map(r => (
                        <div key={r.id} style={{
                          display: 'flex', justifyContent: 'space-between',
                          alignItems: 'center', background: '#f8fafc',
                          borderRadius: 12, padding: '12px 16px',
                          border: '1px solid #f1f5f9'
                        }}>
                          <div>
                            <p style={{ fontWeight: 600, fontSize: 14, color: '#1e293b' }}>
                              {r.candidate_name || r.filename}
                            </p>
                            <p style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>
                              {r.skills?.slice(0, 4).join(' · ')}
                            </p>
                          </div>
                          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                            <span style={s.tag('#2563eb')}>{r.experience_years}y exp</span>
                            {r.is_duplicate === 'yes' && (
                              <span style={s.tag('#f59e0b')}>Duplicate</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* JD Tab */}
            {tab === 'jd' && (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32 }}>
                <div>
                  <p style={{ fontWeight: 700, fontSize: 16, color: '#1e293b', marginBottom: 20 }}>
                    Create Job Description
                  </p>
                  <form onSubmit={handleCreateJD}>
                    <input
                      style={s.input} placeholder="Job Title *"
                      value={jdForm.title}
                      onChange={e => setJdForm({...jdForm, title: e.target.value})}
                      required
                      onFocus={e => e.target.style.borderColor = '#3b82f6'}
                      onBlur={e => e.target.style.borderColor = '#e2e8f0'}
                    />
                    <input
                      style={s.input} placeholder="Company Name"
                      value={jdForm.company}
                      onChange={e => setJdForm({...jdForm, company: e.target.value})}
                      onFocus={e => e.target.style.borderColor = '#3b82f6'}
                      onBlur={e => e.target.style.borderColor = '#e2e8f0'}
                    />
                    <textarea
                      style={{ ...s.input, height: 140, resize: 'none' }}
                      placeholder="Paste full job description here... *"
                      value={jdForm.description_text}
                      onChange={e => setJdForm({...jdForm, description_text: e.target.value})}
                      required
                      onFocus={e => e.target.style.borderColor = '#3b82f6'}
                      onBlur={e => e.target.style.borderColor = '#e2e8f0'}
                    />
                    <input
                      style={s.input}
                      placeholder="Required Skills (Python, SQL, React)"
                      value={jdForm.required_skills}
                      onChange={e => setJdForm({...jdForm, required_skills: e.target.value})}
                      onFocus={e => e.target.style.borderColor = '#3b82f6'}
                      onBlur={e => e.target.style.borderColor = '#e2e8f0'}
                    />
                    <input
                      style={s.input}
                      placeholder="Required Experience (e.g. 2-4 years)"
                      value={jdForm.required_experience}
                      onChange={e => setJdForm({...jdForm, required_experience: e.target.value})}
                      onFocus={e => e.target.style.borderColor = '#3b82f6'}
                      onBlur={e => e.target.style.borderColor = '#e2e8f0'}
                    />
                    <button type="submit" style={{ ...s.btn(), width: '100%', padding: 12 }}>
                      + Create Job Description
                    </button>
                  </form>
                </div>

                <div>
                  <p style={{ fontWeight: 700, fontSize: 16, color: '#1e293b', marginBottom: 20 }}>
                    Your JDs ({jds.length})
                  </p>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                    {jds.map(jd => (
                      <div key={jd.id} style={{
                        border: '1.5px solid #e2e8f0', borderRadius: 14, padding: 16
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                          <div>
                            <p style={{ fontWeight: 700, color: '#1e293b', fontSize: 15 }}>{jd.title}</p>
                            <p style={{ fontSize: 12, color: '#94a3b8' }}>{jd.company}</p>
                          </div>
                          <div style={{ display: 'flex', gap: 8 }}>
                            <button
                              onClick={() => handleAnalyze(jd.id)}
                              disabled={analyzing || resumes.length === 0}
                              style={{
                                ...s.btn(),
                                padding: '6px 14px', fontSize: 12,
                                opacity: (analyzing || resumes.length === 0) ? 0.5 : 1
                              }}
                            >
                              {analyzing ? '...' : '▶ Analyze'}
                            </button>
                            <button
                               onClick={() => handleExport(jd.id)}
                               style={{
                                 ...s.btn('#059669'),
                                  padding: '6px 14px',
                                  fontSize: 12
                                 }}
                            >
                                 ↓ CSV
                              </button>
                          </div>
                        </div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                          {jd.required_skills?.slice(0, 5).map(skill => (
                            <span key={skill} style={s.tag('#2563eb')}>{skill}</span>
                          ))}
                        </div>
                      </div>
                    ))}
                    {jds.length === 0 && (
                      <p style={{ color: '#94a3b8', textAlign: 'center', padding: 32, fontSize: 14 }}>
                        No job descriptions yet
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Results Tab */}
            {tab === 'results' && (
              <div>
                {results.length > 0 ? (
                  <>
                    <div style={{ marginBottom: 24 }}>
                      <p style={{ fontWeight: 700, fontSize: 16, color: '#1e293b', marginBottom: 16 }}>
                        Score Comparison
                      </p>
                      <ResponsiveContainer width="100%" height={260}>
                        <BarChart data={results.slice(0, 10)}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                          <XAxis
                            dataKey="candidate_name"
                            tick={{ fontSize: 11 }}
                            tickFormatter={v => v?.split(' ')[0] || 'N/A'}
                          />
                          <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                          <Tooltip />
                          <Bar dataKey="overall_score" fill="#3b82f6" radius={[6,6,0,0]} name="Overall" />
                          <Bar dataKey="skills_score" fill="#10b981" radius={[6,6,0,0]} name="Skills" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>

                    <p style={{ fontWeight: 700, fontSize: 16, color: '#1e293b', marginBottom: 12 }}>
                      Candidate Rankings
                    </p>
                    <div style={{ overflowX: 'auto' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
                        <thead>
                          <tr style={{ background: '#f8fafc' }}>
                            {['Rank','Candidate','Overall','Skills','Exp','Matched Skills'].map(h => (
                              <th key={h} style={{
                                padding: '12px 16px', textAlign: 'left',
                                fontWeight: 600, color: '#64748b', fontSize: 13
                              }}>{h}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {results.map(r => (
                            <tr key={r.resume_id} style={{ borderTop: '1px solid #f1f5f9' }}>
                              <td style={{ padding: '14px 16px' }}>
                                <span style={{
                                  fontWeight: 800, fontSize: 18,
                                  color: r.rank === 1 ? '#f59e0b' : r.rank === 2 ? '#94a3b8' : r.rank === 3 ? '#b45309' : '#64748b'
                                }}>#{r.rank}</span>
                              </td>
                              <td style={{ padding: '14px 16px' }}>
                                <p style={{ fontWeight: 600, color: '#1e293b' }}>{r.candidate_name}</p>
                                <p style={{ fontSize: 12, color: '#94a3b8' }}>{r.candidate_email}</p>
                              </td>
                              <td style={{ padding: '14px 16px' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                  <div style={{ width: 60, height: 6, background: '#e2e8f0', borderRadius: 3 }}>
                                    <div style={{
                                      width: `${r.overall_score}%`, height: '100%',
                                      background: '#3b82f6', borderRadius: 3
                                    }} />
                                  </div>
                                  <span style={{ fontWeight: 700, color: '#3b82f6' }}>
                                    {r.overall_score?.toFixed(1)}
                                  </span>
                                </div>
                              </td>
                              <td style={{ padding: '14px 16px', color: '#059669', fontWeight: 600 }}>
                                {r.skills_score?.toFixed(1)}
                              </td>
                              <td style={{ padding: '14px 16px', color: '#64748b' }}>
                                {r.experience_years}y
                              </td>
                              <td style={{ padding: '14px 16px' }}>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                                  {r.matched_skills?.slice(0, 3).map(sk => (
                                    <span key={sk} style={s.tag('#059669')}>{sk}</span>
                                  ))}
                                  {r.matched_skills?.length > 3 && (
                                    <span style={{ fontSize: 11, color: '#94a3b8' }}>
                                      +{r.matched_skills.length - 3}
                                    </span>
                                  )}
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </>
                ) : (
                  <div style={{ textAlign: 'center', padding: 64, color: '#94a3b8' }}>
                    <div style={{ fontSize: 64, marginBottom: 16 }}>📊</div>
                    <p style={{ fontWeight: 600 }}>No results yet</p>
                    <p style={{ fontSize: 13, marginTop: 4 }}>
                      Go to Job Description tab and click Analyze
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}