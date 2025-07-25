// frontend/src/MoodboardSection.jsx
import React from "react";

export default function MoodboardSection() {
  // Each image has a custom fixed size [width, height]
  const images = [
    { src: "/assets/ispymoodboardimage1.png", width: 320, height: 374 },
    { src: "/assets/ispymoodboardimage2.png", width: 208, height: 244 },
    { src: "/assets/ispymoodboardimage3.png", width: 208, height: 244 },
    { src: "/assets/ispymoodboardimage4.png", width: 320, height: 374 },
    { src: "/assets/ispymoodboardimage5.png", width: 208, height: 244 },
  ];

  return (
    <section className="px-6 py-12 text-center">
      <h2 className="text-3xl italic mb-2">Moodboard</h2>
      <p className="text-sm mb-10">
        Save looks, rename folders,
        <br />
        plan every vibe visually.
      </p>
      <div className="flex justify-center flex-wrap gap-4">
        {images.map(({ src, width, height }, i) => (
          <div
            key={i}
            className="overflow-hidden relative rounded-xl"
            style={{ width: `${width}px`, height: `${height}px` }}
          >
            <img
              src={src}
              alt={`moodboard ${i + 1}`}
              className="absolute top-1/2 left-1/2 h-full w-auto -translate-x-1/2 -translate-y-1/2"
              loading="lazy"
            />
          </div>
        ))}
      </div>
    </section>
  );
}
