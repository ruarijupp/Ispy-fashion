// frontend/src/HeroSection.jsx
import React from "react";

export default function HeroSection() {
  const images = [
    "/assets/ispyheroimage1.png",
    "/assets/ispyheroimage2.png",
    "/assets/ispyheroimage3.png",
    "/assets/ispyheroimage4.png",
  ];

  return (
    <section className="px-6 py-12">
      <h1 className="text-xl font-light mb-6">
        Fashion discovery
        <br />
        just got smarter.
      </h1>
      <div className="flex gap-4">
        {images.map((src, i) => (
          <div
            key={i}
            className="w-[320px] h-[316px] overflow-hidden relative rounded-xl"
          >
            <img
              src={src}
              alt={`hero ${i + 1}`}
              className="absolute top-1/2 left-1/2 h-full w-auto -translate-x-1/2 -translate-y-1/2"
              loading="lazy"
            />
          </div>
        ))}
      </div>
    </section>
  );
}
