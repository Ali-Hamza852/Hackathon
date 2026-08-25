export function Header() {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl flex-col gap-0.5 px-4 py-4">
        <div className="flex items-center gap-2">
          <span className="text-2xl" aria-hidden="true">
            🌬️
          </span>
          <h1 className="font-heading text-2xl font-extrabold text-slate-900">SAANS</h1>
        </div>
        <p className="text-sm text-slate-500">Smog advisory for Lahore schools, updated daily</p>
      </div>
    </header>
  );
}
