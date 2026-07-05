import { api } from "./api";
import type { ScannerRefreshResponse, ScannerResponse } from "../types/scanner";

export async function scanMarket(limit: number): Promise<ScannerResponse> {
  const response = await api.get("/scanner/market", {
    params: { limit },
  });

  return response.data;
}

export async function refreshScanner(): Promise<ScannerRefreshResponse> {
  const response = await api.get("/scanner/refresh");
  return response.data;
}