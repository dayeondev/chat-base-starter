// Runtime Configuration Loader
window.__ENV__ = window.__ENV__ || {};

// Fallback for development (when running with npm run dev)
if (!window.__ENV__.VITE_API_URL && import.meta.env.VITE_API_URL) {
  window.__ENV__.VITE_API_URL = import.meta.env.VITE_API_URL;
}

// Default fallback
if (!window.__ENV__.VITE_API_URL) {
  window.__ENV__.VITE_API_URL = 'http://localhost:8080';
}

export const env = window.__ENV__;
