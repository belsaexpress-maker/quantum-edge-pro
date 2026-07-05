import { useEffect, useMemo, useState } from "react";
import { Brain, RefreshCcw, Search, ShieldAlert, Target, TrendingUp } from "lucide-react";

import { getAIConfidenceAll } from "../services/aiService";
import type { AIConfidenceResult } from "../types/ai";

export default function AISignalsPage() {
  const [items, setItems] = useState<AIConfidenceResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");

  useEffect(() => {
    loadAI();
  }, []);

  async function loadAI() {
    setLoading(true);

    try {
      const data = await getAIConfidenceAll();
      setItems(Object.values(data));
    } finally {
      setLoading(false);
    }
  }

  const filteredItems = useMemo(() => {
    return items.filter((item) =>
      item.symbol.toLowerCase().includes(search.toLowerCase())
    );
  }, [items, search]);

  const averageScore =
    filteredItems.length > 0
      ? Math.round(
          filteredItems.reduce((total, item) => total + item.ai_confidence, 0) /
            filteredItems.length
        )
      : 0;

  const strongBuyCount = filteredItems.filter((item) =>
    item.signal.includes("STRONG BUY")
  ).length;

  const highRiskCount = filteredItems.filter(
    (item) => item.risk === "High" || item.risk === "Very High"
  ).length;

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 rounded-3xl border border-white/10 bg-[#070b1f] p-6 xl:flex-row xl:items-center">
        <div>
          <h2 className="text-2xl font-bold">Quantum AI Engine</h2>
          <p className="mt-1 text-slate-400">
            Top coinleri analiz eder; RSI, MACD, EMA, SuperTrend, VWAP, Order Book,
            Funding, Whale, Haber ve Sentiment verilerinden 0–100 AI güven skoru üretir.
          </p>
        </div>

        <button
          onClick={loadAI}
          className="flex items-center justify-center gap-2 rounded-xl bg-cyan-500 px-5 py-3 font-bold text-black hover:bg-cyan-400"
        >
          <RefreshCcw size={18} />
          {loading ? "Analiz ediliyor..." : "AI Refresh"}
        </button>
      </div>

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-4">
        <MetricCard icon={<Brain />} label="Coins Scanned" value={filteredItems.length} />
        <MetricCard icon={<TrendingUp />} label="Avg Confidence" value={`${averageScore}/100`} />
        <MetricCard icon={<Target />} label="Strong Buy" value={strongBuyCount} />
        <MetricCard icon={<ShieldAlert />} label="High Risk" value={highRiskCount} />
      </section>

      <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-5">
        <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
          <Search size={18} className="text-slate-400" />
          <input
            className="w-full bg-transparent outline-none"
            placeholder="Coin ara... BTCUSDT, ETHUSDT, SOLUSDT"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-2 2xl:grid-cols-3">
        {filteredItems.map((item) => (
          <div
            key={item.symbol}
            className="rounded-3xl border border-white/10 bg-[#070b1f] p-6 shadow-2xl shadow-black/30"
          >
            <div className="mb-5 flex items-center justify-between">
              <div>
                <h3 className="text-2xl font-bold">{item.symbol}</h3>
                <p className="text-sm text-slate-400">AI Market Analysis</p>
              </div>

              <span className="rounded-full bg-cyan-500/10 px-3 py-1 text-sm text-cyan-300">
                {item.signal}
              </span>
            </div>

            <Progress label="AI Confidence" value={item.ai_confidence} />
            <Progress label="Risk Pressure" value={riskToScore(item.risk)} danger />

            <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-sm text-slate-400">AI Summary</p>
              <p className="mt-2 text-sm text-slate-200">{item.summary}</p>
            </div>

            <div className="mt-5 grid grid-cols-1 gap-3">
              {Object.entries(item.indicators).map(([name, value]) => (
                <MiniIndicator key={name} name={name} value={value} />
              ))}
            </div>
          </div>
        ))}
      </section>
    </div>
  );
}

function riskToScore(risk: string) {
  if (risk === "Very High") return 90;
  if (risk === "High") return 75;
  if (risk === "Medium") return 55;
  if (risk === "Controlled") return 35;
  return 45;
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

function Progress({
  label,
  value,
  danger = false,
}: {
  label: string;
  value: number;
  danger?: boolean;
}) {
  return (
    <div className="mb-4">
      <div className="mb-2 flex justify-between text-sm">
        <span className="text-slate-400">{label}</span>
        <span>{value}%</span>
      </div>

      <div className="h-2 rounded-full bg-white/10">
        <div
          className={`h-2 rounded-full ${danger ? "bg-red-400" : "bg-cyan-400"}`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}

function MiniIndicator({ name, value }: { name: string; value: number }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-3">
      <div className="mb-2 flex justify-between text-xs">
        <span className="text-slate-400">{name}</span>
        <span>{value}/100</span>
      </div>

      <div className="h-1.5 rounded-full bg-white/10">
        <div
          className="h-1.5 rounded-full bg-cyan-400"
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}