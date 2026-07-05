export default function MarketTicker({ market }: { market: any }) {
  const crypto = market?.crypto || [];

  const btc = find(crypto, "BTCUSDT");
  const eth = find(crypto, "ETHUSDT");
  const bnb = find(crypto, "BNBUSDT");
  const sol = find(crypto, "SOLUSDT");

  const items = [btc, eth, bnb, sol].filter(Boolean);

  return (
    <div className="mb-5 overflow-hidden rounded-3xl border border-cyan-400/20 bg-[#070b1f] shadow-xl shadow-cyan-500/5">
      <div className="grid grid-cols-1 divide-y divide-cyan-400/10 md:grid-cols-4 md:divide-x md:divide-y-0">
        {items.map((item: any) => (
          <TickerItem key={item.symbol} item={item} />
        ))}

        {items.length === 0 && (
          <div className="p-5 text-sm text-slate-400">
            Canlı market verisi bekleniyor...
          </div>
        )}
      </div>
    </div>
  );
}

function TickerItem({ item }: { item: any }) {
  const positive = Number(item.change_24h || 0) >= 0;

  return (
    <div className="flex items-center justify-between gap-4 p-5">
      <div>
        <p className="font-bold text-white">{item.symbol}</p>
        <p className="text-xs text-slate-400">{item.name}</p>
      </div>

      <div className="text-right">
        <p className="font-bold text-white">${formatNumber(item.price)}</p>
        <p className={positive ? "text-sm text-green-400" : "text-sm text-red-400"}>
          {positive ? "▲" : "▼"} {Number(item.change_24h || 0).toFixed(2)}%
        </p>
      </div>
    </div>
  );
}

function find(list: any[], symbol: string) {
  return list.find((item) => item.symbol === symbol);
}

function formatNumber(value: number) {
  if (!value) return "0";
  if (Math.abs(value) < 0.01) return value.toFixed(8);
  if (Math.abs(value) < 1) return value.toFixed(6);

  return Number(value).toLocaleString(undefined, {
    maximumFractionDigits: 2,
  });
}