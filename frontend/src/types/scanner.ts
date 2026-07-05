export type ScannerItem = {
  symbol: string;
  price: number;
  change_24h: number;
  volume_24h: number;
  confidence: number;
  direction: string;
  signal: string;
  risk: string;
  entry_zone: {
    low: number;
    high: number;
  };
  take_profit: {
    tp1: number;
    tp2: number;
    tp3: number;
  };
  stop_loss: number;
};

export type ScannerResponse = {
  last_updated: string | null;
  total_scanned: number;
  count: number;
  items: ScannerItem[];
};

export type ScannerRefreshResponse = {
  message: string;
  last_updated: string;
  total_scanned: number;
};