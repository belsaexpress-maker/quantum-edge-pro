import { api } from "./api";
import type { PlaybookResult } from "../types/playbook";

export async function getPlaybook(
  symbol: string,
  timeframe: string
): Promise<PlaybookResult> {
  const response = await api.get(`/playbook/${symbol}`, {
    params: { timeframe },
  });

  return response.data;
}