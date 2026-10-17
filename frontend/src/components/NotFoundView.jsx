import React from 'react';
import { Sparkles, ArrowLeft, Layout, FolderGit2 } from 'lucide-react';

export default function NotFoundView({ onNavigate }) {
  return (
    <div className="relative min-h-screen bg-[#070709] text-white selection:bg-pink-500 selection:text-white flex flex-col items-center justify-center p-6 overflow-hidden">
      
      {/* Background glow effects */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-cyan-500/10 blur-[160px] pointer-events-none" />
      <div className="absolute top-1/3 right-1/4 w-[400px] h-[400px] bg-pink-500/10 blur-[180px] pointer-events-none" />

      {/* 404 Glassmorphic Card */}
      <div className="relative z-10 max-w-lg w-full p-8 md:p-12 rounded-3xl border border-white/10 bg-[#090b10]/80 backdrop-blur-2xl text-center space-y-6 shadow-2xl">
        
        {/* Brand Icon */}
        <div className="mx-auto w-16 h-16 rounded-2xl bg-gradient-to-tr from-cyan-400 to-pink-500 flex items-center justify-center shadow-[0_0_25px_#22d3ee]">
          <Sparkles className="w-8 h-8 text-black font-bold" />
        </div>

        {/* 404 Heading */}
        <div className="space-y-2">
          <div className="text-6xl md:text-7xl font-bold font-mono tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-pink-500 to-indigo-400">
            404
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight">
            Page Not Found
          </h1>
          <p className="text-xs text-zinc-400 max-w-sm mx-auto leading-relaxed">
            The view state you are looking for does not exist in the Sketch2UI engine routing table.
          </p>
        </div>

        {/* Navigation CTAs */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          <button
            onClick={() => onNavigate('studio')}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 text-xs font-semibold uppercase tracking-wider text-white shadow-[0_0_20px_rgba(6,182,212,0.35)] transition-all cursor-pointer"
          >
            <Layout className="w-4 h-4" />
            <span>Back to Studio</span>
          </button>

          <button
            onClick={() => onNavigate('projects')}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-medium text-zinc-300 hover:text-white transition-all cursor-pointer"
          >
            <FolderGit2 className="w-4 h-4" />
            <span>Go to Projects</span>
          </button>
        </div>

        {/* Back to Home Link */}
        <div className="pt-2">
          <button
            onClick={() => onNavigate('landing')}
            className="text-xs text-zinc-500 hover:text-cyan-400 transition-colors inline-flex items-center gap-1.5 cursor-pointer"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Return to Landing Page</span>
          </button>
        </div>

      </div>

    </div>
  );
}
