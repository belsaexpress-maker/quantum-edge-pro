import { api } from "./api";

export async function getMyMembership() {
  const response = await api.get("/membership/me");
  return response.data;
}

export async function getUsers() {
  const response = await api.get("/membership/users");
  return response.data;
}

export async function grantRole(payload: { email: string; role: string }) {
  const response = await api.post("/membership/grant-role", payload);
  return response.data;
}