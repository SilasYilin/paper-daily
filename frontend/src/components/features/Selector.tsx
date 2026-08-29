import type { Paper } from '../../types/data';

export function Selector({
  papers,
  cur,
  onPick,
}: {
  papers: Paper[];
  cur: number;
  onPick: (i: number) => void;
}) {
  return (
    <div className="mx-auto mt-6 flex max-w-3xl flex-wrap items-center gap-2 px-5">
      <span className="mr-1 text-[11px] tracking-[2px] text-paper-muted">本期论文</span>
      {papers.map((p, i) => (
        <button
          key={i}
          onClick={() => onPick(i)}
          title={p.titleZh || p.title}
          className={
            i === cur
              ? 'flex h-7.5 w-7.5 items-center justify-center rounded-lg border border-paper-ink bg-paper-ink text-[13px] font-bold text-paper-50 transition-all'
              : 'flex h-7.5 w-7.5 items-center justify-center rounded-lg border border-paper-line bg-paper-card text-[13px] text-paper-ink2 transition-all hover:border-paper-accent'
          }
        >
          {i + 1}
        </button>
      ))}
    </div>
  );
}
