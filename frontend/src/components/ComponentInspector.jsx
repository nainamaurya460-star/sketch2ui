import React from 'react';
import { 
  X, 
  Trash2, 
  Sliders, 
  Type, 
  Layers, 
  Palette, 
  Maximize2 
} from 'lucide-react';

const COMPONENT_TYPES = [
  { value: 'Button', label: 'Button' },
  { value: 'TextBox', label: 'Text Input / Field' },
  { value: 'Heading', label: 'Heading / Title' },
  { value: 'Paragraph', label: 'Paragraph / Description' },
  { value: 'Label', label: 'Label' },
  { value: 'CheckBox', label: 'Checkbox' },
  { value: 'RadioButton', label: 'Radio Button' },
  { value: 'Image', label: 'Image Placeholder' },
  { value: 'Select', label: 'Select / Dropdown' },
  { value: 'Link', label: 'Anchor Link' },
];

export default function ComponentInspector({ element, onUpdateElement, onDeleteElement, onClose }) {
  if (!element) return null;

  const currentType = element.name || 'TextBox';
  const isButton = ['button', 'btn', 'submit'].includes(currentType.toLowerCase());

  return (
    <div className="w-80 border-l border-white/10 bg-[#090b10]/95 backdrop-blur-2xl flex flex-col h-full z-20 shrink-0 shadow-2xl animate-in slide-in-from-right duration-200">
      
      {/* Header */}
      <div className="h-14 px-5 border-b border-white/10 flex items-center justify-between shrink-0 bg-white/[0.01]">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
            <Sliders className="w-3.5 h-3.5 text-cyan-400" />
          </div>
          <span className="text-xs font-semibold text-white tracking-wide uppercase font-mono">
            Element Inspector
          </span>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-lg text-zinc-400 hover:text-white hover:bg-white/5 transition-colors cursor-pointer"
          title="Close Inspector"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-5 space-y-6">
        
        {/* Active Badge & Summary */}
        <div className="p-3.5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono uppercase tracking-wider text-zinc-500">
              Component Type
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              {element.conf || '100%'}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className={`w-2.5 h-2.5 rounded-full ${element.color || 'bg-cyan-500'}`} />
            <span className="text-sm font-semibold text-white">
              {element.name || 'Component'}
            </span>
          </div>
        </div>

        {/* 1. Component Type Dropdown */}
        <div className="space-y-2">
          <label className="text-[11px] font-mono text-zinc-400 flex items-center gap-1.5">
            <Layers className="w-3 h-3 text-cyan-400" />
            <span>Swap Component Type</span>
          </label>
          <select
            value={currentType}
            onChange={(e) => onUpdateElement({ name: e.target.value })}
            className="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-xs text-white focus:outline-none focus:border-cyan-500/50 cursor-pointer"
          >
            {COMPONENT_TYPES.map(type => (
              <option key={type.value} value={type.value} className="bg-[#090b10] text-white">
                {type.label}
              </option>
            ))}
          </select>
        </div>

        {/* 2. Text / Placeholder Input */}
        <div className="space-y-2">
          <label className="text-[11px] font-mono text-zinc-400 flex items-center gap-1.5">
            <Type className="w-3 h-3 text-cyan-400" />
            <span>{isButton ? 'Button Label' : 'Label / Placeholder Text'}</span>
          </label>
          <input
            type="text"
            value={element.text || ''}
            placeholder={isButton ? 'e.g. Submit, Cancel' : 'e.g. Enter your email...'}
            onChange={(e) => onUpdateElement({ text: e.target.value })}
            className="w-full px-3.5 py-2.5 rounded-xl bg-white/5 border border-white/10 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-cyan-500/50"
          />
        </div>

        {/* 3. Button Variant Toggle */}
        {isButton && (
          <div className="space-y-2">
            <label className="text-[11px] font-mono text-zinc-400 flex items-center gap-1.5">
              <Palette className="w-3 h-3 text-cyan-400" />
              <span>Button Variant</span>
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => onUpdateElement({ variant: 'primary' })}
                className={`py-2 px-3 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                  (element.variant !== 'secondary')
                    ? 'bg-cyan-500 text-black shadow-lg shadow-cyan-500/20'
                    : 'bg-white/5 text-zinc-400 border border-white/10 hover:text-white'
                }`}
              >
                Primary
              </button>
              <button
                type="button"
                onClick={() => onUpdateElement({ variant: 'secondary' })}
                className={`py-2 px-3 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                  element.variant === 'secondary'
                    ? 'border border-cyan-400 text-cyan-400 bg-cyan-500/10'
                    : 'bg-white/5 text-zinc-400 border border-white/10 hover:text-white'
                }`}
              >
                Secondary
              </button>
            </div>
          </div>
        )}

        {/* 4. Geometry / Bounding Box Details */}
        {Array.isArray(element.box) && (
          <div className="p-3.5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-2 text-[11px] font-mono text-zinc-400">
            <span className="flex items-center gap-1.5 text-zinc-300">
              <Maximize2 className="w-3 h-3 text-cyan-400" />
              <span>Bounding Coordinates</span>
            </span>
            <div className="grid grid-cols-2 gap-2 text-[10px] text-zinc-500 pt-1">
              <div>Top-Left: [{element.box[0]}, {element.box[1]}]</div>
              <div>Btm-Right: [{element.box[2]}, {element.box[3]}]</div>
            </div>
          </div>
        )}

      </div>

      {/* Footer Actions */}
      <div className="p-5 border-t border-white/10 bg-[#090b10] shrink-0 space-y-2">
        <button
          onClick={() => onDeleteElement(element.id || element)}
          className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-400 text-xs font-semibold transition-all cursor-pointer"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span>Delete Component</span>
        </button>
      </div>

    </div>
  );
}
