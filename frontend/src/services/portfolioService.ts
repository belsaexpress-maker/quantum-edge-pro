import { api } from "./api";
import type {
  PortfolioAsset,
  PortfolioCreatePayload,
  PortfolioSummary,
} from "../types/portfolio";

export async function getPortfolio(): Promise<PortfolioAsset[]> {
  const response = await api.get("/portfolio/");
  return response.data;
}

export async function addPortfolioAsset(payload: PortfolioCreatePayload) {
  const response = await api.post("/portfolio/", payload);
  return response.data;
}

export async function getPortfolioSummary(): Promise<PortfolioSummary> {
  const response = await api.get("/portfolio/summary");
  return response.data;
}