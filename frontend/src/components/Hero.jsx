import React from 'react';
import { Sparkles, Play, ArrowRight } from 'lucide-react';

export default function Hero({ onStart, onWatchDemo }) {
  return (
    <div className="space-y-6">
      {/* Badge */}
      <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-mono">
        <Sparkles className="w-3.5 h-3.5" />
        <span>AI Powered UI Generation</span>
      </div>

      {/* Main Headline */}
      <h1 className="text-5xl font-bold tracking-tight text-white leading-tight">
        Turn your sketches into <br />
        <span className="bg-gradient-to-r from-cyan-400 via-pink-400 to-purple-500 bg-clip-text text-transparent">
          real interfaces.
        </span>
      </h1>

      <p className="text-zinc-400 text-sm max-w-md leading-relaxed">
        Convert hand-drawn wireframes into clean, responsive React and Tailwind interfaces automatically in seconds.
      </p>

      {/* Action Buttons */}
      <div className="flex items-center gap-4 pt-2">
        <button 
          onClick={onStart}
          className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-xs font-semibold uppercase tracking-wider text-white shadow-[0_0_25px_rgba(6,182,212,0.4)] transition-all cursor-pointer"
        >
          <span>Start Creating</span>
          <ArrowRight className="w-4 h-4" />
        </button>

        <button 
          onClick={onWatchDemo}
          className="flex items-center gap-2 px-5 py-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-medium text-zinc-300 hover:text-white transition-all cursor-pointer group"
        >
          <div className="w-5 h-5 rounded-full bg-cyan-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
            <Play className="w-3 h-3 text-cyan-400 ml-0.5 fill-cyan-400" />
          </div>
          <span>Watch Demo</span>
        </button>
      </div>
    </div>
  );
}