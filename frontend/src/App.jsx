import React, { useState } from 'react';
import CustomCursor from './components/CustomCursor';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import VisualPipeline from './components/VisualPipeline';
import FeatureGrid from './components/FeatureGrid';
import HowItWorks from './components/HowItWorks';
import StudioWorkspace from './components/StudioWorkspace';

export default function App() {
  // Views: 'landing' | 'studio'
  const [currentView, setCurrentView] = useState('landing');
  const [isDemoMode, setIsDemoMode] = useState(false);

  const startNormalStudio = () => {
    setIsDemoMode(false);
    setCurrentView('studio');
  };

  const startDemoTour = () => {
    setIsDemoMode(true);
    setCurrentView('studio');
  };

  return (
    <div className="relative min-h-screen bg-[#070709] text-white selection:bg-pink-500 selection:text-white overflow-x-hidden">
      
      {/* Floating Cursor */}
      <CustomCursor />

      {/* Atmospheric Ambient Glows */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[350px] bg-gradient-to-b from-indigo-500/15 via-purple-500/5 to-transparent blur-[140px] pointer-events-none" />
      <div className="absolute top-[400px] right-[-100px] w-[500px] h-[500px] bg-cyan-500/10 blur-[150px] pointer-events-none" />

      {/* Navbar (Sirf Landing Page par) */}
      {currentView === 'landing' && (
        <Navbar 
          onStartClick={startNormalStudio} 
          currentView={currentView} 
          onLogoClick={() => setCurrentView('landing')} 
        />
      )}

      {/* Main Views Container */}
      <main className="relative pt-32 pb-20 px-6 max-w-7xl mx-auto">
        {currentView === 'landing' && (
          <div className="space-y-28">
            <section className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
              <div className="lg:col-span-6">
                <Hero 
                  onStart={startNormalStudio} 
                  onWatchDemo={startDemoTour} 
                />
              </div>
              <div className="lg:col-span-6">
                <VisualPipeline />
              </div>
            </section>
            <FeatureGrid />
            <HowItWorks />
          </div>
        )}

        {currentView === 'studio' && (
          <StudioWorkspace 
            onBack={() => setCurrentView('landing')} 
            isDemoMode={isDemoMode}
          />
        )}
      </main>
    </div>
  );
}