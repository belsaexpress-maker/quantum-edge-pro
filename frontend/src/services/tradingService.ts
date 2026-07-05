import { api } from "./api";
import type { TradePayload, TradeResponse } from "../types/tradingConsole";

export async function executeTrade(
  payload: TradePayload
): Promise<TradeResponse> {
  const response = await api.post("/trading/execute", payload);
  return response.data;
}