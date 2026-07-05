export type PaperPosition = {
  symbol: string;
  quantity: number;
  entry_price: number;
  current_price: number;
  unrealized_pnl: number;
};

export type PaperOrder = {
  id: number;
  symbol: string;
  side: string;
  price: number;
  quantity: number;
  value: number;
  created_at: string;
  status: string;
};

export type PaperAccount = {
  balance: number;
  position_count: number;
  total_position_value: number;
  unrealized_pnl: number;
  equity: number;
  positions: PaperPosition[];
  orders: PaperOrder[];
};

export type PaperOrderPayload = {
  symbol: string;
  side: "BUY" | "SELL";
  price: number;
  quantity: number;
};