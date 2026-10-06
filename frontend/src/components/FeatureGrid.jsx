import React from 'react';
import { Zap, Target, Code2, Smartphone } from 'lucide-react';

const features = [
  {
    icon: Zap,
    title: 'Fast Processing',
    desc: 'Sub-second inference',
    color: 'text-cyan-400',
  },
  {
    icon: Target,
    title: 'Accurate Detection',
    desc: 'Custom YOLOv8',
    color: 'text-pink-400',
  },
  {
    icon: Code2,
    title: 'Clean Code',
    desc: 'Semantic Tailwind',
    color: 'text-indigo-400',
  },
  {
    icon: Smartphone,
    title: 'Responsive UI',
    desc: 'Mobile to desktop',
    color: 'text-emerald-400',
  },
];

export default function FeatureGrid() {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-10 border-t border-white/5">
      {features.map((item, idx) => {
        const Icon = item.icon;
        return (
          <div 
            key={idx} 
            className="flex items-center gap-3 p-4 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-colors"
          >
            <Icon className={`w-5 h-5 ${item.color}`} />
            <div>
              <p className="text-xs font-medium text-white">{item.title}</p>
              <p className="text-[11px] text-zinc-400">{item.desc}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}