import { useEffect, useState } from "react";
import { Play, RefreshCcw, Shield, Square, TrendingUp } from "lucide-react";

import {
  getQuantumProBots,
  runQuantumProCycle,
  startQuantumProBot,
  stopQuantumProBot,
} from "../services/quantumProBotService";

export default function QuantumProBotsPage() {
  const [mode, setMode] = useState("PAPER");
  const [templates, setTemplates] = useState<any[]>([]);
  const [running, setRunning] = useState<any[]>([]);
  const [balance, setBalance] = useState("30");
  const [target, setTarget] = useState("15");
  const [loss, setLoss] = useState("3");
  const [compound, setCompound] = useState(true);
  const [message, setMessage] = useState("");

  useEffect(() => {
    load();
    const interval = setInterval(load, 3000);
    return () => clearInterval(interval);
  }, []);

  async function load() {
    const data = await getQuantumProBots();
    setMode(data.mode);
    setTemplates(data.templates);
    setRunning(data.running);
  }

  async function start(id: string) {
    const result = await startQuantumProBot({
      bot_id: id,
      balance: Number(balance),
      target_percent: Number(target),
      max_loss_percent: Number(loss),
      compound,
    });

    if (result.error) setMessage(result.error);
    else setMessage(`${result.bot.name} başlatıldı.`);
    await load();
  }

  async function stop(id: number) {
    await stopQuantumProBot(id);
    await load();
  }

  async function cycle() {
    const result = await runQuantumProCycle();
    setMessage(result.message);
    await load();
  }

  const totalPnl = running.reduce((t, b) => t + (b.total_pnl || 0), 0);
  const totalEquity = running.reduce((t, b) => t + (b.current_equity || 0), 0);
  const avgOpportunity =
    running.length > 0
      ? running.reduce((t, b) => t + (b.opportunity_score || 0), 0) /
        running.length
      : 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 rounded-3xl border border-white/10 bg-[#070b1f] p-6 xl:flex-row xl:items-center">
        <div>
          <h2 className="text-2xl font-bold">QuantumEdge Pro Bots</h2>
          <p className="mt-1 text-slate-400">
            Opportunity Engine + Smart Money + Compound Mode + Trend Hold destekli Pro bot merkezi.
          </p>
        </div>

        <div className="flex gap-3">
          <span className="rounded-xl bg-yellow-500/20 px-4 py-3 text-sm font-bold text-yellow-300">
            Mode: {mode}
          </span>

          <button
            onClick={cycle}
            className="flex items-center gap-2 rounded-xl bg-cyan-500 px-5 py-3 font-bold text-black"
          >
            <RefreshCcw size={18} />
            Run Cycle
          </button>
        </div>
      </div>

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-5">
        <Metric label="Running" value={running.filter((b) => b.status === "RUNNING").length} />
        <Metric label="Total Equity" value={`$${totalEquity.toFixed(2)}`} />
        <Metric label="Total PnL" value={`$${totalPnl.toFixed(2)}`} danger={totalPnl < 0} />
        <Metric label="Avg Opportunity" value={`${avgOpportunity.toFixed(0)}/100`} />
        <Metric label="Target" value={`${target}%`} />
      </section>

      <section className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
        <h3 className="mb-4 text-xl font-bold">Quantum Compound Settings</h3>

        <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
          <Input label="Start Balance" value={balance} onChange={setBalance} />
          <Input label="Target %" value={target} onChange={setTarget} />
          <Input label="Max Loss %" value={loss} onChange={setLoss} />

          <label className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm">
            <span>Compound</span>
            <input
              type="checkbox"
              checked={compound}
              onChange={(e) => setCompound(e.target.checked)}
            />
          </label>
        </div>

        {message && (
          <p className="mt-4 rounded-xl bg-white/5 p-3 text-sm text-slate-300">
            {message}
          </p>
        )}
      </section>

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-4">
        {templates.map((bot) => (
          <div key={bot.id} className="rounded-3xl border border-white/10 bg-[#070b1f] p-5">
            <div className="mb-4 flex items-center justify-between">
              <Shield className="text-cyan-300" />
              <span className="rounded-full bg-white/10 px-3 py-1 text-xs">
                {bot.market}
              </span>
            </div>

            <h3 className="text-lg font-bold">{bot.name}</h3>
            <p className="mt-2 text-sm text-slate-400">Risk: {bot.risk}</p>

            <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
              <Mini label="AI Min" value={bot.min_score} />
              <Mini label="TP" value={`${bot.tp}%`} />
              <Mini label="SL" value={`${bot.sl}%`} />
              <Mini label="Trades" value={bot.max_trades} />
              <Mini label="Trend Hold" value={`${bot.trend_hold_score}+`} />
            </div>

            <button
              onClick={() => start(bot.id)}
              className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-green-500 py-3 font-bold text-black"
            >
              <Play size={18} />
              Start
            </button>
          </div>
        ))}
      </section>

      <section className="space-y-4">
        {running.map((bot) => {
          const targetProgress = progress(
            bot.current_equity - bot.cycle_start_balance,
            bot.cycle_target_balance - bot.cycle_start_balance
          );

          const lossProgress = progress(
            Math.abs(Math.min(bot.total_pnl || 0, 0)),
            bot.cycle_start_balance * (bot.max_loss_percent / 100)
          );

          const trailingStop =
            bot.highest_price * (1 - bot.trailing_stop_percent / 100);

          return (
            <div key={bot.id} className="rounded-3xl border border-white/10 bg-[#070b1f] p-5">
              <div className="flex flex-col justify-between gap-4 xl:flex-row xl:items-center">
                <div>
                  <h3 className="text-xl font-bold">
                    #{bot.id} {bot.name}
                  </h3>

                  <p className="text-sm text-slate-400">
                    {bot.symbol} • {bot.market} • Cycle {bot.cycle}
                  </p>

                  <p className="text-xs text-slate-500">
                    Entry ${formatNumber(bot.entry_price)} • Current ${formatNumber(bot.current_price)} • Highest ${formatNumber(bot.highest_price)}
                  </p>
                </div>

                <div className="flex flex-wrap gap-2">
                  <Badge label={bot.status} />
                  <Badge label={bot.position_status} />
                  <Badge label={bot.trend_hold_mode ? "TREND HOLD ON" : "MICRO TP"} />

                  <button
                    onClick={() => stop(bot.id)}
                    className="flex items-center gap-2 rounded-xl bg-red-500/20 px-4 py-2 text-red-300"
                  >
                    <Square size={15} />
                    Stop
                  </button>
                </div>
              </div>

              <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-5">
                <Mini label="AI Score" value={`${bot.ai_score || 0}/100`} />
                <Mini label="SMC Score" value={`${bot.smart_money_score || 0}/100`} />
                <Mini label="Opportunity" value={`${bot.opportunity_score || 0}/100`} />
                <Mini label="Exit Mode" value={bot.exit_mode} />
                <Mini label="Last Action" value={bot.last_action} />

                <Mini label="Portfolio" value={`$${bot.portfolio_balance}`} />
                <Mini label="Equity" value={`$${bot.current_equity}`} />
                <Mini label="Target Balance" value={`$${bot.cycle_target_balance}`} />
                <Mini label="Daily Profit" value={`${bot.daily_profit_percent}%`} />
                <Mini label="Max Loss" value={`${bot.max_loss_percent}%`} />

                <Mini label="Trade Amount" value={`$${bot.trade_amount}`} />
                <Mini label="Open PnL" value={`$${bot.unrealized_pnl}`} />
                <Mini label="Total PnL" value={`$${bot.total_pnl}`} />
                <Mini label="Trades" value={`${bot.trade_count}/${bot.max_trades}`} />
                <Mini label="Loss Streak" value={bot.consecutive_losses} />

                <Mini label="Trailing Stop" value={`$${formatNumber(trailingStop)}`} />
                <Mini label="TP" value={`${bot.tp_percent}%`} />
                <Mini label="SL" value={`${bot.sl_percent}%`} />
              </div>

              <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
                <Progress
                  label="Target Progress"
                  value={`${bot.daily_profit_percent}% / ${bot.target_percent}%`}
                  percent={targetProgress}
                />
                <Progress
                  label="Loss Risk"
                  value={`${lossProgress.toFixed(1)}% used`}
                  percent={lossProgress}
                  danger
                />
              </div>

              <div className="mt-4 rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="mb-2 flex items-center gap-2 font-bold">
                  <TrendingUp size={18} />
                  Opportunity + Trend Hold
                </div>

                <p className={bot.trend_hold_mode ? "text-green-300" : "text-slate-400"}>
                  {bot.trend_hold_mode
                    ? "Aktif — küçük TP yerine satış sinyali / trailing stop bekleniyor."
                    : "Kapalı — micro TP modu aktif."}
                </p>

                <p className="mt-2 text-sm text-slate-400">
                  {bot.trend_hold_reason}
                </p>
              </div>

              <div className="mt-4 rounded-xl border border-white/10 bg-white/5 p-4">
                <p className="mb-2 font-bold">Trade Reasons</p>

                {bot.reasons?.map((r: string, i: number) => (
                  <p key={i} className="text-sm text-slate-300">
                    ✓ {r}
                  </p>
                ))}
              </div>

              <div className="mt-4 max-h-72 overflow-auto rounded-xl border border-white/10">
                <table className="w-full text-sm">
                  <thead className="bg-white/5 text-slate-300">
                    <tr>
                      <th className="p-3 text-left">Time</th>
                      <th className="p-3 text-left">Side</th>
                      <th className="p-3 text-left">Symbol</th>
                      <th className="p-3 text-right">Value</th>
                      <th className="p-3 text-right">PnL</th>
                      <th className="p-3 text-left">AI</th>
                      <th className="p-3 text-left">SMC</th>
                      <th className="p-3 text-left">Opp</th>
                      <th className="p-3 text-left">Trend</th>
                      <th className="p-3 text-left">Reason</th>
                    </tr>
                  </thead>

                  <tbody>
                    {bot.orders?.map((o: any, i: number) => (
                      <tr key={i} className="border-t border-white/10">
                        <td className="p-3">{formatDate(o.created_at)}</td>
                        <td className={o.side === "BUY" ? "p-3 text-green-400" : "p-3 text-red-400"}>
                          {o.side}
                        </td>
                        <td className="p-3">{o.symbol}</td>
                        <td className="p-3 text-right">${o.value}</td>
                        <td className="p-3 text-right">
                          {o.pnl == null ? "-" : `$${o.pnl}`}
                        </td>
                        <td className="p-3">{o.ai_score || "-"}</td>
                        <td className="p-3">{o.smart_money_score || "-"}</td>
                        <td className="p-3">{o.opportunity_score || "-"}</td>
                        <td className="p-3">{o.trend_hold ? "ON" : "OFF"}</td>
                        <td className="p-3">{o.reason}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          );
        })}
      </section>
    </div>
  );
}

function Metric({
  label,
  value,
  danger = false,
}: {
  label: string;
  value: string | number;
  danger?: boolean;
}) {
  return (
    <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-5">
      <p className="text-sm text-slate-400">{label}</p>
      <p className={`mt-2 text-2xl font-bold ${danger ? "text-red-400" : "text-white"}`}>
        {value}
      </p>
    </div>
  );
}

function Mini({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-3">
      <p className="text-xs text-slate-400">{label}</p>
      <p className="mt-1 font-bold">{value}</p>
    </div>
  );
}

function Badge({ label }: { label: string }) {
  return (
    <span
      className={`rounded-full px-3 py-1 text-xs ${
        label.includes("ON") ||
        label.includes("RUNNING") ||
        label.includes("OPEN")
          ? "bg-green-500/10 text-green-300"
          : label.includes("LOCKED")
          ? "bg-red-500/10 text-red-300"
          : "bg-slate-500/10 text-slate-300"
      }`}
    >
      {label}
    </span>
  );
}

function Input({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <label>
      <span className="mb-1 block text-xs text-slate-400">{label}</span>
      <input
        className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3"
        type="number"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </label>
  );
}

function Progress({
  label,
  value,
  percent,
  danger = false,
}: {
  label: string;
  value: string;
  percent: number;
  danger?: boolean;
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-3">
      <div className="mb-2 flex justify-between text-xs">
        <span className="text-slate-400">{label}</span>
        <span>{value}</span>
      </div>

      <div className="h-2 overflow-hidden rounded-full bg-white/10">
        <div
          className={`h-full rounded-full ${danger ? "bg-red-400" : "bg-cyan-400"}`}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}

function progress(value: number, max: number) {
  if (!max || max <= 0) return 0;
  return Math.max(0, Math.min(100, (value / max) * 100));
}

function formatDate(value: string) {
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "-";
  return d.toLocaleTimeString("tr-TR");
}

function formatNumber(value: number) {
  if (!value) return "0";
  if (Math.abs(value) < 0.01) return value.toFixed(8);
  if (Math.abs(value) < 1) return value.toFixed(6);
  return value.toLocaleString();
}