export type MarketItem = {
  symbol: string;
  name: string;
  asset_type: string;
  exchange?: string;
  price: number;
  change_24h: number;
  volume_24h?: number;
  signal: string;
};

export type MarketOverview = {
  crypto: MarketItem[];
  stocks: MarketItem[];
  indices: MarketItem[];
  commodities: MarketItem[];
  forex: MarketItem[];
};