export default function TradingViewWidget({ symbol = "BTCUSDT" }: { symbol?: string }) {
  const tvSymbol = buildTradingViewSymbol(symbol);

  return (
    <div className="h-[520px] w-full overflow-hidden rounded-2xl bg-black">
      <iframe
        key={tvSymbol}
        title={`TradingView ${tvSymbol}`}
        src={`https://www.tradingview.com/widgetembed/?symbol=${encodeURIComponent(
          tvSymbol
        )}&interval=15&theme=dark&style=1&timezone=Etc%2FUTC&withdateranges=1&hide_side_toolbar=0&allow_symbol_change=1&save_image=0&studies=[]`}
        className="h-full w-full border-0"
        allowFullScreen
      />
    </div>
  );
}

function buildTradingViewSymbol(symbol: string) {
  const clean = symbol.replace("/", "").replace("_", "").toUpperCase();

  if (clean.endsWith("USDT")) return `GATEIO:${clean}`;
  if (["AAPL", "TSLA", "NVDA"].includes(clean)) return `NASDAQ:${clean}`;
  if (["EURUSD", "GBPUSD", "USDTRY"].includes(clean)) return `FX:${clean}`;
  if (["XAUUSD", "XAGUSD"].includes(clean)) return `OANDA:${clean}`;

  return `GATEIO:${clean}`;
}