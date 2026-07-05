export type OrderBookRow = {
  price: number;
  amount: number;
  total: number;
};

export type TradeRow = {
  price: number;
  amount: number;
  side: "buy" | "sell";
  time: string;
};