// API Configuration
// Centralizing the API URL to avoid hardcoded strings across the app

const getApiUrl = () => {
  if (import.meta.env.VITE_API_URL) return import.meta.env.VITE_API_URL;
  // If no env var, use the current domain as the backend (since they are bundled)
  if (typeof window !== 'undefined') {
    return window.location.origin;
  }
  return 'http://localhost:5000';
};

export const API_BASE_URL = getApiUrl();

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: `${API_BASE_URL}/api/auth/login`,
    REGISTER: `${API_BASE_URL}/api/auth/register`,
    VERIFY: `${API_BASE_URL}/api/auth/verify`,
  },
  TASKS: {
    BASE: `${API_BASE_URL}/api/tasks`,
    BY_ID: (id) => `${API_BASE_URL}/api/tasks/${id}`,
    COMPLETE: (id) => `${API_BASE_URL}/api/tasks/${id}/complete`,
  },
  USERS: {
    BASE: `${API_BASE_URL}/api/users`,
    PROFILE: (id) => `${API_BASE_URL}/api/users/profile/${id}`,
  },
  COMPANY: {
    BASE: `${API_BASE_URL}/api/company`,
    TEAM: (id) => `${API_BASE_URL}/api/company/${id}/team`,
  },
  AI: {
    ASK: `${API_BASE_URL}/api/ai/ask`,
    SMART_PLAN: `${API_BASE_URL}/api/ai/smart-plan`,
  }
};
