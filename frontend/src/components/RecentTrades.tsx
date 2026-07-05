import type { TradeRow } from "../types/trading";

const trades: TradeRow[] = [
  { price: 67140, amount: 0.022, side: "buy", time: "22:41:12" },
  { price: 67130, amount: 0.014, side: "sell", time: "22:41:08" },
  { price: 67155, amount: 0.051, side: "buy", time: "22:40:55" },
  { price: 67110, amount: 0.019, side: "sell", time: "22:40:42" },
  { price: 67180, amount: 0.032, side: "buy", time: "22:40:21" },
];

export default function RecentTrades() {
  return (
    <div className="rounded-3xl border border-white/10 bg-[#070b1f]/90 p-5 shadow-2xl shadow-black/30">
      <h3 className="mb-4 text-xl font-bold">Recent Trades</h3>

      <div className="grid grid-cols-3 border-b border-white/10 pb-2 text-xs text-slate-400">
        <span>Price</span>
        <span className="text-right">Amount</span>
        <span className="text-right">Time</span>
      </div>

      <div className="mt-3 space-y-3">
        {trades.map((trade, index) => (
          <div key={index} className="grid grid-cols-3 text-sm">
            <span
              className={
                trade.side === "buy" ? "text-green-400" : "text-red-400"
              }
            >
              {trade.price.toLocaleString()}
            </span>
            <span className="text-right text-slate-300">{trade.amount}</span>
            <span className="text-right text-slate-400">{trade.time}</span>
          </div>
        ))}
      </div>
    </div>
  );
}