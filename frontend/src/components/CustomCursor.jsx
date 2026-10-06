import React, { useEffect, useState } from 'react';

export default function CustomCursor() {
  const [position, setPosition] = useState({ x: -100, y: -100 });
  const [isHovered, setIsHovered] = useState(false);
  const [isClicked, setIsClicked] = useState(false);

  useEffect(() => {
    const onMouseMove = (e) => {
      setPosition({ x: e.clientX, y: e.clientY });

      // Check karein agar cursor kisi button, link ya input par hai
      const target = e.target;
      const isInteractive = target.closest('button, a, input, [role="button"], label');
      setIsHovered(!!isInteractive);
    };

    const onMouseDown = () => setIsClicked(true);
    const onMouseUp = () => setIsClicked(false);

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mousedown', onMouseDown);
    window.addEventListener('mouseup', onMouseUp);

    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mousedown', onMouseDown);
      window.removeEventListener('mouseup', onMouseUp);
    };
  }, []);

  return (
    <>
      {/* 1. Center Tiny Glowing Dot */}
      <div
        className="fixed top-0 left-0 pointer-events-none z-[9999] -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-400 shadow-[0_0_10px_#22d3ee] transition-transform duration-75 ease-out"
        style={{
          transform: `translate3d(${position.x}px, ${position.y}px, 0) scale(${isClicked ? 0.6 : 1})`,
          width: '6px',
          height: '6px',
        }}
      />

      {/* 2. Glassmorphic Outer Floating Ring */}
      <div
        className={`fixed top-0 left-0 pointer-events-none z-[9998] -translate-x-1/2 -translate-y-1/2 rounded-full border border-cyan-400/40 bg-white/[0.03] backdrop-blur-[2px] transition-all duration-300 ease-out shadow-[0_0_20px_rgba(34,211,238,0.2)] ${
          isHovered 
            ? 'w-16 h-16 border-pink-500/60 bg-pink-500/10 shadow-[0_0_25px_rgba(236,72,153,0.4)] scale-110' 
            : 'w-10 h-10'
        }`}
        style={{
          transform: `translate3d(${position.x}px, ${position.y}px, 0) scale(${isClicked ? 0.85 : 1})`,
        }}
      />
    </>
  );
}