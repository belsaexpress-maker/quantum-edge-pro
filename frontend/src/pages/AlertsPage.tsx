import { useState } from "react";
import { Bell, Plus, ShieldCheck, Zap } from "lucide-react";

type AlertItem = {
  id: number;
  symbol: string;
  condition: "above" | "below";
  target: number;
  active: boolean;
};

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<AlertItem[]>([
    { id: 1, symbol: "BTC", condition: "above", target: 70000, active: true },
    { id: 2, symbol: "ETH", condition: "below", target: 3200, active: true },
  ]);

  const [symbol, setSymbol] = useState("BTC");
  const [condition, setCondition] = useState<"above" | "below">("above");
  const [target, setTarget] = useState("75000");

  function addAlert() {
    const newAlert: AlertItem = {
      id: Date.now(),
      symbol: symbol.toUpperCase(),
      condition,
      target: Number(target),
      active: true,
    };

    setAlerts([newAlert, ...alerts]);
  }

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
        <h2 className="text-2xl font-bold">Alerts</h2>
        <p className="mt-1 text-slate-400">
          Fiyat, sinyal ve haber bazlı akıllı alarm sistemi.
        </p>
      </div>

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <MetricCard icon={<Bell />} label="Active Alerts" value={alerts.length} />
        <MetricCard icon={<Zap />} label="Signal Alerts" value="Coming Soon" />
        <MetricCard icon={<ShieldCheck />} label="Risk Alerts" value="Enabled" />
      </section>

      <section className="grid grid-cols-1 gap-6 2xl:grid-cols-[420px_1fr]">
        <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
          <h3 className="mb-4 flex items-center gap-2 text-xl font-bold">
            <Plus size={20} />
            Create Alert
          </h3>

          <div className="space-y-3">
            <input
              className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 outline-none focus:border-cyan-400"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              placeholder="Symbol"
            />

            <select
              className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 outline-none focus:border-cyan-400"
              value={condition}
              onChange={(e) => setCondition(e.target.value as "above" | "below")}
            >
              <option value="above">Above</option>
              <option value="below">Below</option>
            </select>

            <input
              className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 outline-none focus:border-cyan-400"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              placeholder="Target Price"
              type="number"
            />

            <button
              onClick={addAlert}
              className="w-full rounded-xl bg-cyan-500 py-3 font-bold text-black hover:bg-cyan-400"
            >
              Add Alert
            </button>
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
          <h3 className="mb-4 text-xl font-bold">Alert List</h3>

          <div className="space-y-3">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 p-4"
              >
                <div>
                  <p className="font-bold">{alert.symbol}</p>
                  <p className="text-sm text-slate-400">
                    Price {alert.condition} ${alert.target.toLocaleString()}
                  </p>
                </div>

                <span className="rounded-full bg-green-500/10 px-3 py-1 text-sm text-green-300">
                  Active
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
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