// Thin fetch wrapper around the FastAPI backend.

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const TOKEN_KEY = "ekko-token";

export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (token) =>
  token ? localStorage.setItem(TOKEN_KEY, token) : localStorage.removeItem(TOKEN_KEY);

async function request(path, { method = "GET", body } = {}) {
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail ?? `${res.status} ${res.statusText}`);
  }
  return res.status === 204 ? null : res.json();
}

export const api = {
  health: () => request("/health"),

  signup: (email, password) => request("/auth/signup", { method: "POST", body: { email, password } }),
  login: (email, password) => request("/auth/login", { method: "POST", body: { email, password } }),
  me: () => request("/auth/me"),

  topics: () => request("/topics"),
  myTopics: () => request("/topics/me"),
  setMyTopics: (slugs) => request("/topics/me", { method: "PUT", body: { slugs } }),

  todayDigest: () => request("/digest/today"),
  interact: (digestItemId, action) =>
    request(`/digest/items/${digestItemId}/interactions`, { method: "POST", body: { action } }),

  tasks: () => request("/tasks"),
  createTask: (title) => request("/tasks", { method: "POST", body: { title } }),
  updateTask: (id, patch) => request(`/tasks/${id}`, { method: "PATCH", body: patch }),
  deleteTask: (id) => request(`/tasks/${id}`, { method: "DELETE" }),
};
