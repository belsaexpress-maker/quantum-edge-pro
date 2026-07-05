import { useState } from "react";
import { Send, ShieldCheck } from "lucide-react";

import { executeTrade } from "../services/tradingService";

export default function TradingConsolePage() {
  const [symbol, setSymbol] = useState("BTCUSDT");
  const [side, setSide] = useState<"BUY" | "SELL">("BUY");
  const [price, setPrice] = useState("65000");
  const [quantity, setQuantity] = useState("0.01");
  const [result, setResult] = useState<any>(null);

  async function submitTrade() {
    const data = await executeTrade({
      symbol,
      side,
      price: Number(price),
      quantity: Number(quantity),
    });

    setResult(data);
  }

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
        <h2 className="text-2xl font-bold">Trading Console</h2>
        <p className="mt-1 text-slate-400">
          Emir motoru. Şu an güvenli PAPER modda çalışır.
        </p>
      </div>

      <div className="rounded-3xl border border-yellow-400/20 bg-yellow-400/10 p-5">
        <div className="flex items-center gap-3 text-yellow-300">
          <ShieldCheck />
          <strong>Güvenli Mod: PAPER</strong>
        </div>
        <p className="mt-2 text-sm text-slate-300">
          Bu ekrandan gönderilen emirler gerçek borsaya gitmez. Paper Trading
          hesabına sanal emir olarak yazılır.
        </p>
      </div>

      <section className="grid grid-cols-1 gap-6 2xl:grid-cols-[420px_1fr]">
        <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
          <h3 className="mb-4 text-xl font-bold">Create Order</h3>

          <div className="space-y-3">
            <input
              className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 uppercase outline-none focus:border-cyan-400"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            />

            <select
              className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 outline-none focus:border-cyan-400"
              value={side}
              onChange={(e) => setSide(e.target.value as "BUY" | "SELL")}
            >
              <option value="BUY">BUY</option>
              <option value="SELL">SELL</option>
            </select>

            <input
              className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 outline-none focus:border-cyan-400"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              type="number"
            />

            <input
              className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 outline-none focus:border-cyan-400"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              type="number"
            />

            <button
              onClick={submitTrade}
              className={`flex w-full items-center justify-center gap-2 rounded-xl py-3 font-bold text-black ${
                side === "BUY"
                  ? "bg-green-500 hover:bg-green-400"
                  : "bg-red-500 hover:bg-red-400"
              }`}
            >
              <Send size={18} />
              Execute {side}
            </button>
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
          <h3 className="mb-4 text-xl font-bold">Execution Result</h3>

          {!result && (
            <p className="text-slate-400">
              Henüz emir gönderilmedi.
            </p>
          )}

          {result?.error && (
            <div className="rounded-2xl border border-red-400/20 bg-red-500/10 p-4 text-red-300">
              {result.error}
            </div>
          )}

          {result?.message && (
            <div className="space-y-4">
              <div className="rounded-2xl border border-green-400/20 bg-green-500/10 p-4 text-green-300">
                {result.message}
              </div>

              {result.order && (
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <Row label="Order ID" value={`#${result.order.id}`} />
                  <Row label="Symbol" value={result.order.symbol} />
                  <Row label="Side" value={result.order.side} />
                  <Row label="Price" value={`$${result.order.price}`} />
                  <Row label="Quantity" value={result.order.quantity} />
                  <Row label="Value" value={`$${result.order.value}`} />
                  <Row label="Status" value={result.order.status} />
                </div>
              )}
            </div>
          )}
        </div>
      </section>
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