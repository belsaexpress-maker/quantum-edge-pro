import type { MarketItem } from "../types/market";

export default function MarketCard({ item }: { item: MarketItem }) {
  const positive = item.change_24h >= 0;

  return (
    <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-5 shadow-xl shadow-black/20">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold">{item.symbol}</h3>
          <p className="text-sm text-slate-400">{item.name}</p>
        </div>

        <span
          className={`rounded-full px-3 py-1 text-sm ${
            positive
              ? "bg-green-500/10 text-green-400"
              : "bg-red-500/10 text-red-400"
          }`}
        >
          {item.change_24h}%
        </span>
      </div>

      <p className="mt-4 text-2xl font-bold">
        ${Number(item.price).toLocaleString()}
      </p>

      <p className="mt-3 text-sm text-cyan-300">{item.signal}</p>
    </div>
  );
}