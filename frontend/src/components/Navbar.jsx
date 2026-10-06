import React from 'react';
import { Sparkles, ArrowRight } from 'lucide-react';

export default function Navbar({ onStartClick, onLogoClick }) {
  return (
    <header className="fixed top-6 left-1/2 -translate-x-1/2 z-50 w-[92%] max-w-5xl">
      <nav className="flex items-center justify-between px-6 py-3 rounded-full bg-white/[0.04] backdrop-blur-2xl border border-white/10 shadow-[0_8px_32px_0_rgba(0,0,0,0.4)]">
        
        {/* Logo par click karne se wapas Landing page par aayenge */}
        <div 
          onClick={onLogoClick} 
          className="flex items-center gap-2.5 cursor-pointer"
        >
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-400 to-pink-500 flex items-center justify-center shadow-[0_0_15px_#22d3ee]">
            <Sparkles className="w-4 h-4 text-black" />
          </div>
          <span className="font-semibold tracking-wider text-base text-white">Sketch2UI</span>
        </div>

        <div className="hidden md:flex items-center gap-7 text-xs tracking-wider uppercase text-zinc-400">
          <a href="#how-it-works" className="hover:text-white transition-colors">How it Works</a>
          <a href="#examples" className="hover:text-white transition-colors">Examples</a>
          <a href="#docs" className="hover:text-white transition-colors">Docs</a>
          <a href="https://github.com" target="_blank" rel="noreferrer" className="hover:text-white transition-colors">GitHub ↗</a>
        </div>

        {/* Is button par click karne se Studio Workspace khulega */}
        <button 
          onClick={onStartClick}
          className="flex items-center gap-2 px-5 py-2 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-xs font-semibold uppercase tracking-wider text-white shadow-[0_0_20px_rgba(6,182,212,0.4)] transition-all cursor-pointer"
        >
          <span>Try Sketch2UI</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </nav>
    </header>
  );
}