export default function Header({ onRefresh }: { onRefresh: () => void }) {
  return (
    <header className="mb-6 flex items-center justify-between">
      <div>
        <h2 className="text-3xl font-bold">Global Market Dashboard</h2>
        <p className="text-slate-400">
          Kripto, hisse, endeks, emtia, forex ve AI analiz merkezi
        </p>
      </div>

      <button
        onClick={onRefresh}
        className="rounded-xl bg-cyan-500 px-5 py-2 font-semibold text-black hover:bg-cyan-400"
      >
        Refresh
      </button>
    </header>
  );
}