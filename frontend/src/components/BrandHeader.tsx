
import { Bot, Brain, ChevronDown, RefreshCcw, Radio, ShieldCheck, UserCircle } from "lucide-react";

export default function BrandHeader({
  onRefresh,
  user,
  isLoggedIn,
}: {
  onRefresh?: () => void;
  user?: any;
  isLoggedIn?: boolean;
}) {
  return (
    <div className="relative mb-5 overflow-hidden rounded-3xl border border-cyan-400/20 bg-[#050816] p-6 shadow-2xl shadow-cyan-500/10">
      <div className="absolute inset-0 opacity-40">
        <div className="quantum-grid-bg" />
      </div>

      <div className="relative z-10 flex flex-col gap-6 xl:flex-row xl:items-center xl:justify-between">
        <div className="flex items-center gap-5">
          <div className="relative flex h-28 w-28 items-center justify-center">
            <div className="absolute h-24 w-24 rounded-full border-[10px] border-[#f6c453] shadow-[0_0_35px_rgba(246,196,83,0.45)]" />
            <div className="absolute h-20 w-20 rounded-full border-r-[10px] border-b-[10px] border-cyan-400 shadow-[0_0_30px_rgba(0,170,255,0.6)]" />
            <div className="absolute h-1 w-32 rotate-[-38deg] rounded-full bg-cyan-400 shadow-[0_0_25px_rgba(0,170,255,1)]" />
            <div className="z-10 text-4xl font-black text-white">Q</div>
          </div>

          <div>
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="quantum-logo-text text-4xl font-black tracking-wider md:text-6xl">
                QUANTUM
              </h1>

              <span className="rounded-xl border border-cyan-400/60 bg-cyan-500/10 px-3 py-1 text-2xl font-black text-cyan-300 shadow-[0_0_20px_rgba(0,170,255,0.5)]">
                PRO
              </span>
            </div>

            <h2 className="quantum-gold-text mt-[-4px] text-4xl font-black tracking-[0.18em] md:text-6xl">
              EDGE
            </h2>

            <p className="mt-2 tracking-[0.45em] text-slate-300">
              AI <span className="text-cyan-400">•</span> TRADING{" "}
              <span className="text-cyan-400">•</span> INTELLIGENCE
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-3 md:grid-cols-3 xl:min-w-[520px]">
          <StatusBox
            icon={<Radio size={24} />}
            title="GATE.IO"
            value="LIVE"
            color="green"
          />

          <StatusBox
            icon={<Brain size={24} />}
            title="AI ENGINE"
            value="ACTIVE"
            color="green"
          />

          <StatusBox
            icon={<Bot size={24} />}
            title="BOT ENGINE"
            value="READY"
            color="green"
          />
        </div>
      </div>

      <div className="relative z-10 mt-5 flex flex-col justify-between gap-3 border-t border-cyan-400/20 pt-4 md:flex-row md:items-center">
        <div className="flex flex-wrap items-center gap-3 text-sm">
          <Badge icon={<ShieldCheck size={16} />} text="Risk Control Active" />
          <Badge icon={<Brain size={16} />} text="Quantum AI Online" />
          <Badge icon={<Radio size={16} />} text="Real-Time Market Data" />
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={onRefresh}
            className="flex items-center gap-2 rounded-xl border border-cyan-400/30 bg-cyan-500/10 px-4 py-2 text-sm font-bold text-cyan-300 hover:bg-cyan-500/20"
          >
            <RefreshCcw size={16} />
            Refresh
          </button>

          <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-2">
            <UserCircle size={22} className="text-cyan-300" />
            <div>
              <p className="text-xs text-slate-400">
                {isLoggedIn ? "PRO ACCOUNT" : "GUEST MODE"}
              </p>
              <p className="text-sm font-bold">
                {isLoggedIn ? user?.email || "Quantum Edge" : "Quantum Edge"}
              </p>
            </div>
            <ChevronDown size={16} className="text-slate-400" />
          </div>
        </div>
      </div>
    </div>
  );
}

function StatusBox({
  icon,
  title,
  value,
}: {
  icon: React.ReactNode;
  title: string;
  value: string;
  color: "green";
}) {
  return (
    <div className="rounded-2xl border border-cyan-400/20 bg-white/[0.03] p-4 shadow-[0_0_25px_rgba(0,170,255,0.08)]">
      <div className="flex items-center gap-3">
        <div className="text-cyan-300">{icon}</div>
        <div>
          <p className="text-sm font-bold text-white">{title}</p>
          <p className="mt-1 text-xs font-bold text-green-400">● {value}</p>
        </div>
      </div>
    </div>
  );
}

function Badge({ icon, text }: { icon: React.ReactNode; text: string }) {
  return (
    <span className="flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-cyan-200">
      {icon}
      {text}
    </span>
  );
}