import { useEffect, useMemo, useState } from "react";
import { Newspaper, TrendingDown, TrendingUp, Zap } from "lucide-react";

import { getLatestNews } from "../services/marketService";

type NewsItem = {
  title: string;
  category: string;
  impact: string;
  sentiment: string;
  source?: string;
};

type Category = "all" | "Crypto" | "Stocks" | "Commodities";

export default function NewsPage() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [category, setCategory] = useState<Category>("all");

  useEffect(() => {
    loadNews();
  }, []);

  async function loadNews() {
    const data = await getLatestNews();
    setNews(data);
  }

  const filteredNews = useMemo(() => {
    if (category === "all") return news;
    return news.filter((item) => item.category === category);
  }, [news, category]);

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
        <h2 className="text-2xl font-bold">News Center</h2>
        <p className="mt-1 text-slate-400">
          Finans haberleri, piyasa etkisi ve AI duyarlılık analizleri.
        </p>
      </div>

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-4">
        <MetricCard icon={<Newspaper />} label="News Feed" value="Online" />
        <MetricCard icon={<Zap />} label="Impact Engine" value="Active" />
        <MetricCard icon={<TrendingUp />} label="Positive" value={news.filter((n) => n.sentiment === "positive").length} />
        <MetricCard icon={<TrendingDown />} label="High Impact" value={news.filter((n) => n.impact === "high").length} />
      </section>

      <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-5">
        <div className="flex flex-wrap gap-2">
          <FilterButton label="All" active={category === "all"} onClick={() => setCategory("all")} />
          <FilterButton label="Crypto" active={category === "Crypto"} onClick={() => setCategory("Crypto")} />
          <FilterButton label="Stocks" active={category === "Stocks"} onClick={() => setCategory("Stocks")} />
          <FilterButton label="Commodities" active={category === "Commodities"} onClick={() => setCategory("Commodities")} />
        </div>
      </div>

      <section className="grid grid-cols-1 gap-6 2xl:grid-cols-[1fr_420px]">
        <div className="space-y-4">
          {filteredNews.map((item, index) => (
            <div
              key={index}
              className="rounded-3xl border border-white/10 bg-[#070b1f] p-6 shadow-2xl shadow-black/20"
            >
              <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
                <span className="rounded-full bg-cyan-500/10 px-3 py-1 text-sm text-cyan-300">
                  {item.category}
                </span>

                <div className="flex gap-2">
                  <Badge label={item.impact} type="impact" />
                  <Badge label={item.sentiment} type="sentiment" />
                </div>
              </div>

              <h3 className="text-xl font-bold">{item.title}</h3>

              <p className="mt-3 text-sm text-slate-400">
                Source: {item.source || "Quantum Edge News"}
              </p>

              <div className="mt-5 rounded-2xl border border-white/10 bg-white/5 p-4">
                <p className="text-sm text-slate-400">AI Summary</p>
                <p className="mt-2 text-slate-200">
                  Bu haber piyasa üzerinde {item.impact} etki oluşturabilir.
                  Duyarlılık analizi: {item.sentiment}.
                </p>
              </div>
            </div>
          ))}
        </div>

        <aside className="space-y-6">
          <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
            <h3 className="text-xl font-bold">Market Impact</h3>

            <div className="mt-5 space-y-4">
              <ImpactRow label="Crypto" value={72} />
              <ImpactRow label="Stocks" value={58} />
              <ImpactRow label="Commodities" value={64} />
              <ImpactRow label="Forex" value={46} />
            </div>
          </div>

          <div className="rounded-3xl border border-cyan-400/20 bg-cyan-400/10 p-6">
            <p className="text-sm text-cyan-300">Premium News AI</p>
            <h3 className="mt-2 text-xl font-bold">Haberden Sinyale</h3>
            <p className="mt-3 text-sm text-slate-300">
              İleride haberler otomatik olarak AI sinyal skoruna bağlanacak.
            </p>
          </div>
        </aside>
      </section>
    </div>
  );
}

function FilterButton({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`rounded-xl px-4 py-2 text-sm font-semibold ${
        active ? "bg-cyan-500 text-black" : "bg-white/5 text-slate-300 hover:bg-white/10"
      }`}
    >
      {label}
    </button>
  );
}

function Badge({ label, type }: { label: string; type: "impact" | "sentiment" }) {
  const color =
    label === "high"
      ? "bg-red-500/10 text-red-300"
      : label === "positive"
      ? "bg-green-500/10 text-green-300"
      : "bg-white/10 text-slate-300";

  return <span className={`rounded-full px-3 py-1 text-xs ${color}`}>{type}: {label}</span>;
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

function ImpactRow({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="mb-2 flex justify-between text-sm">
        <span className="text-slate-400">{label}</span>
        <span>{value}%</span>
      </div>
      <div className="h-2 rounded-full bg-white/10">
        <div className="h-2 rounded-full bg-cyan-400" style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}