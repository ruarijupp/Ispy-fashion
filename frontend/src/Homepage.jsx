import React, { useState } from 'react';
import { Link } from 'react-router-dom';

export default function Homepage() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);

  const heroImages = [
    "/assets/ispyheroimage1.png",
    "/assets/ispyheroimage2.png",
    "/assets/ispyheroimage3.png",
    "/assets/ispyheroimage4.png",
  ];

  const moodboardImages = [
    { src: "/assets/ispymoodboardimage1.png", user: "allise_outfits", width: 320, height: 374 },
    { src: "/assets/ispymoodboardimage2.png", user: "jessywho", width: 208, height: 244 },
    { src: "/assets/ispymoodboardimage3.png", user: "sandra_cp", width: 208, height: 244 },
    { src: "/assets/ispymoodboardimage4.png", user: "sophie.hips", width: 320, height: 374 },
    { src: "/assets/ispymoodboardimage5.png", user: "olivia.picks", width: 208, height: 244 },
  ];

  const handleImageSearch = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    console.log("📤 Uploading file:", file);

    const formData = new FormData();
    formData.append('file', file);
    setLoading(true);
    setResults([]);

    try {
      const res = await fetch('http://localhost:8000/search', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      console.log("📦 Search result:", data);

      if (data?.results) {
        setResults(data.results);
      } else {
        setResults([]);
      }
    } catch (err) {
      console.error('❌ Image search failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen font-sans bg-white text-black">
      {/* Navbar */}
      <header className="flex justify-between items-center px-6 py-4 border-b">
        <div className="text-2xl font-serif italic">i spy</div>
        <nav className="space-x-6 text-sm">
          <Link to="/">Home</Link>
          <Link to="/moodboard">Moodboard</Link>
          <Link to="/discover">Discover</Link>
        </nav>
        <div className="flex items-center space-x-2">
          <button className="text-xl">📍</button>
          <button className="text-sm">Log in</button>
        </div>
      </header>

      {/* Hero + Search Bar */}
      <section className="px-6 py-12 text-center">
        <h1 className="text-xl font-light mb-6 text-left">Fashion discovery<br />just got smarter.</h1>

        <div className="mb-10 flex justify-center">
          <label htmlFor="image-upload" className="flex items-center border rounded-full px-4 py-2 w-[320px] cursor-pointer">
            <span className="text-gray-400 mr-2">📷</span>
            <span className="text-sm text-gray-500">Upload an image to search</span>
            <input id="image-upload" type="file" accept="image/*" onChange={handleImageSearch} className="hidden" />
          </label>
        </div>

        <div className="flex flex-wrap justify-center gap-[50px]">
          {heroImages.map((src, idx) => (
            <div
              key={idx}
              className="overflow-hidden relative rounded-xl"
              style={{ width: 320, height: 316 }}
            >
              <img
                src={src}
                alt={`hero ${idx + 1}`}
                className="w-full h-full object-cover"
                loading="lazy"
              />
            </div>
          ))}
        </div>
      </section>

      {/* Search Status */}
      {loading && (
        <div className="text-center text-sm text-gray-500 pb-8 animate-pulse">
          🔍 Searching for matches...
        </div>
      )}

      {!loading && results.length === 0 && (
        <div className="text-center text-sm text-gray-400 pb-10">
          No results found. Try a clearer or different image.
        </div>
      )}

      {results.length > 0 && (
        <section className="px-6 py-12 text-center">
          <h2 className="text-xl italic mb-4">Results</h2>
          <div className="flex flex-wrap justify-center gap-[30px]">
            {results.map(({ payload, id }, idx) => (
              <a
                key={id || idx}
                href={payload.url || '#'}
                target="_blank"
                rel="noopener noreferrer"
                className="block w-[200px] rounded-xl overflow-hidden border hover:shadow-lg transition"
              >
                <img
                  src={payload.image_url || ''}
                  alt={payload.title || 'Product'}
                  className="w-full h-[250px] object-cover"
                />
                <div className="px-2 py-2 text-left text-sm">
                  <p className="font-semibold truncate">{payload.title || 'No title'}</p>
                  <p className="text-xs text-gray-500">{payload.price || ''}</p>
                </div>
              </a>
            ))}
          </div>
        </section>
      )}

      {/* Moodboard */}
      <section className="px-6 py-12 text-center">
        <h2 className="text-3xl italic mb-2">MOODBOARD</h2>
        <p className="text-sm mb-10">Save looks, rename folders,<br />plan every vibe visually.</p>
        <div className="flex justify-center flex-wrap gap-[50px]">
          {moodboardImages.map(({ src, user, width, height }, idx) => (
            <div
              key={idx}
              className="overflow-hidden relative rounded-xl text-left"
              style={{ width, height }}
            >
              <img
                src={src}
                alt={`moodboard ${idx + 1}`}
                className="w-full h-full object-cover"
                loading="lazy"
              />
              <p className="text-xs px-2 pt-1">📂 {user}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
