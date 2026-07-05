import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  Bot,
  Clock3,
  Play,
  RefreshCcw,
  Square,
} from "lucide-react";

import { getBots, runBotCycle, startBot, stopBot } from "../services/botService";
import type { BotOrder, BotTemplate, RunningBot } from "../types/bots";

export default function BotsPage() {
  const [mode, setMode] = useState("PAPER");
  const [templates, setTemplates] = useState<BotTemplate[]>([]);
  const [running, setRunning] = useState<RunningBot[]>([]);
  const [selectedBot, setSelectedBot] = useState("quantum_ai");

  const [symbol, setSymbol] = useState("AUTO");
  const [amount, setAmount] = useState("100");
  const [target, setTarget] = useState("10");
  const [lossLimit, setLossLimit] = useState("5");
  const [maxTrades, setMaxTrades] = useState("100");
  const [tpPercent, setTpPercent] = useState("0.25");
  const [slPercent, setSlPercent] = useState("0.7");
  const [autoSelect, setAutoSelect] = useState(true);
  const [autoReentry, setAutoReentry] = useState(true);
  const [message, setMessage] = useState("");
  const [seconds, setSeconds] = useState(10);

  useEffect(() => {
    loadBots();

    const dataInterval = setInterval(loadBots, 3000);
    const timer = setInterval(() => {
      setSeconds((prev) => (prev <= 1 ? 10 : prev - 1));
    }, 1000);

    return () => {
      clearInterval(dataInterval);
      clearInterval(timer);
    };
  }, []);

  const selectedTemplate = useMemo(
    () => templates.find((item) => item.id === selectedBot),
    [templates, selectedBot]
  );

  useEffect(() => {
    if (!selectedTemplate) return;

    setTpPercent(String(selectedTemplate.default_tp_percent));
    setSlPercent(String(selectedTemplate.default_sl_percent));
    setMaxTrades(String(selectedTemplate.default_daily_trades));
  }, [selectedTemplate]);

  async function loadBots() {
    const data = await getBots();
    setMode(data.mode || "PAPER");
    setTemplates(data.templates);
    setRunning(data.running);
  }

  async function handleStart(botId?: string) {
    const finalBotId = botId || selectedBot;
    setMessage("");

    const result = await startBot({
      bot_id: finalBotId,
      symbol,
      amount_usd: Number(amount),
      daily_target_usd: Number(target),
      daily_loss_limit_usd: Number(lossLimit),
      auto_select: autoSelect,
      auto_reentry: autoReentry,
      max_daily_trades: Number(maxTrades),
      tp_percent: Number(tpPercent),
      sl_percent: Number(slPercent),
    });

    if (result.error) {
      setMessage(result.error);
      return;
    }

    setMessage(`${result.bot?.name || "Bot"} başlatıldı.`);
    await loadBots();
  }

  async function handleStop(id: number) {
    const result = await stopBot(id);

    if (result.error) {
      setMessage(result.error);
      return;
    }

    setMessage("Bot durduruldu.");
    await loadBots();
  }

  async function handleCycle() {
    const result = await runBotCycle();
    setSeconds(10);
    setMessage(result.message || "Bot cycle completed");
    await loadBots();
  }

  const runningCount = running.filter((b) => b.status === "RUNNING").length;
  const openPositionCount = running.filter((b) => b.position_status === "OPEN").length;
  const totalOpenPnl = running.reduce((t, b) => t + (b.unrealized_pnl || 0), 0);
  const totalPnl = running.reduce((t, b) => t + (b.total_pnl || 0), 0);
  const totalTrades = running.reduce((t, b) => t + (b.trade_count || 0), 0);

  const allOrders: BotOrder[] = running
    .flatMap((bot) => bot.orders || [])
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 100);

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 rounded-3xl border border-white/10 bg-[#070b1f] p-6 xl:flex-row xl:items-center">
        <div>
          <h2 className="text-2xl font-bold">Quantum AI Bots Pro</h2>
          <p className="mt-1 text-slate-400">
            Grid, DCA, scalping, momentum ve AI botları için TESTNET/PAPER işlem merkezi.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Badge label={`Mode: ${mode}`} />
          <Badge label={`Next Scan: ${seconds}s`} />

          <button
            onClick={handleCycle}
            className="flex items-center justify-center gap-2 rounded-xl bg-cyan-500 px-5 py-3 font-bold text-black hover:bg-cyan-400"
          >
            <RefreshCcw size={18} />
            Run Cycle Now
          </button>
        </div>
      </div>

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-5">
        <Metric label="Running Bots" value={runningCount} />
        <Metric label="Open Positions" value={openPositionCount} />
        <Metric label="Total Trades" value={totalTrades} />
        <Metric label="Open PnL" value={`$${totalOpenPnl.toFixed(2)}`} danger={totalOpenPnl < 0} />
        <Metric label="Total PnL" value={`$${totalPnl.toFixed(2)}`} danger={totalPnl < 0} />
      </section>

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-4">
        {templates.map((template) => {
          const activeCount = running.filter(
            (bot) => bot.bot_id === template.id && bot.status === "RUNNING"
          ).length;

          return (
            <div
              key={template.id}
              onClick={() => setSelectedBot(template.id)}
              className={`cursor-pointer rounded-3xl border p-5 transition ${
                selectedBot === template.id
                  ? "border-cyan-400 bg-cyan-400/10"
                  : "border-white/10 bg-[#070b1f] hover:bg-white/5"
              }`}
            >
              <div className="mb-4 flex items-center justify-between">
                <div className="rounded-2xl bg-white/10 p-3 text-cyan-300">
                  <Bot size={22} />
                </div>

                <span className="rounded-full bg-white/10 px-3 py-1 text-xs text-slate-300">
                  {template.strategy}
                </span>
              </div>

              <h3 className="text-xl font-bold">{template.name}</h3>
              <p className="mt-2 min-h-[42px] text-sm text-slate-400">
                {template.description}
              </p>

              <div className="mt-4 grid grid-cols-2 gap-2">
                <Mini label="Risk" value={template.risk} />
                <Mini label="Running" value={activeCount} />
                <Mini label="TP" value={`${template.default_tp_percent}%`} />
                <Mini label="Trades" value={template.default_daily_trades} />
                {template.grid_levels && <Mini label="Grid" value={template.grid_levels} />}
                {template.max_dca_orders && <Mini label="DCA" value={template.max_dca_orders} />}
              </div>

              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedBot(template.id);
                  void handleStart(template.id);
                }}
                className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-green-500 py-3 font-bold text-black hover:bg-green-400"
              >
                <Play size={18} />
                Start
              </button>
            </div>
          );
        })}
      </section>

      <section className="grid grid-cols-1 gap-6 2xl:grid-cols-[430px_1fr]">
        <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
          <h3 className="mb-4 text-xl font-bold">Bot Settings</h3>

          <div className="space-y-3">
            <select
              className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3"
              value={selectedBot}
              onChange={(e) => setSelectedBot(e.target.value)}
            >
              {templates.map((bot) => (
                <option key={bot.id} value={bot.id}>
                  {bot.name} — {bot.strategy}
                </option>
              ))}
            </select>

            <label className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm">
              <span>Auto select best coin</span>
              <input
                type="checkbox"
                checked={autoSelect}
                onChange={(e) => {
                  setAutoSelect(e.target.checked);
                  if (e.target.checked) setSymbol("AUTO");
                }}
              />
            </label>

            <input
              className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 uppercase"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              placeholder="AUTO veya BTCUSDT"
              disabled={autoSelect}
            />

            <label className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm">
              <span>Auto re-entry after TP/SL</span>
              <input
                type="checkbox"
                checked={autoReentry}
                onChange={(e) => setAutoReentry(e.target.checked)}
              />
            </label>

            <Input label="Order Amount USD" value={amount} onChange={setAmount} />
            <Input label="Daily Target USD" value={target} onChange={setTarget} />
            <Input label="Daily Loss Limit USD" value={lossLimit} onChange={setLossLimit} />
            <Input label="Max Daily Trades" value={maxTrades} onChange={setMaxTrades} />
            <Input label="Take Profit %" value={tpPercent} onChange={setTpPercent} />
            <Input label="Stop Loss %" value={slPercent} onChange={setSlPercent} />

            <button
              onClick={() => handleStart()}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-green-500 py-3 font-bold text-black hover:bg-green-400"
            >
              <Play size={18} />
              Start Selected Bot
            </button>

            {message && (
              <p className="rounded-xl border border-white/10 bg-white/5 p-3 text-sm text-slate-300">
                {message}
              </p>
            )}
          </div>
        </div>

        <div className="space-y-6">
          <LivePositions bots={running} mode={mode} onStop={handleStop} />
          <OrderHistory orders={allOrders} />
          <LiveLog orders={allOrders.slice(0, 25)} />
        </div>
      </section>
    </div>
  );
}

function LivePositions({
  bots,
  mode,
  onStop,
}: {
  bots: RunningBot[];
  mode: string;
  onStop: (id: number) => void;
}) {
  return (
    <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
      <h3 className="mb-4 flex items-center gap-2 text-xl font-bold">
        <Activity size={20} />
        Live Bot Positions
      </h3>

      <div className="space-y-3">
        {bots.map((bot) => {
          const nextTp = bot.entry_price * (1 + bot.tp_percent / 100);
          const nextSl = bot.entry_price * (1 - bot.sl_percent / 100);
          const targetProgress = progress(bot.total_pnl, bot.daily_target_usd);
          const tradeProgress = progress(bot.trade_count, bot.max_daily_trades);
          const intervalLeft = secondsLeft(bot.next_allowed_trade_at);

          return (
            <div key={bot.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="flex flex-col justify-between gap-4 xl:flex-row xl:items-center">
                <div>
                  <p className="font-bold">
                    #{bot.id} {bot.name}
                  </p>
                  <p className="text-sm text-slate-400">
                    {bot.symbol} • {bot.strategy} • {bot.trading_mode || mode}
                  </p>
                  <p className="text-xs text-slate-500">
                    Entry: ${formatNumber(bot.entry_price)} • Current: ${formatNumber(bot.current_price)}
                  </p>
                </div>

                <div className="flex flex-wrap items-center gap-3">
                  <Badge label={bot.status} />
                  <Badge label={bot.position_status} />
                  <button
                    onClick={() => onStop(bot.id)}
                    className="flex items-center gap-2 rounded-xl bg-red-500/20 px-4 py-2 text-sm font-bold text-red-300 hover:bg-red-500/30"
                  >
                    <Square size={15} />
                    Stop
                  </button>
                </div>
              </div>

              <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-4">
                <Small label="Qty" value={bot.quantity} />
                <Small label="Price %" value={`${bot.price_change_percent ?? 0}%`} danger={(bot.price_change_percent ?? 0) < 0} />
                <Small label="Open PnL" value={`$${bot.unrealized_pnl}`} danger={bot.unrealized_pnl < 0} />
                <Small label="Total PnL" value={`$${bot.total_pnl}`} danger={bot.total_pnl < 0} />
                <Small label="Next TP" value={`$${formatNumber(nextTp)}`} />
                <Small label="Next SL" value={`$${formatNumber(nextSl)}`} danger />
                <Small label="Next Trade" value={`${intervalLeft}s`} />
                <Small label="Last Action" value={bot.last_action} />
                <Small label="DCA" value={`${bot.dca_count ?? 0}/${bot.max_dca_orders ?? 0}`} />
                <Small label="Grid" value={`${bot.grid_completed ?? 0}/${bot.grid_levels?.length ?? 0}`} />
              </div>

              {bot.strategy === "GRID" && bot.grid_levels && bot.grid_levels.length > 0 && (
                <div className="mt-4 rounded-xl border border-white/10 bg-[#070b1f] p-3">
                  <p className="mb-2 text-xs text-slate-400">Grid Levels</p>
                  <div className="grid grid-cols-3 gap-2 md:grid-cols-6">
                    {bot.grid_levels.map((level, index) => (
                      <div
                        key={`${bot.id}-grid-${index}`}
                        className={`rounded-lg px-2 py-1 text-center text-xs ${
                          bot.current_price >= level
                            ? "bg-green-500/20 text-green-300"
                            : "bg-white/5 text-slate-400"
                        }`}
                      >
                        {formatNumber(level)}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
                <Progress label="Daily Target" value={`${bot.total_pnl} / ${bot.daily_target_usd}$`} percent={targetProgress} />
                <Progress label="Trades" value={`${bot.trade_count} / ${bot.max_daily_trades}`} percent={tradeProgress} />
              </div>
            </div>
          );
        })}

        {bots.length === 0 && (
          <p className="rounded-2xl border border-white/10 bg-white/5 p-5 text-center text-slate-400">
            Henüz çalışan bot yok.
          </p>
        )}
      </div>
    </div>
  );
}

function OrderHistory({ orders }: { orders: BotOrder[] }) {
  return (
    <div className="max-h-[520px] overflow-auto rounded-3xl border border-white/10 bg-[#070b1f]">
      <div className="sticky top-0 z-10 bg-[#070b1f] p-5">
        <h3 className="text-xl font-bold">Bot Order History</h3>
      </div>

      <table className="w-full text-left text-sm">
        <thead className="bg-white/5 text-slate-300">
          <tr>
            <th className="p-4">Time</th>
            <th className="p-4">Side</th>
            <th className="p-4">Symbol</th>
            <th className="p-4 text-right">Price</th>
            <th className="p-4 text-right">Qty</th>
            <th className="p-4 text-right">Value</th>
            <th className="p-4 text-right">PnL</th>
            <th className="p-4">Mode</th>
            <th className="p-4">Reason</th>
          </tr>
        </thead>

        <tbody>
          {orders.map((order, index) => (
            <tr key={`${order.created_at}-${index}`} className="border-t border-white/10">
              <td className="p-4 text-slate-400">{formatDate(order.created_at)}</td>
              <td className={`p-4 font-bold ${order.side === "BUY" ? "text-green-400" : "text-red-400"}`}>{order.side}</td>
              <td className="p-4 font-bold">{order.symbol}</td>
              <td className="p-4 text-right">${formatNumber(order.price)}</td>
              <td className="p-4 text-right">{order.quantity}</td>
              <td className="p-4 text-right">${order.value}</td>
              <td className={`p-4 text-right ${Number(order.pnl || 0) >= 0 ? "text-green-400" : "text-red-400"}`}>
                {order.pnl === null || order.pnl === undefined ? "-" : `$${order.pnl}`}
              </td>
              <td className="p-4">{order.mode}</td>
              <td className="p-4 text-slate-300">{order.reason}</td>
            </tr>
          ))}

          {orders.length === 0 && (
            <tr>
              <td colSpan={9} className="p-8 text-center text-slate-400">
                Henüz bot emri yok.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

function LiveLog({ orders }: { orders: BotOrder[] }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
      <h3 className="mb-4 flex items-center gap-2 text-xl font-bold">
        <Clock3 size={20} />
        Live Bot Log
      </h3>

      <div className="space-y-2">
        {orders.map((order, index) => (
          <div key={`${order.created_at}-log-${index}`} className="flex flex-wrap justify-between gap-3 rounded-xl border border-white/10 bg-white/5 p-3 text-sm">
            <span className="text-slate-400">{formatDate(order.created_at)}</span>
            <span className={order.side === "BUY" ? "text-green-400" : "text-red-400"}>
              {order.side} {order.symbol}
            </span>
            <span className="text-slate-300">{order.reason}</span>
            <span className={Number(order.pnl || 0) >= 0 ? "text-green-400" : "text-red-400"}>
              {order.pnl === null || order.pnl === undefined ? "-" : `$${order.pnl}`}
            </span>
          </div>
        ))}

        {orders.length === 0 && (
          <p className="rounded-xl border border-white/10 bg-white/5 p-4 text-center text-slate-400">
            Henüz canlı log yok.
          </p>
        )}
      </div>
    </div>
  );
}

function Metric({ label, value, danger = false }: { label: string; value: string | number; danger?: boolean }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-5">
      <p className="text-sm text-slate-400">{label}</p>
      <p className={`mt-2 text-2xl font-bold ${danger ? "text-red-400" : "text-white"}`}>{value}</p>
    </div>
  );
}

function Mini({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-xl border border-white/10 bg-[#050816] p-3">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-1 font-bold text-slate-200">{value}</p>
    </div>
  );
}

function Small({ label, value, danger = false }: { label: string; value: string | number; danger?: boolean }) {
  return (
    <div className="rounded-xl border border-white/10 bg-[#070b1f] p-3">
      <p className="text-xs text-slate-400">{label}</p>
      <p className={`mt-1 font-bold ${danger ? "text-red-400" : "text-green-400"}`}>{value}</p>
    </div>
  );
}

function Badge({ label }: { label: string }) {
  return (
    <span className={`rounded-full px-3 py-1 text-xs ${
      label.includes("RUNNING") || label.includes("OPEN") || label.includes("TESTNET")
        ? "bg-green-500/10 text-green-300"
        : label.includes("PAUSED")
        ? "bg-yellow-500/10 text-yellow-300"
        : "bg-slate-500/10 text-slate-300"
    }`}>
      {label}
    </span>
  );
}

function Input({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs text-slate-400">{label}</span>
      <input
        className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        type="number"
      />
    </label>
  );
}

function Progress({ label, value, percent }: { label: string; value: string; percent: number }) {
  return (
    <div className="rounded-xl border border-white/10 bg-[#070b1f] p-3">
      <div className="mb-2 flex justify-between text-xs">
        <span className="text-slate-400">{label}</span>
        <span className="text-slate-300">{value}</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-white/10">
        <div className="h-full rounded-full bg-cyan-400" style={{ width: `${percent}%` }} />
      </div>
    </div>
  );
}

function progress(value: number, max: number) {
  if (!max || max <= 0) return 0;
  return Math.max(0, Math.min(100, (value / max) * 100));
}

function secondsLeft(value?: string) {
  if (!value) return 0;
  const target = new Date(value).getTime();
  if (Number.isNaN(target)) return 0;
  const diff = Math.ceil((target - Date.now()) / 1000);
  return Math.max(0, diff);
}

function formatDate(value: string) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "-";

  return date.toLocaleString("tr-TR", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function formatNumber(value: number) {
  if (!value) return "0";
  if (Math.abs(value) < 0.01) return value.toFixed(8);
  if (Math.abs(value) < 1) return value.toFixed(6);
  return value.toLocaleString();
}