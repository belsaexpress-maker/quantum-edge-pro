import { api } from "./api";

const TOKEN_KEY = "quantum_token";
const USER_KEY = "quantum_user";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getUser() {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;

  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function saveAuth(token: string, user: any) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export async function loginWithGoogle(credential: string) {
  const response = await api.post("/auth/google", { credential });
  saveAuth(response.data.access_token, response.data.user);
  return response.data;
}

export async function demoAdminLogin() {
  const response = await api.post("/auth/demo-admin");
  saveAuth(response.data.access_token, response.data.user);
  return response.data;
}