import { api } from "./api";

export async function getQuantumProBots() {
  const response = await api.get("/quantum-pro-bots/");
  return response.data;
}

export async function startQuantumProBot(payload: {
  bot_id: string;
  balance: number;
  target_percent: number;
  max_loss_percent: number;
  compound: boolean;
}) {
  const response = await api.post("/quantum-pro-bots/start", payload);
  return response.data;
}

export async function stopQuantumProBot(id: number) {
  const response = await api.post(`/quantum-pro-bots/stop/${id}`);
  return response.data;
}

export async function runQuantumProCycle() {
  const response = await api.post("/quantum-pro-bots/cycle");
  return response.data;
}