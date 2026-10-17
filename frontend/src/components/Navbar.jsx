import React from 'react';
import { Sparkles, ArrowRight } from 'lucide-react';

export default function Navbar({ onLaunchStudio, onStartClick, onLogoClick, onNavigate }) {
  const handleLaunch = onLaunchStudio || onStartClick;

  const scrollToSection = (id) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-40 border-b border-white/10 bg-[#070709]/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        {/* Brand Logo */}
        <div 
          onClick={onLogoClick}
          className="flex items-center gap-2.5 cursor-pointer group"
        >
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-400 to-pink-500 flex items-center justify-center shadow-[0_0_15px_#22d3ee] group-hover:scale-105 transition-transform">
            <Sparkles className="w-4 h-4 text-black font-bold" />
          </div>
          <span className="font-semibold tracking-wider text-base text-white group-hover:text-cyan-300 transition-colors">
            Sketch2UI
          </span>
        </div>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-8 text-xs font-medium text-zinc-400">
          <button 
            type="button"
            onClick={() => scrollToSection('how-it-works')} 
            className="hover:text-white transition-colors cursor-pointer"
          >
            HOW IT WORKS
          </button>
          
          <button 
            type="button"
            onClick={() => scrollToSection('examples')} 
            className="hover:text-white transition-colors cursor-pointer"
          >
            EXAMPLES
          </button>

          <button 
            type="button"
            onClick={() => onNavigate && onNavigate('docs')} 
            className="hover:text-white transition-colors cursor-pointer"
          >
            DOCS
          </button>

          <a 
            href="https://github.com/nainamaurya460-star/sketch2ui" 
            target="_blank" 
            rel="noreferrer" 
            className="hover:text-white transition-colors"
          >
            GITHUB ↗
          </a>
        </nav>

        {/* CTA Launch Studio Button */}
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={handleLaunch}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 text-xs font-semibold uppercase tracking-wider text-white shadow-[0_0_20px_rgba(6,182,212,0.35)] transition-all cursor-pointer"
          >
            <span>TRY SKETCH2UI</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </header>
  );
}