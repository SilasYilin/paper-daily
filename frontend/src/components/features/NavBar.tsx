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
    <div className="flex items-center gap-2.5 border-t border-paper-line bg-paper-soft px-6 py-4">
      <button
        onClick={onPrev}
        disabled={sub === 0}
        className="flex items-center gap-0.5 rounded-lg border border-paper-line bg-paper-card px-3.5 py-1.5 text-[13px] text-paper-ink2 transition-colors hover:border-paper-accent hover:text-paper-accent disabled:pointer-events-none disabled:opacity-30"
      >
        <ChevronLeft className="size-4" />
        上一篇卡
      </button>
      <div className="flex flex-1 justify-center gap-1.5">
        {Array.from({ length: total }, (_, i) => (
          <button
            key={i}
            aria-label={`第 ${i + 1} 张卡`}
            onClick={() => onDot(i)}
            className={
              i === sub
                ? 'h-[7px] w-5 rounded-full bg-paper-accent transition-all'
                : 'h-[7px] w-[7px] rounded-full bg-paper-line transition-all hover:bg-paper-muted'
            }
          />
        ))}
      </div>
      <span className="min-w-[52px] text-center text-[11px] text-paper-muted">
        {sub + 1} / {total}
      </span>
      <button
        onClick={onNext}
        className="flex items-center gap-0.5 rounded-lg border border-paper-line bg-paper-card px-3.5 py-1.5 text-[13px] text-paper-ink2 transition-colors hover:border-paper-accent hover:text-paper-accent"
      >
        {isLast ? '下一篇论文' : '下一张卡'}
        <ChevronRight className="size-4" />
      </button>
    </div>
  );
}
