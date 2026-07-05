import { api } from "./api";

export async function getMarketOverview() {
  const response = await api.get("/market/overview");
  return response.data;
}

export async function getLatestNews() {
  const response = await api.get("/news/latest");
  return response.data;
}