import { api } from "./api";
import type { BotsResponse, StartBotPayload } from "../types/bots";

export async function getBots(): Promise<BotsResponse> {
  const response = await api.get("/bots/");
  return response.data;
}

export async function startBot(payload: StartBotPayload) {
  const response = await api.post("/bots/start", payload);
  return response.data;
}

export async function stopBot(botInstanceId: number) {
  const response = await api.post(`/bots/stop/${botInstanceId}`);
  return response.data;
}

export async function runBotCycle() {
  const response = await api.post("/bots/cycle");
  return response.data;
}