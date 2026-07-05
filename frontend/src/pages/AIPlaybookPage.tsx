import { useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { getPlaybook } from "../services/playbookService";
import type { PlaybookResult, SmartMoneyZone } from "../types/playbook";

export default function AIPlaybookPage() {
  const [symbol, setSymbol] = useState("BTCUSDT");
  const [timeframe, setTimeframe] = useState("1h");
  const [data, setData] = useState<PlaybookResult | null>(null);
  const [loading, setLoading] = useState(false);

  async function analyze() {
    setLoading(true);

    try {
      const result = await getPlaybook(symbol, timeframe);
      setData(result);
    } finally {
      setLoading(false);
    }
  }

  const chartData =
    data?.chart.map((candle) => ({
      time: new Date(candle.time).toLocaleTimeString("tr-TR", {
        hour: "2-digit",
        minute: "2-digit",
      }),
      close: candle.close,
    })) || [];

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
        <h2 className="text-2xl font-bold">AI Playbook Pro</h2>
        <p className="mt-1 text-slate-400">
          RSI, EMA, MACD, ATR, Pivot, Camarilla, Fibonacci ve Smart Money
          Concepts ile işlem planı üretir.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 rounded-3xl border border-white/10 bg-[#070b1f] p-5 xl:grid-cols-[1fr_220px_180px]">
        <input
          className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 uppercase outline-none focus:border-cyan-400"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          placeholder="BTCUSDT, ETHUSDT, PEPEUSDT"
        />

        <select
          className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 outline-none focus:border-cyan-400"
          value={timeframe}
          onChange={(e) => setTimeframe(e.target.value)}
        >
          <option value="15m">15m</option>
          <option value="1h">1h</option>
          <option value="4h">4h</option>
          <option value="1d">1d</option>
        </select>

        <button
          onClick={analyze}
          className="rounded-xl bg-cyan-500 px-5 py-3 font-bold text-black hover:bg-cyan-400"
        >
          {loading ? "Analiz..." : "Analyze"}
        </button>
      </div>

      {data && (
        <>
          <section className="grid grid-cols-1 gap-4 xl:grid-cols-5">
            <MetricCard label="Symbol" value={data.symbol} />
            <MetricCard label="Signal" value={data.signal} />
            <MetricCard label="Confidence" value={`${data.confidence}/100`} />
            <MetricCard label="Price" value={`$${data.current_price}`} />
            <MetricCard label="SMC Score" value={`${data.smart_money.score}/100`} />
          </section>

          <section className="grid grid-cols-1 gap-6 2xl:grid-cols-[1fr_420px]">
            <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
              <h3 className="mb-4 text-xl font-bold">
                AI Chart Plan — {data.symbol}
              </h3>

              <div className="h-[520px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <defs>
                      <linearGradient id="close" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.4} />
                        <stop offset="95%" stopColor="#22d3ee" stopOpacity={0} />
                      </linearGradient>
                    </defs>

                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="time" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" domain={["auto", "auto"]} />
                    <Tooltip
                      contentStyle={{
                        background: "#020617",
                        border: "1px solid rgba(255,255,255,0.1)",
                        borderRadius: "12px",
                      }}
                    />

                    <Area
                      type="monotone"
                      dataKey="close"
                      stroke="#22d3ee"
                      fill="url(#close)"
                      strokeWidth={2}
                    />

                    <ReferenceLine y={data.entry_zone.low} stroke="#22c55e" label="Entry Low" />
                    <ReferenceLine y={data.entry_zone.high} stroke="#84cc16" label="Entry High" />
                    <ReferenceLine y={data.stop_loss} stroke="#ef4444" label="Stop" />
                    <ReferenceLine y={data.take_profit.tp1} stroke="#38bdf8" label="TP1" />
                    <ReferenceLine y={data.take_profit.tp2} stroke="#06b6d4" label="TP2" />
                    <ReferenceLine y={data.take_profit.tp3} stroke="#a78bfa" label="TP3" />

                    {data.smart_money.order_blocks.slice(-2).map((zone, index) => (
                      <ReferenceLine
                        key={`ob-${index}`}
                        y={(zone.low + zone.high) / 2}
                        stroke="#f59e0b"
                        label="OB"
                      />
                    ))}

                    {data.smart_money.fvg.slice(-2).map((zone, index) => (
                      <ReferenceLine
                        key={`fvg-${index}`}
                        y={(zone.low + zone.high) / 2}
                        stroke="#e879f9"
                        label="FVG"
                      />
                    ))}
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="space-y-6">
              <PlanCard title="Entry Zone">
                <Row label="Low" value={data.entry_zone.low} />
                <Row label="High" value={data.entry_zone.high} />
              </PlanCard>

              <PlanCard title="Take Profit">
                <Row label="TP1" value={data.take_profit.tp1} />
                <Row label="TP2" value={data.take_profit.tp2} />
                <Row label="TP3" value={data.take_profit.tp3} />
              </PlanCard>

              <PlanCard title="Risk">
                <Row label="Stop Loss" value={data.stop_loss} />
                <Row label="Direction" value={data.direction} />
              </PlanCard>
            </div>
          </section>

          <section className="grid grid-cols-1 gap-6 xl:grid-cols-3">
            <LevelCard
              title="Indicators"
              levels={{
                rsi: data.indicators.rsi ?? 0,
                ema20: data.indicators.ema20 ?? 0,
                ema50: data.indicators.ema50 ?? 0,
                ema100: data.indicators.ema100 ?? 0,
                ema200: data.indicators.ema200 ?? 0,
                atr: data.indicators.atr ?? 0,
                macd: data.indicators.macd.macd ?? 0,
                macd_signal: data.indicators.macd.signal ?? 0,
                macd_histogram: data.indicators.macd.histogram ?? 0,
              }}
            />

            <PlanCard title="Smart Money Structure">
              <Row label="SMC Score" value={`${data.smart_money.score}/100`} />
              <Row label="Structure" value={data.smart_money.structure.structure} />
              <Row label="BOS" value={data.smart_money.structure.bos || "-"} />
              <Row label="CHoCH" value={data.smart_money.structure.choch || "-"} />
              <Row
                label="Liquidity"
                value={data.smart_money.liquidity_sweep?.type || "-"}
              />
            </PlanCard>

            <ZonesCard title="Order Blocks" zones={data.smart_money.order_blocks} />
            <ZonesCard title="Fair Value Gaps" zones={data.smart_money.fvg} />

            <LevelCard title="Support / Resistance" levels={data.support_resistance} />
            <LevelCard title="Pivot Levels" levels={data.pivot_levels} />
            <LevelCard title="Camarilla" levels={data.camarilla_levels} />
            <LevelCard title="Fibonacci" levels={data.fibonacci} />

            <PlanCard title="AI Reasons">
              <div className="space-y-2">
                {data.reasons.map((reason, index) => (
                  <p key={index} className="text-sm text-slate-300">
                    ✓ {reason}
                  </p>
                ))}
              </div>
            </PlanCard>
          </section>
        </>
      )}
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-5">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-2 text-2xl font-bold">{value}</p>
    </div>
  );
}

function PlanCard({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-5">
      <h3 className="mb-4 text-xl font-bold">{title}</h3>
      {children}
    </div>
  );
}

function Row({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex justify-between gap-3 border-b border-white/10 py-2 text-sm">
      <span className="text-slate-400">{label}</span>
      <span className="text-right font-semibold">{value}</span>
    </div>
  );
}

function LevelCard({
  title,
  levels,
}: {
  title: string;
  levels: Record<string, number>;
}) {
  return (
    <PlanCard title={title}>
      {Object.entries(levels).map(([key, value]) => (
        <Row key={key} label={key.toUpperCase()} value={value} />
      ))}
    </PlanCard>
  );
}

function ZonesCard({
  title,
  zones,
}: {
  title: string;
  zones: SmartMoneyZone[];
}) {
  return (
    <PlanCard title={title}>
      {zones.length === 0 && (
        <p className="text-sm text-slate-400">Bölge bulunamadı.</p>
      )}

      {zones.map((zone, index) => (
        <div key={index} className="mb-3 rounded-2xl border border-white/10 bg-white/5 p-3">
          <p className="font-semibold text-cyan-300">{zone.type}</p>
          <Row label="Low" value={zone.low} />
          <Row label="High" value={zone.high} />
        </div>
      ))}
    </PlanCard>
  );
}