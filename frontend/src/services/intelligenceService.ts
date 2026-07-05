import { api } from "./api";

export async function getSmartMoney(symbol: string) {
  const response = await api.get(`/intelligence/smart-money/${symbol}`);
  return response.data;
}

export async function getPlaybook(symbol: string) {
  const response = await api.get(`/intelligence/playbook/${symbol}`);
  return response.data;
}