import { useEffect, useMemo, useState } from "react";
import { getMarketOverview } from "../services/marketService";
import type { MarketItem, MarketOverview } from "../types/market";

type Category = "all" | "crypto" | "stocks" | "indices" | "commodities" | "forex";

export default function MarketsPage() {
  const [market, setMarket] = useState<MarketOverview | null>(null);
  const [category, setCategory] = useState<Category>("all");
  const [search, setSearch] = useState("");

  useEffect(() => {
    loadMarkets();
  }, []);

  async function loadMarkets() {
    const data = await getMarketOverview();
    setMarket(data);
  }

  const allItems = useMemo(() => {
    if (!market) return [];

    const list: MarketItem[] = [
      ...market.crypto,
      ...market.stocks,
      ...market.indices,
      ...market.commodities,
      ...market.forex,
    ];

    return list.filter((item) => {
      const matchCategory = category === "all" || item.asset_type === category.slice(0, -1) || item.asset_type === category;
      const matchSearch =
        item.symbol.toLowerCase().includes(search.toLowerCase()) ||
        item.name.toLowerCase().includes(search.toLowerCase());

      return matchCategory && matchSearch;
    });
  }, [market, category, search]);

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
        <h2 className="text-2xl font-bold">Markets</h2>
        <p className="mt-1 text-slate-400">
          Kripto, hisse, endeks, emtia ve forex piyasalarını tek ekranda takip et.
        </p>
      </div>

      <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-5">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
          <div className="flex flex-wrap gap-2">
            <FilterButton label="All" active={category === "all"} onClick={() => setCategory("all")} />
            <FilterButton label="Crypto" active={category === "crypto"} onClick={() => setCategory("crypto")} />
            <FilterButton label="Stocks" active={category === "stocks"} onClick={() => setCategory("stocks")} />
            <FilterButton label="Indices" active={category === "indices"} onClick={() => setCategory("indices")} />
            <FilterButton label="Commodities" active={category === "commodities"} onClick={() => setCategory("commodities")} />
            <FilterButton label="Forex" active={category === "forex"} onClick={() => setCategory("forex")} />
          </div>

          <input
            className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 outline-none focus:border-cyan-400 xl:w-80"
            placeholder="Search symbol or name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="overflow-hidden rounded-3xl border border-white/10 bg-[#070b1f]">
        <table className="w-full text-left text-sm">
          <thead className="bg-white/5 text-slate-300">
            <tr>
              <th className="p-4">Symbol</th>
              <th className="p-4">Name</th>
              <th className="p-4">Type</th>
              <th className="p-4 text-right">Price</th>
              <th className="p-4 text-right">24h</th>
              <th className="p-4 text-right">Signal</th>
            </tr>
          </thead>

          <tbody>
            {allItems.map((item) => (
              <tr key={`${item.asset_type}-${item.symbol}`} className="border-t border-white/10">
                <td className="p-4 font-bold">{item.symbol}</td>
                <td className="p-4 text-slate-300">{item.name}</td>
                <td className="p-4 text-slate-400">{item.asset_type}</td>
                <td className="p-4 text-right">${Number(item.price).toLocaleString()}</td>
                <td
                  className={`p-4 text-right ${
                    item.change_24h >= 0 ? "text-green-400" : "text-red-400"
                  }`}
                >
                  {item.change_24h}%
                </td>
                <td className="p-4 text-right text-cyan-300">{item.signal}</td>
              </tr>
            ))}

            {allItems.length === 0 && (
              <tr>
                <td colSpan={6} className="p-8 text-center text-slate-400">
                  Veri bulunamadı.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
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