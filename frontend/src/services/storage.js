/**
 * Storage Service for Sketch2UI
 * Unified localStorage persistence adhering to the project schema.
 */

export const STORAGE_KEY = 'sketch2ui_projects';

/**
 * Generates a unique project identifier.
 */
function generateId() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `proj_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * Returns all saved projects sorted by updatedAt descending.
 * @returns {Array<Object>}
 */
export function getProjects() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];

    return parsed.sort((a, b) => {
      const timeA = new Date(a.updatedAt || a.createdAt || 0).getTime();
      const timeB = new Date(b.updatedAt || b.createdAt || 0).getTime();
      return timeB - timeA;
    });
  } catch (err) {
    console.error('[storage] Failed to parse sketch2ui_projects:', err);
    return [];
  }
}

/**
 * Retrieves a single project by id.
 * @param {string} id
 * @returns {Object|null}
 */
export function getProjectById(id) {
  if (!id) return null;
  const projects = getProjects();
  return projects.find((p) => p.id === id) || null;
}

/**
 * Saves a project (creates or updates).
 * Enforces unified project schema:
 * {
 *   id: string,
 *   name: string,
 *   createdAt: ISO string,
 *   updatedAt: ISO string,
 *   thumbnail: string (base64 or dataURL),
 *   elements_count: number,
 *   detected_elements: Array<{ name, conf, box, color }>,
 *   generated_code: {
 *     framework: "React + Tailwind",
 *     jsx: string,
 *     tailwind: string,
 *     json: string
 *   }
 * }
 * @param {Object} projectData
 * @returns {Object} Saved project
 */
export function saveProject(projectData) {
  if (!projectData) return null;

  const now = new Date().toISOString();
  const projects = getProjects();

  const id = projectData.id || generateId();
  const existingIndex = projects.findIndex((p) => p.id === id);
  const existing = existingIndex >= 0 ? projects[existingIndex] : null;

  const elements = Array.isArray(projectData.detected_elements)
    ? projectData.detected_elements
    : (existing?.detected_elements || []);

  const elementsCount = typeof projectData.elements_count === 'number'
    ? projectData.elements_count
    : (elements.length || existing?.elements_count || 0);

  const thumbnail = projectData.thumbnail || projectData.preview || existing?.thumbnail || existing?.preview || '';

  const generatedCode = {
    framework: projectData.generated_code?.framework || existing?.generated_code?.framework || "React + Tailwind",
    jsx: projectData.generated_code?.jsx || existing?.generated_code?.jsx || "",
    tailwind: projectData.generated_code?.tailwind || existing?.generated_code?.tailwind || "",
    json: projectData.generated_code?.json || existing?.generated_code?.json || ""
  };

  const name = (
    projectData.name ||
    existing?.name ||
    projectData.project_name ||
    `Wireframe - ${new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`
  ).trim();

  const projectToSave = {
    id,
    name,
    createdAt: existing?.createdAt || projectData.createdAt || now,
    updatedAt: now,
    thumbnail,
    elements_count: elementsCount,
    detected_elements: elements,
    generated_code: generatedCode
  };

  if (existingIndex >= 0) {
    projects[existingIndex] = projectToSave;
  } else {
    projects.unshift(projectToSave);
  }

  // Keep sorted by updatedAt descending
  projects.sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime());

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(projects));
  } catch (err) {
    console.error('[storage] Failed to write to localStorage:', err);
  }

  return projectToSave;
}

/**
 * Removes a project by id and returns updated array.
 * @param {string} id
 * @returns {Array<Object>} Updated projects list
 */
export function deleteProject(id) {
  if (!id) return getProjects();
  const current = getProjects();
  const updated = current.filter((p) => p.id !== id);

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  } catch (err) {
    console.error('[storage] Failed to delete project from localStorage:', err);
  }

  return updated;
}

/**
 * Renames an existing project and updates its updatedAt timestamp.
 * @param {string} id
 * @param {string} newName
 * @returns {Object|null} Updated project or null
 */
export function renameProject(id, newName) {
  if (!id || typeof newName !== 'string') return null;

  const projects = getProjects();
  const target = projects.find((p) => p.id === id);
  if (!target) return null;

  target.name = newName.trim() || 'Untitled Wireframe';
  target.updatedAt = new Date().toISOString();

  projects.sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime());

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(projects));
  } catch (err) {
    console.error('[storage] Failed to update project name in localStorage:', err);
  }

  return target;
}

/**
 * Converts a File or Blob into a compressed base64 dataURL for localStorage safety.
 * Max dimensions: 640x640 JPEG (typically 20KB - 40KB).
 * @param {File|Blob|string} fileOrDataUrl
 * @returns {Promise<string>}
 */
export function fileToDataUrl(fileOrDataUrl) {
  return new Promise((resolve) => {
    if (!fileOrDataUrl) {
      resolve('');
      return;
    }

    if (typeof fileOrDataUrl === 'string') {
      if (fileOrDataUrl.startsWith('data:')) {
        // Compress data URL if needed via Image
        const img = new Image();
        img.onload = () => {
          const MAX_DIM = 640;
          let w = img.width;
          let h = img.height;
          if (w > MAX_DIM || h > MAX_DIM) {
            if (w > h) {
              h = Math.round((h * MAX_DIM) / w);
              w = MAX_DIM;
            } else {
              w = Math.round((w * MAX_DIM) / h);
              h = MAX_DIM;
            }
          }
          const canvas = document.createElement('canvas');
          canvas.width = w;
          canvas.height = h;
          const ctx = canvas.getContext('2d');
          ctx.drawImage(img, 0, 0, w, h);
          resolve(canvas.toDataURL('image/jpeg', 0.85));
        };
        img.onerror = () => resolve(fileOrDataUrl);
        img.src = fileOrDataUrl;
        return;
      }
      resolve(fileOrDataUrl);
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const dataUrl = e.target?.result;
      if (!dataUrl) {
        resolve('');
        return;
      }
      const img = new Image();
      img.onload = () => {
        const MAX_DIM = 640;
        let w = img.width;
        let h = img.height;
        if (w > MAX_DIM || h > MAX_DIM) {
          if (w > h) {
            h = Math.round((h * MAX_DIM) / w);
            w = MAX_DIM;
          } else {
            w = Math.round((w * MAX_DIM) / h);
            h = MAX_DIM;
          }
        }
        const canvas = document.createElement('canvas');
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, w, h);
        resolve(canvas.toDataURL('image/jpeg', 0.85));
      };
      img.onerror = () => resolve(dataUrl);
      img.src = dataUrl;
    };
    reader.onerror = () => resolve('');
    reader.readAsDataURL(fileOrDataUrl);
  });
}

/**
 * Returns human-readable relative time string.
 * e.g., "Modified just now", "Modified 2 mins ago", "Modified 3 hours ago"
 * @param {string|Date} dateValue
 * @returns {string}
 */
export function formatRelativeTime(dateValue) {
  if (!dateValue) return 'Recently';
  const date = new Date(dateValue);
  const now = new Date();
  const diffInSec = Math.floor((now - date) / 1000);

  if (diffInSec < 0 || diffInSec < 30) return 'Modified just now';
  if (diffInSec < 60) return `Modified ${diffInSec}s ago`;

  const diffInMin = Math.floor(diffInSec / 60);
  if (diffInMin < 60) return `Modified ${diffInMin} min${diffInMin > 1 ? 's' : ''} ago`;

  const diffInHours = Math.floor(diffInMin / 60);
  if (diffInHours < 24) return `Modified ${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`;

  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays === 1) return 'Modified yesterday';
  if (diffInDays < 7) return `Modified ${diffInDays} days ago`;

  return `Modified ${date.toLocaleDateString()}`;
}

export const SETTINGS_KEY = 'sketch2ui_settings';

export const DEFAULT_SETTINGS = {
  framework: 'React 19',
  styling: 'Tailwind CSS',
  targetFormat: 'Functional Component JSX',
  includeMockStateHooks: false,
};

/**
 * Retrieves persisted settings or default values.
 * @returns {Object}
 */
export function getSettings() {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    if (!raw) return { ...DEFAULT_SETTINGS };
    const parsed = JSON.parse(raw);
    return { ...DEFAULT_SETTINGS, ...parsed };
  } catch (err) {
    console.error('[storage] Failed to parse sketch2ui_settings:', err);
    return { ...DEFAULT_SETTINGS };
  }
}

/**
 * Persists settings to localStorage.
 * @param {Object} newSettings
 * @returns {Object} Updated settings
 */
export function saveSettings(newSettings) {
  try {
    const current = getSettings();
    const updated = { ...current, ...newSettings };
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(updated));
    return updated;
  } catch (err) {
    console.error('[storage] Failed to write settings to localStorage:', err);
    return { ...DEFAULT_SETTINGS, ...newSettings };
  }
}

/**
 * Safely clears all projects from localStorage.
 */
export function clearAllProjects() {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (err) {
    console.error('[storage] Failed to clear projects from localStorage:', err);
  }
}

/**
 * Calculates current storage footprint in projects count and estimated KB.
 * @returns {{ count: number, bytes: number, kb: string }}
 */
export function getStorageUsage() {
  try {
    const rawProjects = localStorage.getItem(STORAGE_KEY) || '[]';
    const rawSettings = localStorage.getItem(SETTINGS_KEY) || '{}';
    const projects = getProjects();
    // Rough character byte size in UTF-16
    const totalBytes = (rawProjects.length + rawSettings.length) * 2;
    const kb = (totalBytes / 1024).toFixed(1);

    return {
      count: projects.length,
      bytes: totalBytes,
      kb
    };
  } catch {
    return { count: 0, bytes: 0, kb: '0.0' };
  }
}

/**
 * Exports all projects as a formatted JSON string backup.
 * @returns {string}
 */
export function exportAllProjectsJson() {
  const projects = getProjects();
  return JSON.stringify({
    version: '1.0.0',
    exportedAt: new Date().toISOString(),
    totalProjects: projects.length,
    projects
  }, null, 2);
}

export default {
  STORAGE_KEY,
  SETTINGS_KEY,
  DEFAULT_SETTINGS,
  getProjects,
  getProjectById,
  saveProject,
  deleteProject,
  renameProject,
  clearAllProjects,
  fileToDataUrl,
  formatRelativeTime,
  getSettings,
  saveSettings,
  getStorageUsage,
  exportAllProjectsJson
};
