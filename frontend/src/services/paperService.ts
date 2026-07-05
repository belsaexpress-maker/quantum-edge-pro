import { api } from "./api";
import type { PaperAccount, PaperOrderPayload } from "../types/paper";

export async function getPaperAccount(): Promise<PaperAccount> {
  const response = await api.get("/paper/account");
  return response.data;
}

export async function createPaperOrder(payload: PaperOrderPayload) {
  const response = await api.post("/paper/order", payload);
  return response.data;
}

export async function resetPaperAccount(): Promise<PaperAccount> {
  const response = await api.post("/paper/reset");
  return response.data;
}