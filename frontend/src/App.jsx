import { useState } from 'react';
import axios from 'axios';
import { Upload, FileText, Target, Brain, CheckCircle, AlertCircle, Sparkles } from 'lucide-react';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function App() {
  const [file, setFile] = useState(null);
  const [resume, setResume] = useState('');
  const [jd, setJd] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [status, setStatus] = useState('');

  async function uploadResume() {
    if (!file) { setError('Please select a PDF resume first.'); return; }
    const data = new FormData();
    data.append('file', file);
    setLoading(true); setError(''); setStatus('');
    try {
      const response = await axios.post(`${API}/api/upload-resume`, data);
      setResume(response.data.resume_text);
      setStatus(`Resume extracted. Detected skills: ${response.data.skills.join(', ') || 'none from the built-in list'}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Is the backend running?');
    } finally { setLoading(false); }
  }

  async function analyze() {
    if (!resume.trim() || !jd.trim()) { setError('Upload a resume and paste a job description.'); return; }
    const data = new FormData();
    data.append('resume_text', resume);
    data.append('job_description', jd);
    setLoading(true); setError(''); setStatus('');
    try {
      const response = await axios.post(`${API}/api/analyze`, data);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed. Is the backend running?');
    } finally { setLoading(false); }
  }

  return <div className="app">
    <header className="navbar">
      <h2><Brain /> CareerPilot AI</h2><span>Smart Career Assistant</span>
    </header>
    <main>
      <section className="hero">
        <div className="tag"><Sparkles size={16}/> AI CAREER INTELLIGENCE</div>
        <h1>Your Resume.<br/><span>Your Next Opportunity.</span></h1>
        <p>Compare your resume with a job description and discover practical ways to strengthen your application.</p>
      </section>
      <section className="workspace">
        <div className="panel">
          <h2><Upload /> Upload Resume</h2>
          <label className="upload">
            <FileText size={35}/>
            <strong>{file?.name || 'Choose your PDF resume'}</strong>
            <small>PDF files only · Maximum 5 MB</small>
            <input type="file" accept=".pdf,application/pdf" onChange={e => setFile(e.target.files?.[0] || null)} />
          </label>
          <button onClick={uploadResume} disabled={loading}>{loading ? 'Please wait…' : 'Upload Resume'}</button>
          {resume && <p className="success">Resume text extracted successfully.</p>}
        </div>
        <div className="panel">
          <h2><Target /> Job Description</h2>
          <textarea placeholder="Paste the complete job description here…" value={jd} onChange={e => setJd(e.target.value)} />
          <button onClick={analyze} disabled={loading}><Sparkles size={17}/>{loading ? 'Analyzing…' : 'Analyze My Resume'}</button>
        </div>
      </section>
      {error && <div className="error"><AlertCircle size={18}/>{error}</div>}
      {status && <div className="success status">{status}</div>}
      {result && <section className="results">
        <h2>Resume Analysis</h2>
        <div className="score-card">
          <div><small>Skills Match Indicator</small><h1>{result.match_score}%</h1><p>Based on detected job skills</p></div>
          <div className="score-circle" style={{'--score': `${result.match_score}%`}}>{result.match_score}%</div>
        </div>
        <div className="result-grid">
          <div className="result-card"><h3><CheckCircle/> Matching Skills</h3>
            {result.matching_skills.length ? result.matching_skills.map(s => <span className="skill green" key={s}>{s}</span>) : <p>No matching skills detected.</p>}
          </div>
          <div className="result-card"><h3><AlertCircle/> Missing Skills</h3>
            {result.missing_skills.length ? result.missing_skills.map(s => <span className="skill red" key={s}>{s}</span>) : <p>No missing skills detected from the list.</p>}
          </div>
        </div>
        <div className="result-card"><h3>Recommended Improvements</h3>{result.suggestions.map((s, i) => <p key={i}>• {s}</p>)}</div>
        <div className="result-card"><h3>Suggested Projects</h3>{result.projects.map((p, i) => <p key={i}><strong>{p.title}</strong> — {p.description}</p>)}</div>
        <div className="result-card"><h3>30-Day Learning Roadmap</h3>{result.roadmap.map((r, i) => <p key={i}><strong>{r.week}:</strong> {r.task}</p>)}</div>
        <p className="note">{result.note}</p>
      </section>}
    </main>
    <footer>CareerPilot AI · Build your future with intelligence.</footer>
  </div>;
}
