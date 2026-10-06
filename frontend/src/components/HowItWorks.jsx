import React from 'react';
import { UploadCloud, Cpu, FileCode2 } from 'lucide-react';

const steps = [
  {
    number: '01',
    icon: UploadCloud,
    title: 'Upload',
    desc: 'Upload your paper sketch or capture wireframes live using your webcam.',
    accent: 'border-cyan-500/30 text-cyan-400 bg-cyan-500/10',
    hover: 'hover:border-cyan-500/40',
  },
  {
    number: '02',
    icon: Cpu,
    title: 'Understand',
    desc: 'Vision pipeline detects UI elements, nesting hierarchy, and coordinates.',
    accent: 'border-purple-500/30 text-purple-400 bg-purple-500/10',
    hover: 'hover:border-purple-500/40',
  },
  {
    number: '03',
    icon: FileCode2,
    title: 'Generate',
    desc: 'Get real-time rendered preview and production-ready React/Tailwind code.',
    accent: 'border-pink-500/30 text-pink-400 bg-pink-500/10',
    hover: 'hover:border-pink-500/40',
  },
];

export default function HowItWorks() {
  return (
    <div id="how-it-works" className="text-center space-y-12">
      <div className="space-y-2">
        <h2 className="text-2xl sm:text-3xl font-light tracking-tight">
          How It <span className="font-serif italic text-cyan-300">Works</span>
        </h2>
        <p className="text-xs uppercase tracking-widest text-zinc-400">
          From sketch to UI in 3 simple steps
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
        {steps.map((step, idx) => {
          const Icon = step.icon;
          return (
            <div 
              key={idx} 
              className={`p-6 rounded-2xl bg-white/[0.02] border border-white/10 ${step.hover} transition-colors space-y-4`}
            >
              <div className="flex items-center justify-between">
                <span className={`w-8 h-8 rounded-full border font-mono text-xs flex items-center justify-center font-bold ${step.accent}`}>
                  {step.number}
                </span>
                <Icon className="w-5 h-5 text-zinc-400" />
              </div>
              <h3 className="text-base font-semibold text-white">{step.title}</h3>
              <p className="text-xs text-zinc-400 leading-relaxed">
                {step.desc}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}