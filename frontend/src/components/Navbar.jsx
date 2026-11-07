import React from 'react';
import { Sparkles, ArrowRight, User, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Navbar({ onLaunchStudio, onStartClick, onLogoClick, onNavigate }) {
  const { user, isAuthenticated, openAuthModal, logout } = useAuth();
  const handleLaunch = onLaunchStudio || onStartClick;

  const scrollToSection = (id) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-40 border-b border-white/10 bg-[#070709]/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        {/* Brand Logo */}
        <div 
          onClick={onLogoClick}
          className="flex items-center gap-2.5 cursor-pointer group"
        >
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-400 to-pink-500 flex items-center justify-center shadow-[0_0_15px_#22d3ee] group-hover:scale-105 transition-transform">
            <Sparkles className="w-4 h-4 text-black font-bold" />
          </div>
          <span className="font-semibold tracking-wider text-base text-white group-hover:text-cyan-300 transition-colors">
            Sketch2UI
          </span>
        </div>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-8 text-xs font-medium text-zinc-400">
          <button 
            type="button"
            onClick={() => scrollToSection('how-it-works')} 
            className="hover:text-white transition-colors cursor-pointer"
          >
            HOW IT WORKS
          </button>
          
          <button 
            type="button"
            onClick={() => scrollToSection('examples')} 
            className="hover:text-white transition-colors cursor-pointer"
          >
            EXAMPLES
          </button>

          <button 
            type="button"
            onClick={() => onNavigate && onNavigate('projects')} 
            className="hover:text-white transition-colors cursor-pointer"
          >
            PROJECTS
          </button>

          <button 
            type="button"
            onClick={() => onNavigate && onNavigate('docs')} 
            className="hover:text-white transition-colors cursor-pointer"
          >
            DOCS
          </button>

          <a 
            href="https://github.com/nainamaurya460-star/sketch2ui" 
            target="_blank" 
            rel="noreferrer" 
            className="hover:text-white transition-colors"
          >
            GITHUB ↗
          </a>
        </nav>

        {/* CTA Launch Studio & Auth Actions */}
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 text-xs text-zinc-300">
                <div className="w-5 h-5 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center text-[10px] font-bold">
                  {(user.name || user.email || 'U')[0].toUpperCase()}
                </div>
                <span className="hidden sm:inline font-medium text-white max-w-[120px] truncate">
                  {user.name || user.email}
                </span>
                <span className="px-1.5 py-0.2 rounded bg-cyan-500/20 text-cyan-400 font-mono text-[9px] uppercase">
                  {user.tier || 'free'}
                </span>
              </div>
              <button
                type="button"
                onClick={logout}
                title="Sign Out"
                className="p-2 rounded-xl bg-white/5 hover:bg-rose-500/20 text-zinc-400 hover:text-rose-400 border border-white/10 transition-colors cursor-pointer"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => openAuthModal('login')}
              className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-semibold uppercase tracking-wider text-zinc-300 hover:text-white transition-all cursor-pointer"
            >
              <User className="w-3.5 h-3.5 text-cyan-400" />
              <span>SIGN IN</span>
            </button>
          )}

          <button
            type="button"
            onClick={handleLaunch}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 text-xs font-semibold uppercase tracking-wider text-white shadow-[0_0_20px_rgba(6,182,212,0.35)] transition-all cursor-pointer"
          >
            <span>TRY SKETCH2UI</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </header>
  );
}
