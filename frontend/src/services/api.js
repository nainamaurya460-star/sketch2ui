export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Predicts UI components from an uploaded sketch file.
 * Hits real FastAPI endpoint: POST ${API_BASE_URL}/api/v1/sketch/predict
 */
export async function predictSketch(file) {
  const formData = new FormData();
  formData.append('file', file);

  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/sketch/predict`, {
      method: 'POST',
      body: formData,
    });
  } catch {
    throw new Error(`Cannot connect to AI inference engine (${API_BASE_URL}). Please verify that the FastAPI backend server is running.`);
  }

  if (!response.ok) {
    let errorDetail = `HTTP ${response.status} ${response.statusText}`;
    try {
      const errJson = await response.json();
      if (errJson && errJson.detail) {
        errorDetail = errJson.detail;
      }
    } catch {
      try {
        const errText = await response.text();
        if (errText) errorDetail = errText;
      } catch {
        // Fallback to HTTP status text
      }
    }
    throw new Error(errorDetail);
  }

  return await response.json();
}

/**
 * Exports the complete synthesized React + Tailwind project boilerplate as a ZIP.
 * Hits POST ${API_BASE_URL}/api/v1/sketch/export-zip
 * Creates a blob download trigger in the browser.
 */
export async function exportProjectZip(projectName, jsxCode) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/sketch/export-zip`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        project_name: projectName || 'Synthesized Wireframe',
        jsx_code: jsxCode || '// Empty UI component',
      }),
    });
  } catch {
    throw new Error(`Cannot connect to backend server (${API_BASE_URL}) to export ZIP. Please verify the backend is running.`);
  }

  if (!response.ok) {
    let errorDetail = `Failed to generate ZIP (HTTP ${response.status})`;
    try {
      const errJson = await response.json();
      if (errJson && errJson.detail) {
        errorDetail = errJson.detail;
      }
    } catch {
      try {
        const errText = await response.text();
        if (errText) errorDetail = errText;
      } catch {
        // Fallback
      }
    }
    throw new Error(errorDetail);
  }

  // Determine download filename from Content-Disposition header if available
  let filename = `${(projectName || 'wireframe').toLowerCase().replace(/[^\\w\\s-]/g, '').trim().replace(/[\\s-]+/g, '_')}.zip`;
  if (!filename.startsWith('sketch2ui_')) {
    filename = `sketch2ui_${filename}`;
  }

  const disposition = response.headers.get('Content-Disposition');
  if (disposition && disposition.includes('filename=')) {
    const match = disposition.match(/filename[^;=\\n]*=((['"]).*?\\2|[^;\\n]*)/);
    if (match && match[1]) {
      filename = match[1].replace(/['"]/g, '').trim();
    }
  }

  const blob = await response.blob();
  const blobUrl = window.URL.createObjectURL(blob);
  const downloadLink = document.createElement('a');
  downloadLink.href = blobUrl;
  downloadLink.download = filename;
  document.body.appendChild(downloadLink);
  downloadLink.click();
  document.body.removeChild(downloadLink);
  window.URL.revokeObjectURL(blobUrl);

  return { success: true, filename };
}