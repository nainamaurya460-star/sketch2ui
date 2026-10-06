import React, { useState, useEffect, useRef } from 'react';
import ProcessingScreen from './ProcessingScreen';
import StudioResultView from './StudioResultView';
import { 
  Sparkles, 
  Plus, 
  Layout, 
  FolderGit2, 
  History, 
  BookOpen, 
  GitBranch, 
  Settings, 
  Save, 
  Download, 
  CloudUpload, 
  FolderOpen, 
  Camera, 
  Lightbulb, 
  CheckCircle2, 
  ChevronDown, 
  ArrowLeft 
} from 'lucide-react';

export default function StudioWorkspace({ onBack, onNavigate, isDemoMode = false }) {
  // 'upload' | 'processing' | 'result'
  const [workflowState, setWorkflowState] = useState(isDemoMode ? 'processing' : 'upload');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  // Agar user "Watch Demo" dabakar aya hai, toh 3 seconds auto-process hokar Result dikhayega
  useEffect(() => {
    if (isDemoMode) {
      setWorkflowState('processing');
      const timer = setTimeout(() => {
        setWorkflowState('result');
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [isDemoMode]);

  const handleFile = (file) => {
    if (file) {
      setWorkflowState('processing');
      setTimeout(() => {
        setWorkflowState('result');
      }, 3500);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") setDragActive(true);
    else if (e.type === "dragleave") setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  if (workflowState === 'processing') {
    return <ProcessingScreen onComplete={() => setWorkflowState('result')} />;
  }

  if (workflowState === 'result') {
    return <StudioResultView onReset={() => setWorkflowState('upload')} />;
  }

  return (
    <div className="flex h-screen bg-[#070709] text-white selection:bg-pink-500 selection:text-white overflow-hidden -mt-32 -mx-6">
      
      {/* 1. Left Sidebar */}
      <aside className="w-64 border-r border-white/10 bg-[#090b10]/90 backdrop-blur-2xl flex flex-col justify-between p-5 z-20 shrink-0">
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-400 to-pink-500 flex items-center justify-center shadow-[0_0_15px_#22d3ee]">
                <Sparkles className="w-4 h-4 text-black font-bold" />
              </div>
              <span className="font-semibold tracking-wider text-base text-white">Sketch2UI</span>
            </div>
            {onBack && (
              <button 
                onClick={onBack}
                title="Back to Landing"
                className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-zinc-400 hover:text-white transition-all cursor-pointer"
              >
                <ArrowLeft className="w-4 h-4" />
              </button>
            )}
          </div>

          <button 
            onClick={() => setWorkflowState('upload')}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-xs font-semibold uppercase tracking-wider text-white shadow-[0_0_20px_rgba(6,182,212,0.35)] transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>New Project</span>
          </button>

          <div className="space-y-1">
            <p className="text-[10px] uppercase font-mono tracking-widest text-zinc-500 px-3">Workspace</p>
            <nav className="space-y-0.5 pt-1">
              <button className="w-full flex items-center gap-3 px-3 py-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-xs font-medium cursor-pointer">
                <Layout className="w-4 h-4" />
                <span>Workspace</span>
              </button>
              <button 
                onClick={() => onNavigate && onNavigate('projects')}
                className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.04] text-xs font-medium transition-all cursor-pointer"
              >
                <FolderGit2 className="w-4 h-4" />
                <span>Projects</span>
              </button>
              <button 
                onClick={() => onNavigate && onNavigate('history')}
                className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.04] text-xs font-medium transition-all cursor-pointer"
              >
                <History className="w-4 h-4" />
                <span>History</span>
              </button>
            </nav>
          </div>

          <div className="space-y-1">
            <p className="text-[10px] uppercase font-mono tracking-widest text-zinc-500 px-3">Resources</p>
            <nav className="space-y-0.5 pt-1">
              <a href="#docs" className="flex items-center gap-3 px-3 py-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.04] text-xs font-medium transition-all">
                <BookOpen className="w-4 h-4" />
                <span>Documentation</span>
              </a>
              <a href="https://github.com" target="_blank" rel="noreferrer" className="flex items-center gap-3 px-3 py-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.04] text-xs font-medium transition-all">
                <GitBranch className="w-4 h-4" />
                <span>GitHub</span>
              </a>
              <button 
                onClick={() => onNavigate && onNavigate('settings')}
                className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.04] text-xs font-medium transition-all cursor-pointer"
              >
                <Settings className="w-4 h-4" />
                <span>Settings</span>
              </button>
            </nav>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 space-y-2">
          <div className="w-6 h-6 rounded-md bg-gradient-to-tr from-cyan-400 to-pink-500 flex items-center justify-center">
            <Sparkles className="w-3 h-3 text-black font-bold" />
          </div>
          <p className="text-xs font-medium text-white leading-tight">Turn your ideas into real interfaces.</p>
          <p className="text-[10px] text-zinc-500 font-mono">Sketch → AI → Code</p>
        </div>
      </aside>

      {/* 2. Main Content Area */}
      <div className="flex-1 flex flex-col overflow-y-auto">
        <header className="h-16 border-b border-white/10 bg-[#070709]/80 backdrop-blur-xl px-8 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-2 cursor-pointer hover:bg-white/5 px-3 py-1.5 rounded-lg border border-transparent hover:border-white/10 transition-all">
            <span className="text-xs text-zinc-400">✏️</span>
            <span className="text-sm font-medium text-zinc-200">Demo Project</span>
            <ChevronDown className="w-3.5 h-3.5 text-zinc-500" />
          </div>

          <div className="flex items-center gap-3">
            <button className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-medium text-zinc-300 transition-all cursor-pointer">
              <Save className="w-3.5 h-3.5" />
              <span>Save</span>
            </button>
            <button className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-xs font-medium text-white shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all cursor-pointer">
              <Download className="w-3.5 h-3.5" />
              <span>Export</span>
              <ChevronDown className="w-3.5 h-3.5 ml-0.5" />
            </button>
          </div>
        </header>

        <main className="p-8 max-w-5xl mx-auto w-full space-y-6">
          <div className="space-y-1">
            <div className="flex items-center gap-2.5">
              <span className="w-6 h-6 rounded-md bg-blue-600 text-white font-mono text-xs flex items-center justify-center font-bold">1</span>
              <h2 className="text-lg font-semibold text-white">Upload Your Sketch</h2>
            </div>
            <p className="text-xs text-zinc-400 pl-8.5">
              Turn your wireframe into a beautiful, responsive UI.
            </p>
          </div>

          <div 
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`relative rounded-3xl border-2 border-dashed transition-all duration-300 p-12 flex flex-col items-center justify-center min-h-[380px] bg-white/[0.01] ${
              dragActive 
                ? 'border-cyan-400 bg-cyan-500/[0.04] shadow-[0_0_40px_rgba(34,211,238,0.15)]' 
                : 'border-white/10 hover:border-white/20'
            }`}
          >
            <div className="relative z-10 flex flex-col items-center text-center space-y-5">
              <div className="w-20 h-20 rounded-full bg-blue-500/10 border border-blue-500/20 flex items-center justify-center shadow-[0_0_30px_rgba(59,130,246,0.25)]">
                <CloudUpload className="w-10 h-10 text-blue-400" />
              </div>

              <div className="space-y-1.5">
                <h3 className="text-xl font-semibold tracking-tight text-white">
                  Drag & Drop your sketch here
                </h3>
                <p className="text-xs text-zinc-400 font-mono">PNG, JPG or JPEG • Max 10MB</p>
              </div>

              <div className="flex flex-col sm:flex-row items-center gap-3 pt-2">
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  onChange={(e) => handleFile(e.target.files[0])} 
                  accept="image/*" 
                  className="hidden" 
                />

                <button 
                  onClick={() => fileInputRef.current.click()}
                  className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-xs font-semibold text-white shadow-[0_0_20px_rgba(37,99,235,0.4)] transition-all cursor-pointer"
                >
                  <FolderOpen className="w-4 h-4" />
                  <span>Browse Files</span>
                </button>

                <button className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/10 text-xs font-medium text-zinc-300 transition-all cursor-pointer">
                  <Camera className="w-4 h-4 text-zinc-400" />
                  <span>Use Camera</span>
                </button>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 text-xs text-zinc-400">
            <div className="flex items-center gap-2 text-zinc-300 font-medium">
              <Lightbulb className="w-4 h-4 text-amber-400" />
              <span>Tips for better detection</span>
            </div>
            <div className="flex flex-wrap items-center gap-5 text-[11px]">
              <span className="flex items-center gap-1.5 text-emerald-400/90">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Use clear dark lines</span>
              </span>
              <span className="flex items-center gap-1.5 text-zinc-400">
                <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                <span>Keep components separated</span>
              </span>
            </div>
          </div>
        </main>
      </div>

    </div>
  );
}