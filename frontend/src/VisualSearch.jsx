// src/VisualSearch.jsx
import React, { useState } from 'react';

export default function VisualSearch() {
  const [file, setFile] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:8000/search-html', {
        method: 'POST',
        body: formData,
      });
      const html = await res.text();
      document.getElementById('results').innerHTML = html;
    } catch (err) {
      console.error('Upload failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h1>🧠 Visual Fashion Search</h1>
      <input type="file" accept="image/*" onChange={e => setFile(e.target.files[0])} />
      <button onClick={handleUpload} disabled={!file || loading} style={{ marginLeft: '1rem' }}>
        {loading ? 'Searching...' : 'Search'}
      </button>
      <div id="results" style={{ marginTop: '2rem' }}></div>
    </div>
  );
}
