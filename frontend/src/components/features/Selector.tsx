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
          title={`${p.titleZh || p.title}${p.scores?.innovation != null ? `（创新 ${p.scores.innovation}/10 · 效果 ${p.scores.effectiveness ?? '–'}/10）` : ''}`}
          aria-label={`第 ${i + 1} 篇：${p.titleZh || p.title}`}
          aria-current={i === cur}
          className={
            (i === cur
              ? 'border-paper-ink bg-paper-ink font-bold text-paper-50'
              : 'border-paper-line bg-paper-card text-paper-ink2 hover:border-paper-accent') +
            ' flex h-8 w-8 cursor-pointer items-center justify-center rounded-lg border text-[13px] transition-colors duration-200'
          }
        >
          {i + 1}
        </button>
      ))}
    </div>
  );
}
