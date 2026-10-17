import io
import json
import re
import zipfile
from typing import Optional


def sanitize_project_name(name: Optional[str]) -> str:
    """
    Sanitizes project name into a safe, filesystem-compatible slug.
    Example: 'My Wireframe #1' -> 'my_wireframe_1'
    """
    if not name or not name.strip():
        return "wireframe"
    
    # Strip illegal filename characters
    cleaned = re.sub(r"[^\w\s-]", "", name).strip()
    cleaned = re.sub(r"[\s-]+", "_", cleaned).lower()
    return cleaned or "wireframe"


def sanitize_package_name(name: Optional[str]) -> str:
    """
    Sanitizes project name into a valid npm package name.
    Example: 'My Wireframe #1' -> 'sketch2ui-my-wireframe-1'
    """
    slug = sanitize_project_name(name).replace("_", "-")
    return f"sketch2ui-{slug}"


def format_app_jsx(jsx_code: str) -> str:
    """
    Ensures jsx_code is formatted as a valid ES module with a default export.
    """
    code = (jsx_code or "").strip()
    if not code:
        code = '<div className="text-center p-8 text-zinc-400">No wireframe components generated</div>'

    if "export default" in code:
        if "import React" not in code:
            return f'import React from "react";\n\n{code}\n'
        return f"{code}\n"
    
    # If it's a function declaration without default export
    if code.startswith("function ") or "function " in code:
        return f'import React from "react";\n\nexport default {code}\n'

    # Otherwise wrap raw JSX elements in a standard App component
    return f'''import React from "react";

export default function App() {{
  return (
    <div className="min-h-screen bg-[#070709] text-white flex items-center justify-center p-6">
      {code}
    </div>
  );
}}
'''


def generate_project_zip(project_name: str, jsx_code: str) -> io.BytesIO:
    """
    Generates a complete, production-ready Vite + React 19 + Tailwind CSS project
    boilerplate in-memory as a ZIP archive.
    
    Returns an in-memory io.BytesIO buffer positioned at the beginning.
    """
    safe_name = (project_name or "Synthesized Wireframe").strip()
    pkg_name = sanitize_package_name(safe_name)
    app_jsx_content = format_app_jsx(jsx_code)

    # 1. package.json
    package_json = {
        "name": pkg_name,
        "private": True,
        "version": "0.1.0",
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "vite build",
            "preview": "vite preview"
        },
        "dependencies": {
            "react": "^19.0.0",
            "react-dom": "^19.0.0",
            "lucide-react": "^1.49.0"
        },
        "devDependencies": {
            "@tailwindcss/vite": "^4.0.0",
            "@types/react": "^19.0.0",
            "@types/react-dom": "^19.0.0",
            "@vitejs/plugin-react": "^4.3.4",
            "tailwindcss": "^4.0.0",
            "vite": "^6.0.0"
        }
    }
    package_json_str = json.dumps(package_json, indent=2) + "\n"

    # 2. vite.config.js
    vite_config_str = """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
});
"""

    # 3. index.html
    index_html_str = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2306b6d4' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><polygon points='12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2'/></svg>" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{safe_name} | Sketch2UI</title>
  </head>
  <body class="bg-[#070709] text-white antialiased min-h-screen">
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
"""

    # 4. README.md
    readme_str = f"""# {safe_name}

> Synthesized with **[Sketch2UI](https://github.com/nainamaurya460-star/sketch2ui)** — AI-Powered Hand-Drawn Wireframe to Responsive React + Tailwind Component.

---

## 🚀 Quick Start

Ensure you have [Node.js](https://nodejs.org/) installed (v18+ recommended).

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

### 3. Build for Production
```bash
npm run build
```

---

## 📁 Package Architecture
```text
├── index.html           # HTML entry point with dark backdrop
├── package.json         # React 19, Tailwind CSS v4, Vite 6
├── vite.config.js       # Vite configuration with Tailwind CSS v4 plugin
├── README.md            # Quick start instructions
└── src/
    ├── main.jsx         # React application bootstrap
    ├── index.css        # Tailwind CSS v4 directives & global resets
    └── App.jsx          # Synthesized wireframe component
```

---

## 🎨 Tech Stack
- **React 19**
- **Vite 6**
- **Tailwind CSS v4** (`@tailwindcss/vite`)
- **Lucide Icons**
"""

    # 5. src/main.jsx
    main_jsx_str = """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
"""

    # 6. src/index.css
    index_css_str = """@import "tailwindcss";

body {
  margin: 0;
  min-height: 100vh;
  background-color: #070709;
  color: #ffffff;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
"""

    # Assemble ZIP in-memory without touching disk
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("index.html", index_html_str)
        zf.writestr("package.json", package_json_str)
        zf.writestr("vite.config.js", vite_config_str)
        zf.writestr("README.md", readme_str)
        zf.writestr("src/main.jsx", main_jsx_str)
        zf.writestr("src/index.css", index_css_str)
        zf.writestr("src/App.jsx", app_jsx_content)

    zip_buffer.seek(0)
    return zip_buffer
