import React, { useState } from 'react';
import { 
  FolderGit2, 
  Plus, 
  Trash2, 
  Layers, 
  ArrowLeft, 
  Sparkles, 
  Layout, 
  History, 
  Search, 
  Edit3, 
  Check, 
  X, 
  ExternalLink, 
  Clock,
  BookOpen,
  Settings 
} from 'lucide-react';
import { getProjects, deleteProject, renameProject, formatRelativeTime } from '../services/storage';

export default function ProjectsView({ onNavigate, onOpenProject, onViewDetails }) {
  const [projects, setProjects] = useState(() => getProjects());
  const [searchQuery, setSearchQuery] = useState('');
  const [elementFilter, setElementFilter] = useState('all');
  const [editingId, setEditingId] = useState(null);
  const [editName, setEditName] = useState('');

  // Inline rename handlers
  const handleStartRename = (proj, e) => {
    e.stopPropagation();
    setEditingId(proj.id);
    setEditName(proj.name || '');
  };

  const handleSaveRename = (id) => {
    const trimmed = editName.trim();
    if (trimmed) {
      renameProject(id, trimmed);
      setProjects(getProjects());
    }
    setEditingId(null);
  };

  const handleCancelRename = (e) => {
    if (e) e.stopPropagation();
    setEditingId(null);
    setEditName('');
  };

  // Delete project handler
  const handleDelete = (id, e) => {
    e.stopPropagation();
    const updated = deleteProject(id);
    setProjects(updated);
  };

  // Live search and filter: matches project name OR component count
  const filtered = projects.filter((proj) => {
    const query = searchQuery.trim().toLowerCase();
    const nameMatches = !query || (proj.name || '').toLowerCase().includes(query);
    const countMatches = !query || String(proj.elements_count ?? 0).includes(query);
    const matchesSearch = nameMatches || countMatches;

    let matchesFilter = true;
    const count = proj.elements_count || 0;
    if (elementFilter === '1-3') {
      matchesFilter = count >= 1 && count <= 3;
    } else if (elementFilter === '4-7') {
      matchesFilter = count >= 4 && count <= 7;
    } else if (elementFilter === '8+') {
      matchesFilter = count >= 8;
    }

    return matchesSearch && matchesFilter;
  });

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
            <Plus className="w-4 h-4" />
            <span>New Sketch</span>
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
          <p className="text-xs font-medium text-white leading-tight">Persistent Local Projects</p>
          <p className="text-[10px] text-zinc-500 font-mono">Synced to localStorage</p>
        </div>
      </aside>

      {/* 2. Main Dashboard Content */}
      <div className="flex-1 flex flex-col overflow-y-auto">
        
        {/* Header Bar */}
        <header className="h-16 border-b border-white/10 px-8 flex items-center justify-between sticky top-0 bg-[#070709]/80 backdrop-blur-xl z-10 shrink-0">
          <div className="flex items-center gap-3">
            <h1 className="text-sm font-semibold tracking-tight text-white">Projects Dashboard</h1>
            <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-[11px] font-mono">
              {projects.length} Saved
            </span>
          </div>

          <div className="flex items-center gap-3">
            {/* Filter Pills */}
            <div className="hidden md:flex items-center gap-1 p-1 rounded-xl bg-white/[0.02] border border-white/10 text-xs font-mono">
              {[
                { id: 'all', label: 'All' },
                { id: '1-3', label: '1-3 Elms' },
                { id: '4-7', label: '4-7 Elms' },
                { id: '8+', label: '8+ Elms' },
              ].map(f => (
                <button
                  key={f.id}
                  onClick={() => setElementFilter(f.id)}
                  className={`px-2.5 py-1 rounded-lg transition-all cursor-pointer ${
                    elementFilter === f.id
                      ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                      : 'text-zinc-400 hover:text-white'
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>

            {/* Search Input */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-zinc-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input 
                type="text" 
                placeholder="Search name or count..." 
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="pl-8 pr-3 py-1.5 rounded-xl bg-white/5 border border-white/10 text-xs text-white placeholder-zinc-500 outline-none focus:border-cyan-500/60 focus:bg-white/[0.08] transition-all w-52 md:w-64"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-white cursor-pointer"
                >
                  <X className="w-3 h-3" />
                </button>
              )}
            </div>

            <button
              onClick={() => onNavigate('studio')}
              className="hidden sm:flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 text-xs font-semibold text-white shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all cursor-pointer"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>New</span>
            </button>
          </div>
        </header>

        {/* Dashboard Body */}
        <main className="p-8 max-w-7xl w-full mx-auto">
          {/* Honest Empty State when no projects exist */}
          {projects.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-12 md:p-20 rounded-3xl border border-white/10 bg-[#090b10]/60 backdrop-blur-xl text-center space-y-6 max-w-lg mx-auto mt-16 shadow-2xl">
              <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 shadow-[0_0_25px_rgba(6,182,212,0.15)]">
                <FolderGit2 className="w-8 h-8" />
              </div>
              <div className="space-y-2">
                <h3 className="text-lg font-semibold text-white tracking-tight">No projects yet. Create your first project.</h3>
                <p className="text-xs text-zinc-400 max-w-sm mx-auto">
                  Upload or sketch wireframes in Studio to generate production-ready React + Tailwind interfaces.
                </p>
              </div>
              <button
                onClick={() => onNavigate('studio')}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 text-xs font-semibold uppercase tracking-wider text-white shadow-[0_0_20px_rgba(6,182,212,0.35)] transition-all cursor-pointer"
              >
                <Plus className="w-4 h-4" />
                <span>Start Creating in Studio</span>
              </button>
            </div>
          ) : filtered.length === 0 ? (
            /* Search filter with 0 matches */
            <div className="flex flex-col items-center justify-center p-16 rounded-2xl border border-white/10 bg-white/[0.01] text-center space-y-3 max-w-md mx-auto mt-12">
              <Search className="w-8 h-8 text-zinc-600" />
              <h4 className="text-sm font-semibold text-white">No matching projects found</h4>
              <p className="text-xs text-zinc-500">No projects match "{searchQuery}" with the selected filter.</p>
              <button
                onClick={() => { setSearchQuery(''); setElementFilter('all'); }}
                className="mt-2 text-xs text-cyan-400 hover:underline cursor-pointer"
              >
                Reset Search Filters
              </button>
            </div>
          ) : (
            /* Non-Empty Real Projects Cards Grid */
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filtered.map((proj) => (
                <div
                  key={proj.id}
                  onClick={() => onViewDetails ? onViewDetails(proj) : onOpenProject(proj)}
                  className="group relative rounded-2xl border border-white/10 bg-[#090b10]/80 hover:border-cyan-500/40 hover:bg-[#0d1017] transition-all duration-200 cursor-pointer flex flex-col overflow-hidden shadow-xl"
                >
                  {/* Real Sketch Thumbnail */}
                  <div className="aspect-[16/10] bg-black/60 border-b border-white/5 relative overflow-hidden flex items-center justify-center p-3">
                    {proj.thumbnail || proj.preview ? (
                      <img
                        src={proj.thumbnail || proj.preview}
                        alt={proj.name}
                        className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300"
                      />
                    ) : (
                      <div className="flex flex-col items-center gap-2 text-zinc-600">
                        <Layers className="w-8 h-8" />
                        <span className="text-[10px] font-mono uppercase tracking-wider">No Sketch Image</span>
                      </div>
                    )}
                    
                    {/* Badge on thumbnail */}
                    <span className="absolute top-3 right-3 px-2 py-0.5 rounded-md bg-black/80 border border-white/10 text-cyan-400 font-mono text-[10px] backdrop-blur-md">
                      {proj.elements_count || 0} ELMS
                    </span>
                  </div>

                  {/* Card Content */}
                  <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
                    
                    {/* Title with Inline Rename Support */}
                    <div>
                      {editingId === proj.id ? (
                        <div 
                          className="flex items-center gap-1.5" 
                          onClick={(e) => e.stopPropagation()}
                        >
                          <input
                            type="text"
                            value={editName}
                            onChange={(e) => setEditName(e.target.value)}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') handleSaveRename(proj.id);
                              if (e.key === 'Escape') handleCancelRename();
                            }}
                            autoFocus
                            className="flex-1 px-2.5 py-1 rounded-lg bg-black/80 border border-cyan-500 text-xs text-white outline-none"
                          />
                          <button
                            onClick={() => handleSaveRename(proj.id)}
                            className="p-1.5 rounded-md bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30 cursor-pointer"
                            title="Save name"
                          >
                            <Check className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={handleCancelRename}
                            className="p-1.5 rounded-md bg-white/5 text-zinc-400 hover:text-white cursor-pointer"
                            title="Cancel"
                          >
                            <X className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      ) : (
                        <div className="flex items-center justify-between gap-2">
                          <h4 className="text-sm font-semibold text-white tracking-tight truncate group-hover:text-cyan-300 transition-colors">
                            {proj.name}
                          </h4>
                          <button
                            onClick={(e) => handleStartRename(proj, e)}
                            className="opacity-0 group-hover:opacity-100 p-1 rounded-md hover:bg-white/5 text-zinc-400 hover:text-cyan-400 transition-all cursor-pointer shrink-0"
                            title="Rename project"
                          >
                            <Edit3 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      )}

                      {/* Real relative timestamp & component count badge */}
                      <div className="flex items-center justify-between text-xs pt-2">
                        <span className="flex items-center gap-1.5 text-[11px] font-mono text-zinc-500">
                          <Clock className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
                          <span>{formatRelativeTime(proj.updatedAt || proj.createdAt)}</span>
                        </span>
                        <span className="px-2 py-0.5 rounded-md bg-white/[0.03] border border-white/5 text-zinc-400 font-mono text-[10px]">
                          {proj.elements_count || 0} components
                        </span>
                      </div>
                    </div>

                    {/* Card Actions Footer */}
                    <div className="flex items-center justify-between pt-3 border-t border-white/5">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onOpenProject(proj);
                        }}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-medium text-zinc-300 hover:text-white transition-all cursor-pointer"
                      >
                        <ExternalLink className="w-3.5 h-3.5 text-cyan-400" />
                        <span>Open in Studio</span>
                      </button>

                      <button
                        onClick={(e) => handleDelete(proj.id, e)}
                        className="p-1.5 rounded-xl bg-white/5 hover:bg-rose-500/20 border border-white/5 hover:border-rose-500/30 text-zinc-400 hover:text-rose-400 transition-all cursor-pointer"
                        title="Delete project"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>

                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>

    </div>
  );
}