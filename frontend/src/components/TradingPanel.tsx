export default function TradingPanel() {
  return (
    <div className="rounded-3xl border border-white/10 bg-[#070b1f]/90 p-5 shadow-2xl shadow-black/30">
      <h3 className="mb-4 text-xl font-bold">Quick Trade</h3>

      <div className="mb-4 grid grid-cols-2 rounded-2xl bg-white/5 p-1">
        <button className="rounded-xl bg-green-500 py-2 font-bold text-black">
          Buy
        </button>
        <button className="rounded-xl py-2 font-bold text-slate-300">
          Sell
        </button>
      </div>

      <div className="space-y-3">
        <input
          className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 outline-none focus:border-cyan-400"
          placeholder="Price"
          defaultValue="67140"
        />

        <input
          className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 outline-none focus:border-cyan-400"
          placeholder="Amount"
          defaultValue="0.01"
        />

        <button className="w-full rounded-xl bg-cyan-500 py-3 font-bold text-black hover:bg-cyan-400">
          Simulate Order
        </button>

        <p className="text-xs text-slate-500">
          Demo paneldir. Gerçek emir gönderimi ileride API izinleriyle eklenecek.
        </p>
      </div>
    </div>
  );
}