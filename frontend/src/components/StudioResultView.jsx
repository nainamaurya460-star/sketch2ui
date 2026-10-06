import React, { useState } from 'react';
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
  Network, 
  Cpu, 
  Edit3, 
  Save, 
  Download, 
  ChevronDown, 
  Monitor, 
  Tablet, 
  Smartphone, 
  RotateCw, 
  ExternalLink, 
  Copy, 
  Check, 
  CheckCircle2,
  ArrowLeft,
  FileCode2,
  Image as ImageIcon
} from 'lucide-react';

export default function StudioResultView({ data, sketchImage, onReset }) {
  const [deviceView, setDeviceView] = useState('desktop');
  const [codeTab, setCodeTab] = useState('jsx');
  const [copied, setCopied] = useState(false);

  // Fallback defaults agar data empty ho
  const projectName = data?.project_name || "Generated UI";
  const elementsCount = data?.elements_count || data?.detected_elements?.length || 0;
  const detectedElements = data?.detected_elements || [];
  
  const codeSnippets = {
    jsx: data?.generated_code?.jsx || `// No JSX generated`,
    tailwind: data?.generated_code?.tailwind || `<!-- No Tailwind generated -->`,
    json: data?.generated_code?.json || JSON.stringify(data || {}, null, 2)
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

  return (
    <div className="flex h-screen bg-[#070709] text-white selection:bg-pink-500 selection:text-white overflow-hidden -mt-32 -mx-6">
      
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
              <button className="w-full flex items-center gap-3 px-3 py-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-xs font-medium cursor-pointer">
                <Layout className="w-4 h-4" />
                <span>Workspace</span>
              </button>
              <button className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.04] text-xs font-medium transition-all cursor-pointer">
                <FolderGit2 className="w-4 h-4" />
                <span>Projects</span>
              </button>
              <button className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.04] text-xs font-medium transition-all cursor-pointer">
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
              <button className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.04] text-xs font-medium transition-all cursor-pointer">
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
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-white/10 bg-white/[0.02]">
              <span className="text-xs text-zinc-400">✏️</span>
              <span className="text-sm font-medium text-zinc-200">{projectName}</span>
            </div>
            <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[11px] font-mono">
              <CheckCircle2 className="w-3 h-3" />
              <span>Generated successfully</span>
            </span>
          </div>

          <div className="flex items-center gap-3">
            <button 
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-medium text-zinc-300 transition-all cursor-pointer"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied!' : 'Copy Code'}</span>
            </button>
            <button 
              onClick={handleDownloadFile}
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 text-xs font-medium text-white shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export .JSX</span>
            </button>
          </div>
        </header>

        <div className="px-8 py-3.5 border-b border-white/5 bg-[#090b10]/40 flex flex-wrap items-center justify-between gap-4 shrink-0">
          <div>
            <h2 className="text-lg font-semibold tracking-tight text-white">{projectName}</h2>
            <p className="text-xs text-zinc-400">Your sketch was synthesized into responsive React + Tailwind code.</p>
          </div>

          <div className="flex items-center gap-3 text-xs font-mono text-zinc-400">
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/[0.02] border border-white/5">
              <Layers className="w-3.5 h-3.5 text-cyan-400" />
              <span>{elementsCount} Components Detected</span>
            </span>
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/[0.02] border border-white/5 text-pink-400">
              <Cpu className="w-3.5 h-3.5" />
              <span>YOLOv8 + CV Engine</span>
            </span>
          </div>
        </div>

        <main className="p-6 max-w-[1700px] w-full grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          {/* LEFT: Uploaded Sketch & Detected Components */}
          <div className="lg:col-span-3 space-y-4">
            <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/10 space-y-3">
              <span className="text-[11px] font-mono uppercase tracking-wider text-zinc-400 flex items-center gap-2">
                <ImageIcon className="w-3.5 h-3.5 text-cyan-400" />
                Original Sketch
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
                <span className="text-[10px] font-mono text-cyan-400">{detectedElements.length} elements</span>
              </div>
              <div className="space-y-1.5 max-h-[260px] overflow-y-auto pr-1">
                {detectedElements.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 rounded-xl bg-white/[0.015] border border-white/5 text-xs">
                    <div className="flex items-center gap-2">
                      <span className={`w-2.5 h-2.5 rounded ${item.color || 'bg-cyan-500'}`} />
                      <span className="text-zinc-300 font-medium capitalize">{item.name.replace('_', ' ')}</span>
                    </div>
                    <span className="font-mono text-zinc-400 text-[11px]">{item.conf || '95%'}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* CENTER: Interactive Sandbox Canvas */}
          <div className="lg:col-span-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono uppercase tracking-wider text-zinc-400">Live Preview</span>
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
              <div className="px-4 py-2 bg-black/40 border-b border-white/5 flex items-center gap-3">
                <div className="flex gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-rose-500/80" />
                  <div className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
                </div>
                <div className="flex-1 mx-3 px-3 py-0.5 rounded-md bg-white/[0.03] border border-white/5 text-[11px] font-mono text-zinc-400 flex items-center justify-center">
                  <span>sandbox:render</span>
                </div>
              </div>

              <div className="flex-1 p-6 flex items-center justify-center bg-[#08090e]">
                <div className={`transition-all duration-300 w-full ${
                  deviceView === 'mobile' ? 'max-w-[280px]' : deviceView === 'tablet' ? 'max-w-[340px]' : 'max-w-sm'
                }`}>
                  <div className="w-full bg-white text-zinc-900 rounded-2xl shadow-2xl p-7 space-y-4">
                    <h3 className="text-xl font-bold tracking-tight text-center text-zinc-900">{projectName}</h3>
                    <p className="text-[11px] text-zinc-500 text-center">Interactive UI synthesized from sketch.</p>
                    <input type="text" placeholder="Type here..." className="w-full px-3 py-2 border border-zinc-200 rounded-xl text-xs outline-none focus:ring-2 focus:ring-blue-500" />
                    <button className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-semibold shadow-md transition-all">
                      Action Button
                    </button>
                  </div>
                </div>
              </div>

              <div className="px-4 py-2 bg-black/30 border-t border-white/5 flex items-center justify-between text-[11px] text-zinc-400 font-mono">
                <span className="flex items-center gap-1.5 text-emerald-400">
                  <CheckCircle2 className="w-3 h-3" />
                  <span>Responsive Container</span>
                </span>
                <span className="text-zinc-500">Live DOM Sandbox</span>
              </div>
            </div>
          </div>

          {/* RIGHT: Generated Code Tabs & Actions */}
          <div className="lg:col-span-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono uppercase tracking-wider text-zinc-400 flex items-center gap-2">
                <FileCode2 className="w-3.5 h-3.5 text-cyan-400" />
                Generated Code
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
                >
                  <Download className="w-3 h-3" />
                  <span>Download</span>
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

    </div>
  );
}