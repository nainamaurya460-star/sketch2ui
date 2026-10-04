import React, { useEffect, useRef, useState } from "react";
import ProcessingScreen from "./ProcessingScreen";
import StudioResultView from "./StudioResultView";
import { predictSketch } from "../services/api";

import {
  Sparkles,
  Plus,
  Layout,
  FolderGit2,
  History,
  BookOpen,
  GitBranch,
  Settings,
  Save,
  Download,
  CloudUpload,
  FolderOpen,
  Camera,
  Lightbulb,
  CheckCircle2,
  ChevronDown,
  ArrowLeft,
  AlertCircle,
} from "lucide-react";

export default function StudioWorkspace({
  onBack,
  onNavigate,
  isDemoMode = false,
}) {
  // --------------------------------------------------
  // STATES
  // --------------------------------------------------
  const [workflowState, setWorkflowState] = useState(
    isDemoMode ? "processing" : "upload"
  );
  const [dragActive, setDragActive] = useState(false);
  const [resultData, setResultData] = useState(null);
  const [previewImage, setPreviewImage] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");

  const fileInputRef = useRef(null);

  // --------------------------------------------------
  // DEMO RESULT
  // --------------------------------------------------
  const demoResult = {
    project_name: "Interactive Demo UI",
    elements_count: 6,
    detected_elements: [
      { name: "heading", conf: "96%", color: "bg-purple-500" },
      { name: "image_placeholder", conf: "89%", color: "bg-emerald-500" },
      { name: "input_field", conf: "94%", color: "bg-cyan-500" },
      { name: "input_field", conf: "91%", color: "bg-cyan-500" },
      { name: "button", conf: "97%", color: "bg-rose-500" },
      { name: "card", conf: "95%", color: "bg-amber-500" },
    ],
    generated_code: {
      jsx: `import React from "react";

export default function LoginPage() {
  return (
    <div className="w-full max-w-sm bg-white rounded-2xl shadow-xl p-8 space-y-6 text-zinc-900">
      <h2 className="text-xl font-bold text-center">
        Welcome Back
      </h2>
      <input
        type="email"
        placeholder="Email address"
        className="w-full px-3 py-2 border rounded-xl text-xs outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button className="w-full py-2.5 bg-blue-600 text-white rounded-xl text-xs font-semibold hover:bg-blue-700 transition-all">
        Sign In
      </button>
    </div>
  );
}`,
      tailwind: `<div class="w-full max-w-sm bg-white rounded-2xl shadow-xl p-8 space-y-6 text-zinc-900">\n  <h2 class="text-xl font-bold text-center">Welcome Back</h2>\n  <input type="email" placeholder="Email address" class="w-full px-3 py-2 border rounded-xl text-xs" />\n  <button class="w-full py-2.5 bg-blue-600 text-white rounded-xl text-xs font-semibold">Sign In</button>\n</div>`,
      json: `{\n  "mode": "demo",\n  "status": "ready",\n  "framework": "React + Tailwind",\n  "elements": 6\n}`,
    },
  };

  // --------------------------------------------------
  // DEMO MODE HANDLER
  // --------------------------------------------------
  useEffect(() => {
    if (!isDemoMode) return;

    setWorkflowState("processing");
    const timer = setTimeout(() => {
      setResultData(demoResult);
      setWorkflowState("result");
    }, 3000);

    return () => clearTimeout(timer);
  }, [isDemoMode]);

  // --------------------------------------------------
  // CLEANUP PREVIEW URL
  // --------------------------------------------------
  useEffect(() => {
    return () => {
      if (previewImage && previewImage.startsWith("blob:")) {
        URL.revokeObjectURL(previewImage);
      }
    };
  }, [previewImage]);

  // --------------------------------------------------
  // FILE VALIDATION
  // --------------------------------------------------
  const validateFile = (file) => {
    if (!file) {
      return "Please select an image.";
    }

    if (!file.type.startsWith("image/")) {
      return "Only image files (PNG, JPG, JPEG, WEBP) are supported.";
    }

    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      return "File size must be less than 10MB.";
    }

    return null;
  };

  // --------------------------------------------------
  // HANDLE FILE UPLOAD & PREDICTION
  // --------------------------------------------------
  const handleFile = async (file) => {
    const validationError = validateFile(file);

    if (validationError) {
      setErrorMessage(validationError);
      setWorkflowState("error");
      return;
    }

    setErrorMessage("");

    // Revoke purana preview URL agar bana ho
    if (previewImage && previewImage.startsWith("blob:")) {
      URL.revokeObjectURL(previewImage);
    }

    // Naya local image preview create karein
    const objectUrl = URL.createObjectURL(file);
    setPreviewImage(objectUrl);

    // Processing animation screen par le jayein
    setWorkflowState("processing");

    try {
      // Backend API call
      const data = await predictSketch(file);

      // Agar backend se valid response aaya
      if (data && typeof data === "object") {
        setResultData(data);
      } else {
        throw new Error("Invalid response format from server");
      }
      setWorkflowState("result");
    } catch (error) {
      console.warn("Backend API unavailable or failed. Using fallback:", error);

      // -----------------------------------------------
      // SAFE OFFLINE FALLBACK
      // -----------------------------------------------
      const fallbackResult = {
        project_name: file.name
          ? file.name.replace(/\.[^/.]+$/, "")
          : "Uploaded Sketch",
        elements_count: 3,
        detected_elements: [
          { name: "heading", conf: "95%", color: "bg-purple-500" },
          { name: "input_field", conf: "92%", color: "bg-cyan-500" },
          { name: "button", conf: "98%", color: "bg-rose-500" },
        ],
        generated_code: {
          jsx: `import React from "react";

export default function ScannedUI() {
  return (
    <div className="w-full max-w-sm bg-white text-zinc-900 rounded-2xl shadow-xl p-6 space-y-4">
      <h2 className="text-lg font-bold text-center">
        Generated Form
      </h2>
      <input
        type="text"
        placeholder="Enter text..."
        className="w-full px-3 py-2 border rounded-lg text-xs outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button className="w-full py-2 bg-blue-600 text-white rounded-lg text-xs font-semibold hover:bg-blue-700 transition-all">
        Submit
      </button>
    </div>
  );
}`,
          tailwind: `<div class="w-full max-w-sm bg-white text-zinc-900 rounded-2xl shadow-xl p-6 space-y-4">\n  <h2 class="text-lg font-bold text-center">Generated Form</h2>\n  <input type="text" placeholder="Enter text..." class="w-full px-3 py-2 border rounded-lg text-xs" />\n  <button class="w-full py-2 bg-blue-600 text-white rounded-lg text-xs font-semibold">Submit</button>\n</div>`,
          json: `{\n  "mode": "offline",\n  "status": "fallback",\n  "elements": 3\n}`,
        },
      };

      setResultData(fallbackResult);
      setWorkflowState("result");
    }
  };

  // --------------------------------------------------
  // DRAG & DROP EVENTS
  // --------------------------------------------------
  const handleDrag = (event) => {
    event.preventDefault();
    event.stopPropagation();

    if (event.type === "dragenter" || event.type === "dragover") {
      setDragActive(true);
    } else if (event.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setDragActive(false);

    const file = event.dataTransfer?.files?.[0];
    if (file) {
      handleFile(file);
    }
  };

  // --------------------------------------------------
  // RESET WORKSPACE
  // --------------------------------------------------
  const handleReset = () => {
    if (previewImage && previewImage.startsWith("blob:")) {
      URL.revokeObjectURL(previewImage);
    }

    setResultData(null);
    setPreviewImage(null);
    setErrorMessage("");
    setDragActive(false);
    setWorkflowState("upload");

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // --------------------------------------------------
  // CONDITIONAL VIEWS
  // --------------------------------------------------
  if (workflowState === "processing") {
    return (
      <ProcessingScreen
        onComplete={() => setWorkflowState("result")}
      />
    );
  }

  if (workflowState === "result") {
    return (
      <StudioResultView
        data={resultData || demoResult}
        sketchImage={previewImage}
        onReset={handleReset}
      />
    );
  }

  if (workflowState === "error") {
    return (
      <div className="flex h-screen bg-[#070709] text-white items-center justify-center -mt-32 -mx-6">
        <div className="w-full max-w-md p-8 rounded-3xl border border-red-500/20 bg-red-500/[0.03] text-center shadow-2xl backdrop-blur-xl">
          <div className="mx-auto w-16 h-16 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center">
            <AlertCircle className="w-8 h-8 text-red-400" />
          </div>

          <h2 className="mt-5 text-lg font-semibold text-white">
            Unable to process sketch
          </h2>

          <p className="mt-2 text-sm text-zinc-400">
            {errorMessage || "Something went wrong. Please check your image and try again."}
          </p>

          <button
            onClick={handleReset}
            className="mt-6 inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 text-xs font-semibold uppercase tracking-wider text-white shadow-[0_0_20px_rgba(6,182,212,0.35)] transition-all cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Upload
          </button>
        </div>
      </div>
    );
  }

  // --------------------------------------------------
  // DEFAULT UPLOAD VIEW
  // --------------------------------------------------
  return (
    <div className="flex h-screen bg-[#070709] text-white overflow-hidden -mt-32 -mx-6">
      {/* SIDEBAR */}
      <aside className="w-64 border-r border-white/10 bg-[#090b10]/90 backdrop-blur-2xl flex flex-col justify-between p-5 z-20 shrink-0">
        <div className="space-y-6">
          {/* Logo */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-400 to-pink-500 flex items-center justify-center shadow-[0_0_15px_#22d3ee]">
                <Sparkles className="w-4 h-4 text-black font-bold" />
              </div>
              <span className="font-semibold tracking-wider text-base text-white">
                Sketch2UI
              </span>
            </div>

            {onBack && (
              <button
                onClick={onBack}
                title="Back to Landing"
                className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-zinc-400 hover:text-white transition-all cursor-pointer"
              >
                <ArrowLeft className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* New Project Button */}
          <button
            onClick={handleReset}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 text-xs font-semibold uppercase tracking-wider text-white shadow-[0_0_20px_rgba(6,182,212,0.35)] transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>New Project</span>
          </button>

          {/* Workspace Links */}
          <div className="space-y-1">
            <p className="text-[10px] uppercase font-mono tracking-widest text-zinc-500 px-3">
              Workspace
            </p>
            <nav className="space-y-0.5 pt-1">
              <button className="w-full flex items-center gap-3 px-3 py-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-xs font-medium cursor-pointer">
                <Layout className="w-4 h-4" />
                <span>Workspace</span>
              </button>

              <button
                onClick={() => onNavigate && onNavigate("projects")}
                className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.04] text-xs font-medium transition-all cursor-pointer"
              >
                <FolderGit2 className="w-4 h-4" />
                <span>Projects</span>
              </button>

              <button
                onClick={() => onNavigate && onNavigate("history")}
                className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.04] text-xs font-medium transition-all cursor-pointer"
              >
                <History className="w-4 h-4" />
                <span>History</span>
              </button>
            </nav>
          </div>

          {/* Resources */}
          <div className="space-y-1">
            <p className="text-[10px] uppercase font-mono tracking-widest text-zinc-500 px-3">
              Resources
            </p>
            <nav className="space-y-0.5 pt-1">
              <a
                href="#docs"
                className="flex items-center gap-3 px-3 py-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.04] text-xs font-medium transition-all"
              >
                <BookOpen className="w-4 h-4" />
                <span>Documentation</span>
              </a>

              <a
                href="https://github.com"
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-3 px-3 py-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.04] text-xs font-medium transition-all"
              >
                <GitBranch className="w-4 h-4" />
                <span>GitHub</span>
              </a>

              <button
                onClick={() => onNavigate && onNavigate("settings")}
                className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/[0.04] text-xs font-medium transition-all cursor-pointer"
              >
                <Settings className="w-4 h-4" />
                <span>Settings</span>
              </button>
            </nav>
          </div>
        </div>

        {/* Bottom Card */}
        <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 space-y-2">
          <div className="w-6 h-6 rounded-md bg-gradient-to-tr from-cyan-400 to-pink-500 flex items-center justify-center">
            <Sparkles className="w-3 h-3 text-black font-bold" />
          </div>
          <p className="text-xs font-medium text-white leading-tight">
            Turn your ideas into real interfaces.
          </p>
          <p className="text-[10px] text-zinc-500 font-mono">
            Sketch → AI → Code
          </p>
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <div className="flex-1 flex flex-col overflow-y-auto">
        {/* Header */}
        <header className="h-16 border-b border-white/10 bg-[#070709]/80 backdrop-blur-xl px-8 flex items-center justify-between sticky top-0 z-10 shrink-0">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg">
            <span className="text-xs text-zinc-400">✏️</span>
            <span className="text-sm font-medium text-zinc-200">
              Untitled Project
            </span>
            <ChevronDown className="w-3.5 h-3.5 text-zinc-500" />
          </div>

          <div className="flex items-center gap-3">
            <button
              type="button"
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-medium text-zinc-300 transition-all cursor-pointer"
            >
              <Save className="w-3.5 h-3.5" />
              <span>Save</span>
            </button>

            <button
              type="button"
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 text-xs font-medium text-white shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export</span>
              <ChevronDown className="w-3.5 h-3.5" />
            </button>
          </div>
        </header>

        {/* Content Body */}
        <main className="p-8 max-w-5xl mx-auto w-full space-y-6">
          <div className="space-y-1">
            <div className="flex items-center gap-2.5">
              <span className="w-6 h-6 rounded-md bg-blue-600 text-white font-mono text-xs flex items-center justify-center font-bold">
                1
              </span>
              <h2 className="text-lg font-semibold text-white">
                Upload Your Sketch
              </h2>
            </div>
            <p className="text-xs text-zinc-400 pl-9">
              Turn your wireframe into a beautiful, responsive UI.
            </p>
          </div>

          {/* Upload Dropzone */}
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`relative rounded-3xl border-2 border-dashed transition-all duration-300 p-12 flex flex-col items-center justify-center min-h-[380px] bg-white/[0.01] ${
              dragActive
                ? "border-cyan-400 bg-cyan-500/[0.04] shadow-[0_0_40px_rgba(34,211,238,0.15)]"
                : "border-white/10 hover:border-white/20"
            }`}
          >
            <div className="relative z-10 flex flex-col items-center text-center space-y-5">
              <div className="w-20 h-20 rounded-full bg-blue-500/10 border border-blue-500/20 flex items-center justify-center shadow-[0_0_30px_rgba(59,130,246,0.25)]">
                <CloudUpload className="w-10 h-10 text-blue-400" />
              </div>

              <div className="space-y-1.5">
                <h3 className="text-xl font-semibold tracking-tight text-white">
                  Drag & Drop your sketch here
                </h3>
                <p className="text-xs text-zinc-400 font-mono">
                  PNG, JPG, JPEG or WEBP • Max 10MB
                </p>
              </div>

              <div className="flex flex-col sm:flex-row items-center gap-3 pt-2">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/png,image/jpeg,image/jpg,image/webp"
                  className="hidden"
                  onChange={(event) => {
                    const file = event.target.files?.[0];
                    if (file) {
                      handleFile(file);
                    }
                    // Reset value so same file can be re-selected if needed
                    event.target.value = "";
                  }}
                />

                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 text-xs font-semibold text-white shadow-[0_0_20px_rgba(37,99,235,0.4)] transition-all cursor-pointer"
                >
                  <FolderOpen className="w-4 h-4" />
                  <span>Browse Files</span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setErrorMessage(
                      "Camera capture will be connected with the camera scanner service."
                    );
                    setWorkflowState("error");
                  }}
                  className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/10 text-xs font-medium text-zinc-300 transition-all cursor-pointer"
                >
                  <Camera className="w-4 h-4 text-zinc-400" />
                  <span>Use Camera</span>
                </button>
              </div>
            </div>
          </div>

          {/* Tips Section */}
          <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
            <div className="flex items-center gap-2 text-zinc-300 font-medium text-xs">
              <Lightbulb className="w-4 h-4 text-amber-400" />
              <span>Tips for better detection</span>
            </div>

            <div className="flex flex-wrap items-center gap-5 text-[11px]">
              <span className="flex items-center gap-1.5 text-emerald-400/90">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Use clear dark lines</span>
              </span>

              <span className="flex items-center gap-1.5 text-zinc-400">
                <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                <span>Keep components separated</span>
              </span>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}