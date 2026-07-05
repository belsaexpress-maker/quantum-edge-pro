import {
  Bell,
  Bot,
  Brain,
  BookOpen,
  LayoutDashboard,
  LineChart,
  LogIn,
  LogOut,
  Newspaper,
  ScanSearch,
  Settings,
  Shield,
  Sparkles,
  Target,
  TerminalSquare,
  Wallet,
  WalletCards,
} from "lucide-react";

export type Page =
  | "dashboard"
  | "markets"
  | "portfolio"
  | "ai"
  | "playbook"
  | "scanner"
  | "opportunities"
  | "intelligence"
  | "paper"
  | "trading"
  | "bots"
  | "quantum_pro"
  | "news"
  | "alerts"
  | "login";

function MenuItem({
  icon,
  label,
  active = false,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  active?: boolean;
  onClick?: () => void;
}) {
  return (
    <div
      onClick={onClick}
      className={`flex cursor-pointer items-center gap-3 rounded-xl px-4 py-3 text-sm transition ${
        active
          ? "bg-cyan-500 text-black"
          : "text-slate-300 hover:bg-white/10 hover:text-white"
      }`}
    >
      {icon}
      {label}
    </div>
  );
}

export default function Sidebar({
  currentPage,
  onPageChange,
  onLogout,
  user,
  isLoggedIn,
}: {
  currentPage: Page;
  onPageChange: (page: Page) => void;
  onLogout: () => void;
  user: any;
  isLoggedIn: boolean;
}) {
  return (
    <aside className="w-72 min-h-screen border-r border-white/10 bg-[#070b1f] p-5">
      <div className="mb-10">
        <h1 className="text-2xl font-bold tracking-wide">Quantum Edge</h1>
        <p className="text-sm text-slate-400">Ultimate Trading Platform</p>
      </div>

      <nav className="space-y-2">
        <MenuItem icon={<LayoutDashboard size={18} />} label="Dashboard" active={currentPage === "dashboard"} onClick={() => onPageChange("dashboard")} />
        <MenuItem icon={<LineChart size={18} />} label="Markets" active={currentPage === "markets"} onClick={() => onPageChange("markets")} />
        <MenuItem icon={<Wallet size={18} />} label="Portfolio" active={currentPage === "portfolio"} onClick={() => onPageChange("portfolio")} />
        <MenuItem icon={<Brain size={18} />} label="AI Signals" active={currentPage === "ai"} onClick={() => onPageChange("ai")} />
        <MenuItem icon={<BookOpen size={18} />} label="AI Playbook" active={currentPage === "playbook"} onClick={() => onPageChange("playbook")} />
        <MenuItem icon={<ScanSearch size={18} />} label="AI Scanner" active={currentPage === "scanner"} onClick={() => onPageChange("scanner")} />
        <MenuItem icon={<Target size={18} />} label="Opportunities" active={currentPage === "opportunities"} onClick={() => onPageChange("opportunities")} />
        <MenuItem icon={<Sparkles size={18} />} label="Market Intelligence" active={currentPage === "intelligence"} onClick={() => onPageChange("intelligence")} />
        <MenuItem icon={<WalletCards size={18} />} label="Paper Trading" active={currentPage === "paper"} onClick={() => onPageChange("paper")} />
        <MenuItem icon={<TerminalSquare size={18} />} label="Trading Console" active={currentPage === "trading"} onClick={() => onPageChange("trading")} />
        <MenuItem icon={<Bot size={18} />} label="Bots" active={currentPage === "bots"} onClick={() => onPageChange("bots")} />
        <MenuItem icon={<Shield size={18} />} label="Quantum Pro Bots" active={currentPage === "quantum_pro"} onClick={() => onPageChange("quantum_pro")} />
        <MenuItem icon={<Newspaper size={18} />} label="News" active={currentPage === "news"} onClick={() => onPageChange("news")} />
        <MenuItem icon={<Bell size={18} />} label="Alerts" active={currentPage === "alerts"} onClick={() => onPageChange("alerts")} />
        <MenuItem icon={<Settings size={18} />} label="Settings" />
      </nav>

      <div className="mt-10 rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-4">
        <p className="text-sm text-cyan-300">
          {isLoggedIn ? "Logged in" : "Guest Mode"}
        </p>

        <h3 className="mt-1 font-semibold">
          {isLoggedIn ? user?.email : "Arayüz herkese açık"}
        </h3>

        <p className="mt-2 text-xs text-slate-400">
          Bot işlemleri ve gerçek emirler için giriş gerekir.
        </p>
      </div>

      {isLoggedIn ? (
        <button
          onClick={onLogout}
          className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl border border-red-400/20 bg-red-500/10 px-4 py-3 text-sm text-red-300 hover:bg-red-500/20"
        >
          <LogOut size={18} />
          Çıkış Yap
        </button>
      ) : (
        <button
          onClick={() => onPageChange("login")}
          className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl border border-cyan-400/20 bg-cyan-500 px-4 py-3 text-sm font-bold text-black hover:bg-cyan-400"
        >
          <LogIn size={18} />
          Giriş Yap
        </button>
      )}
    </aside>
  );
}