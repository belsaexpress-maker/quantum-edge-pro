import type { MarketItem } from "../types/market";

export default function SignalPanel({ items }: { items: MarketItem[] }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-5">
      <h3 className="mb-4 text-xl font-bold">AI Signal Center</h3>

      <div className="space-y-3">
        {items.map((item) => (
          <div
            key={item.symbol}
            className="rounded-2xl border border-white/10 bg-white/5 p-4"
          >
            <div className="flex justify-between">
              <strong>{item.symbol}</strong>
              <span className="text-cyan-300">{item.signal}</span>
            </div>
            <p className="mt-2 text-sm text-slate-400">
              24h change: {item.change_24h}%
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}