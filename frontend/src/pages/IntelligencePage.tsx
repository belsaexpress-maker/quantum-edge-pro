import { useState } from "react";
import { Brain, RefreshCcw } from "lucide-react";
import { getPlaybook, getSmartMoney } from "../services/intelligenceService";

export default function IntelligencePage() {
  const [symbol, setSymbol] = useState("BTCUSDT");
  const [smc, setSmc] = useState<any>(null);
  const [playbook, setPlaybook] = useState<any>(null);

  async function analyze() {
    const smcData = await getSmartMoney(symbol);
    const playbookData = await getPlaybook(symbol);

    setSmc(smcData);
    setPlaybook(playbookData);
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 rounded-3xl border border-white/10 bg-[#070b1f] p-6 xl:flex-row xl:items-center">
        <div>
          <h2 className="text-2xl font-bold">Market Intelligence</h2>
          <p className="text-slate-400">Smart Money + AI Playbook analiz merkezi.</p>
        </div>

        <div className="flex gap-3">
          <input
            className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 uppercase"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          />

          <button onClick={analyze} className="flex items-center gap-2 rounded-xl bg-cyan-500 px-5 py-3 font-bold text-black">
            <RefreshCcw size={18} />
            Analyze
          </button>
        </div>
      </div>

      {!playbook && (
        <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-10 text-center text-slate-400">
          Analiz için coin seçip Analyze butonuna bas.
        </div>
      )}

      {playbook && (
        <>
          <section className="grid grid-cols-1 gap-4 xl:grid-cols-5">
            <Metric label="Signal" value={playbook.signal} />
            <Metric label="AI Score" value={playbook.ai_score} />
            <Metric label="SMC Score" value={playbook.smart_money_score} />
            <Metric label="Confidence" value={playbook.confidence} />
            <Metric label="RR" value={playbook.risk_reward} />
          </section>

          <section className="grid grid-cols-1 gap-6 xl:grid-cols-2">
            <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
              <h3 className="mb-4 flex items-center gap-2 text-xl font-bold">
                <Brain size={20} />
                Playbook
              </h3>

              <div className="grid grid-cols-2 gap-3">
                <Small label="Entry Low" value={`$${playbook.entry_zone.low}`} />
                <Small label="Entry High" value={`$${playbook.entry_zone.high}`} />
                <Small label="Stop Loss" value={`$${playbook.stop_loss}`} danger />
                <Small label="TP1" value={`$${playbook.take_profit.tp1}`} />
                <Small label="TP2" value={`$${playbook.take_profit.tp2}`} />
                <Small label="TP3" value={`$${playbook.take_profit.tp3}`} />
              </div>

              <div className="mt-4 rounded-xl border border-white/10 bg-white/5 p-4">
                {playbook.reasons.map((r: string, i: number) => (
                  <p key={i} className="text-sm text-slate-300">✓ {r}</p>
                ))}
              </div>
            </div>

            {smc && (
              <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
                <h3 className="mb-4 text-xl font-bold">Smart Money Concepts</h3>

                <div className="grid grid-cols-2 gap-3">
                  <Small label="Structure" value={smc.market_structure} />
                  <Small label="Decision" value={smc.decision} />
                  <Small label="Order Block" value={smc.order_block.status} />
                  <Small label="FVG" value={smc.fair_value_gap.status} />
                  <Small label="BOS" value={smc.bos ? "YES" : "NO"} />
                  <Small label="CHOCH" value={smc.choch ? "YES" : "NO"} />
                  <Small label="Support" value={`$${smc.support}`} />
                  <Small label="Resistance" value={`$${smc.resistance}`} />
                </div>
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-5">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-2 text-2xl font-bold">{value}</p>
    </div>
  );
}

function Small({
  label,
  value,
  danger = false,
}: {
  label: string;
  value: string | number;
  danger?: boolean;
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-3">
      <p className="text-xs text-slate-400">{label}</p>
      <p className={`mt-1 font-bold ${danger ? "text-red-400" : "text-green-400"}`}>
        {value}
      </p>
    </div>
  );
}