import { useEffect, useState } from "react";
import { RefreshCcw, Target } from "lucide-react";
import { getOpportunities } from "../services/opportunityService";

export default function OpportunitiesPage() {
  const [items, setItems] = useState<any[]>([]);
  const [bestLong, setBestLong] = useState<any>(null);
  const [bestShort, setBestShort] = useState<any>(null);

  useEffect(() => {
    load();
    const interval = setInterval(load, 10000);
    return () => clearInterval(interval);
  }, []);

  async function load() {
    const data = await getOpportunities(100);
    setItems(data.items || []);
    setBestLong(data.best_long);
    setBestShort(data.best_short);
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between rounded-3xl border border-white/10 bg-[#070b1f] p-6">
        <div>
          <h2 className="text-2xl font-bold">Quantum Opportunities</h2>
          <p className="text-slate-400">En güçlü LONG / SHORT fırsat tarayıcı.</p>
        </div>

        <button onClick={load} className="flex items-center gap-2 rounded-xl bg-cyan-500 px-5 py-3 font-bold text-black">
          <RefreshCcw size={18} />
          Refresh
        </button>
      </div>

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <Card title="Best LONG" item={bestLong} />
        <Card title="Best SHORT" item={bestShort} />
      </section>

      <div className="overflow-auto rounded-3xl border border-white/10 bg-[#070b1f]">
        <table className="w-full text-left text-sm">
          <thead className="bg-white/5 text-slate-300">
            <tr>
              <th className="p-4">Symbol</th>
              <th className="p-4 text-right">Price</th>
              <th className="p-4 text-right">AI</th>
              <th className="p-4 text-right">SMC</th>
              <th className="p-4 text-right">Opportunity</th>
              <th className="p-4">Decision</th>
              <th className="p-4 text-right">24h</th>
              <th className="p-4 text-right">Volume</th>
            </tr>
          </thead>

          <tbody>
            {items.map((item) => (
              <tr key={item.symbol} className="border-t border-white/10">
                <td className="p-4 font-bold">{item.symbol}</td>
                <td className="p-4 text-right">${format(item.price)}</td>
                <td className="p-4 text-right">{item.ai_score}</td>
                <td className="p-4 text-right">{item.smart_money_score}</td>
                <td className="p-4 text-right font-bold text-cyan-300">{item.opportunity_score}</td>
                <td className="p-4">{item.decision}</td>
                <td className={`p-4 text-right ${item.change_24h >= 0 ? "text-green-400" : "text-red-400"}`}>
                  {item.change_24h}%
                </td>
                <td className="p-4 text-right">${Number(item.volume_24h || 0).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Card({ title, item }: { title: string; item: any }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
      <h3 className="mb-3 flex items-center gap-2 text-xl font-bold">
        <Target size={20} />
        {title}
      </h3>

      {!item ? (
        <p className="text-slate-400">Fırsat yok.</p>
      ) : (
        <div className="space-y-2">
          <p className="text-3xl font-bold">{item.symbol}</p>
          <p className="text-slate-400">Decision: {item.decision}</p>
          <p className="text-cyan-300">Opportunity Score: {item.opportunity_score}/100</p>
          <p className="text-slate-400">AI: {item.ai_score} • SMC: {item.smart_money_score}</p>
        </div>
      )}
    </div>
  );
}

function format(value: number) {
  if (!value) return "0";
  if (value < 1) return Number(value).toFixed(6);
  return Number(value).toLocaleString();
}