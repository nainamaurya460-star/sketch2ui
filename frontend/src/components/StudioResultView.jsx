import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  Plus, 
  Layout, 
  FolderGit2, 
  History, 
  BookOpen, 
  GitBranch, 
  Settings, 
  Layers, 
  Cpu, 
  Download, 
  Monitor, 
  Tablet, 
  Smartphone, 
  Copy, 
  Check, 
  CheckCircle2,
  ArrowLeft,
  FileCode2,
  Save,
  FileArchive,
  Loader2,
  RotateCcw
} from 'lucide-react';
import { saveProject } from '../services/storage';
import { exportProjectZip } from '../services/api';
import ComponentInspector from './ComponentInspector';
import { generateJsxAndTailwind } from '../utils/astCodeGenerator';

export default function StudioResultView({ data, sketchImage, onReset, onNavigate, onProjectUpdated }) {
  const [deviceView, setDeviceView] = useState('desktop');
  const [codeTab, setCodeTab] = useState('jsx');
  const [copied, setCopied] = useState(false);

  // Fallback defaults
  const [projectName, setProjectName] = useState(() => {
    return data?.name || data?.project_name || `Wireframe - ${new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
  });
  const [isEditingName, setIsEditingName] = useState(false);
  const [isSaved, setIsSaved] = useState(() => Boolean(data?.id));
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [isExportingZip, setIsExportingZip] = useState(false);

  // Human-in-the-Loop Elements State
  const [elements, setElements] = useState(() => {
    const raw = data?.detected_elements || [];
    return raw.map((el, i) => ({
      ...el,
      id: el.id || `node_${i}_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`
    }));
  });

  // Original snapshot of AI detection for Revert action
  const [originalElements, setOriginalElements] = useState(() => {
    const raw = data?.detected_elements || [];
    return JSON.parse(JSON.stringify(raw));
  });

  // Selected Element for Inspector Drawer
  const [selectedElementId, setSelectedElementId] = useState(null);

  // Dynamic Synthesized Code State
  const [codeSnippets, setCodeSnippets] = useState(() => {
    if (data?.generated_code?.jsx) {
      return {
        jsx: data.generated_code.jsx,
        tailwind: data.generated_code.tailwind || '',
        json: data.generated_code.json || JSON.stringify(data.detected_elements || [], null, 2)
      };
    }
    const raw = data?.detected_elements || [];
    return generateJsxAndTailwind(raw, data?.name || data?.project_name);
  });

  useEffect(() => {
    if (data?.name || data?.project_name) {
      setProjectName(data.name || data.project_name);
    }
    if (data?.id) {
      setIsSaved(true);
    }
    if (data?.detected_elements && Array.isArray(data.detected_elements)) {
      const initialized = data.detected_elements.map((el, i) => ({
        ...el,
        id: el.id || `node_${i}_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`
      }));
      setElements(initialized);
      setOriginalElements(JSON.parse(JSON.stringify(data.detected_elements)));

      if (data.generated_code?.jsx) {
        setCodeSnippets({
          jsx: data.generated_code.jsx,
          tailwind: data.generated_code.tailwind || '',
          json: data.generated_code.json || JSON.stringify(initialized, null, 2)
        });
      } else {
        const synthesized = generateJsxAndTailwind(initialized, data.name || data.project_name);
        setCodeSnippets(synthesized);
      }
    }
  }, [data]);

  // Synchronous Auto-Save Helper
  const autoSaveCurrentAst = (currentElements, currentCode, currentName) => {
    const nameToUse = (currentName || projectName).trim() || 'Untitled Wireframe';
    const projectPayload = {
      id: data?.id || `proj_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
      name: nameToUse,
      createdAt: data?.createdAt || new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      thumbnail: sketchImage || data?.thumbnail || data?.preview || '',
      elements_count: currentElements.length,
      detected_elements: currentElements,
      generated_code: {
        framework: 'React + Tailwind',
        jsx: currentCode.jsx,
        tailwind: currentCode.tailwind,
        json: currentCode.json,
      }
    };
    const saved = saveProject(projectPayload);
    if (onProjectUpdated) {
      onProjectUpdated(saved);
    }
    setIsSaved(true);
  };

  // Update properties on the active element
  const handleUpdateElement = (updatedFields) => {
    if (!selectedElementId) return;

    setElements((prev) => {
      const updated = prev.map((el) => {
        if (el.id === selectedElementId) {
          return { ...el, ...updatedFields };
        }
        return el;
      });

      const newCode = generateJsxAndTailwind(updated, projectName);
      setCodeSnippets(newCode);
      autoSaveCurrentAst(updated, newCode, projectName);

      return updated;
    });
  };

  // Delete element from AST
  const handleDeleteElement = (elementId) => {
    setElements((prev) => {
      const updated = prev.filter((el) => el.id !== elementId);
      setSelectedElementId(null);

      const newCode = generateJsxAndTailwind(updated, projectName);
      setCodeSnippets(newCode);
      autoSaveCurrentAst(updated, newCode, projectName);

      setToastMessage('Element removed from layout');
      setShowToast(true);
      setTimeout(() => setShowToast(false), 2500);

      return updated;
    });
  };

  // Reset to Original AI Detection
  const handleResetToOriginal = () => {
    const restored = originalElements.map((el, i) => ({
      ...el,
      id: el.id || `node_${i}_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`
    }));
    setElements(restored);
    setSelectedElementId(null);

    const newCode = generateJsxAndTailwind(restored, projectName);
    setCodeSnippets(newCode);
    autoSaveCurrentAst(restored, newCode, projectName);

    setToastMessage('Reverted to original AI detection');
    setShowToast(true);
    setTimeout(() => setShowToast(false), 2500);
  };

  // Save Project Handler
  const handleSaveProject = (customName) => {
    const nameToUse = (typeof customName === 'string' ? customName : projectName).trim() || 'Untitled Wireframe';
    autoSaveCurrentAst(elements, codeSnippets, nameToUse);
    setToastMessage('Saved successfully');
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  // Clipboard copy handler
  const handleCopy = () => {
    navigator.clipboard.writeText(codeSnippets[codeTab]);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Real .jsx file download handler
  const handleDownloadFile = () => {
    const element = document.createElement("a");
    const file = new Blob([codeSnippets.jsx], { type: 'text/javascript' });
    element.href = URL.createObjectURL(file);
    element.download = `${projectName.toLowerCase().replace(/\s+/g, '_')}.jsx`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  // In-Memory Project ZIP export handler
  const handleExportZip = async () => {
    if (isExportingZip) return;
    setIsExportingZip(true);
    try {
      await exportProjectZip(projectName, codeSnippets.jsx);
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

  const selectedElement = elements.find(el => el.id === selectedElementId);

  return (
    <div className="flex h-screen bg-[#070709] text-white selection:bg-pink-500 selection:text-white overflow-hidden">
      
      {/* 1. Left Navigation Sidebar */}
      <aside className="w-64 border-r border-white/10 bg-[#090b10]/90 backdrop-blur-2xl flex flex-col justify-between p-5 z-20 shrink-0">
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-400 to-pink-500 flex items-center justify-center shadow-[0_0_15px_#22d3ee]">
                <Sparkles className="w-4 h-4 text-black font-bold" />
              </div>
              <span className="font-semibold tracking-wider text-base text-white">Sketch2UI</span>
            </div>
            {onReset && (
              <button 
                onClick={onReset}
                title="New Upload"
                className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-zinc-400 hover:text-white transition-all cursor-pointer"
              >
                <ArrowLeft className="w-4 h-4" />
              </button>
            )}
          </div>

          <button 
            onClick={onReset}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 text-xs font-semibold uppercase tracking-wider text-white shadow-[0_0_20px_rgba(6,182,212,0.35)] transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>New Project</span>
          </button>

          <div className="space-y-1">
            <p className="text-[10px] uppercase font-mono tracking-widest text-zinc-500 px-3">Workspace</p>
            <nav className="space-y-0.5 pt-1">
              <button 
                onClick={onReset}
                className="w-full flex items-center gap-3 px-3 py-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-xs font-medium cursor-pointer"
              >
                <Layout className="w-4 h-4" />
                <span>Workspace</span>
              </button>
              <button 
                onClick={() => onNavigate && onNavigate("projects")}
                className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.04] text-xs font-medium transition-all cursor-pointer"
              >
                <FolderGit2 className="w-4 h-4" />
                <span>Projects</span>
              </button>
              <button 
                onClick={() => onNavigate && onNavigate("history")}
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
              <button 
                type="button"
                onClick={() => onNavigate && onNavigate("docs")} 
                className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.04] text-xs font-medium transition-all cursor-pointer"
              >
                <BookOpen className="w-4 h-4" />
                <span>Documentation</span>
              </button>
              <a href="https://github.com/nainamaurya460-star/sketch2ui" target="_blank" rel="noreferrer" className="flex items-center gap-3 px-3 py-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.04] text-xs font-medium transition-all">
                <GitBranch className="w-4 h-4" />
                <span>GitHub</span>
              </a>
              <button 
                type="button"
                onClick={() => onNavigate && onNavigate("settings")} 
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

      {/* 2. Main Studio Content */}
      <div className="flex-1 flex flex-col overflow-y-auto">
        <header className="h-16 border-b border-white/10 bg-[#070709]/80 backdrop-blur-xl px-8 flex items-center justify-between sticky top-0 z-10 shrink-0">
          <div className="flex items-center gap-3">
            {isEditingName ? (
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg border border-cyan-500 bg-white/[0.04]">
                <input
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      setIsEditingName(false);
                      handleSaveProject(projectName);
                    } else if (e.key === 'Escape') {
                      setIsEditingName(false);
                    }
                  }}
                  onBlur={() => {
                    setIsEditingName(false);
                    handleSaveProject(projectName);
                  }}
                  autoFocus
                  className="bg-transparent text-sm font-medium text-white outline-none w-48 sm:w-64"
                />
                <button
                  onClick={() => {
                    setIsEditingName(false);
                    handleSaveProject(projectName);
                  }}
                  className="p-1 text-cyan-400 hover:text-cyan-300 cursor-pointer"
                  title="Save name"
                >
                  <Check className="w-3.5 h-3.5" />
                </button>
              </div>
            ) : (
              <button
                onClick={() => setIsEditingName(true)}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-white/10 bg-white/[0.02] hover:border-cyan-500/30 hover:bg-white/[0.05] transition-all cursor-pointer group"
                title="Click to rename project"
              >
                <span className="text-xs text-zinc-400 group-hover:text-cyan-400">✏️</span>
                <span className="text-sm font-medium text-zinc-200">{projectName}</span>
              </button>
            )}

            {isSaved ? (
              <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[11px] font-mono">
                <CheckCircle2 className="w-3 h-3" />
                <span>Saved successfully</span>
              </span>
            ) : (
              <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-[11px] font-mono">
                <Sparkles className="w-3 h-3" />
                <span>Draft</span>
              </span>
            )}
          </div>

          <div className="flex items-center gap-2.5">
            <button 
              onClick={handleResetToOriginal}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-medium text-zinc-400 hover:text-white transition-all cursor-pointer"
              title="Reset all manual edits back to initial AI detection"
            >
              <RotateCcw className="w-3.5 h-3.5 text-zinc-400" />
              <span>Reset AI</span>
            </button>
            <button 
              onClick={() => handleSaveProject(projectName)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-xs font-medium text-cyan-300 shadow-[0_0_12px_rgba(6,182,212,0.15)] transition-all cursor-pointer"
              title="Save Project to Local Storage"
            >
              <Save className="w-3.5 h-3.5 text-cyan-400" />
              <span>Save</span>
            </button>
            <button 
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-medium text-zinc-300 transition-all cursor-pointer"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied!' : 'Copy Code'}</span>
            </button>
            <button 
              onClick={handleDownloadFile}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-medium text-zinc-300 transition-all cursor-pointer"
              title="Download single .JSX component"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export .JSX</span>
            </button>
            <button 
              onClick={handleExportZip}
              disabled={isExportingZip}
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 text-xs font-semibold text-white shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all cursor-pointer disabled:opacity-50"
              title="Download ready-to-run Vite + React 19 + Tailwind project (.zip)"
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
        </header>

        <div className="px-8 py-3.5 border-b border-white/5 bg-[#090b10]/40 flex flex-wrap items-center justify-between gap-4 shrink-0">
          <div>
            <h2 className="text-lg font-semibold tracking-tight text-white">{projectName}</h2>
            <p className="text-xs text-zinc-400">Click any rendered element below to edit text, swap types, or delete from the layout.</p>
          </div>

          <div className="flex items-center gap-3 text-xs font-mono text-zinc-400">
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/[0.02] border border-white/5">
              <Layers className="w-3.5 h-3.5 text-cyan-400" />
              <span>{elements.length} Components</span>
            </span>
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/[0.02] border border-white/5 text-pink-400">
              <Cpu className="w-3.5 h-3.5" />
              <span>YOLOv8 + CV Engine</span>
            </span>
          </div>
        </div>

        {/* Studio Workspace 3-Column Layout */}
        <main className="p-8 grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 items-start">
          
          {/* LEFT: Wireframe Source + Detected Elements List */}
          <div className="lg:col-span-3 space-y-4">
            <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/10 space-y-3">
              <span className="text-[11px] font-mono uppercase tracking-wider text-zinc-400 flex items-center justify-between">
                <span>Input Source</span>
                <span className="text-cyan-400 text-[10px]">Active</span>
              </span>
              <div className="rounded-xl border border-dashed border-zinc-700/80 p-2 bg-[#0a0d14] flex flex-col items-center justify-center min-h-[180px] overflow-hidden">
                {sketchImage ? (
                  <img 
                    src={sketchImage} 
                    alt="Original Sketch" 
                    className="w-full max-h-48 object-contain rounded-lg"
                  />
                ) : (
                  <div className="text-center p-4 text-xs font-mono text-zinc-500">
                    Demo Wireframe Preview
                  </div>
                )}
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/10 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-mono uppercase tracking-wider text-zinc-400">Detected Classes</span>
                <span className="text-[10px] font-mono text-cyan-400">{elements.length} elements</span>
              </div>
              <div className="space-y-1.5 max-h-[260px] overflow-y-auto pr-1">
                {elements.map((item, idx) => (
                  <div 
                    key={item.id || idx} 
                    onClick={() => setSelectedElementId(item.id)}
                    className={`flex items-center justify-between p-2 rounded-xl border text-xs cursor-pointer transition-all ${
                      selectedElementId === item.id 
                        ? 'border-cyan-500 bg-cyan-500/10 text-cyan-300' 
                        : 'border-white/5 bg-white/[0.015] hover:border-cyan-500/30 text-zinc-300'
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <span className={`w-2.5 h-2.5 rounded shrink-0 ${item.color || 'bg-cyan-500'}`} />
                      <span className="font-medium capitalize truncate">{item.name.replace('_', ' ')}</span>
                      {item.text && <span className="text-[10px] text-zinc-500 truncate">"{item.text}"</span>}
                    </div>
                    <span className="font-mono text-zinc-400 text-[11px] shrink-0">{item.conf || '95%'}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* CENTER: Interactive Sandbox Canvas with Selection Bounds */}
          <div className="lg:col-span-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono uppercase tracking-wider text-zinc-400">Interactive Sandbox</span>
              <div className="flex items-center gap-1 p-1 rounded-xl bg-white/[0.04] border border-white/10 text-xs">
                <button 
                  onClick={() => setDeviceView('desktop')}
                  className={`p-1.5 rounded-lg transition-all cursor-pointer ${deviceView === 'desktop' ? 'bg-cyan-500/20 text-cyan-400' : 'text-zinc-400 hover:text-white'}`}
                >
                  <Monitor className="w-3.5 h-3.5" />
                </button>
                <button 
                  onClick={() => setDeviceView('tablet')}
                  className={`p-1.5 rounded-lg transition-all cursor-pointer ${deviceView === 'tablet' ? 'bg-cyan-500/20 text-cyan-400' : 'text-zinc-400 hover:text-white'}`}
                >
                  <Tablet className="w-3.5 h-3.5" />
                </button>
                <button 
                  onClick={() => setDeviceView('mobile')}
                  className={`p-1.5 rounded-lg transition-all cursor-pointer ${deviceView === 'mobile' ? 'bg-cyan-500/20 text-cyan-400' : 'text-zinc-400 hover:text-white'}`}
                >
                  <Smartphone className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-[#0d1017] shadow-2xl overflow-hidden flex flex-col min-h-[500px]">
              <div className="px-4 py-2 bg-black/40 border-b border-white/5 flex items-center justify-between">
                <div className="flex gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-rose-500/80" />
                  <div className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
                </div>
                <div className="px-3 py-0.5 rounded-md bg-white/[0.03] border border-white/5 text-[11px] font-mono text-zinc-400">
                  <span>sandbox:render</span>
                </div>
                <span className="text-[10px] font-mono text-zinc-500">Click elements to inspect</span>
              </div>

              <div className="flex-1 p-6 flex items-center justify-center bg-[#08090e]">
                <div className={`transition-all duration-300 w-full ${
                  deviceView === 'mobile' ? 'max-w-[280px]' : deviceView === 'tablet' ? 'max-w-[340px]' : 'max-w-sm'
                }`}>
                  <div className="w-full bg-[#090b10]/95 border border-white/10 text-white rounded-3xl shadow-2xl p-6 space-y-4 backdrop-blur-xl">
                    <h3 className="text-lg font-bold tracking-tight text-center text-white">{projectName}</h3>
                    {elements && elements.length > 0 ? (
                      elements.map((el, i) => {
                        const isSelected = selectedElementId === el.id;
                        const type = (el.name || "").toLowerCase();
                        const customText = (el.text || "").trim();

                        return (
                          <div
                            key={el.id || i}
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedElementId(el.id);
                            }}
                            className={`relative group rounded-2xl p-1.5 transition-all cursor-pointer ${
                              isSelected
                                ? 'ring-2 ring-cyan-400 bg-cyan-500/[0.08] shadow-[0_0_20px_rgba(6,182,212,0.25)]'
                                : 'hover:ring-1 hover:ring-cyan-400/50 hover:bg-white/[0.02]'
                            }`}
                            title="Click to inspect and edit element"
                          >
                            {/* Floating Element Pill on Hover/Select */}
                            <div className={`absolute -top-2.5 right-2 px-2 py-0.5 rounded-full text-[9px] font-mono uppercase tracking-wider transition-opacity flex items-center gap-1 z-10 ${
                              isSelected
                                ? 'bg-cyan-500 text-black font-bold shadow'
                                : 'bg-black/90 text-cyan-400 border border-cyan-500/30 opacity-0 group-hover:opacity-100'
                            }`}>
                              <span>{el.name || 'Component'}</span>
                              {isSelected && <span>• Selected</span>}
                            </div>

                            {/* Rendered Element */}
                            {(() => {
                              if (type.includes("heading") || type.includes("title") || type.includes("header")) {
                                return <h4 className="text-base font-bold text-white tracking-tight">{customText || "Section Title"}</h4>;
                              }
                              if (type.includes("button") || type.includes("btn") || type.includes("submit")) {
                                const isSec = el.variant === 'secondary';
                                return (
                                  <button className={`w-full px-4 py-2.5 rounded-xl font-semibold text-xs shadow-lg transition-all pointer-events-none ${
                                    isSec 
                                      ? 'border border-white/10 bg-white/5 text-zinc-300' 
                                      : 'bg-cyan-500 text-black shadow-cyan-500/20'
                                  }`}>
                                    {customText || (isSec ? "Cancel" : "Action Button")}
                                  </button>
                                );
                              }
                              if (type.includes("text") || type.includes("input")) {
                                const isPwd = customText.toLowerCase().includes("password");
                                return (
                                  <input 
                                    type={isPwd ? "password" : "text"} 
                                    placeholder={customText || "Enter text..."} 
                                    readOnly 
                                    className="w-full px-3.5 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-xs placeholder-zinc-500 focus:outline-none pointer-events-none" 
                                  />
                                );
                              }
                              if (type.includes("image") || type.includes("img") || type.includes("photo")) {
                                return (
                                  <div className="w-full aspect-video rounded-xl bg-white/5 border border-dashed border-white/10 flex items-center justify-center text-zinc-500 text-xs font-mono">
                                    {customText || "Image Placeholder"}
                                  </div>
                                );
                              }
                              if (type.includes("paragraph") || type.includes("desc")) {
                                return <p className="text-xs text-zinc-400 leading-relaxed">{customText || "Turn sketches into production-ready UI components."}</p>;
                              }
                              if (type.includes("label")) {
                                return <label className="block text-xs font-medium text-zinc-300">{customText || "Label Field"}</label>;
                              }
                              if (type.includes("check")) {
                                return (
                                  <label className="flex items-center gap-2 text-xs text-zinc-300 pointer-events-none">
                                    <input type="checkbox" className="w-4 h-4 rounded bg-white/5 border-white/10 text-cyan-500" readOnly />
                                    <span>{customText || "Option Checkbox"}</span>
                                  </label>
                                );
                              }
                              if (type.includes("radio")) {
                                return (
                                  <label className="flex items-center gap-2 text-xs text-zinc-300 pointer-events-none">
                                    <input type="radio" name="preview-radio" defaultChecked readOnly className="w-4 h-4 bg-white/5 border-white/10 text-cyan-500" />
                                    <span>{customText || "Radio Option"}</span>
                                  </label>
                                );
                              }
                              if (type.includes("select") || type.includes("dropdown")) {
                                return (
                                  <select disabled className="w-full px-3.5 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-xs pointer-events-none">
                                    <option>{customText || "Select Option"}</option>
                                  </select>
                                );
                              }
                              if (type.includes("link") || type.includes("anchor")) {
                                return <span className="text-xs text-cyan-400 underline underline-offset-2">{customText || "Learn More →"}</span>;
                              }
                              return (
                                <div className="p-3 rounded-xl bg-white/5 border border-white/10 text-xs text-zinc-300">
                                  {customText || el.name || "Component"}
                                </div>
                              );
                            })()}
                          </div>
                        );
                      })
                    ) : (
                      <div className="text-center p-8 text-xs font-mono text-zinc-500">
                        No elements in layout. Click New Project or Reset AI.
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="px-4 py-2 bg-black/30 border-t border-white/5 flex items-center justify-between text-[11px] text-zinc-400 font-mono">
                <span className="flex items-center gap-1.5 text-emerald-400">
                  <CheckCircle2 className="w-3 h-3" />
                  <span>Deterministic AST Renderer</span>
                </span>
                <span className="text-zinc-500">Interactive Canvas</span>
              </div>
            </div>
          </div>

          {/* RIGHT: Generated Code Tabs & Actions */}
          <div className="lg:col-span-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono uppercase tracking-wider text-zinc-400 flex items-center gap-2">
                <FileCode2 className="w-3.5 h-3.5 text-cyan-400" />
                Live Generated Code
              </span>
              <div className="flex items-center gap-2">
                <button 
                  onClick={handleCopy}
                  className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-xs text-zinc-300 hover:text-white transition-all cursor-pointer"
                >
                  {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
                <button 
                  onClick={handleDownloadFile}
                  className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-xs text-zinc-300 hover:text-white transition-all cursor-pointer"
                  title="Download single .JSX file"
                >
                  <Download className="w-3 h-3" />
                  <span>.JSX</span>
                </button>
                <button 
                  onClick={handleExportZip}
                  disabled={isExportingZip}
                  className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-xs text-cyan-300 hover:text-cyan-200 transition-all cursor-pointer disabled:opacity-50"
                  title="Download Full Project ZIP"
                >
                  {isExportingZip ? (
                    <>
                      <Loader2 className="w-3 h-3 animate-spin text-cyan-400" />
                      <span>Packaging...</span>
                    </>
                  ) : (
                    <>
                      <FileArchive className="w-3 h-3 text-cyan-400" />
                      <span>.ZIP</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-[#06080d] shadow-2xl flex flex-col min-h-[500px]">
              <div className="flex items-center border-b border-white/5 px-3 pt-2 gap-1 bg-[#090b10]">
                {['jsx', 'tailwind', 'json'].map((tab) => (
                  <button 
                    key={tab}
                    onClick={() => setCodeTab(tab)}
                    className={`px-3 py-1.5 rounded-t-lg text-xs font-mono transition-all uppercase cursor-pointer ${
                      codeTab === tab 
                        ? 'bg-[#06080d] text-cyan-400 border-t border-x border-white/10' 
                        : 'text-zinc-500 hover:text-zinc-300'
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              <pre className="flex-1 p-4 font-mono text-[11px] text-zinc-300 overflow-x-auto leading-relaxed max-h-[460px] selection:bg-cyan-500/30">
                <code>{codeSnippets[codeTab]}</code>
              </pre>
            </div>
          </div>

        </main>
      </div>

      {/* 3. Component Inspector Drawer */}
      {selectedElement && (
        <ComponentInspector
          element={selectedElement}
          onUpdateElement={handleUpdateElement}
          onDeleteElement={handleDeleteElement}
          onClose={() => setSelectedElementId(null)}
        />
      )}

      {/* Floating Save Toast Feedback */}
      {showToast && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2.5 px-4 py-2.5 rounded-xl bg-[#090b10]/95 border border-emerald-500/40 text-emerald-300 text-xs font-mono shadow-[0_0_25px_rgba(16,185,129,0.2)] backdrop-blur-xl">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{toastMessage}</span>
        </div>
      )}

    </div>
  );
}