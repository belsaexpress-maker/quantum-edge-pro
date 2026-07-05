import { useState } from "react";
import { Radar, RefreshCcw, ShieldAlert, Target, TrendingUp } from "lucide-react";

import { refreshScanner, scanMarket } from "../services/scannerService";
import type { ScannerItem } from "../types/scanner";

export default function AIScannerPage() {
  const [limit, setLimit] = useState(100);
  const [items, setItems] = useState<ScannerItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [totalScanned, setTotalScanned] = useState(0);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  async function runScan() {
    setLoading(true);

    try {
      await refreshScanner();
      const data = await scanMarket(limit);

      setItems(data.items);
      setTotalScanned(data.total_scanned);
      setLastUpdated(data.last_updated);
    } finally {
      setLoading(false);
    }
  }

  const best = items[0];

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 rounded-3xl border border-white/10 bg-[#070b1f] p-6 xl:flex-row xl:items-center">
        <div>
          <h2 className="text-2xl font-bold">Quantum AI Scanner v2</h2>
          <p className="mt-1 text-slate-400">
            Gate.io’daki tüm USDT coinleri hızlı skorlar, en iyi fırsatları sıralar.
          </p>
          {lastUpdated && (
            <p className="mt-2 text-xs text-slate-500">
              Son tarama: {new Date(lastUpdated).toLocaleString("tr-TR")}
            </p>
          )}
        </div>

        <div className="flex gap-3">
          <select
            className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 outline-none"
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
          >
            <option value={50}>Top 50</option>
            <option value={100}>Top 100</option>
            <option value={250}>Top 250</option>
            <option value={500}>Top 500</option>
          </select>

          <button
            onClick={runScan}
            className="flex items-center gap-2 rounded-xl bg-cyan-500 px-5 py-3 font-bold text-black hover:bg-cyan-400"
          >
            <RefreshCcw size={18} />
            {loading ? "Taranıyor..." : "Scan All Market"}
          </button>
        </div>
      </div>

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-4">
        <MetricCard icon={<Radar />} label="Total Scanned" value={totalScanned} />
        <MetricCard icon={<TrendingUp />} label="Best Coin" value={best?.symbol || "-"} />
        <MetricCard icon={<Target />} label="Best Score" value={best ? `${best.confidence}/100` : "-"} />
        <MetricCard icon={<ShieldAlert />} label="Risk" value={best?.risk || "-"} />
      </section>

      <div className="max-h-[720px] overflow-auto rounded-3xl border border-white/10 bg-[#070b1f]">
        <table className="w-full text-left text-sm">
          <thead className="sticky top-0 z-10 bg-[#11162d] text-slate-300">
            <tr>
              <th className="p-4">Rank</th>
              <th className="p-4">Symbol</th>
              <th className="p-4 text-right">Price</th>
              <th className="p-4 text-right">24h</th>
              <th className="p-4 text-right">Volume</th>
              <th className="p-4 text-right">AI Score</th>
              <th className="p-4 text-right">Direction</th>
              <th className="p-4 text-right">Risk</th>
              <th className="p-4 text-right">Signal</th>
            </tr>
          </thead>

          <tbody>
            {items.map((item, index) => (
              <tr key={item.symbol} className="border-t border-white/10 hover:bg-white/5">
                <td className="p-4 text-slate-400">#{index + 1}</td>
                <td className="p-4 font-bold">{item.symbol}</td>
                <td className="p-4 text-right">${formatNumber(item.price)}</td>
                <td className={`p-4 text-right ${item.change_24h >= 0 ? "text-green-400" : "text-red-400"}`}>
                  {item.change_24h}%
                </td>
                <td className="p-4 text-right text-slate-400">
                  ${formatCompact(item.volume_24h)}
                </td>
                <td className="p-4 text-right font-bold text-cyan-300">
                  {item.confidence}/100
                </td>
                <td className="p-4 text-right">{item.direction}</td>
                <td className="p-4 text-right">{item.risk}</td>
                <td className="p-4 text-right text-cyan-300">{item.signal}</td>
              </tr>
            ))}

            {items.length === 0 && (
              <tr>
                <td colSpan={9} className="p-8 text-center text-slate-400">
                  Henüz tarama yapılmadı. Scan All Market butonuna bas.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {best && (
        <section className="grid grid-cols-1 gap-6 xl:grid-cols-3">
          <PlanCard title={`Best Setup — ${best.symbol}`}>
            <Row label="Entry Low" value={best.entry_zone.low} />
            <Row label="Entry High" value={best.entry_zone.high} />
            <Row label="Stop Loss" value={best.stop_loss} />
          </PlanCard>

          <PlanCard title="Take Profit">
            <Row label="TP1" value={best.take_profit.tp1} />
            <Row label="TP2" value={best.take_profit.tp2} />
            <Row label="TP3" value={best.take_profit.tp3} />
          </PlanCard>

          <PlanCard title="AI Decision">
            <Row label="Signal" value={best.signal} />
            <Row label="Confidence" value={`${best.confidence}/100`} />
            <Row label="Risk" value={best.risk} />
          </PlanCard>
        </section>
      )}
    </div>
  );
}

function MetricCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
}) {
  return (
    <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-5">
      <div className="mb-3 text-cyan-300">{icon}</div>
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
    <div className="flex justify-between border-b border-white/10 py-2 text-sm">
      <span className="text-slate-400">{label}</span>
      <span className="font-semibold">{value}</span>
    </div>
  );
}

function formatCompact(value: number) {
  if (value >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(2)}B`;
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(2)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(2)}K`;
  return value.toFixed(2);
}

function formatNumber(value: number) {
  if (value < 0.01) return value.toFixed(8);
  if (value < 1) return value.toFixed(6);
  return value.toLocaleString();
}