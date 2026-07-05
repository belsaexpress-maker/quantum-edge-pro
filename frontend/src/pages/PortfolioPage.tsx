import { useEffect, useState } from "react";
import {
  addPortfolioAsset,
  getPortfolio,
  getPortfolioSummary,
} from "../services/portfolioService";
import type { PortfolioAsset, PortfolioSummary } from "../types/portfolio";

export default function PortfolioPage() {
  const [assets, setAssets] = useState<PortfolioAsset[]>([]);
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);

  const [symbol, setSymbol] = useState("BTC");
  const [assetType, setAssetType] = useState("crypto");
  const [quantity, setQuantity] = useState("0.1");
  const [buyPrice, setBuyPrice] = useState("50000");

  useEffect(() => {
    loadPortfolio();
  }, []);

  async function loadPortfolio() {
    const portfolioData = await getPortfolio();
    const summaryData = await getPortfolioSummary();

    setAssets(portfolioData);
    setSummary(summaryData);
  }

  async function handleAdd() {
    await addPortfolioAsset({
      symbol,
      asset_type: assetType,
      quantity: Number(quantity),
      buy_price: Number(buyPrice),
    });

    await loadPortfolio();
  }

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
        <h2 className="text-2xl font-bold">Portfolio</h2>
        <p className="mt-1 text-slate-400">
          Varlıklarını takip et, maliyetini gör ve portföyünü yönet.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-6">
          <h3 className="mb-4 text-xl font-bold">Add Asset</h3>

          <div className="space-y-3">
            <input
              className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 outline-none focus:border-cyan-400"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              placeholder="Symbol"
            />

            <select
              className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 outline-none focus:border-cyan-400"
              value={assetType}
              onChange={(e) => setAssetType(e.target.value)}
            >
              <option value="crypto">Crypto</option>
              <option value="stock">Stock</option>
              <option value="forex">Forex</option>
              <option value="commodity">Commodity</option>
              <option value="index">Index</option>
            </select>

            <input
              className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 outline-none focus:border-cyan-400"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              placeholder="Quantity"
              type="number"
            />

            <input
              className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 outline-none focus:border-cyan-400"
              value={buyPrice}
              onChange={(e) => setBuyPrice(e.target.value)}
              placeholder="Buy Price"
              type="number"
            />

            <button
              onClick={handleAdd}
              className="w-full rounded-xl bg-cyan-500 py-3 font-bold text-black hover:bg-cyan-400"
            >
              Add to Portfolio
            </button>
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-6 xl:col-span-2">
          <h3 className="mb-4 text-xl font-bold">Summary</h3>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <SummaryCard label="Assets" value={summary?.asset_count ?? 0} />
            <SummaryCard
              label="Total Cost"
              value={`$${summary?.total_cost ?? 0}`}
            />
            <SummaryCard label="Currency" value={summary?.currency ?? "USD"} />
          </div>

          <div className="mt-6 overflow-hidden rounded-2xl border border-white/10">
            <table className="w-full text-left text-sm">
              <thead className="bg-white/5 text-slate-300">
                <tr>
                  <th className="p-4">Symbol</th>
                  <th className="p-4">Type</th>
                  <th className="p-4">Quantity</th>
                  <th className="p-4">Buy Price</th>
                  <th className="p-4">Cost</th>
                </tr>
              </thead>
              <tbody>
                {assets.map((asset) => (
                  <tr key={asset.id} className="border-t border-white/10">
                    <td className="p-4 font-bold">{asset.symbol}</td>
                    <td className="p-4 text-slate-400">{asset.asset_type}</td>
                    <td className="p-4">{asset.quantity}</td>
                    <td className="p-4">${asset.buy_price}</td>
                    <td className="p-4">
                      ${(asset.quantity * asset.buy_price).toFixed(2)}
                    </td>
                  </tr>
                ))}

                {assets.length === 0 && (
                  <tr>
                    <td colSpan={5} className="p-6 text-center text-slate-400">
                      Henüz portföy varlığı eklenmedi.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

function SummaryCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-2 text-2xl font-bold">{value}</p>
    </div>
  );
}