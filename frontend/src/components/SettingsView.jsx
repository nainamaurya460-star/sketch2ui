import React, { useState } from 'react';
import { 
  Sparkles, 
  ArrowLeft, 
  Settings, 
  Database, 
  Trash2, 
  Download, 
  CheckCircle2, 
  AlertTriangle, 
  FileCode2, 
  FolderGit2, 
  Layout, 
  History, 
  BookOpen, 
  X,
  Cpu
} from 'lucide-react';
import { 
  getSettings, 
  saveSettings, 
  getStorageUsage, 
  clearAllProjects, 
  exportAllProjectsJson 
} from '../services/storage';
import { API_BASE_URL } from '../services/api';

export default function SettingsView({ onNavigate, onStorageCleared }) {
  const [settings, setSettings] = useState(() => getSettings());
  const [storageUsage, setStorageUsage] = useState(() => getStorageUsage());
  const [isConfirmModalOpen, setIsConfirmModalOpen] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');

  const triggerToast = (msg) => {
    setToastMessage(msg);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 2500);
  };

  // Toggle state hooks setting
  const handleToggleMockHooks = () => {
    const updated = saveSettings({
      includeMockStateHooks: !settings.includeMockStateHooks
    });
    setSettings(updated);
    triggerToast(
      updated.includeMockStateHooks 
        ? "Enabled inline interactive state hooks" 
        : "Switched to clean stateless presentation markup"
    );
  };

  // Export full JSON backup
  const handleExportBackup = () => {
    const jsonStr = exportAllProjectsJson();
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `sketch2ui_backup_${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    triggerToast("Exported all projects and history as JSON backup");
  };

  // Confirm clear all projects
  const handleClearAllConfirm = () => {
    clearAllProjects();
    setStorageUsage(getStorageUsage());
    setIsConfirmModalOpen(false);
    triggerToast("All projects and conversion logs cleared");
    if (onStorageCleared) {
      onStorageCleared();
    }
  };

  return (
    <div className="flex h-screen bg-[#070709] text-white selection:bg-pink-500 selection:text-white overflow-hidden">
      
      {/* 1. Left Sidebar Navigation */}
      <aside className="w-64 border-r border-white/10 bg-[#090b10]/90 backdrop-blur-2xl flex flex-col justify-between p-5 z-20 shrink-0">
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-400 to-pink-500 flex items-center justify-center shadow-[0_0_15px_#22d3ee]">
                <Sparkles className="w-4 h-4 text-black font-bold" />
              </div>
              <span className="font-semibold tracking-wider text-base text-white">Sketch2UI</span>
            </div>
            <button 
              onClick={() => onNavigate('landing')} 
              title="Back to Landing"
              className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-zinc-400 hover:text-white transition-all cursor-pointer"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
          </div>

          <button 
            onClick={() => onNavigate('studio')} 
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 text-xs font-semibold uppercase tracking-wider text-white shadow-[0_0_20px_rgba(6,182,212,0.35)] transition-all cursor-pointer"
          >
            <Sparkles className="w-4 h-4" />
            <span>Launch Studio</span>
          </button>

          <div className="space-y-1">
            <p className="text-[10px] uppercase font-mono tracking-widest text-zinc-500 px-3">Workspace</p>
            <nav className="space-y-0.5 pt-1">
              <button 
                onClick={() => onNavigate('studio')} 
                className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.04] text-xs font-medium transition-all cursor-pointer"
              >
                <Layout className="w-4 h-4" />
                <span>Workspace</span>
              </button>
              <button 
                onClick={() => onNavigate('projects')} 
                className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.04] text-xs font-medium transition-all cursor-pointer"
              >
                <FolderGit2 className="w-4 h-4" />
                <span>Projects</span>
              </button>
              <button 
                onClick={() => onNavigate('history')} 
                className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.04] text-xs font-medium transition-all cursor-pointer"
              >
                <History className="w-4 h-4" />
                <span>History</span>
              </button>
            </nav>
          </div>

          <div className="space-y-1">
            <p className="text-[10px] uppercase font-mono tracking-widest text-zinc-500 px-3">System</p>
            <nav className="space-y-0.5 pt-1">
              <button 
                onClick={() => onNavigate('docs')} 
                className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.04] text-xs font-medium transition-all cursor-pointer"
              >
                <BookOpen className="w-4 h-4" />
                <span>Documentation</span>
              </button>
              <button 
                className="w-full flex items-center gap-3 px-3 py-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-xs font-medium cursor-pointer"
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
          <p className="text-xs font-medium text-white leading-tight">Preferences & Storage</p>
          <p className="text-[10px] text-zinc-500 font-mono">React 19 • Tailwind CSS</p>
        </div>
      </aside>

      {/* 2. Main Settings Content */}
      <div className="flex-1 flex flex-col overflow-y-auto">
        
        {/* Header Bar */}
        <header className="h-16 border-b border-white/10 px-8 flex items-center justify-between sticky top-0 bg-[#070709]/80 backdrop-blur-xl z-10 shrink-0">
          <div className="flex items-center gap-3">
            <h1 className="text-sm font-semibold tracking-tight text-white">System Settings & Preferences</h1>
            <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-[11px] font-mono">
              sketch2ui_settings
            </span>
          </div>

          <span className="text-xs font-mono text-zinc-500">
            Engine Config: v1.0.0
          </span>
        </header>

        {/* Settings Body */}
        <main className="p-8 max-w-4xl w-full mx-auto space-y-8 pb-24">
          
          {/* SECTION 1: Real Code Export Preferences */}
          <section className="rounded-2xl border border-white/10 bg-[#090b10]/80 p-6 space-y-5 backdrop-blur-xl shadow-xl">
            <div className="flex items-center gap-2 pb-2 border-b border-white/5">
              <FileCode2 className="w-4 h-4 text-cyan-400" />
              <h2 className="text-sm font-semibold text-white">Code Export & Architecture Preferences</h2>
            </div>

            <div className="space-y-4">
              
              {/* Framework Item */}
              <div className="flex items-center justify-between p-4 rounded-xl bg-white/[0.015] border border-white/5">
                <div>
                  <h3 className="text-xs font-semibold text-white">Target Framework</h3>
                  <p className="text-[11px] text-zinc-400 mt-0.5">
                    Standard output targeting modern functional component architecture.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-1 rounded-md bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 font-mono text-[11px]">
                    React 19 (Active)
                  </span>
                </div>
              </div>

              {/* Styling System Item */}
              <div className="flex items-center justify-between p-4 rounded-xl bg-white/[0.015] border border-white/5">
                <div>
                  <h3 className="text-xs font-semibold text-white">Styling Engine</h3>
                  <p className="text-[11px] text-zinc-400 mt-0.5">
                    Atomic utilities with glassmorphic cards and dark luxury palette.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-1 rounded-md bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 font-mono text-[11px]">
                    Tailwind CSS (Active)
                  </span>
                </div>
              </div>

              {/* Target Format & Interactive Hooks Toggle */}
              <div className="flex items-center justify-between p-4 rounded-xl bg-white/[0.015] border border-white/5">
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <h3 className="text-xs font-semibold text-white">Mock State Hooks (`useState`)</h3>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/[0.04] text-zinc-400">
                      Functional Component JSX
                    </span>
                  </div>
                  <p className="text-[11px] text-zinc-400">
                    Include inline mock state bindings for input text and checkboxes vs pure presentation markup.
                  </p>
                </div>

                <button
                  onClick={handleToggleMockHooks}
                  className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                    settings.includeMockStateHooks ? 'bg-cyan-500' : 'bg-zinc-800'
                  }`}
                  role="switch"
                  aria-checked={settings.includeMockStateHooks}
                >
                  <span
                    className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-lg ring-0 transition duration-200 ease-in-out ${
                      settings.includeMockStateHooks ? 'translate-x-5' : 'translate-x-0'
                    }`}
                  />
                </button>
              </div>

            </div>
          </section>

          {/* SECTION 2: Real Storage Management */}
          <section className="rounded-2xl border border-white/10 bg-[#090b10]/80 p-6 space-y-5 backdrop-blur-xl shadow-xl">
            <div className="flex items-center justify-between pb-2 border-b border-white/5">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-pink-400" />
                <h2 className="text-sm font-semibold text-white">Local Storage & Backup Management</h2>
              </div>
              <span className="text-[11px] font-mono text-zinc-500">Key: sketch2ui_projects</span>
            </div>

            {/* Storage Usage Metrics Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="p-4 rounded-xl bg-white/[0.015] border border-white/5 space-y-1">
                <span className="text-[10px] font-mono uppercase text-zinc-500">Saved Projects</span>
                <p className="text-lg font-bold font-mono text-white">{storageUsage.count}</p>
                <p className="text-[10px] text-zinc-400">Recorded wireframes</p>
              </div>

              <div className="p-4 rounded-xl bg-white/[0.015] border border-white/5 space-y-1">
                <span className="text-[10px] font-mono uppercase text-zinc-500">Storage Used</span>
                <p className="text-lg font-bold font-mono text-cyan-400">{storageUsage.kb} KB</p>
                <p className="text-[10px] text-zinc-400">Approx. localStorage</p>
              </div>

              <div className="p-4 rounded-xl bg-white/[0.015] border border-white/5 space-y-1">
                <span className="text-[10px] font-mono uppercase text-zinc-500">Quota Limit</span>
                <p className="text-lg font-bold font-mono text-zinc-300">~5,120 KB</p>
                <p className="text-[10px] text-zinc-400">Standard browser quota</p>
              </div>
            </div>

            {/* Storage Action Buttons */}
            <div className="flex flex-wrap items-center justify-between gap-4 pt-2">
              <button
                onClick={handleExportBackup}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-medium text-zinc-300 hover:text-white transition-all cursor-pointer"
                title="Download full JSON backup of all saved projects"
              >
                <Download className="w-3.5 h-3.5 text-cyan-400" />
                <span>Export All Projects as JSON</span>
              </button>

              <button
                onClick={() => setIsConfirmModalOpen(true)}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 hover:border-rose-500/40 text-xs font-semibold text-rose-400 transition-all cursor-pointer"
                title="Permanently remove all projects from local storage"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Clear All Projects & History</span>
              </button>
            </div>
          </section>

          {/* SECTION 3: Active AI & Vision Specs */}
          <section className="rounded-2xl border border-white/10 bg-[#090b10]/60 p-5 space-y-3">
            <div className="flex items-center gap-2">
              <Cpu className="w-3.5 h-3.5 text-cyan-400" />
              <h3 className="text-xs font-semibold text-zinc-300 uppercase tracking-wider font-mono">
                Hardware & Vision Runtime Specs
              </h3>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-[11px] font-mono text-zinc-400">
              <div className="p-2.5 rounded-lg bg-black/40 border border-white/5">
                <span className="text-zinc-500">Vision Weights: </span>
                <span className="text-zinc-200">app/models/best.pt (YOLOv8n)</span>
              </div>
              <div className="p-2.5 rounded-lg bg-black/40 border border-white/5">
                <span className="text-zinc-500">Backend Server: </span>
                <span className="text-zinc-200">FastAPI @ {API_BASE_URL}</span>
              </div>
              <div className="p-2.5 rounded-lg bg-black/40 border border-white/5">
                <span className="text-zinc-500">Warp Engine: </span>
                <span className="text-zinc-200">OpenCV 4-Point Homography</span>
              </div>
              <div className="p-2.5 rounded-lg bg-black/40 border border-white/5">
                <span className="text-zinc-500">Supported Classes: </span>
                <span className="text-cyan-400">10 Primitives</span>
              </div>
            </div>
          </section>

        </main>
      </div>

      {/* Confirmation Modal for Clearing All Storage */}
      {isConfirmModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="w-full max-w-md p-6 rounded-3xl border border-rose-500/30 bg-[#090b10] shadow-2xl space-y-5 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-rose-400">
                <AlertTriangle className="w-5 h-5" />
                <h3 className="text-sm font-bold text-white">Clear All Projects?</h3>
              </div>
              <button
                onClick={() => setIsConfirmModalOpen(false)}
                className="p-1 rounded-lg text-zinc-500 hover:text-white cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-xs text-zinc-300 leading-relaxed">
              This action will permanently delete all <strong className="text-white">{storageUsage.count} projects</strong> and conversion history from your browser's local storage. This cannot be undone.
            </p>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setIsConfirmModalOpen(false)}
                className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-xs font-medium text-zinc-300 transition-all cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleClearAllConfirm}
                className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-xs font-semibold text-white shadow-[0_0_15px_rgba(225,29,72,0.4)] transition-all cursor-pointer"
              >
                Confirm & Clear Everything
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Floating Settings Toast Notification */}
      {showToast && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2.5 px-4 py-2.5 rounded-xl bg-[#090b10]/95 border border-cyan-500/40 text-cyan-300 text-xs font-mono shadow-[0_0_25px_rgba(6,182,212,0.2)] backdrop-blur-xl">
          <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" />
          <span>{toastMessage}</span>
        </div>
      )}

    </div>
  );
}
