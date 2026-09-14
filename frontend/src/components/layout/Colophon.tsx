export function Colophon({ axes, count, date }: { axes: string; count: number; date: string }) {
  return (
    <footer className="px-4 pb-12 pt-2 text-center text-xs text-paper-muted">
      <div className="mx-auto mb-3 h-px max-w-24 bg-paper-line" aria-hidden />
      {count} 篇 · {date} · {axes}
    </footer>
  );
}
