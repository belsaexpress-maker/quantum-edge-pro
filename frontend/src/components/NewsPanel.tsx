type NewsItem = {
  title: string;
  category: string;
  impact: string;
  sentiment: string;
  source?: string;
};

export default function NewsPanel({ news }: { news: NewsItem[] }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-[#070b1f] p-5">
      <h3 className="mb-4 text-xl font-bold">Latest News</h3>

      <div className="space-y-3">
        {news.map((item, index) => (
          <div
            key={index}
            className="rounded-2xl border border-white/10 bg-white/5 p-4"
          >
            <div className="flex justify-between gap-3">
              <h4 className="font-semibold">{item.title}</h4>
              <span className="text-sm text-cyan-300">{item.category}</span>
            </div>
            <p className="mt-2 text-sm text-slate-400">
              Impact: {item.impact} • Sentiment: {item.sentiment}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}