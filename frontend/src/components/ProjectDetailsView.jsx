import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  ArrowLeft, 
  Calendar, 
  Clock, 
  Layers, 
  Trash2, 
  ExternalLink, 
  Copy, 
  Check, 
  Download, 
  Edit3, 
  X, 
  GitBranch, 
  FileCode2, 
  Image as ImageIcon, 
  FolderGit2, 
  Layout, 
  History,
  CheckCircle2,
  BookOpen,
  Settings,
  FileArchive,
  Loader2
} from 'lucide-react';
import { renameProject, deleteProject, formatRelativeTime, getProjects } from '../services/storage';
import { exportProjectZip } from '../services/api';

export default function ProjectDetailsView({ 
  project: initialProject, 
  onNavigate, 
  onOpenInStudio, 
  onProjectDeleted,
  onProjectRenamed 
}) {
  // Fallback to latest project if passed project is missing
  const [project, setProject] = useState(() => initialProject || getProjects()[0] || null);
  const [isEditingName, setIsEditingName] = useState(false);
  const [projectName, setProjectName] = useState(() => project?.name || 'Untitled Wireframe');
  const [codeTab, setCodeTab] = useState('jsx');
  const [copied, setCopied] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [showRawJson, setShowRawJson] = useState(false);
  const [isExportingZip, setIsExportingZip] = useState(false);

  useEffect(() => {
    if (initialProject) {
      setProject(initialProject);
      setProjectName(initialProject.name || 'Untitled Wireframe');
    }
  }, [initialProject]);

  // Handle Save Rename
  const handleSaveRename = () => {
    const trimmed = projectName.trim();
    if (!trimmed || !project?.id) {
      setIsEditingName(false);
      return;
    }
    const updated = renameProject(project.id, trimmed);
    if (updated) {
      setProject(updated);
      setProjectName(updated.name);
      if (onProjectRenamed) onProjectRenamed(updated);
      setToastMessage('Project renamed successfully');
      setShowToast(true);
      setTimeout(() => setShowToast(false), 2500);
    }
    setIsEditingName(false);
  };

  // Handle Delete Project
  const handleDelete = () => {
    if (!project?.id) return;
    deleteProject(project.id);
    if (onProjectDeleted) {
      onProjectDeleted(project.id);
    } else {
      onNavigate('projects');
    }
  };

  // 1-Click Code Copy
  const handleCopyCode = () => {
    const code = codeTab === 'jsx' 
      ? (project?.generated_code?.jsx || '// No JSX generated')
      : codeTab === 'tailwind'
      ? (project?.generated_code?.tailwind || '<!-- No Tailwind generated -->')
      : (project?.generated_code?.json || JSON.stringify(project || {}, null, 2));

    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Single-file .jsx download trigger
  const handleDownloadFile = () => {
    const jsxContent = project?.generated_code?.jsx || `// Empty UI component`;
    const blob = new Blob([jsxContent], { type: 'text/javascript' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${(project?.name || 'wireframe').toLowerCase().replace(/\s+/g, '_')}.jsx`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Full project boilerplate ZIP download trigger
  const handleExportZip = async () => {
    if (isExportingZip) return;
    setIsExportingZip(true);
    try {
      const jsxContent = project?.generated_code?.jsx || `// Empty UI component`;
      await exportProjectZip(project?.name || projectName, jsxContent);
      setToastMessage('ZIP downloaded successfully');
      setShowToast(true);
      setTimeout(() => setShowToast(false), 3000);
    } catch (err) {
      setToastMessage(err.message || 'Failed to download ZIP');
      setShowToast(true);
      setTimeout(() => setShowToast(false), 4000);
    } finally {
      setIsExportingZip(false);
    }
  };


  // If no project exists at all
  if (!project) {
    return (
      <div className="flex h-screen bg-[#070709] text-white selection:bg-pink-500 selection:text-white">
        <div className="m-auto text-center p-12 max-w-md rounded-3xl border border-white/10 bg-[#090b10] space-y-4">
          <FolderGit2 className="w-12 h-12 text-zinc-600 mx-auto" />
          <h2 className="text-base font-semibold text-white">Project Not Found</h2>
          <p className="text-xs text-zinc-400">
            No project is currently loaded or selected.
          </p>
          <button
            onClick={() => onNavigate('projects')}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-xs font-semibold text-white shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all cursor-pointer"
          >
            Back to Projects
          </button>
        </div>
      </div>
    );
  }

  const detectedElements = Array.isArray(project.detected_elements) ? project.detected_elements : [];
  const codeContent = {
    jsx: project.generated_code?.jsx || '// No JSX code generated for this project.',
    tailwind: project.generated_code?.tailwind || '<!-- No Tailwind HTML generated. -->',
    json: project.generated_code?.json || JSON.stringify(project.generated_code || {}, null, 2)
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
              onClick={() => onNavigate('projects')} 
              title="Back to Projects"
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
            <span>New Sketch</span>
          </button>

          <div className="space-y-1">
            <p className="text-[10px] uppercase font-mono tracking-widest text-zinc-500 px-3">Navigation</p>
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
                className="w-full flex items-center gap-3 px-3 py-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-xs font-medium cursor-pointer"
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
                onClick={() => onNavigate('settings')} 
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
          <p className="text-xs font-medium text-white leading-tight">Project Inspection</p>
          <p className="text-[10px] text-zinc-500 font-mono">Real CV & Code Specs</p>
        </div>
      </aside>

      {/* 2. Main Inspection Container */}
      <div className="flex-1 flex flex-col overflow-y-auto">
        
        {/* Header Bar */}
        <header className="min-h-16 border-b border-white/10 bg-[#070709]/80 backdrop-blur-xl px-8 py-3 flex flex-wrap items-center justify-between gap-4 sticky top-0 z-10 shrink-0">
          
          {/* Left: Back button & Title with inline edit */}
          <div className="flex items-center gap-3 min-w-0">
            <button
              onClick={() => onNavigate('projects')}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-medium text-zinc-300 hover:text-white transition-all cursor-pointer"
              title="Back to Projects"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back</span>
            </button>

            {/* Inline Title Editor */}
            {isEditingName ? (
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl border border-cyan-500 bg-white/[0.04]">
                <input
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleSaveRename();
                    if (e.key === 'Escape') setIsEditingName(false);
                  }}
                  onBlur={handleSaveRename}
                  autoFocus
                  className="bg-transparent text-sm font-semibold text-white outline-none w-48 sm:w-64"
                />
                <button
                  onClick={handleSaveRename}
                  className="p-1 text-cyan-400 hover:text-cyan-300 cursor-pointer"
                  title="Save name"
                >
                  <Check className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => setIsEditingName(false)}
                  className="p-1 text-zinc-400 hover:text-white cursor-pointer"
                  title="Cancel"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ) : (
              <button
                onClick={() => setIsEditingName(true)}
                className="flex items-center gap-2 px-3 py-1.5 rounded-xl border border-white/10 bg-white/[0.02] hover:border-cyan-500/30 hover:bg-white/[0.05] transition-all cursor-pointer group text-left"
                title="Click to rename project"
              >
                <span className="text-xs text-zinc-400 group-hover:text-cyan-400">✏️</span>
                <span className="text-sm font-semibold text-zinc-200 tracking-tight truncate max-w-xs sm:max-w-md">
                  {project.name}
                </span>
                <Edit3 className="w-3.5 h-3.5 text-zinc-500 opacity-0 group-hover:opacity-100 transition-opacity" />
              </button>
            )}

            {/* Metadata badges */}
            <div className="hidden xl:flex items-center gap-2 text-[11px] font-mono text-zinc-400">
              <span className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white/[0.02] border border-white/5">
                <Calendar className="w-3 h-3 text-zinc-500" />
                <span>Created {new Date(project.createdAt).toLocaleDateString()}</span>
              </span>
              <span className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white/[0.02] border border-white/5">
                <Clock className="w-3 h-3 text-cyan-400" />
                <span>{formatRelativeTime(project.updatedAt || project.createdAt)}</span>
              </span>
              <span className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
                <Layers className="w-3 h-3" />
                <span>{project.elements_count || 0} Elements</span>
              </span>
            </div>
          </div>

          {/* Right: Actions */}
          <div className="flex items-center gap-2.5 shrink-0">
            <button
              onClick={handleExportZip}
              disabled={isExportingZip}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-xs font-semibold text-cyan-300 shadow-[0_0_12px_rgba(6,182,212,0.15)] transition-all cursor-pointer disabled:opacity-50"
              title="Download ready-to-run Vite + React 19 + Tailwind project (.zip)"
            >
              {isExportingZip ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-cyan-400" />
                  <span>Packaging ZIP...</span>
                </>
              ) : (
                <>
                  <FileArchive className="w-3.5 h-3.5 text-cyan-400" />
                  <span className="hidden sm:inline">Download Full Project (.zip)</span>
                  <span className="sm:hidden">.ZIP</span>
                </>
              )}
            </button>

            <button
              onClick={() => onOpenInStudio(project)}
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 text-xs font-semibold text-white shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all cursor-pointer"
              title="Open into active Studio session"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              <span>Open in Studio</span>
            </button>

            <button
              onClick={handleDelete}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-rose-500/20 border border-white/10 hover:border-rose-500/30 text-xs font-medium text-zinc-400 hover:text-rose-400 transition-all cursor-pointer"
              title="Delete Project"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Delete</span>
            </button>
          </div>
        </header>

        {/* Sub-header on smaller screens for metadata */}
        <div className="xl:hidden px-8 py-2.5 border-b border-white/5 bg-[#090b10]/40 flex flex-wrap items-center gap-2 text-[11px] font-mono text-zinc-400">
          <span className="flex items-center gap-1 px-2 py-0.5 rounded bg-white/[0.02] border border-white/5">
            <Calendar className="w-3 h-3 text-zinc-500" />
            <span>{new Date(project.createdAt).toLocaleDateString()}</span>
          </span>
          <span className="flex items-center gap-1 px-2 py-0.5 rounded bg-white/[0.02] border border-white/5">
            <Clock className="w-3 h-3 text-cyan-400" />
            <span>{formatRelativeTime(project.updatedAt || project.createdAt)}</span>
          </span>
          <span className="flex items-center gap-1 px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <Layers className="w-3 h-3" />
            <span>{project.elements_count || 0} Elements</span>
          </span>
        </div>

        {/* Two-Column Layout */}
        <main className="p-8 max-w-[1700px] w-full grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* ============================================================ */}
          {/* LEFT PANEL (5 cols): Original Sketch & Detected Hierarchy */}
          {/* ============================================================ */}
          <div className="lg:col-span-5 space-y-6">
            
            {/* 1. Original Sketch Box */}
            <div className="rounded-2xl border border-white/10 bg-[#090b10]/80 p-5 space-y-4 backdrop-blur-xl shadow-xl">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-mono uppercase tracking-wider text-zinc-400 flex items-center gap-2">
                  <ImageIcon className="w-3.5 h-3.5 text-cyan-400" />
                  Original Wireframe Sketch
                </span>
                <span className="text-[10px] font-mono text-zinc-500">
                  {project.thumbnail ? 'Stored Base64 DataURL' : 'No Thumbnail'}
                </span>
              </div>

              <div className="rounded-xl border border-dashed border-zinc-800 bg-[#06080d] p-3 flex flex-col items-center justify-center min-h-[220px] max-h-[380px] overflow-hidden">
                {project.thumbnail || project.preview ? (
                  <img
                    src={project.thumbnail || project.preview}
                    alt={project.name}
                    className="w-full h-full max-h-[340px] object-contain rounded-lg"
                  />
                ) : (
                  <div className="text-center p-8 space-y-2">
                    <ImageIcon className="w-10 h-10 text-zinc-700 mx-auto" />
                    <p className="text-xs font-mono text-zinc-500">No sketch image stored with this project record.</p>
                  </div>
                )}
              </div>
            </div>

            {/* 2. Detected Hierarchy / Element Tree */}
            <div className="rounded-2xl border border-white/10 bg-[#090b10]/80 p-5 space-y-4 backdrop-blur-xl shadow-xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <GitBranch className="w-3.5 h-3.5 text-pink-400" />
                  <span className="text-[11px] font-mono uppercase tracking-wider text-zinc-400">
                    Detected Hierarchy & Elements
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded-md bg-white/[0.04] text-[10px] font-mono text-cyan-400">
                    {detectedElements.length} elements
                  </span>
                  <button
                    onClick={() => setShowRawJson(!showRawJson)}
                    className="text-[10px] font-mono text-zinc-400 hover:text-cyan-400 underline cursor-pointer"
                  >
                    {showRawJson ? 'Tree View' : 'Raw JSON'}
                  </button>
                </div>
              </div>

              {showRawJson ? (
                <div className="rounded-xl bg-[#06080d] border border-white/5 p-4 max-h-[360px] overflow-auto">
                  <pre className="font-mono text-[11px] text-zinc-300 leading-relaxed">
                    <code>{JSON.stringify(detectedElements, null, 2)}</code>
                  </pre>
                </div>
              ) : (
                <div className="space-y-2 max-h-[360px] overflow-y-auto pr-1">
                  {detectedElements.length === 0 ? (
                    <div className="p-6 text-center text-xs font-mono text-zinc-500">
                      No individual elements detected in this record.
                    </div>
                  ) : (
                    detectedElements.map((el, idx) => (
                      <div 
                        key={idx} 
                        className="p-3 rounded-xl bg-white/[0.015] border border-white/5 hover:border-cyan-500/20 transition-all flex items-center justify-between text-xs"
                      >
                        <div className="flex items-center gap-2.5">
                          <span className={`w-2.5 h-2.5 rounded shrink-0 ${el.color || 'bg-cyan-500'}`} />
                          <div>
                            <span className="text-zinc-200 font-medium capitalize">
                              {(el.name || 'Component').replace('_', ' ')}
                            </span>
                            {Array.isArray(el.box) && (
                              <p className="text-[10px] font-mono text-zinc-500 mt-0.5">
                                bbox: [{el.box.map(n => Math.round(n)).join(', ')}]
                              </p>
                            )}
                          </div>
                        </div>

                        <span className="font-mono text-cyan-400 text-[11px] px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">
                          {el.conf || '100%'}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>

          </div>

          {/* ============================================================ */}
          {/* RIGHT PANEL (7 cols): Generated Code Viewer & Actions */}
          {/* ============================================================ */}
          <div className="lg:col-span-7 space-y-4">
            
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono uppercase tracking-wider text-zinc-400 flex items-center gap-2">
                <FileCode2 className="w-3.5 h-3.5 text-cyan-400" />
                Synthesized Code Viewer
              </span>

              <div className="flex items-center gap-2">
                <button
                  onClick={handleCopyCode}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-medium text-zinc-300 hover:text-white transition-all cursor-pointer"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>

                <button
                  onClick={handleDownloadFile}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-medium text-zinc-300 hover:text-white transition-all cursor-pointer"
                  title="Export single .JSX file"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Export .JSX</span>
                </button>

                <button
                  onClick={handleExportZip}
                  disabled={isExportingZip}
                  className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 text-xs font-semibold text-white shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all cursor-pointer disabled:opacity-50"
                  title="Download complete Vite + React 19 + Tailwind project (.zip)"
                >
                  {isExportingZip ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin text-cyan-200" />
                      <span>Packaging ZIP...</span>
                    </>
                  ) : (
                    <>
                      <FileArchive className="w-3.5 h-3.5" />
                      <span>Download Full Project (.zip)</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Code Box with Tabs */}
            <div className="rounded-2xl border border-white/10 bg-[#06080d] shadow-2xl flex flex-col min-h-[580px] overflow-hidden">
              
              {/* Tabs */}
              <div className="flex items-center border-b border-white/5 px-4 pt-2.5 gap-2 bg-[#090b10]">
                {[
                  { id: 'jsx', label: 'React JSX' },
                  { id: 'tailwind', label: 'Tailwind Markup' },
                  { id: 'json', label: 'AST JSON' }
                ].map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setCodeTab(tab.id)}
                    className={`px-3.5 py-2 rounded-t-xl text-xs font-mono transition-all uppercase cursor-pointer ${
                      codeTab === tab.id
                        ? 'bg-[#06080d] text-cyan-400 border-t border-x border-white/10'
                        : 'text-zinc-500 hover:text-zinc-300'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Code Pre container */}
              <pre className="flex-1 p-6 font-mono text-[12px] text-zinc-300 overflow-x-auto leading-relaxed max-h-[560px] selection:bg-cyan-500/30">
                <code>{codeContent[codeTab]}</code>
              </pre>

              {/* Code footer status */}
              <div className="px-5 py-2.5 bg-black/40 border-t border-white/5 flex items-center justify-between text-[11px] font-mono text-zinc-500">
                <span>Framework: {project.generated_code?.framework || 'React + Tailwind'}</span>
                <span>Synthesized via Vision-to-Code Pipeline</span>
              </div>
            </div>

          </div>

        </main>
      </div>

      {/* Floating Rename Toast Notification */}
      {showToast && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2.5 px-4 py-2.5 rounded-xl bg-[#090b10]/95 border border-emerald-500/40 text-emerald-300 text-xs font-mono shadow-[0_0_25px_rgba(16,185,129,0.2)] backdrop-blur-xl">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{toastMessage}</span>
        </div>
      )}

    </div>
  );
}
