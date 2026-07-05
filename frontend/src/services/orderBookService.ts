import { api } from "./api";

export async function getOrderBook(symbol: string, limit = 20) {
  const response = await api.get(`/orderbook/${symbol}?limit=${limit}`);
  return response.data;
}