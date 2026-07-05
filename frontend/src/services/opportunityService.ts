import { api } from "./api";

export async function getOpportunities(limit = 100) {
  const response = await api.get(`/opportunities/?limit=${limit}`);
  return response.data;
}