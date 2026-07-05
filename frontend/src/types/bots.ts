export type BotTemplate = {
  id: string;
  name: string;
  strategy: string;
  risk: string;
  description: string;
  default_tp_percent: number;
  default_sl_percent: number;
  default_daily_trades: number;
  min_interval_seconds?: number;
  grid_levels?: number;
  grid_range_percent?: number;
  dca_step_percent?: number;
  max_dca_orders?: number;
};

export type BotOrder = {
  side: string;
  symbol: string;
  price: number;
  quantity: number;
  value: number;
  pnl: number | null;
  mode: string;
  created_at: string;
  reason: string;
};

export type RunningBot = {
  id: number;
  bot_id: string;
  name: string;
  strategy: string;
  symbol: string;
  amount_usd: number;
  daily_target_usd: number;
  daily_loss_limit_usd: number;
  max_daily_trades: number;
  tp_percent: number;
  sl_percent: number;
  min_interval_seconds: number;
  next_allowed_trade_at?: string;
  dca_step_percent?: number;
  max_dca_orders?: number;
  dca_count?: number;
  grid_levels?: number[];
  grid_completed?: number;
  entry_price: number;
  current_price: number;
  quantity: number;
  status: string;
  position_status: string;
  risk: string;
  unrealized_pnl: number;
  realized_pnl: number;
  total_pnl: number;
  trade_count: number;
  cycle_count: number;
  price_change_percent?: number;
  auto_select: boolean;
  auto_reentry: boolean;
  trading_mode?: string;
  last_action: string;
  orders: BotOrder[];
  created_at: string;
  updated_at: string;
};

export type BotsResponse = {
  mode: string;
  templates: BotTemplate[];
  running: RunningBot[];
};

export type StartBotPayload = {
  bot_id: string;
  symbol: string;
  amount_usd: number;
  daily_target_usd: number;
  daily_loss_limit_usd: number;
  auto_select: boolean;
  auto_reentry: boolean;
  max_daily_trades: number;
  tp_percent: number;
  sl_percent: number;
};