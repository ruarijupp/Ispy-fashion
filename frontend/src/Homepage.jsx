import React, { useState } from 'react';

export default function SearchPage() {
  const [loading, setLoading] = useState(false);

  const handleImageSearch = async (e) => {
    const file = e.target.files[0];
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
      const resultsEl = document.getElementById('results');
      resultsEl.innerHTML = html;

      if (!html.includes('<img')) {
        resultsEl.innerHTML = `
          <div class="text-center text-gray-400 text-sm">
            No results found. Try a clearer or different image.
          </div>
        `;
      }
    } catch (err) {
      console.error(err);
      document.getElementById('results').innerHTML = `
        <div class="text-center text-red-500 text-sm">
          Error while searching. Please try again.
        </div>
      `;
    }

    setLoading(false);
  };

  return (
    <div className="max-w-screen-lg mx-auto px-4 pt-16">
      <div className="text-center pb-8">
        <h1 className="text-3xl font-semibold">Search by Image</h1>
        <p className="text-gray-500 mt-2">
          Upload a fashion image or screenshot to find visually similar products.
        </p>
      </div>

      <div className="flex flex-col items-center gap-4">
        <label className="border border-dashed border-gray-300 p-6 rounded-lg cursor-pointer hover:bg-gray-50 transition">
          <span className="text-sm text-gray-600">Click to upload an image</span>
          <input
            type="file"
            accept="image/*"
            onChange={handleImageSearch}
            className="hidden"
          />
        </label>

        {loading && (
          <div className="text-sm text-gray-400 pb-6">Searching...</div>
        )}
      </div>

      <div id="results" className="pt-12 px-4" />
    </div>
  );
}
