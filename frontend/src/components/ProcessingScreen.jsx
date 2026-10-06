import React from 'react';
import { 
  Sparkles, 
  Eye, 
  Grid2X2, 
  Network, 
  Code2, 
  Layers, 
  Check, 
  Loader2, 
  Cpu, 
  FileText,
  Save, 
  ArrowRight, 
  HelpCircle,
  Clock
} from 'lucide-react';

export default function ProcessingScreen({ onComplete }) {
  return (
    <div className="flex-1 flex flex-col min-h-screen bg-[#070709] text-white overflow-y-auto">
      
      {/* 1. Header Bar */}
      <header className="h-16 border-b border-white/10 bg-[#070709]/80 backdrop-blur-xl px-8 flex items-center justify-between sticky top-0 z-20">
        <div className="flex items-center gap-2">
          <span className="text-xs text-zinc-500">✏️</span>
          <span className="text-sm font-medium text-zinc-200">Untitled Project</span>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-medium text-zinc-300 transition-all cursor-pointer">
            <Save className="w-3.5 h-3.5" />
            <span>Save</span>
          </button>
          <button 
            onClick={onComplete}
            className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 text-xs font-medium text-white shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all cursor-pointer"
          >
            <span>Export</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </header>

      {/* 2. Main Content Grid */}
      <div className="p-8 max-w-7xl mx-auto w-full grid grid-cols-1 xl:grid-cols-12 gap-8 items-start">
        
        {/* Left 9-Column: Active Pipeline Stage */}
        <div className="xl:col-span-9 space-y-6">
          
          {/* Headline */}
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-cyan-400 animate-pulse" />
              <h2 className="text-lg font-semibold tracking-tight text-white">Processing</h2>
            </div>
            <p className="text-xs text-zinc-400">
              Analyzing your sketch using AI. This will only take a few seconds...
            </p>
          </div>

          {/* Stepper Pipeline Pills (Top Stage Tracker) */}
          <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/10 backdrop-blur-xl flex items-center justify-between overflow-x-auto gap-2">
            
            {/* Step 1: Sketch */}
            <div className="flex flex-col items-center gap-2">
              <div className="relative w-11 h-11 rounded-2xl bg-cyan-500/10 border border-cyan-500/40 flex items-center justify-center text-cyan-400 shadow-[0_0_15px_rgba(34,211,238,0.2)]">
                <FileText className="w-5 h-5" />
                <span className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-emerald-500 flex items-center justify-center text-[9px] text-black font-bold">✓</span>
              </div>
              <span className="text-[11px] font-mono text-zinc-400">Sketch</span>
            </div>

            <div className="h-[2px] flex-1 bg-gradient-to-r from-cyan-500/60 to-cyan-500/60" />

            {/* Step 2: Vision */}
            <div className="flex flex-col items-center gap-2">
              <div className="relative w-11 h-11 rounded-2xl bg-cyan-500/10 border border-cyan-500/40 flex items-center justify-center text-cyan-400 shadow-[0_0_15px_rgba(34,211,238,0.2)]">
                <Eye className="w-5 h-5" />
                <span className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-emerald-500 flex items-center justify-center text-[9px] text-black font-bold">✓</span>
              </div>
              <span className="text-[11px] font-mono text-zinc-400">Vision</span>
            </div>

            <div className="h-[2px] flex-1 bg-gradient-to-r from-cyan-500/60 to-cyan-500/60" />

            {/* Step 3: Components */}
            <div className="flex flex-col items-center gap-2">
              <div className="relative w-11 h-11 rounded-2xl bg-cyan-500/10 border border-cyan-500/40 flex items-center justify-center text-cyan-400 shadow-[0_0_15px_rgba(34,211,238,0.2)]">
                <Grid2X2 className="w-5 h-5" />
                <span className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-emerald-500 flex items-center justify-center text-[9px] text-black font-bold">✓</span>
              </div>
              <span className="text-[11px] font-mono text-zinc-400">Components</span>
            </div>

            <div className="h-[2px] flex-1 bg-gradient-to-r from-cyan-500/60 to-purple-500/60" />

            {/* Step 4: Structure (Active) */}
            <div className="flex flex-col items-center gap-2">
              <div className="relative w-12 h-12 rounded-2xl bg-purple-500/20 border-2 border-purple-400 flex items-center justify-center text-purple-300 shadow-[0_0_25px_rgba(168,85,247,0.5)] animate-pulse">
                <Network className="w-6 h-6" />
              </div>
              <span className="text-[11px] font-mono text-purple-300 font-semibold">Structure</span>
            </div>

            <div className="h-[2px] flex-1 bg-white/10" />

            {/* Step 5: Code */}
            <div className="flex flex-col items-center gap-2 opacity-50">
              <div className="w-11 h-11 rounded-2xl bg-white/[0.03] border border-white/10 flex items-center justify-center text-zinc-400">
                <Code2 className="w-5 h-5" />
              </div>
              <span className="text-[11px] font-mono text-zinc-500">Code</span>
            </div>

            <div className="h-[2px] flex-1 bg-white/10" />

            {/* Step 6: UI */}
            <div className="flex flex-col items-center gap-2 opacity-50">
              <div className="w-11 h-11 rounded-2xl bg-white/[0.03] border border-white/10 flex items-center justify-center text-zinc-400">
                <Layers className="w-5 h-5" />
              </div>
              <span className="text-[11px] font-mono text-zinc-500">UI</span>
            </div>

          </div>

          {/* Center 3-Stage Visual Pipeline Box */}
          <div className="p-8 rounded-3xl bg-white/[0.015] border border-white/10 backdrop-blur-2xl grid grid-cols-1 md:grid-cols-3 gap-6 items-center justify-center min-h-[360px]">
            
            {/* Box 1: Wireframe Sketch */}
            <div className="relative p-4 rounded-2xl bg-[#0c0f16] border border-white/15 shadow-xl flex flex-col items-center">
              <span className="text-[10px] font-mono uppercase tracking-widest text-zinc-400 mb-3">Input Wireframe</span>
              <div className="w-full h-44 rounded-xl border border-dashed border-zinc-700/80 p-3 space-y-2.5 bg-[#07090e]">
                <div className="text-[11px] font-mono text-zinc-400 pb-1 border-b border-zinc-800">Login Form</div>
                <div className="w-8 h-8 rounded border border-zinc-700 flex items-center justify-center text-[10px] text-zinc-500">Img</div>
                <div className="h-4 rounded bg-zinc-800/80 border border-zinc-700 text-[9px] text-zinc-500 px-2 flex items-center">Email input</div>
                <div className="h-4 rounded bg-zinc-800/80 border border-zinc-700 text-[9px] text-zinc-500 px-2 flex items-center">Password</div>
                <div className="h-5 rounded bg-zinc-700 text-[9px] text-zinc-300 flex items-center justify-center font-mono">Submit</div>
              </div>
            </div>

            {/* Box 2: Center YOLOv8 Processor Node */}
            <div className="flex flex-col items-center justify-center">
              <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 p-[1px] shadow-[0_0_35px_rgba(168,85,247,0.4)]">
                <div className="w-full h-full rounded-3xl bg-[#0b0c14] flex flex-col items-center justify-center space-y-1">
                  <Cpu className="w-8 h-8 text-cyan-400 animate-spin [animation-duration:10s]" />
                  <span className="text-[11px] font-bold tracking-widest text-white">YOLOv8</span>
                  <span className="text-[9px] text-purple-400 font-mono">Inferencing</span>
                </div>
              </div>
            </div>

            {/* Box 3: Hierarchy Tree Output */}
            <div className="p-4 rounded-2xl bg-[#0c0f16] border border-cyan-500/20 shadow-xl space-y-2">
              <div className="flex items-center gap-1.5 pb-2 border-b border-white/5 text-[10px] font-mono text-cyan-400">
                <Network className="w-3.5 h-3.5" />
                <span>Element Hierarchy</span>
              </div>
              <div className="font-mono text-xs space-y-1.5 text-zinc-300">
                <p className="text-purple-400">▾ page</p>
                <p className="pl-4 text-indigo-400">▾ card</p>
                <p className="pl-8 text-emerald-400 flex items-center gap-1.5"><span className="w-2 h-2 rounded-sm bg-emerald-400 inline-block"/> heading</p>
                <p className="pl-8 text-blue-400 flex items-center gap-1.5"><span className="w-2 h-2 rounded-sm bg-blue-400 inline-block"/> image_box</p>
                <p className="pl-8 text-amber-400 flex items-center gap-1.5"><span className="w-2 h-2 rounded-sm bg-amber-400 inline-block"/> input_field</p>
                <p className="pl-8 text-rose-400 flex items-center gap-1.5"><span className="w-2 h-2 rounded-sm bg-rose-400 inline-block"/> button</p>
              </div>
            </div>

          </div>

          {/* Bottom Stage Progress Checkpoints */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            
            <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 space-y-1">
              <div className="flex items-center gap-1.5 text-emerald-400 text-xs font-medium">
                <Check className="w-3.5 h-3.5" />
                <span>Preprocessing</span>
              </div>
              <p className="text-[10px] text-zinc-500">Enhanced & resized</p>
            </div>

            <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 space-y-1">
              <div className="flex items-center gap-1.5 text-emerald-400 text-xs font-medium">
                <Check className="w-3.5 h-3.5" />
                <span>Detecting</span>
              </div>
              <p className="text-[10px] text-zinc-500">6 components found</p>
            </div>

            <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 space-y-1">
              <div className="flex items-center gap-1.5 text-emerald-400 text-xs font-medium">
                <Check className="w-3.5 h-3.5" />
                <span>Hierarchy</span>
              </div>
              <p className="text-[10px] text-zinc-500">Parent-child mapped</p>
            </div>

            <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/30 space-y-1">
              <div className="flex items-center gap-1.5 text-purple-400 text-xs font-medium">
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Generating</span>
              </div>
              <p className="text-[10px] text-purple-300/70">React + Tailwind</p>
            </div>

            <div className="p-3 rounded-xl bg-white/[0.01] border border-white/5 space-y-1 opacity-50">
              <div className="flex items-center gap-1.5 text-zinc-400 text-xs font-medium">
                <Clock className="w-3.5 h-3.5" />
                <span>Preview</span>
              </div>
              <p className="text-[10px] text-zinc-600">Pending final render</p>
            </div>

          </div>

          {/* 78% Gradient Progress Bar */}
          <div className="space-y-2 pt-2">
            <div className="flex justify-between items-center text-xs font-mono">
              <span className="text-zinc-400 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                Synthesizing semantic markup...
              </span>
              <span className="text-cyan-400 font-bold">78%</span>
            </div>
            <div className="w-full h-2 rounded-full bg-white/5 overflow-hidden p-0.5 border border-white/10">
              <div className="h-full rounded-full bg-gradient-to-r from-cyan-400 via-indigo-500 to-pink-500 shadow-[0_0_15px_#22d3ee] w-[78%] transition-all duration-500" />
            </div>
          </div>

        </div>

        {/* Right 3-Column: Quick Info & Telemetry Cards */}
        <div className="xl:col-span-3 space-y-6">
          
          {/* Card 1: Processing Steps */}
          <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/10 space-y-4">
            <h3 className="text-xs font-semibold tracking-wider uppercase text-zinc-400 font-mono">
              Processing Steps
            </h3>
            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between text-zinc-300">
                <span className="flex items-center gap-2 text-emerald-400">
                  <Check className="w-3.5 h-3.5" /> Image preprocessing
                </span>
                <span className="text-[10px] font-mono text-zinc-500">Completed</span>
              </div>
              <div className="flex items-center justify-between text-zinc-300">
                <span className="flex items-center gap-2 text-emerald-400">
                  <Check className="w-3.5 h-3.5" /> Component detection
                </span>
                <span className="text-[10px] font-mono text-zinc-500">Completed</span>
              </div>
              <div className="flex items-center justify-between text-zinc-300">
                <span className="flex items-center gap-2 text-emerald-400">
                  <Check className="w-3.5 h-3.5" /> Hierarchy parsing
                </span>
                <span className="text-[10px] font-mono text-zinc-500">Completed</span>
              </div>
              <div className="flex items-center justify-between text-purple-300">
                <span className="flex items-center gap-2">
                  <Loader2 className="w-3.5 h-3.5 animate-spin" /> Code generation
                </span>
                <span className="text-[10px] font-mono text-purple-400">In progress</span>
              </div>
              <div className="flex items-center justify-between text-zinc-500">
                <span className="flex items-center gap-2">
                  <Clock className="w-3.5 h-3.5" /> UI rendering
                </span>
                <span className="text-[10px] font-mono">Pending</span>
              </div>
            </div>
          </div>

          {/* Card 2: Quick Info Metadata */}
          <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/10 space-y-3">
            <h3 className="text-xs font-semibold tracking-wider uppercase text-zinc-400 font-mono">
              Quick Info
            </h3>
            <div className="space-y-2.5 text-xs">
              <div className="flex justify-between items-center">
                <span className="text-zinc-500">Model</span>
                <span className="text-zinc-200 font-mono">YOLOv8</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-zinc-500">Components Found</span>
                <span className="text-zinc-200 font-mono">6</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-zinc-500">Image Size</span>
                <span className="text-zinc-200 font-mono">1024 × 768</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-zinc-500">Output Format</span>
                <span className="text-cyan-400 font-mono">React + Tailwind</span>
              </div>
            </div>
          </div>

          {/* Card 3: Did you know? */}
          <div className="p-4 rounded-2xl bg-blue-500/5 border border-blue-500/15 space-y-1.5">
            <div className="flex items-center gap-1.5 text-blue-400 text-xs font-medium">
              <HelpCircle className="w-3.5 h-3.5" />
              <span>Did you know?</span>
            </div>
            <p className="text-[11px] text-zinc-400 leading-relaxed">
              The spatial engine understands parent-child relationships between UI elements for optimal nesting layout.
            </p>
          </div>

        </div>

      </div>

    </div>
  );
}