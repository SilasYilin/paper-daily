import { ChevronLeft, ChevronRight } from 'lucide-react';

export function NavBar({
  sub,
  total,
  isLast,
  onPrev,
  onNext,
  onDot,
}: {
  sub: number;
  total: number;
  isLast: boolean;
  onPrev: () => void;
  onNext: () => void;
  onDot: (i: number) => void;
}) {
  return (
    <nav className="mx-auto flex max-w-3xl items-center gap-2.5 px-5" aria-label="卡片导航">
      <button
        onClick={onPrev}
        disabled={sub === 0}
        aria-label="上一张卡"
        className="flex min-h-11 cursor-pointer items-center gap-0.5 rounded-lg border border-paper-line bg-paper-card px-3.5 text-[13px] text-paper-ink2 transition-colors duration-200 hover:border-paper-accent hover:text-paper-accent disabled:pointer-events-none disabled:opacity-30"
      >
        <ChevronLeft className="size-4" aria-hidden />
        上一篇卡
      </button>
      <div className="flex flex-1 justify-center gap-1.5 py-2">
        {Array.from({ length: total }, (_, i) => (
          <button
            key={i}
            aria-label={`第 ${i + 1} 张卡`}
            onClick={() => onDot(i)}
            className={
              (i === sub
                ? 'h-2 w-5 cursor-pointer rounded-full bg-paper-accent transition-all'
                : 'h-2 w-2 cursor-pointer rounded-full bg-paper-line transition-all hover:bg-paper-muted') +
              ' min-h-11 flex items-center justify-center'
            }
          >
            <span className={i === sub ? 'block h-1.5 w-4 rounded-full bg-paper-accent' : 'block h-1.5 w-1.5 rounded-full bg-paper-line'} />
          </button>
        ))}
      </div>
      <span className="min-w-[52px] text-center text-[11px] text-paper-muted">
        {sub + 1} / {total}
      </span>
      <button
        onClick={onNext}
        aria-label={isLast ? '下一篇论文' : '下一张卡'}
        className="flex min-h-11 cursor-pointer items-center gap-0.5 rounded-lg border border-paper-line bg-paper-card px-3.5 text-[13px] text-paper-ink2 transition-colors duration-200 hover:border-paper-accent hover:text-paper-accent"
      >
        {isLast ? '下一篇论文' : '下一张卡'}
        <ChevronRight className="size-4" aria-hidden />
      </button>
    </nav>
  );
}
