export type Candle = {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

export type SmartMoneyZone = {
  type: string;
  low: number;
  high: number;
  time: number;
};

export type LiquiditySweep = {
  type: string;
  level: number;
  time: number;
} | null;

export type SmartMoney = {
  score: number;
  order_blocks: SmartMoneyZone[];
  fvg: SmartMoneyZone[];
  structure: {
    bos: string | null;
    choch: string | null;
    structure: string;
    previous_high?: number;
    previous_low?: number;
  };
  liquidity_sweep: LiquiditySweep;
  reasons: string[];
};

export type PlaybookResult = {
  symbol: string;
  timeframe: string;
  current_price: number;
  direction: string;
  signal: string;
  confidence: number;
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
  support_resistance: {
    support: number;
    resistance: number;
  };
  pivot_levels: Record<string, number>;
  camarilla_levels: Record<string, number>;
  fibonacci: Record<string, number>;
  indicators: {
    rsi: number | null;
    ema20: number | null;
    ema50: number | null;
    ema100: number | null;
    ema200: number | null;
    macd: {
      macd: number | null;
      signal: number | null;
      histogram: number | null;
    };
    atr: number | null;
  };
  smart_money: SmartMoney;
  wolfe_wave: {
    detected: boolean;
    type: string;
    target_line: number;
  };
  chart: Candle[];
  reasons: string[];
};