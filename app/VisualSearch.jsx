import React, { useState } from "react";

export default function VisualSearch() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [htmlResult, setHtmlResult] = useState("");
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setImage(file);
    setPreview(URL.createObjectURL(file));
  };

  const handleSearch = async () => {
    if (!image) return;
    setLoading(true);

    const formData = new FormData();
    formData.append("file", image);

    const res = await fetch("http://localhost:8000/search-html", {
      method: "POST",
      body: formData,
    });

    const html = await res.text();
    setHtmlResult(html);
    setLoading(false);
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4 text-center">Visual Search</h1>
      <div className="flex flex-col items-center space-y-4">
        <input type="file" accept="image/*" onChange={handleFileChange} />
        {preview && <img src={preview} alt="preview" className="w-48 rounded" />}
        <button
          onClick={handleSearch}
          disabled={!image || loading}
          className="px-4 py-2 bg-black text-white rounded"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>
      <div
        className="mt-8"
        dangerouslySetInnerHTML={{ __html: htmlResult }}
      />
    </div>
  );
}
