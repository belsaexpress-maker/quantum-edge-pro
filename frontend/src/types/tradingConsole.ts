export type TradePayload = {
  symbol: string;
  side: "BUY" | "SELL";
  price: number;
  quantity: number;
};

export type TradeResponse = {
  message?: string;
  error?: string;
  mode?: string;
  order?: {
    id: number;
    symbol: string;
    side: string;
    price: number;
    quantity: number;
    value: number;
    status: string;
  };
};