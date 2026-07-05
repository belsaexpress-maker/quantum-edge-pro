import { useEffect, useMemo, useState } from "react";
import {
  Bot,
  Brain,
  RefreshCcw,
  Search,
  ShieldAlert,
  Target,
  TrendingDown,
  TrendingUp,
} from "lucide-react";

import TradingViewWidget from "../components/TradingViewWidget";
import TradingPanel from "../components/TradingPanel";
import RecentTrades from "../components/RecentTrades";

import { getMarketOverview } from "../services/marketService";
import { getOrderBook } from "../services/orderBookService";
import { getPlaybook, getSmartMoney } from "../services/intelligenceService";

const PAGE_SIZE = 50;

export default function MarketsPage() {
  const [market, setMarket] = useState<any>(null);
  const [selectedSymbol, setSelectedSymbol] = useState("");
  const [filter, setFilter] = useState("crypto");
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("volume_desc");
  const [page, setPage] = useState(1);

  const [orderBook, setOrderBook] = useState<any>({ bids: [], asks: [] });
  const [playbook, setPlaybook] = useState<any>(null);
  const [smartMoney, setSmartMoney] = useState<any>(null);

  useEffect(() => {
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    setPage(1);
  }, [filter, search, sortBy]);

  async function load() {
    const data = await getMarketOverview();
    setMarket(data);

    setSelectedSymbol((current) => {
      if (current) return current;
      return data?.crypto?.[0]?.symbol || "";
    });
  }

  const allItems = useMemo(() => {
    if (!market) return [];

    const list =
      filter === "all"
        ? [
            ...(market.crypto || []),
            ...(market.stocks || []),
            ...(market.indices || []),
            ...(market.commodities || []),
            ...(market.forex || []),
          ]
        : market[filter] || [];

    const q = search.toLowerCase().trim();

    const filtered = list.filter((item: any) => {
      if (!q) return true;
      return (
        item.symbol?.toLowerCase().includes(q) ||
        item.name?.toLowerCase().includes(q)
      );
    });

    return sortItems(filtered, sortBy);
  }, [market, filter, search, sortBy]);

  const selected = useMemo(() => {
    if (!market) return null;

    const all = [
      ...(market.crypto || []),
      ...(market.stocks || []),
      ...(market.indices || []),
      ...(market.commodities || []),
      ...(market.forex || []),
    ];

    return (
      all.find((item: any) => item.symbol === selectedSymbol) ||
      market.crypto?.[0] ||
      all[0] ||
      null
    );
  }, [market, selectedSymbol]);

  useEffect(() => {
    if (!selected?.symbol) return;

    loadSelectedData(selected.symbol);

    const interval = setInterval(() => {
      loadSelectedData(selected.symbol);
    }, 5000);

    return () => clearInterval(interval);
  }, [selected?.symbol]);

  async function loadSelectedData(symbol: string) {
    try {
      const [book, pb, smc] = await Promise.all([
        getOrderBook(symbol, 20),
        getPlaybook(symbol),
        getSmartMoney(symbol),
      ]);

      setOrderBook(book);
      setPlaybook(pb);
      setSmartMoney(smc);
    } catch (error) {
      console.error(error);
    }
  }

  const totalPages = Math.max(1, Math.ceil(allItems.length / PAGE_SIZE));

  const pagedItems = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE;
    return allItems.slice(start, start + PAGE_SIZE);
  }, [allItems, page]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 rounded-3xl border border-white/10 bg-[#070b1f] p-6 xl:flex-row xl:items-center">
        <div>
          <h2 className="text-2xl font-bold">Markets</h2>
          <p className="mt-1 text-slate-400">
            Gate.io canlı pariteler, grafik, gerçek order book ve Quantum AI analiz paneli.
          </p>
        </div>

        <button
          onClick={load}
          className="flex items-center gap-2 rounded-xl bg-cyan-500 px-5 py-3 font-bold text-black"
        >
          <RefreshCcw size={18} />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 gap-6 2xl:grid-cols-[480px_1fr_390px]">
        <MarketList
          filter={filter}
          setFilter={setFilter}
          search={search}
          setSearch={setSearch}
          sortBy={sortBy}
          setSortBy={setSortBy}
          allItems={allItems}
          pagedItems={pagedItems}
          selectedSymbol={selectedSymbol}
          setSelectedSymbol={setSelectedSymbol}
          page={page}
          setPage={setPage}
          totalPages={totalPages}
        />

        <section className="space-y-6">
          {selected && (
            <>
              <MarketHeader selected={selected} filter={filter} />

              <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-5">
                <div className="mb-4 flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-bold">TradingView Chart</h3>
                    <p className="text-sm text-slate-400">
                      {selected.symbol} canlı grafik
                    </p>
                  </div>

                  <span className="rounded-full bg-green-500/10 px-3 py-1 text-sm text-green-400">
                    Live
                  </span>
                </div>

                <TradingViewWidget symbol={selected.symbol} />
              </div>

              <div className="grid grid-cols-1 gap-6 2xl:grid-cols-2">
                <DepthPanel selected={selected} orderBook={orderBook} />
                <TradingPanel symbol={selected.symbol} />
              </div>

              <RecentTrades symbol={selected.symbol} />
            </>
          )}
        </section>

        <QuantumAIPanel
          selected={selected}
          playbook={playbook}
          smartMoney={smartMoney}
        />
      </div>
    </div>
  );
}

function MarketList({
  filter,
  setFilter,
  search,
  setSearch,
  sortBy,
  setSortBy,
  allItems,
  pagedItems,
  selectedSymbol,
  setSelectedSymbol,
  page,
  setPage,
  totalPages,
}: any) {
  return (
    <section className="rounded-3xl border border-white/10 bg-[#070b1f] p-5">
      <div className="mb-4 flex items-center gap-3 rounded-xl border border-white/10 bg-white/5 px-4 py-3">
        <Search size={18} className="text-slate-400" />
        <input
          className="w-full bg-transparent outline-none placeholder:text-slate-500"
          placeholder="BTCUSDT, ETHUSDT, SOL..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="mb-4 flex flex-wrap gap-2">
        {[
          ["all", "All"],
          ["crypto", "Crypto"],
          ["stocks", "Stocks"],
          ["indices", "Indices"],
          ["commodities", "Commodities"],
          ["forex", "Forex"],
        ].map(([key, label]) => (
          <button
            key={key}
            onClick={() => setFilter(key)}
            className={`rounded-xl px-4 py-2 text-sm ${
              filter === key
                ? "bg-cyan-500 text-black"
                : "bg-white/5 text-slate-300 hover:bg-white/10"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="mb-4 grid grid-cols-2 gap-2">
        <select
          className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm outline-none"
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
        >
          <option value="volume_desc">Volume ↓</option>
          <option value="volume_asc">Volume ↑</option>
          <option value="change_desc">24h % ↓</option>
          <option value="change_asc">24h % ↑</option>
          <option value="price_desc">Price ↓</option>
          <option value="price_asc">Price ↑</option>
          <option value="symbol_asc">Symbol A-Z</option>
        </select>

        <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-300">
          {allItems.length.toLocaleString()} parite
        </div>
      </div>

      <div className="max-h-[760px] overflow-auto">
        <table className="w-full text-left text-sm">
          <thead className="sticky top-0 bg-[#070b1f] text-slate-400">
            <tr>
              <th className="p-3">Symbol</th>
              <th className="p-3 text-right">Price</th>
              <th className="p-3 text-right">24h</th>
            </tr>
          </thead>

          <tbody>
            {pagedItems.map((item: any) => (
              <tr
                key={`${item.symbol}-${item.asset_type}`}
                onClick={() => setSelectedSymbol(item.symbol)}
                className={`cursor-pointer border-t border-white/10 hover:bg-white/5 ${
                  selectedSymbol === item.symbol ? "bg-cyan-500/10" : ""
                }`}
              >
                <td className="p-3">
                  <p className="font-bold">{item.symbol}</p>
                  <p className="text-xs text-slate-500">{item.name}</p>
                </td>

                <td className="p-3 text-right">
                  ${formatNumber(item.price)}
                </td>

                <td
                  className={`p-3 text-right ${
                    Number(item.change_24h || 0) >= 0
                      ? "text-green-400"
                      : "text-red-400"
                  }`}
                >
                  {Number(item.change_24h || 0).toFixed(2)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 flex items-center justify-between gap-3">
        <button
          disabled={page <= 1}
          onClick={() => setPage((p: number) => Math.max(1, p - 1))}
          className="rounded-xl bg-white/5 px-4 py-2 text-sm disabled:opacity-40"
        >
          Önceki
        </button>

        <span className="text-sm text-slate-400">
          {page} / {totalPages}
        </span>

        <button
          disabled={page >= totalPages}
          onClick={() => setPage((p: number) => Math.min(totalPages, p + 1))}
          className="rounded-xl bg-white/5 px-4 py-2 text-sm disabled:opacity-40"
        >
          Sonraki
        </button>
      </div>
    </section>
  );
}

function MarketHeader({ selected, filter }: { selected: any; filter: string }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
      <div className="flex flex-col justify-between gap-4 xl:flex-row xl:items-center">
        <div>
          <h3 className="text-2xl font-bold">{selected.symbol}</h3>
          <p className="text-slate-400">{selected.name}</p>
        </div>

        <div className="flex flex-wrap gap-3">
          <Mini label="Price" value={`$${formatNumber(selected.price)}`} />
          <Mini
            label="24h"
            value={`${Number(selected.change_24h || 0).toFixed(2)}%`}
            danger={Number(selected.change_24h || 0) < 0}
          />
          <Mini
            label="Volume"
            value={`$${formatCompact(selected.volume_24h || selected.volume || 0)}`}
          />
          <Mini label="Type" value={selected.asset_type || filter} />
        </div>
      </div>
    </div>
  );
}

function QuantumAIPanel({
  selected,
  playbook,
  smartMoney,
}: {
  selected: any;
  playbook: any;
  smartMoney: any;
}) {
  if (!selected) {
    return (
      <aside className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
        <p className="text-slate-400">Bir parite seç.</p>
      </aside>
    );
  }

  const signal = playbook?.signal || "WAIT";
  const aiScore = playbook?.ai_score || 0;
  const smcScore = playbook?.smart_money_score || smartMoney?.smart_money_score || 0;
  const confidence = playbook?.confidence || 0;
  const rr = playbook?.risk_reward || 0;

  return (
    <aside className="space-y-6">
      <section className="rounded-3xl border border-cyan-400/20 bg-[#070b1f] p-6">
        <div className="mb-4 flex items-center gap-2">
          <Brain className="text-cyan-300" size={22} />
          <h3 className="text-xl font-bold">Quantum AI</h3>
        </div>

        <div className="rounded-3xl border border-white/10 bg-white/5 p-5 text-center">
          <p className="text-sm text-slate-400">AI Score</p>
          <p className="mt-2 text-5xl font-black text-cyan-300">
            {aiScore}
          </p>
          <p className="mt-2 text-sm text-slate-400">/100</p>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-3">
          <Mini label="Signal" value={signal} />
          <Mini label="SMC" value={`${smcScore}/100`} />
          <Mini label="Confidence" value={`${confidence}%`} />
          <Mini label="R/R" value={rr} />
        </div>
      </section>

      <section className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
        <div className="mb-4 flex items-center gap-2">
          <Target className="text-green-300" size={20} />
          <h3 className="text-xl font-bold">Trade Setup</h3>
        </div>

        {playbook?.error ? (
          <p className="text-sm text-red-300">{playbook.error}</p>
        ) : (
          <div className="grid grid-cols-2 gap-3">
            <Mini label="Entry Low" value={`$${formatNumber(playbook?.entry_zone?.low)}`} />
            <Mini label="Entry High" value={`$${formatNumber(playbook?.entry_zone?.high)}`} />
            <Mini label="TP1" value={`$${formatNumber(playbook?.take_profit?.tp1)}`} />
            <Mini label="TP2" value={`$${formatNumber(playbook?.take_profit?.tp2)}`} />
            <Mini label="TP3" value={`$${formatNumber(playbook?.take_profit?.tp3)}`} />
            <Mini label="Stop Loss" value={`$${formatNumber(playbook?.stop_loss)}`} danger />
          </div>
        )}
      </section>

      <section className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
        <div className="mb-4 flex items-center gap-2">
          <ShieldAlert className="text-yellow-300" size={20} />
          <h3 className="text-xl font-bold">Smart Money</h3>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <Mini label="Structure" value={smartMoney?.market_structure || "-"} />
          <Mini label="Decision" value={smartMoney?.decision || "-"} />
          <Mini label="Order Block" value={smartMoney?.order_block?.status || "-"} />
          <Mini label="FVG" value={smartMoney?.fair_value_gap?.status || "-"} />
          <Mini label="BOS" value={smartMoney?.bos ? "YES" : "NO"} />
          <Mini label="CHOCH" value={smartMoney?.choch ? "YES" : "NO"} />
        </div>
      </section>

      <section className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
        <div className="mb-4 flex items-center gap-2">
          <Bot className="text-cyan-300" size={20} />
          <h3 className="text-xl font-bold">Bot Recommendation</h3>
        </div>

        <p className="text-sm text-slate-400">
          {getBotRecommendation(signal, aiScore)}
        </p>

        <button className="mt-4 w-full rounded-xl bg-cyan-500 px-4 py-3 font-bold text-black hover:bg-cyan-400">
          Start Quantum Bot
        </button>
      </section>
    </aside>
  );
}

function DepthPanel({ selected, orderBook }: { selected: any; orderBook: any }) {
  const asks = orderBook?.asks || [];
  const bids = orderBook?.bids || [];

  return (
    <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-5">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold">Real Order Book</h3>
          <p className="text-sm text-slate-400">
            {selected?.symbol} Gate.io canlı alış / satış derinliği
          </p>
        </div>

        <span className="rounded-full bg-green-500/10 px-3 py-1 text-sm text-green-400">
          Live
        </span>
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <div>
          <div className="mb-2 flex items-center gap-2 font-bold text-red-400">
            <TrendingDown size={18} />
            Sell Depth
          </div>

          <DepthTable rows={asks} side="sell" />
        </div>

        <div>
          <div className="mb-2 flex items-center gap-2 font-bold text-green-400">
            <TrendingUp size={18} />
            Buy Depth
          </div>

          <DepthTable rows={bids} side="buy" />
        </div>
      </div>
    </div>
  );
}

function DepthTable({
  rows,
  side,
}: {
  rows: { price: number; quantity: number; total: number }[];
  side: "buy" | "sell";
}) {
  return (
    <table className="w-full text-sm">
      <thead className="text-slate-400">
        <tr>
          <th className="py-2 text-left">Price</th>
          <th className="py-2 text-right">Qty</th>
          <th className="py-2 text-right">Total</th>
        </tr>
      </thead>

      <tbody>
        {rows.map((row, i) => (
          <tr key={i} className="border-t border-white/10">
            <td className={`py-2 ${side === "buy" ? "text-green-400" : "text-red-400"}`}>
              {formatNumber(row.price)}
            </td>
            <td className="py-2 text-right">
              {Number(row.quantity || 0).toFixed(6)}
            </td>
            <td className="py-2 text-right">
              ${Number(row.total || 0).toFixed(2)}
            </td>
          </tr>
        ))}

        {rows.length === 0 && (
          <tr>
            <td colSpan={3} className="py-8 text-center text-slate-500">
              Derinlik bekleniyor...
            </td>
          </tr>
        )}
      </tbody>
    </table>
  );
}

function Mini({
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
        {value || "-"}
      </p>
    </div>
  );
}

function getBotRecommendation(signal: string, score: number) {
  if (score >= 90 && signal.includes("LONG")) {
    return "QuantumEdge Pro Spot 1 veya Futures 1 için güçlü aday.";
  }

  if (score >= 75) {
    return "QuantumEdge Pro Spot 2 veya scalping bot için uygun aday.";
  }

  if (score >= 60) {
    return "İzleme modunda tutulabilir. Bot açmadan önce onay bekle.";
  }

  return "Şu an bot için uygun değil. Bekle.";
}

function sortItems(items: any[], sortBy: string) {
  const list = [...items];

  if (sortBy === "volume_desc") return list.sort((a, b) => Number(b.volume_24h || 0) - Number(a.volume_24h || 0));
  if (sortBy === "volume_asc") return list.sort((a, b) => Number(a.volume_24h || 0) - Number(b.volume_24h || 0));
  if (sortBy === "change_desc") return list.sort((a, b) => Number(b.change_24h || 0) - Number(a.change_24h || 0));
  if (sortBy === "change_asc") return list.sort((a, b) => Number(a.change_24h || 0) - Number(b.change_24h || 0));
  if (sortBy === "price_desc") return list.sort((a, b) => Number(b.price || 0) - Number(a.price || 0));
  if (sortBy === "price_asc") return list.sort((a, b) => Number(a.price || 0) - Number(b.price || 0));
  if (sortBy === "symbol_asc") return list.sort((a, b) => String(a.symbol).localeCompare(String(b.symbol)));

  return list;
}

function formatNumber(value: number) {
  if (!value) return "0";
  if (Math.abs(value) < 0.01) return value.toFixed(8);
  if (Math.abs(value) < 1) return value.toFixed(6);
  return value.toLocaleString();
}

function formatCompact(value: number) {
  return Number(value || 0).toLocaleString(undefined, {
    notation: "compact",
    maximumFractionDigits: 2,
  });
}