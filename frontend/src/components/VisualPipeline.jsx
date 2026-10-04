import React from 'react';
import { Cpu } from 'lucide-react';

export default function VisualPipeline() {
  return (
    <div className="relative flex items-center justify-center gap-3 sm:gap-4 p-8 rounded-3xl bg-white/[0.02] border border-white/10 backdrop-blur-2xl shadow-[0_20px_50px_rgba(0,0,0,0.5)]">
      
      {/* 1. Wireframe Sketch Card */}
      <div className="relative group w-36 sm:w-44 p-3.5 rounded-2xl bg-[#0d0f14]/90 border border-white/15 shadow-2xl rotate-[-3deg] hover:rotate-0 transition-all duration-300 hover:shadow-[0_0_20px_rgba(255,255,255,0.1)]">
        <span className="absolute -top-6 left-2 text-[10px] uppercase tracking-widest text-zinc-400 font-mono">
          Your Sketch
        </span>
        <div className="border border-dashed border-zinc-700 rounded-lg p-2.5 space-y-2 bg-[#08090d]">
          <div className="h-3 w-12 bg-zinc-700/80 rounded" />
          <div className="w-8 h-8 rounded border border-zinc-700 flex items-center justify-center text-[10px] text-zinc-500 font-mono">
            Img
          </div>
          <div className="h-4 w-full border border-zinc-700 rounded" />
          <div className="h-4 w-full border border-zinc-700 rounded" />
          <div className="h-5 w-full bg-zinc-700/80 rounded flex items-center justify-center text-[9px] text-zinc-300 font-mono">
            BTN
          </div>
        </div>
      </div>

      {/* Glowing Neon Laser Connection 1 */}
      <div className="relative w-8 h-[2px] bg-zinc-800 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-400 to-transparent shadow-[0_0_12px_#22d3ee] animate-pulse" />
      </div>

      {/* 2. Core AI Processor with Pulse Halo */}
      <div className="relative flex flex-col items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 shadow-[0_0_30px_rgba(168,85,247,0.7)] border border-white/20 transition-transform duration-300 hover:scale-110">
        <Cpu className="w-6 h-6 text-white animate-spin [animation-duration:8s]" />
        <span className="text-[9px] font-bold tracking-widest mt-0.5 text-white">AI</span>
      </div>

      {/* Glowing Neon Laser Connection 2 */}
      <div className="relative w-8 h-[2px] bg-zinc-800 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-pink-400 to-transparent shadow-[0_0_12px_#ec4899] animate-pulse" />
      </div>

      {/* 3. Live Rendered UI Component */}
      <div className="relative group w-44 sm:w-52 p-4 rounded-2xl bg-[#0c101a] border border-cyan-500/30 shadow-[0_0_35px_rgba(6,182,212,0.18)] rotate-[2deg] hover:rotate-0 transition-all duration-300 hover:border-cyan-400/50">
        <span className="absolute -top-6 right-2 text-[10px] uppercase tracking-widest text-cyan-400 font-mono">
          Generated UI
        </span>
        <div className="flex gap-1 mb-2.5">
          <div className="w-2 h-2 rounded-full bg-rose-500/80" />
          <div className="w-2 h-2 rounded-full bg-amber-500/80" />
          <div className="w-2 h-2 rounded-full bg-emerald-500/80" />
        </div>
        <div className="space-y-2">
          <p className="text-xs font-semibold text-white">Welcome back</p>
          <div className="h-6 w-full rounded bg-zinc-900 border border-zinc-700/80 px-2 text-[10px] text-zinc-400 flex items-center">
            email@domain.com
          </div>
          <div className="h-6 w-full rounded bg-zinc-900 border border-zinc-700/80 px-2 text-[10px] text-zinc-400 flex items-center">
            ••••••••
          </div>
          <button className="w-full py-1.5 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-[10px] font-semibold transition-all shadow-[0_0_15px_rgba(6,182,212,0.4)]">
            Sign In
          </button>
        </div>
      </div>

    </div>
  );
}