export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const TOKEN_STORAGE_KEY = 'sketch2ui_token';
export const USER_STORAGE_KEY = 'sketch2ui_user';

/**
 * Returns current auth token from localStorage if available.
 */
export function getAuthToken() {
  if (typeof localStorage === 'undefined') return null;
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

/**
 * Returns Authorization header with Bearer token if available.
 */
export function getAuthHeaders(token = null) {
  const activeToken = token || getAuthToken();
  return activeToken ? { Authorization: `Bearer ${activeToken}` } : {};
}

/**
 * Normalizes an API project model into the client unified project format.
 */
export function normalizeApiProject(p) {
  if (!p) return null;
  const elements = p.ast_json?.detected_elements || p.ast_json?.elements || [];
  return {
    id: p.id,
    name: p.title || 'Untitled Wireframe',
    createdAt: p.created_at,
    updatedAt: p.updated_at,
    thumbnail: p.thumbnail_url || '',
    elements_count: elements.length || p.ast_json?.elements_count || 0,
    detected_elements: elements,
    generated_code: {
      framework: 'React + Tailwind',
      jsx: p.jsx_code || '',
      tailwind: p.tailwind_code || '',
      json: typeof p.ast_json === 'string' ? p.ast_json : JSON.stringify(p.ast_json || {})
    },
    isCloud: true,
    user_id: p.user_id
  };
}

/**
 * Converts client project format into API ProjectCreate payload.
 */
export function toApiProjectPayload(project) {
  let ast = project.ast_json;
  if (!ast && project.generated_code?.json) {
    try {
      ast = JSON.parse(project.generated_code.json);
    } catch {
      ast = {};
    }
  }

  return {
    title: project.name || project.title || 'Untitled Wireframe',
    thumbnail_url: project.thumbnail || project.preview || '',
    ast_json: ast || {
      detected_elements: project.detected_elements || [],
      elements_count: project.elements_count || 0
    },
    jsx_code: project.generated_code?.jsx || project.jsx_code || '',
    tailwind_code: project.generated_code?.tailwind || project.tailwind_code || ''
  };
}

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
      headers: {
        ...getAuthHeaders(),
      },
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
 */
export async function exportProjectZip(projectName, jsxCode) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/sketch/export-zip`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
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

  let filename = `${(projectName || 'wireframe').toLowerCase().replace(/[^\w\s-]/g, '').trim().replace(/[\s-]+/g, '_')}.zip`;
  if (!filename.startsWith('sketch2ui_')) {
    filename = `sketch2ui_${filename}`;
  }

  const disposition = response.headers.get('Content-Disposition');
  if (disposition && disposition.includes('filename=')) {
    const match = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
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

/* =========================================================================
   AUTH API SERVICES
   ========================================================================= */

/**
 * Authenticates with email and password.
 */
export async function loginUser(email, password) {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to sign in. Please verify your credentials.');
  }
  return data;
}

/**
 * Registers a new user account.
 */
export async function signupUser(email, password, name) {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, name })
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to create account.');
  }
  return data;
}

/**
 * Fetches current authenticated user profile using Bearer token.
 */
export async function fetchCurrentUser(token) {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
    headers: {
      ...getAuthHeaders(token)
    }
  });

  if (!response.ok) {
    throw new Error('Authentication expired or invalid');
  }
  return await response.json();
}

/* =========================================================================
   PROJECTS PERSISTENCE API SERVICES
   ========================================================================= */

/**
 * Fetches all projects for the current user (or guest projects).
 */
export async function fetchProjects(token) {
  const response = await fetch(`${API_BASE_URL}/api/v1/projects`, {
    headers: {
      ...getAuthHeaders(token)
    }
  });

  if (!response.ok) {
    throw new Error('Failed to fetch projects from server');
  }

  const rawProjects = await response.json();
  return rawProjects.map(normalizeApiProject);
}

/**
 * Saves a new project to cloud persistence.
 */
export async function createProject(projectData, token) {
  const payload = toApiProjectPayload(projectData);
  const response = await fetch(`${API_BASE_URL}/api/v1/projects`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(token)
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to create project in cloud');
  }

  const saved = await response.json();
  return normalizeApiProject(saved);
}

/**
 * Updates an existing project on the cloud server.
 */
export async function updateProjectApi(id, projectData, token) {
  const payload = toApiProjectPayload(projectData);
  const response = await fetch(`${API_BASE_URL}/api/v1/projects/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(token)
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to update project');
  }

  const updated = await response.json();
  return normalizeApiProject(updated);
}

/**
 * Deletes a project from cloud persistence.
 */
export async function deleteProjectApi(id, token) {
  const response = await fetch(`${API_BASE_URL}/api/v1/projects/${id}`, {
    method: 'DELETE',
    headers: {
      ...getAuthHeaders(token)
    }
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to delete project');
  }

  return await response.json();
}
