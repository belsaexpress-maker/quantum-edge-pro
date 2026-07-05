import { useEffect, useState } from "react";

import BrandHeader from "./components/BrandHeader";
import MarketTicker from "./components/MarketTicker";

import MarketCard from "./components/MarketCard";
import NewsPanel from "./components/NewsPanel";
import OrderBook from "./components/OrderBook";
import RecentTrades from "./components/RecentTrades";
import Sidebar, { type Page } from "./components/Sidebar";
import SignalPanel from "./components/SignalPanel";
import TradingPanel from "./components/TradingPanel";
import TradingViewWidget from "./components/TradingViewWidget";

import LoginPage from "./pages/LoginPage";
import AISignalsPage from "./pages/AISignalsPage";
import AIPlaybookPage from "./pages/AIPlaybookPage";
import AIScannerPage from "./pages/AIScannerPage";
import AlertsPage from "./pages/AlertsPage";
import BotsPage from "./pages/BotsPage";
import IntelligencePage from "./pages/IntelligencePage";
import MarketsPage from "./pages/MarketsPage";
import NewsPage from "./pages/NewsPage";
import OpportunitiesPage from "./pages/OpportunitiesPage";
import PaperTradingPage from "./pages/PaperTradingPage";
import PortfolioPage from "./pages/PortfolioPage";
import QuantumProBotsPage from "./pages/QuantumProBotsPage";
import TradingConsolePage from "./pages/TradingConsolePage";

import { getLatestNews, getMarketOverview } from "./services/marketService";
import { getToken, getUser, logout } from "./services/authService";
import type { MarketOverview } from "./types/market";

function App() {
  const [currentPage, setCurrentPage] = useState<Page>("dashboard");
  const [market, setMarket] = useState<MarketOverview | null>(null);
  const [news, setNews] = useState<any[]>([]);
  const [user, setUser] = useState<any>(getUser());

  const isLoggedIn = Boolean(getToken());

  useEffect(() => {
    loadData();

    const interval = setInterval(() => {
      loadData();
    }, 8000);

    return () => clearInterval(interval);
  }, []);

  async function loadData() {
    try {
      const marketData = await getMarketOverview();
      setMarket(marketData);

      try {
        const newsData = await getLatestNews();
        setNews(newsData);
      } catch {
        setNews([]);
      }
    } catch (error) {
      console.error("Load data error:", error);
    }
  }

  function handleLogout() {
    logout();
    setUser(null);
    setCurrentPage("dashboard");
  }

  function handleLoginSuccess() {
    setUser(getUser());
    setCurrentPage("dashboard");
  }

  const crypto = market?.crypto || [];
  const stocks = market?.stocks || [];
  const indices = market?.indices || [];
  const forex = market?.forex || [];
  const commodities = market?.commodities || [];

  return (
    <div className="min-h-screen w-full bg-[#050816] text-white">
      <div className="quantum-page-bg flex min-h-screen w-full">
        <Sidebar
          currentPage={currentPage}
          onPageChange={setCurrentPage}
          onLogout={handleLogout}
          user={user}
          isLoggedIn={isLoggedIn}
        />

        <main className="min-w-0 flex-1 overflow-x-hidden p-6">
          <div className="mx-auto max-w-[1800px]">
            <BrandHeader
              onRefresh={loadData}
              user={user}
              isLoggedIn={isLoggedIn}
            />

            <MarketTicker market={market} />

            {currentPage === "login" && (
              <LoginPage onLogin={handleLoginSuccess} />
            )}

            {currentPage === "dashboard" && (
              <>
                <section className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-5">
                  {crypto.slice(0, 3).map((item) => (
                    <MarketCard key={item.symbol} item={item} />
                  ))}

                  {indices.slice(0, 1).map((item) => (
                    <MarketCard key={item.symbol} item={item} />
                  ))}

                  {stocks.slice(0, 1).map((item) => (
                    <MarketCard key={item.symbol} item={item} />
                  ))}
                </section>

                <section className="grid grid-cols-1 gap-6 2xl:grid-cols-[1fr_420px]">
                  <div className="rounded-3xl border border-cyan-400/20 bg-[#070b1f]/90 p-5 shadow-2xl shadow-cyan-500/5 backdrop-blur">
                    <div className="mb-4 flex items-center justify-between">
                      <div>
                        <h3 className="text-xl font-bold">Market Overview</h3>
                        <p className="text-sm text-slate-400">
                          BTC/USDT canlı grafik
                        </p>
                      </div>

                      <span className="rounded-full bg-green-500/10 px-3 py-1 text-sm text-green-400">
                        Live
                      </span>
                    </div>

                    <TradingViewWidget symbol="BTCUSDT" />
                  </div>

                  <div className="space-y-6">
                    <OrderBook symbol="BTCUSDT" />
                    <RecentTrades symbol="BTCUSDT" />
                  </div>
                </section>

                <section className="mt-6 grid grid-cols-1 gap-6 2xl:grid-cols-[1fr_420px]">
                  <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
                    <NewsPanel news={news} />

                    <div className="rounded-3xl border border-cyan-400/20 bg-[#070b1f]/90 p-5 shadow-2xl shadow-cyan-500/5 backdrop-blur">
                      <h3 className="mb-4 text-xl font-bold">
                        World Markets
                      </h3>

                      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                        {[...forex, ...commodities].map((item) => (
                          <div
                            key={item.symbol}
                            className="rounded-2xl border border-white/10 bg-white/5 p-4"
                          >
                            <div className="flex justify-between gap-3">
                              <strong>{item.symbol}</strong>
                              <span className="text-slate-400">
                                {item.asset_type}
                              </span>
                            </div>

                            <p className="mt-2 text-sm text-slate-400">
                              {item.name}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="space-y-6">
                    <SignalPanel items={crypto} />
                    <TradingPanel symbol="BTCUSDT" />
                  </div>
                </section>
              </>
            )}

            {currentPage === "markets" && <MarketsPage />}
            {currentPage === "portfolio" && <PortfolioPage />}
            {currentPage === "ai" && <AISignalsPage />}
            {currentPage === "playbook" && <AIPlaybookPage />}
            {currentPage === "scanner" && <AIScannerPage />}
            {currentPage === "opportunities" && <OpportunitiesPage />}
            {currentPage === "intelligence" && <IntelligencePage />}
            {currentPage === "paper" && <PaperTradingPage />}
            {currentPage === "trading" && <TradingConsolePage />}
            {currentPage === "bots" && <BotsPage />}
            {currentPage === "quantum_pro" && <QuantumProBotsPage />}
            {currentPage === "news" && <NewsPage />}
            {currentPage === "alerts" && <AlertsPage />}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;