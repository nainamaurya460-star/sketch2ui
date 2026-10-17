import React, { useState } from 'react';
import { 
  History, 
  Copy, 
  Check, 
  ArrowLeft, 
  Sparkles, 
  Layout, 
  FolderGit2, 
  Clock, 
  Search, 
  ExternalLink, 
  Trash2, 
  X,
  Layers,
  BookOpen,
  Settings
} from 'lucide-react';
import { getProjects, deleteProject, formatRelativeTime } from '../services/storage';

/**
 * Computes summary count chips from detected elements
 * e.g., ["3 Buttons", "2 Inputs", "1 Heading"]
 */
function getElementSummaryChips(elements, elementsCount) {
  if (!Array.isArray(elements) || elements.length === 0) {
    if (elementsCount && elementsCount > 0) {
      return [`${elementsCount} Components`];
    }
    return ['0 Elements'];
  }

  const counts = {};
  for (const el of elements) {
    const raw = (el.name || 'Component').toLowerCase().replace(/_/g, ' ');
    let label = 'Element';

    if (raw.includes('button') || raw.includes('btn')) label = 'Button';
    else if (raw.includes('input') || raw.includes('text')) label = 'Input';
    else if (raw.includes('heading') || raw.includes('title')) label = 'Heading';
    else if (raw.includes('card')) label = 'Card';
    else if (raw.includes('image') || raw.includes('img')) label = 'Image';
    else if (raw.includes('paragraph') || raw.includes('desc')) label = 'Paragraph';
    else if (raw.includes('radio')) label = 'Radio';
    else if (raw.includes('check')) label = 'Checkbox';
    else if (raw.includes('select')) label = 'Select';
    else label = raw.charAt(0).toUpperCase() + raw.slice(1);

    counts[label] = (counts[label] || 0) + 1;
  }

  return Object.entries(counts).map(([type, count]) => {
    const plural = count === 1 ? type : (type.endsWith('s') ? `${type}es` : `${type}s`);
    return `${count} ${plural}`;
  });
}

/**
 * Returns chronological bucket label based on real createdAt date
 */
function getChronologicalBucket(dateString) {
  if (!dateString) return 'Earlier';
  const itemDate = new Date(dateString);
  const now = new Date();

  // Reset to midnight for clean calendar-day comparison
  const itemMidnight = new Date(itemDate.getFullYear(), itemDate.getMonth(), itemDate.getDate()).getTime();
  const todayMidnight = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  const oneDayMs = 24 * 60 * 60 * 1000;

  const diffDays = Math.round((todayMidnight - itemMidnight) / oneDayMs);

  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays <= 7) return 'Earlier this week';
  if (diffDays <= 30) return 'Earlier this month';
  return 'Older';
}

export default function HistoryView({ onNavigate, onViewDetails }) {
  const [projects, setProjects] = useState(() => getProjects());
  const [searchQuery, setSearchQuery] = useState('');
  const [copiedId, setCopiedId] = useState(null);

  const handleCopy = (id, code, e) => {
    if (e) e.stopPropagation();
    navigator.clipboard.writeText(code || '');
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleDelete = (id, e) => {
    if (e) e.stopPropagation();
    const updated = deleteProject(id);
    setProjects(updated);
  };

  // Filter projects in real-time by search query
  const filteredProjects = projects.filter((proj) => {
    if (!searchQuery.trim()) return true;
    return (proj.name || '').toLowerCase().includes(searchQuery.trim().toLowerCase());
  });

  // Group chronologically
  const BUCKET_ORDER = ['Today', 'Yesterday', 'Earlier this week', 'Earlier this month', 'Older'];
  const groupedProjects = BUCKET_ORDER.reduce((acc, bucket) => {
    acc[bucket] = [];
    return acc;
  }, {});

  for (const proj of filteredProjects) {
    const bucket = getChronologicalBucket(proj.createdAt);
    if (!groupedProjects[bucket]) {
      groupedProjects[bucket] = [];
    }
    groupedProjects[bucket].push(proj);
  }

  return (
    <div className="flex h-screen bg-[#070709] text-white selection:bg-pink-500 selection:text-white overflow-hidden">
      
      {/* 1. Left Sidebar */}
      <aside className="w-64 border-r border-white/10 bg-[#090b10]/90 backdrop-blur-2xl flex flex-col justify-between p-5 shrink-0 z-20">
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
                className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.04] text-xs font-medium transition-all cursor-pointer"
              >
                <FolderGit2 className="w-4 h-4" />
                <span>Projects</span>
              </button>
              <button className="w-full flex items-center gap-3 px-3 py-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-xs font-medium cursor-pointer">
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
          <p className="text-xs font-medium text-white leading-tight">Chronological Audit Log</p>
          <p className="text-[10px] text-zinc-500 font-mono">Real Studio Conversions</p>
        </div>
      </aside>

      {/* 2. Main History Content */}
      <div className="flex-1 flex flex-col overflow-y-auto">
        
        {/* Header Bar */}
        <header className="h-16 border-b border-white/10 px-8 flex items-center justify-between sticky top-0 bg-[#070709]/80 backdrop-blur-xl z-10 shrink-0">
          <div className="flex items-center gap-3">
            <h1 className="text-sm font-semibold tracking-tight text-white">Conversion History</h1>
            <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-[11px] font-mono">
              {projects.length} Total Logs
            </span>
          </div>

          {/* Search Input */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-zinc-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input 
              type="text" 
              placeholder="Filter by sketch name..." 
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="pl-8 pr-3 py-1.5 rounded-xl bg-white/5 border border-white/10 text-xs text-white placeholder-zinc-500 outline-none focus:border-cyan-500/60 focus:bg-white/[0.08] transition-all w-56 md:w-72"
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
        </header>

        {/* Audit Log Body */}
        <main className="p-8 max-w-5xl w-full mx-auto space-y-8">
          
          {/* Honest Empty State when storage has 0 records */}
          {projects.length === 0 ? (
            <div className="p-16 md:p-20 rounded-3xl border border-white/10 bg-[#090b10]/60 backdrop-blur-xl text-center space-y-6 max-w-lg mx-auto mt-12 shadow-2xl">
              <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 mx-auto shadow-[0_0_25px_rgba(6,182,212,0.15)]">
                <History className="w-8 h-8" />
              </div>
              <div className="space-y-2">
                <h3 className="text-lg font-semibold text-white tracking-tight">
                  No conversion history yet. Convert your first sketch to see it here.
                </h3>
                <p className="text-xs text-zinc-400 max-w-sm mx-auto">
                  Every wireframe synthesized through the AI vision pipeline is chronologically recorded here.
                </p>
              </div>
              <button
                onClick={() => onNavigate('studio')}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 text-xs font-semibold uppercase tracking-wider text-white shadow-[0_0_20px_rgba(6,182,212,0.35)] transition-all cursor-pointer"
              >
                <Sparkles className="w-4 h-4" />
                <span>Convert Sketch in Studio</span>
              </button>
            </div>
          ) : filteredProjects.length === 0 ? (
            /* Search filter with 0 matches */
            <div className="flex flex-col items-center justify-center p-16 rounded-2xl border border-white/10 bg-white/[0.01] text-center space-y-3 max-w-md mx-auto mt-12">
              <Search className="w-8 h-8 text-zinc-600" />
              <h4 className="text-sm font-semibold text-white">No matching history records</h4>
              <p className="text-xs text-zinc-500">No conversions match "{searchQuery}".</p>
              <button
                onClick={() => setSearchQuery('')}
                className="mt-2 text-xs text-cyan-400 hover:underline cursor-pointer"
              >
                Clear search filter
              </button>
            </div>
          ) : (
            /* Chronologically Grouped Audit Logs */
            BUCKET_ORDER.map((bucket) => {
              const items = groupedProjects[bucket] || [];
              if (items.length === 0) return null;

              return (
                <section key={bucket} className="space-y-3">
                  
                  {/* Bucket Header */}
                  <div className="flex items-center gap-2 px-1">
                    <span className="text-xs font-mono uppercase tracking-wider font-semibold text-cyan-400">
                      {bucket}
                    </span>
                    <span className="text-[10px] font-mono text-zinc-500">
                      ({items.length} {items.length === 1 ? 'conversion' : 'conversions'})
                    </span>
                    <div className="flex-1 border-t border-white/5 ml-2" />
                  </div>

                  {/* Bucket Cards */}
                  <div className="space-y-3">
                    {items.map((item) => {
                      const summaryChips = getElementSummaryChips(item.detected_elements, item.elements_count);

                      return (
                        <div 
                          key={item.id} 
                          onClick={() => onViewDetails ? onViewDetails(item) : onNavigate('projects')}
                          className="group p-5 rounded-2xl border border-white/10 bg-[#090b10]/80 hover:border-cyan-500/40 hover:bg-[#0c0f17] transition-all flex flex-col md:flex-row md:items-center justify-between gap-4 cursor-pointer shadow-lg"
                        >
                          {/* Left: Thumbnail & Info */}
                          <div className="flex items-start md:items-center gap-4 min-w-0">
                            
                            {/* Sketch Thumbnail / Icon */}
                            <div className="w-12 h-12 rounded-xl bg-black/60 border border-white/10 flex items-center justify-center overflow-hidden shrink-0">
                              {item.thumbnail || item.preview ? (
                                <img 
                                  src={item.thumbnail || item.preview} 
                                  alt={item.name} 
                                  className="w-full h-full object-contain"
                                />
                              ) : (
                                <Layers className="w-5 h-5 text-zinc-600" />
                              )}
                            </div>

                            {/* Details */}
                            <div className="space-y-1.5 min-w-0">
                              <div className="flex items-center gap-2.5">
                                <h4 className="text-sm font-semibold text-white tracking-tight truncate group-hover:text-cyan-300 transition-colors">
                                  {item.name}
                                </h4>
                                <span className="flex items-center gap-1 text-[11px] font-mono text-zinc-500 shrink-0">
                                  <Clock className="w-3 h-3 text-zinc-600" />
                                  <span>
                                    {new Date(item.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                  </span>
                                </span>
                              </div>

                              {/* Summary chips */}
                              <div className="flex flex-wrap items-center gap-1.5">
                                {summaryChips.slice(0, 4).map((chip, idx) => (
                                  <span 
                                    key={idx}
                                    className="px-2 py-0.5 rounded-md bg-white/[0.03] border border-white/5 text-cyan-400 font-mono text-[10px]"
                                  >
                                    {chip}
                                  </span>
                                ))}
                                {summaryChips.length > 4 && (
                                  <span className="text-[10px] font-mono text-zinc-500">
                                    +{summaryChips.length - 4} more
                                  </span>
                                )}
                                <span className="text-[10px] font-mono text-zinc-600 pl-1">
                                  • {formatRelativeTime(item.createdAt)}
                                </span>
                              </div>
                            </div>

                          </div>

                          {/* Right: Quick Actions */}
                          <div className="flex items-center gap-2 shrink-0 self-end md:self-center">
                            
                            {/* Copy Code */}
                            <button 
                              onClick={(e) => handleCopy(item.id, item.generated_code?.jsx, e)} 
                              className="px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-medium text-zinc-300 hover:text-white transition-all flex items-center gap-1.5 cursor-pointer"
                              title="Copy JSX Code"
                            >
                              {copiedId === item.id ? (
                                <>
                                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                                  <span className="text-emerald-400">Copied</span>
                                </>
                              ) : (
                                <>
                                  <Copy className="w-3.5 h-3.5 text-zinc-400" />
                                  <span>Copy JSX</span>
                                </>
                              )}
                            </button>

                            {/* View Details */}
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                if (onViewDetails) onViewDetails(item);
                              }}
                              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-xs font-medium text-cyan-300 transition-all cursor-pointer shadow-[0_0_10px_rgba(6,182,212,0.1)]"
                              title="Inspect Project Details"
                            >
                              <ExternalLink className="w-3.5 h-3.5 text-cyan-400" />
                              <span>View Details</span>
                            </button>

                            {/* Delete Record */}
                            <button 
                              onClick={(e) => handleDelete(item.id, e)} 
                              className="p-1.5 rounded-xl bg-white/5 hover:bg-rose-500/20 border border-white/5 hover:border-rose-500/30 text-zinc-400 hover:text-rose-400 transition-all cursor-pointer"
                              title="Delete Record"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>

                          </div>

                        </div>
                      );
                    })}
                  </div>

                </section>
              );
            })
          )}

        </main>
      </div>

    </div>
  );
}