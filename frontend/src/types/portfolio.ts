export type PortfolioAsset = {
  id: number;
  symbol: string;
  asset_type: string;
  quantity: number;
  buy_price: number;
};

export type PortfolioCreatePayload = {
  symbol: string;
  asset_type: string;
  quantity: number;
  buy_price: number;
};

export type PortfolioSummary = {
  user: string;
  asset_count: number;
  total_cost: number;
  currency: string;
};