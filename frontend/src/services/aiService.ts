import { api } from "./api";
import type { AIConfidenceResponse, AIConfidenceResult } from "../types/ai";

export async function getAIConfidenceAll(): Promise<AIConfidenceResponse> {
  const response = await api.get("/ai/confidence");
  return response.data;
}

export async function getAIConfidenceSymbol(
  symbol: string
): Promise<AIConfidenceResult> {
  const response = await api.get(`/ai/confidence/${symbol}`);
  return response.data;
}