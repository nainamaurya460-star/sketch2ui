/**
 * Deterministic Client-Side AST & Layout Synthesizer for Sketch2UI.
 * Mirrors backend heuristic clustering and JSX/Tailwind code generation with zero latency.
 */

function sanitizeComponentName(name) {
  if (!name || !name.trim()) return "SynthesizedWireframe";
  return name
    .replace(/[^a-zA-Z0-9\s]/g, "")
    .trim()
    .split(/\s+/)
    .map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join("") || "SynthesizedWireframe";
}

function normalizeElementCoords(el, idx) {
  let x1 = 0, y1 = 0, x2 = 100, y2 = 40;
  if (Array.isArray(el.box) && el.box.length === 4) {
    y1 = el.box[0];
    x1 = el.box[1];
    y2 = el.box[2];
    x2 = el.box[3];
  } else if (el.x1 !== undefined && el.y1 !== undefined) {
    x1 = el.x1;
    y1 = el.y1;
    x2 = el.x2;
    y2 = el.y2;
  }

  const w = Math.max(1, x2 - x1);
  const h = Math.max(1, y2 - y1);

  return {
    ...el,
    id: el.id || `el_${idx}`,
    x1,
    y1,
    x2,
    y2,
    w,
    h,
    area: w * h,
  };
}

function computeVerticalOverlap(a, b) {
  const interY = Math.min(a.y2, b.y2) - Math.max(a.y1, b.y1);
  if (interY <= 0) return 0.0;
  const minH = Math.min(a.h, b.h);
  return minH > 0 ? interY / minH : 0.0;
}

function areHorizontallyAligned(a, b) {
  const standalone = ['heading', 'header', 'title', 'image', 'img', 'photo'];
  const aType = (a.name || '').toLowerCase();
  const bType = (b.name || '').toLowerCase();

  if (standalone.includes(aType) || standalone.includes(bType)) return false;
  const overlapY = computeVerticalOverlap(a, b);
  if (overlapY < 0.5) return false;

  const minH = Math.min(a.h, b.h);
  const maxH = Math.max(a.h, b.h);
  if (maxH > 0 && minH / maxH < 0.35) return false;

  const ix1 = Math.max(a.x1, b.x1);
  const ix2 = Math.min(a.x2, b.x2);
  const interX = ix2 - ix1;
  const minW = Math.min(a.w, b.w);
  const tolerance = Math.max(15, Math.floor(0.15 * minW));
  if (interX > tolerance) return false;

  return true;
}

export function clusterElementsIntoRows(elements) {
  if (!elements || elements.length === 0) return [];
  const normalized = elements.map((el, i) => normalizeElementCoords(el, i));
  normalized.sort((a, b) => (a.y1 - b.y1) || (a.x1 - b.x1));

  const n = normalized.length;
  const adj = Array.from({ length: n }, () => []);

  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      if (areHorizontallyAligned(normalized[i], normalized[j])) {
        adj[i].push(j);
        adj[j].push(i);
      }
    }
  }

  const visited = new Set();
  const clusters = [];

  for (let i = 0; i < n; i++) {
    if (visited.has(i)) continue;

    const comp = [];
    const queue = [i];
    visited.add(i);

    while (queue.length > 0) {
      const curr = queue.shift();
      comp.push(curr);
      for (const neighbor of adj[curr]) {
        if (!visited.has(neighbor)) {
          visited.add(neighbor);
          queue.push(neighbor);
        }
      }
    }

    const clusterElems = comp.map(idx => normalized[idx]);
    clusterElems.sort((a, b) => a.x1 - b.x1);

    if (clusterElems.length >= 2) {
      clusters.push({
        type: 'row_cluster',
        is_row: true,
        elements: clusterElems,
        is_all_buttons: clusterElems.every(e => ['button', 'btn', 'submit'].includes((e.name || '').toLowerCase()))
      });
    } else {
      clusters.push({
        type: 'single',
        is_row: false,
        element: clusterElems[0]
      });
    }
  }

  return clusters;
}

function renderElement(el, isJsx = true, inRow = false, isSecondaryBtn = false) {
  const type = (el.name || 'TextBox').toLowerCase().replace(/[- ]/g, '_');
  const attr = isJsx ? 'className' : 'class';
  const customText = (el.text || '').trim();

  // 1. Heading
  if (['heading', 'title', 'header'].includes(type)) {
    const text = customText || 'Section Title';
    return `<h2 ${attr}="text-lg font-bold tracking-tight text-white">${text}</h2>`;
  }

  // 2. Button
  if (['button', 'btn', 'submit'].includes(type)) {
    const isSecondary = isSecondaryBtn || el.variant === 'secondary';
    if (isSecondary) {
      const text = customText || 'Cancel';
      return `<button ${attr}="px-4 py-2.5 rounded-xl border border-white/10 hover:bg-white/5 text-zinc-300 font-semibold text-xs transition-all cursor-pointer">${text}</button>`;
    } else {
      const text = customText || 'Submit';
      return `<button ${attr}="px-4 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black font-semibold text-xs shadow-lg shadow-cyan-500/20 transition-all cursor-pointer">${text}</button>`;
    }
  }

  // 3. TextBox / Input
  if (['textbox', 'input', 'input_field', 'textfield'].includes(type)) {
    const placeholder = customText || 'Enter text...';
    const inputType = placeholder.toLowerCase().includes('password') ? 'password' : 'text';
    const widthCls = inRow ? 'flex-1 w-full' : 'w-full';
    return `<input type="${inputType}" placeholder="${placeholder}" ${attr}="${widthCls} px-3.5 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-xs placeholder-zinc-500 focus:outline-none focus:border-cyan-500/50" />`;
  }

  // 4. Paragraph
  if (['paragraph', 'desc', 'description'].includes(type)) {
    const text = customText || 'Turn your hand-drawn wireframes into production-ready UI components instantly.';
    return `<p ${attr}="text-xs text-zinc-400 leading-relaxed">${text}</p>`;
  }

  // 5. Label
  if (['label', 'text'].includes(type)) {
    const text = customText || 'Label Field';
    return `<label ${attr}="block text-xs font-medium text-zinc-300">${text}</label>`;
  }

  // 6. CheckBox
  if (['checkbox', 'check_box'].includes(type)) {
    const text = customText || 'Remember preference';
    return `<label ${attr}="flex items-center gap-2.5 text-xs text-zinc-300 cursor-pointer">
  <input type="checkbox" ${attr}="w-4 h-4 rounded bg-white/5 border-white/10 text-cyan-500 focus:ring-0 cursor-pointer" />
  <span>${text}</span>
</label>`;
  }

  // 7. RadioButton
  if (['radiobutton', 'radio_button', 'radio'].includes(type)) {
    const text = customText || 'Standard Option';
    return `<label ${attr}="flex items-center gap-2.5 text-xs text-zinc-300 cursor-pointer">
  <input type="radio" name="wireframe_radio_group" ${attr}="w-4 h-4 bg-white/5 border-white/10 text-cyan-500 focus:ring-0 cursor-pointer" />
  <span>${text}</span>
</label>`;
  }

  // 8. Image
  if (['image', 'img', 'photo'].includes(type)) {
    return `<div ${attr}="w-full aspect-video rounded-xl bg-white/5 border border-dashed border-white/10 flex items-center justify-center text-zinc-500 text-xs font-mono">Image Placeholder</div>`;
  }

  // 9. Select
  if (['select', 'dropdown'].includes(type)) {
    const opt = customText || 'Select an option...';
    return `<div ${attr}="relative w-full">
  <select ${attr}="w-full px-3.5 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-xs appearance-none focus:outline-none focus:border-cyan-500/50 cursor-pointer">
    <option value="" disabled selected>${opt}</option>
    <option value="1">Primary Tier</option>
    <option value="2">Secondary Option</option>
  </select>
</div>`;
  }

  // 10. Link
  if (['link', 'anchor'].includes(type)) {
    const text = customText || 'Learn More &rarr;';
    return `<a href="#details" ${attr}="text-xs text-cyan-400 hover:text-cyan-300 underline underline-offset-2 transition-colors">${text}</a>`;
  }

  // Fallback
  return `<div ${attr}="p-3 rounded-xl bg-white/5 border border-white/10 text-xs text-zinc-300">${customText || el.name || 'Component'}</div>`;
}

/**
 * Deterministically generates React JSX and Tailwind markup from an elements array.
 */
export function generateJsxAndTailwind(elements, projectName = 'Synthesized Wireframe') {
  const componentName = sanitizeComponentName(projectName);
  const clusters = clusterElementsIntoRows(elements);

  const lines = [];

  for (const cluster of clusters) {
    if (cluster.is_row) {
      if (cluster.is_all_buttons) {
        // Button row
        lines.push('      <div className="flex items-center justify-end gap-3 w-full pt-2">');
        cluster.elements.forEach((el, idx) => {
          const isSecondary = idx === 0 && cluster.elements.length > 1;
          const rendered = renderElement(el, true, true, isSecondary);
          lines.push(`        ${rendered}`);
        });
        lines.push('      </div>');
      } else {
        // Responsive input/element row
        lines.push('      <div className="flex flex-col sm:flex-row items-center gap-4 w-full">');
        cluster.elements.forEach((el) => {
          const rendered = renderElement(el, true, true, false);
          lines.push(`        ${rendered}`);
        });
        lines.push('      </div>');
      }
    } else {
      const rendered = renderElement(cluster.element, true, false, false);
      lines.push(`      ${rendered}`);
    }
  }

  const innerMarkup = lines.join('\n');

  const jsx = `import React from "react";

export default function ${componentName}() {
  return (
    <div className="w-full max-w-md mx-auto p-6 rounded-3xl bg-[#090b10]/90 border border-white/10 backdrop-blur-2xl shadow-2xl space-y-4">
${innerMarkup}
    </div>
  );
}
`;

  const tailwind = `<div class="w-full max-w-md mx-auto p-6 rounded-3xl bg-[#090b10]/90 border border-white/10 backdrop-blur-2xl shadow-2xl space-y-4">
${lines.map(line => line.replace(/className=/g, 'class=')).join('\n')}
</div>`;

  return {
    jsx,
    tailwind,
    json: JSON.stringify(elements, null, 2),
    framework: 'React + Tailwind',
  };
}
