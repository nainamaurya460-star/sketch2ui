import React from 'react';
import { 
  Sparkles, 
  ArrowLeft, 
  BookOpen, 
  Cpu, 
  Workflow, 
  CheckCircle2, 
  AlertTriangle, 
  FolderGit2, 
  Layout, 
  History, 
  Settings,
  ExternalLink
} from 'lucide-react';

export default function DocumentationView({ onNavigate }) {
  // Real 10 classes supported by best.pt YOLOv8 model
  const supportedClasses = [
    {
      name: "Button",
      badge: "bg-rose-500",
      description: "Interactive call-to-action button element with hover states and responsive styling.",
      syntax: '<button className="px-4 py-2 bg-blue-600 text-white rounded-xl font-medium">Click</button>',
      shapeHint: "Solid or outlined rectangle with centered text stroke."
    },
    {
      name: "CheckBox",
      badge: "bg-emerald-500",
      description: "Square boolean toggle for selection lists, terms acceptance, and filters.",
      syntax: '<label className="flex items-center gap-2"><input type="checkbox" className="rounded" /> Option</label>',
      shapeHint: "Small square with optional internal checkmark stroke."
    },
    {
      name: "Heading",
      badge: "bg-purple-500",
      description: "Top-level or section header typography (H1-H3 semantics with tracking-tight styles).",
      syntax: '<h2 className="text-xl font-bold text-zinc-100">Section Title</h2>',
      shapeHint: "Prominent wide text line or underlined title block."
    },
    {
      name: "Image",
      badge: "bg-emerald-500",
      description: "Visual media frame or graphic container with aspect ratio boundaries.",
      syntax: '<div className="aspect-video bg-zinc-800/50 rounded-xl flex items-center justify-center">Image</div>',
      shapeHint: "Large box with an 'X' drawn corner-to-corner or mountain icon."
    },
    {
      name: "Label",
      badge: "bg-cyan-500",
      description: "Metadata text tag, status badge, or descriptive form field label.",
      syntax: '<span className="text-xs font-mono text-zinc-400">Status: Active</span>',
      shapeHint: "Short text string placed directly adjacent to an input or card."
    },
    {
      name: "Link",
      badge: "bg-blue-500",
      description: "Hyperlink navigation trigger with hover transition accents.",
      syntax: '<a href="#" className="text-cyan-400 hover:underline text-xs">Learn More →</a>',
      shapeHint: "Underlined text line or text accompanied by arrow symbol."
    },
    {
      name: "Paragraph",
      badge: "bg-amber-500",
      description: "Multi-line descriptive body copy container with relaxed reading line-height.",
      syntax: '<p className="text-xs text-zinc-400 leading-relaxed">Turn sketches into UI.</p>',
      shapeHint: "Multiple parallel horizontal wavy or straight text strokes."
    },
    {
      name: "RadioButton",
      badge: "bg-pink-500",
      description: "Circular mutually-exclusive selection toggle within a fieldset option group.",
      syntax: '<label className="flex items-center gap-2"><input type="radio" name="opt" /> Option</label>',
      shapeHint: "Small circle, optionally with central filled dot."
    },
    {
      name: "Select",
      badge: "bg-indigo-500",
      description: "Dropdown option selector with native or custom dropdown disclosure chevron.",
      syntax: '<select className="px-3 py-2 bg-zinc-900 border rounded-xl text-xs"><option>Option</option></select>',
      shapeHint: "Rectangle with downward chevron arrow 'v' in right corner."
    },
    {
      name: "TextBox",
      badge: "bg-cyan-500",
      description: "Text/email input field with focus ring styles and placeholder hint text.",
      syntax: '<input type="text" placeholder="Enter text..." className="w-full px-3 py-2 border rounded-xl" />',
      shapeHint: "Horizontal rectangular box, usually empty or containing placeholder line."
    }
  ];

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
            <Sparkles className="w-4 h-4" />
            <span>Launch Studio</span>
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
                onClick={() => onNavigate('projects')} 
                className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.04] text-xs font-medium transition-all cursor-pointer"
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
                className="w-full flex items-center gap-3 px-3 py-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-xs font-medium cursor-pointer"
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
          <p className="text-xs font-medium text-white leading-tight">YOLOv8 + OpenCV</p>
          <p className="text-[10px] text-zinc-500 font-mono">10-Class Vision Engine</p>
        </div>
      </aside>

      {/* 2. Main Documentation Content */}
      <div className="flex-1 flex flex-col overflow-y-auto">
        
        {/* Header Bar */}
        <header className="h-16 border-b border-white/10 px-8 flex items-center justify-between sticky top-0 bg-[#070709]/80 backdrop-blur-xl z-10 shrink-0">
          <div className="flex items-center gap-3">
            <h1 className="text-sm font-semibold tracking-tight text-white">System Documentation & Pipeline Specs</h1>
            <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-[11px] font-mono">
              FastAPI + YOLOv8 + React 19
            </span>
          </div>

          <button
            onClick={() => onNavigate('studio')}
            className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 text-xs font-semibold text-white shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all cursor-pointer"
          >
            <span>Launch Studio</span>
            <ExternalLink className="w-3 h-3" />
          </button>
        </header>

        {/* Documentation Content Body */}
        <main className="p-8 max-w-5xl w-full mx-auto space-y-12 pb-24">
          
          {/* SECTION 1: Architecture Overview */}
          <section className="space-y-4">
            <div className="space-y-1">
              <span className="text-[11px] font-mono uppercase tracking-widest text-cyan-400 flex items-center gap-1.5">
                <Workflow className="w-3.5 h-3.5" />
                Pipeline Architecture
              </span>
              <h2 className="text-xl font-bold tracking-tight text-white">
                The 4-Stage Sketch-to-Code Vision Pipeline
              </h2>
              <p className="text-xs text-zinc-400 leading-relaxed max-w-3xl">
                Sketch2UI converts analog hand-drawn wireframes into responsive React components using an end-to-end, multi-stage computer vision and code synthesis pipeline.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
              
              <div className="p-5 rounded-2xl border border-white/10 bg-[#090b10]/80 space-y-3 backdrop-blur-xl">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-lg bg-cyan-500/10 text-cyan-400 font-mono text-xs flex items-center justify-center font-bold">1</span>
                  <h3 className="text-sm font-semibold text-white">Multi-Modal Input Ingestion</h3>
                </div>
                <p className="text-xs text-zinc-400 leading-relaxed">
                  Ingests sketches via drag-and-drop image uploads, clipboard pasting, or live camera capture. Accepts PNG, JPEG, and WebP images up to 10MB.
                </p>
                <div className="text-[10px] font-mono text-cyan-400 bg-white/[0.02] p-2 rounded-lg border border-white/5">
                  POST /api/v1/sketch/predict (multipart/form-data)
                </div>
              </div>

              <div className="p-5 rounded-2xl border border-white/10 bg-[#090b10]/80 space-y-3 backdrop-blur-xl">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-lg bg-pink-500/10 text-pink-400 font-mono text-xs flex items-center justify-center font-bold">2</span>
                  <h3 className="text-sm font-semibold text-white">OpenCV Perspective Warp</h3>
                </div>
                <p className="text-xs text-zinc-400 leading-relaxed">
                  Applies bilateral filtering and Otsu thresholding to find paper page boundaries. Warps and rectifies perspective distortion before inference.
                </p>
                <div className="text-[10px] font-mono text-pink-400 bg-white/[0.02] p-2 rounded-lg border border-white/5">
                  cv2.findContours → cv2.getPerspectiveTransform
                </div>
              </div>

              <div className="p-5 rounded-2xl border border-white/10 bg-[#090b10]/80 space-y-3 backdrop-blur-xl">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-lg bg-purple-500/10 text-purple-400 font-mono text-xs flex items-center justify-center font-bold">3</span>
                  <h3 className="text-sm font-semibold text-white">YOLOv8 Component Detection</h3>
                </div>
                <p className="text-xs text-zinc-400 leading-relaxed">
                  A custom-trained YOLOv8 neural network (`app/models/best.pt`) runs object detection with Non-Maximum Suppression to detect 10 distinct UI primitives.
                </p>
                <div className="text-[10px] font-mono text-purple-400 bg-white/[0.02] p-2 rounded-lg border border-white/5">
                  Ultralytics YOLO('app/models/best.pt') @ 640x640
                </div>
              </div>

              <div className="p-5 rounded-2xl border border-white/10 bg-[#090b10]/80 space-y-3 backdrop-blur-xl">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-lg bg-emerald-500/10 text-emerald-400 font-mono text-xs flex items-center justify-center font-bold">4</span>
                  <h3 className="text-sm font-semibold text-white">Spatial Code Synthesizer</h3>
                </div>
                <p className="text-xs text-zinc-400 leading-relaxed">
                  Sorts bounding boxes into a vertical visual hierarchy tree, groups inputs and buttons into interactive glassmorphic cards, and synthesizes pure React 19 + Tailwind CSS code.
                </p>
                <div className="text-[10px] font-mono text-emerald-400 bg-white/[0.02] p-2 rounded-lg border border-white/5">
                  AST Tree Sort → JSX Synthesizer
                </div>
              </div>

            </div>
          </section>

          {/* SECTION 2: Supported Component Classes */}
          <section className="space-y-4">
            <div className="space-y-1">
              <span className="text-[11px] font-mono uppercase tracking-widest text-cyan-400 flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5" />
                Model Specifications
              </span>
              <h2 className="text-xl font-bold tracking-tight text-white">
                Supported UI Component Classes (10 Primitives)
              </h2>
              <p className="text-xs text-zinc-400 leading-relaxed">
                The current active weights (`best.pt`) recognize exactly 10 UI primitive classes trained on labeled wireframe datasets.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {supportedClasses.map((cls) => (
                <div 
                  key={cls.name}
                  className="p-4 rounded-xl border border-white/10 bg-[#090b10]/70 hover:border-cyan-500/30 transition-all space-y-2.5"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className={`w-2.5 h-2.5 rounded ${cls.badge}`} />
                      <h4 className="text-sm font-semibold text-white font-mono">{cls.name}</h4>
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/[0.03] border border-white/5 text-zinc-400">
                      Primitive
                    </span>
                  </div>

                  <p className="text-xs text-zinc-400">{cls.description}</p>
                  
                  <div className="space-y-1 pt-1 text-[11px] font-mono">
                    <p className="text-zinc-500 text-[10px]">Sketch Drawing Hint:</p>
                    <p className="text-zinc-300 bg-white/[0.02] px-2.5 py-1 rounded border border-white/5 text-[10px]">
                      {cls.shapeHint}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* SECTION 3: Best Practices for Wireframing */}
          <section className="space-y-4">
            <div className="space-y-1">
              <span className="text-[11px] font-mono uppercase tracking-widest text-emerald-400 flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Best Practices
              </span>
              <h2 className="text-xl font-bold tracking-tight text-white">
                Best Practices for Drawing Wireframes
              </h2>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Maximize prediction confidence and code quality by following these practical drafting guidelines:
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-2xl border border-white/10 bg-[#090b10]/60 space-y-2">
                <h4 className="text-xs font-semibold text-white flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                  High Contrast Ink
                </h4>
                <p className="text-[11px] text-zinc-400 leading-relaxed">
                  Use black or dark ink pens on clean white unruled paper. Avoid faint pencil strokes and poor ambient lighting.
                </p>
              </div>

              <div className="p-4 rounded-2xl border border-white/10 bg-[#090b10]/60 space-y-2">
                <h4 className="text-xs font-semibold text-white flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                  Clean Rectangular Boxes
                </h4>
                <p className="text-[11px] text-zinc-400 leading-relaxed">
                  Draw clear closed outlines for Buttons, TextBoxes, and Image frames. Ensure outer boundaries are fully connected.
                </p>
              </div>

              <div className="p-4 rounded-2xl border border-white/10 bg-[#090b10]/60 space-y-2">
                <h4 className="text-xs font-semibold text-white flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                  Avoid Overlapping
                </h4>
                <p className="text-[11px] text-zinc-400 leading-relaxed">
                  Keep comfortable padding between elements. Avoid intersecting button strokes with neighboring input boxes.
                </p>
              </div>
            </div>
          </section>

          {/* SECTION 4: Real System Limitations */}
          <section className="space-y-4">
            <div className="space-y-1">
              <span className="text-[11px] font-mono uppercase tracking-widest text-amber-400 flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5" />
                Engineering Transparency
              </span>
              <h2 className="text-xl font-bold tracking-tight text-white">
                Real System Limitations
              </h2>
              <p className="text-xs text-zinc-400 leading-relaxed">
                An honest overview of what the current vision pipeline does and does not support:
              </p>
            </div>

            <div className="p-6 rounded-2xl border border-amber-500/20 bg-amber-500/[0.03] space-y-4">
              <div className="space-y-2 text-xs text-zinc-300 leading-relaxed">
                <div className="flex items-start gap-2.5">
                  <span className="text-amber-400 font-bold">•</span>
                  <p>
                    <strong className="text-white">Structural Primitives Only:</strong> The model detects UI bounding boxes and classes. It does not perform handwriting optical character recognition (OCR) on cursive paragraphs.
                  </p>
                </div>
                <div className="flex items-start gap-2.5">
                  <span className="text-amber-400 font-bold">•</span>
                  <p>
                    <strong className="text-white">Clean Card Normalization:</strong> Complex overlapping gestures or multi-tier carousels are converted into clean structured cards with standard vertical padding.
                  </p>
                </div>
                <div className="flex items-start gap-2.5">
                  <span className="text-amber-400 font-bold">•</span>
                  <p>
                    <strong className="text-white">Perspective Warp Limits:</strong> Camera captures tilted beyond 60 degrees from perpendicular may fail paper contour detection and automatically fallback to raw image coordinates.
                  </p>
                </div>
                <div className="flex items-start gap-2.5">
                  <span className="text-amber-400 font-bold">•</span>
                  <p>
                    <strong className="text-white">Functional React Output:</strong> The synthesizer emits pure client-side React 19 JSX with Tailwind CSS classes. Backend API integration and state management are connected downstream.
                  </p>
                </div>
              </div>
            </div>
          </section>

        </main>
      </div>

    </div>
  );
}
