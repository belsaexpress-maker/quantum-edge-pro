import { useEffect, useState } from "react";
import { RefreshCcw, RotateCcw, Wallet } from "lucide-react";

import {
  createPaperOrder,
  getPaperAccount,
  resetPaperAccount,
} from "../services/paperService";
import type { PaperAccount } from "../types/paper";

export default function PaperTradingPage() {
  const [account, setAccount] = useState<PaperAccount | null>(null);
  const [symbol, setSymbol] = useState("BTCUSDT");
  const [side, setSide] = useState<"BUY" | "SELL">("BUY");
  const [price, setPrice] = useState("65000");
  const [quantity, setQuantity] = useState("0.01");
  const [message, setMessage] = useState("");

  useEffect(() => {
    loadAccount();
  }, []);

  async function loadAccount() {
    const data = await getPaperAccount();
    setAccount(data);
  }

  async function submitOrder() {
    setMessage("");

    const result = await createPaperOrder({
      symbol,
      side,
      price: Number(price),
      quantity: Number(quantity),
    });

    if (result.error) {
      setMessage(result.error);
      return;
    }

    setMessage("Paper order filled");
    setAccount(result.account);
  }

  async function resetAccount() {
    const data = await resetPaperAccount();
    setAccount(data);
    setMessage("Paper account reset");
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 rounded-3xl border border-white/10 bg-[#070b1f] p-6 xl:flex-row xl:items-center">
        <div>
          <h2 className="text-2xl font-bold">Paper Trading</h2>
          <p className="mt-1 text-slate-400">
            Gerçek piyasa mantığıyla sanal bakiye üzerinden emir denemesi.
          </p>
        </div>

        <div className="flex gap-3">
          <button
            onClick={loadAccount}
            className="flex items-center gap-2 rounded-xl bg-white/10 px-5 py-3 font-bold hover:bg-white/20"
          >
            <RefreshCcw size={18} />
            Refresh
          </button>

          <button
            onClick={resetAccount}
            className="flex items-center gap-2 rounded-xl bg-red-500/20 px-5 py-3 font-bold text-red-300 hover:bg-red-500/30"
          >
            <RotateCcw size={18} />
            Reset
          </button>
        </div>
      </div>

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-4">
        <MetricCard label="Balance" value={`$${account?.balance ?? 0}`} />
        <MetricCard label="Equity" value={`$${account?.equity ?? 0}`} />
        <MetricCard
          label="Position Value"
          value={`$${account?.total_position_value ?? 0}`}
        />
        <MetricCard
          label="Unrealized PnL"
          value={`$${account?.unrealized_pnl ?? 0}`}
        />
      </section>

      <section className="grid grid-cols-1 gap-6 2xl:grid-cols-[420px_1fr]">
        <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
          <h3 className="mb-4 flex items-center gap-2 text-xl font-bold">
            <Wallet size={20} />
            Create Paper Order
          </h3>

          <div className="space-y-3">
            <input
              className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 uppercase outline-none focus:border-cyan-400"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              placeholder="BTCUSDT"
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
              placeholder="Price"
            />

            <input
              className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 outline-none focus:border-cyan-400"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              type="number"
              placeholder="Quantity"
            />

            <button
              onClick={submitOrder}
              className={`w-full rounded-xl py-3 font-bold text-black ${
                side === "BUY"
                  ? "bg-green-500 hover:bg-green-400"
                  : "bg-red-500 hover:bg-red-400"
              }`}
            >
              {side} Paper Order
            </button>

            {message && (
              <p className="rounded-xl border border-white/10 bg-white/5 p-3 text-sm text-slate-300">
                {message}
              </p>
            )}
          </div>
        </div>

        <div className="space-y-6">
          <TableCard title="Positions">
            <thead className="bg-white/5 text-slate-300">
              <tr>
                <th className="p-4">Symbol</th>
                <th className="p-4 text-right">Qty</th>
                <th className="p-4 text-right">Entry</th>
                <th className="p-4 text-right">Current</th>
                <th className="p-4 text-right">PnL</th>
              </tr>
            </thead>

            <tbody>
              {account?.positions.map((position) => (
                <tr key={position.symbol} className="border-t border-white/10">
                  <td className="p-4 font-bold">{position.symbol}</td>
                  <td className="p-4 text-right">{position.quantity}</td>
                  <td className="p-4 text-right">${position.entry_price}</td>
                  <td className="p-4 text-right">${position.current_price}</td>
                  <td
                    className={`p-4 text-right ${
                      position.unrealized_pnl >= 0
                        ? "text-green-400"
                        : "text-red-400"
                    }`}
                  >
                    ${position.unrealized_pnl}
                  </td>
                </tr>
              ))}

              {(!account || account.positions.length === 0) && (
                <tr>
                  <td colSpan={5} className="p-6 text-center text-slate-400">
                    Açık pozisyon yok.
                  </td>
                </tr>
              )}
            </tbody>
          </TableCard>

          <TableCard title="Orders">
            <thead className="bg-white/5 text-slate-300">
              <tr>
                <th className="p-4">ID</th>
                <th className="p-4">Symbol</th>
                <th className="p-4">Side</th>
                <th className="p-4 text-right">Price</th>
                <th className="p-4 text-right">Qty</th>
                <th className="p-4 text-right">Value</th>
              </tr>
            </thead>

            <tbody>
              {account?.orders.map((order) => (
                <tr key={order.id} className="border-t border-white/10">
                  <td className="p-4 text-slate-400">#{order.id}</td>
                  <td className="p-4 font-bold">{order.symbol}</td>
                  <td
                    className={`p-4 ${
                      order.side === "BUY" ? "text-green-400" : "text-red-400"
                    }`}
                  >
                    {order.side}
                  </td>
                  <td className="p-4 text-right">${order.price}</td>
                  <td className="p-4 text-right">{order.quantity}</td>
                  <td className="p-4 text-right">${order.value}</td>
                </tr>
              ))}

              {(!account || account.orders.length === 0) && (
                <tr>
                  <td colSpan={6} className="p-6 text-center text-slate-400">
                    Emir geçmişi yok.
                  </td>
                </tr>
              )}
            </tbody>
          </TableCard>
        </div>
      </section>
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

function TableCard({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="overflow-hidden rounded-3xl border border-white/10 bg-[#070b1f]">
      <h3 className="p-5 text-xl font-bold">{title}</h3>
      <table className="w-full text-left text-sm">{children}</table>
    </div>
  );
}