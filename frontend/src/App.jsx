import React, { useState } from 'react';
import ErrorBoundary from './components/ErrorBoundary';
import CustomCursor from './components/CustomCursor';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import VisualPipeline from './components/VisualPipeline';
import FeatureGrid from './components/FeatureGrid';
import HowItWorks from './components/HowItWorks';
import StudioWorkspace from './components/StudioWorkspace';
import ProjectsView from './components/ProjectsView';
import HistoryView from './components/HistoryView';
import ProjectDetailsView from './components/ProjectDetailsView';
import DocumentationView from './components/DocumentationView';
import SettingsView from './components/SettingsView';
import NotFoundView from './components/NotFoundView';

export default function App() {
  // Views: 'landing' | 'studio' | 'projects' | 'project_details' | 'history' | 'docs' | 'settings' | '404'
  const [currentView, setCurrentView] = useState('landing');
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);

  const startNormalStudio = () => {
    setIsDemoMode(false);
    setSelectedProject(null);
    setCurrentView('studio');
  };

  const startDemoTour = () => {
    setIsDemoMode(true);
    setSelectedProject(null);
    setCurrentView('studio');
  };

  const handleOpenStudio = (project) => {
    setSelectedProject(project);
    setIsDemoMode(false);
    setCurrentView('studio');
  };

  const handleViewDetails = (project) => {
    setSelectedProject(project);
    setCurrentView('project_details');
  };

  const handleNavigate = (view) => {
    if (view === 'landing') {
      setSelectedProject(null);
    }
    setCurrentView(view);
  };

  const validViews = [
    'landing',
    'studio',
    'projects',
    'project_details',
    'history',
    'docs',
    'settings'
  ];

  return (
    <ErrorBoundary>
      <div className="relative min-h-screen bg-[#070709] text-white selection:bg-pink-500 selection:text-white overflow-x-hidden">
      
      {/* Floating Custom Cursor */}
      <CustomCursor />

      {/* Atmospheric Ambient Glows */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[350px] bg-gradient-to-b from-indigo-500/15 via-purple-500/5 to-transparent blur-[140px] pointer-events-none" />
      <div className="absolute top-[400px] right-[-100px] w-[500px] h-[500px] bg-cyan-500/10 blur-[150px] pointer-events-none" />

      {/* Navbar (Only on Landing Page) */}
      {currentView === 'landing' && (
        <Navbar 
          onLaunchStudio={startNormalStudio}
          onStartClick={startNormalStudio}
          onNavigate={handleNavigate}
          onLogoClick={() => handleNavigate('landing')} 
        />
      )}

      {/* Landing View Container */}
      {currentView === 'landing' && (
        <main className="relative pt-32 pb-20 px-6 max-w-7xl mx-auto">
          <div className="space-y-28">
            <section className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
              <div className="lg:col-span-6">
                <Hero 
                  onStart={startNormalStudio} 
                  onWatchDemo={startDemoTour} 
                />
              </div>
              <div id="examples" className="lg:col-span-6">
                <VisualPipeline />
              </div>
            </section>
            <FeatureGrid />
            <HowItWorks />
          </div>
        </main>
      )}

      {/* Studio Workspace View */}
      {currentView === 'studio' && (
        <div className="relative min-h-screen">
          <StudioWorkspace 
            onBack={() => handleNavigate('landing')} 
            onNavigate={handleNavigate}
            isDemoMode={isDemoMode}
            initialProject={selectedProject}
          />
        </div>
      )}

      {/* Dedicated Project Details Inspection View */}
      {currentView === 'project_details' && (
        <div className="relative min-h-screen">
          <ProjectDetailsView
            project={selectedProject}
            onNavigate={handleNavigate}
            onOpenInStudio={handleOpenStudio}
            onProjectDeleted={() => {
              setSelectedProject(null);
              handleNavigate('projects');
            }}
            onProjectRenamed={(updated) => {
              setSelectedProject(updated);
            }}
          />
        </div>
      )}

      {/* Projects Dashboard View */}
      {currentView === 'projects' && (
        <div className="relative min-h-screen">
          <ProjectsView 
            onNavigate={handleNavigate}
            onOpenProject={handleOpenStudio}
            onViewDetails={handleViewDetails}
          />
        </div>
      )}

      {/* History & Chronological Audit Logs View */}
      {currentView === 'history' && (
        <div className="relative min-h-screen">
          <HistoryView 
            onNavigate={handleNavigate} 
            onViewDetails={handleViewDetails}
          />
        </div>
      )}

      {/* System Documentation View */}
      {currentView === 'docs' && (
        <div className="relative min-h-screen">
          <DocumentationView 
            onNavigate={handleNavigate}
          />
        </div>
      )}

      {/* System Settings & Storage Preferences View */}
      {currentView === 'settings' && (
        <div className="relative min-h-screen">
          <SettingsView 
            onNavigate={handleNavigate}
            onStorageCleared={() => {
              setSelectedProject(null);
            }}
          />
        </div>
      )}

      {/* 404 / Route Fallback View */}
      {!validViews.includes(currentView) && (
        <div className="relative min-h-screen">
          <NotFoundView 
            onNavigate={handleNavigate}
          />
        </div>
      )}
      </div>
    </ErrorBoundary>
  );
}