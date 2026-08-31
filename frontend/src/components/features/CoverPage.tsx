import type { Paper } from '../../types/data';
import { Lightbulb, Gauge, Star, Users } from 'lucide-react';

/** 双维度评分环（0~10，半环形仪表盘样式） */
function ScoreDial({ label, value, icon: Icon }: { label: string; value?: number | null; icon: typeof Lightbulb }) {
  const v = typeof value === 'number' && value >= 0 && value <= 10 ? value : null;
  const pct = v == null ? 0 : v * 10;
  const R = 15.9155; // r=25.4 周长≈100
  const color = v == null ? 'var(--pd-line)'
    : v >= 8 ? 'var(--pd-accent)'
    : v >= 6 ? 'var(--pd-accent-mid)'
    : 'var(--pd-muted)';
  return (
    <div className="flex flex-col items-center gap-1" title={v == null ? '评分待补' : `${label} ${v}/10`}>
      <div className="relative size-12">
        <svg viewBox="0 0 36 36" className="size-12 -rotate-90">
          <circle cx="18" cy="18" r={R} fill="none" stroke="var(--pd-tagbg)" strokeWidth="3" />
          <circle
            cx="18" cy="18" r={R} fill="none" stroke={color} strokeWidth="3"
            strokeLinecap="round" strokeDasharray={`${pct} 100`}
            style={{ transition: 'stroke-dasharray .6s cubic-bezier(.22,1,.36,1)' }}
          />
        </svg>
        <span className="absolute inset-0 flex items-center justify-center font-display text-[13px] font-bold text-paper-ink">
          {v == null ? '–' : v}
        </span>
      </div>
      <span className="flex items-center gap-1 text-[10px] font-semibold tracking-wide text-paper-muted">
        <Icon className="size-3 text-paper-accent" aria-hidden />
        {label}
      </span>
    </div>
  );
}

export function CoverPage({ p }: { p: Paper }) {
  return (
    <div className="flex flex-1 flex-col">
      {/* 卷头：kicker + 日期行 */}
      <div className="flex items-center justify-between border-b border-paper-line px-6 py-3 sm:px-10">
        <div className="text-[10px] font-bold uppercase tracking-[0.25em] text-paper-accent">
          {p.category || 'PAPER'}
        </div>
        <div className="font-display text-[11px] italic text-paper-muted">{p.venue || ''}</div>
      </div>

      {/* 主体：标题区 + 竖排装饰 */}
      <div className="flex flex-1 gap-4 px-6 py-8 sm:px-10 sm:py-10">
        <div className="flex min-w-0 flex-1 flex-col">
          <h1 className="font-display mb-3 text-[26px] font-bold leading-[1.35] tracking-tight text-paper-ink sm:text-[32px] sm:leading-[1.3]">
            {p.titleZh || p.title}
          </h1>
          <div className="mb-5 max-w-[75ch] font-display text-[13px] italic leading-relaxed text-paper-muted">
            {p.title}
          </div>
          {p.hook && (
            <div className="mb-6 border-l-[3px] border-paper-accent bg-paper-soft py-2 pl-4 pr-3 text-[15px] font-semibold leading-relaxed text-paper-ink">
              「{p.hook}」
            </div>
          )}
        </div>
      </div>

      {/* 评分区：双表盘 */}
      <div className="mx-6 flex items-center justify-end gap-8 border-t border-dashed border-paper-line pb-5 pt-5 sm:mx-10">
        <ScoreDial label="创新" value={p.scores?.innovation} icon={Lightbulb} />
        <ScoreDial label="效果" value={p.scores?.effectiveness} icon={Gauge} />
      </div>

      {/* 页脚：作者 + 影响力 */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-paper-line px-6 py-4 text-xs text-paper-muted sm:px-10">
        <span className="flex min-w-0 items-center gap-1.5">
          <Users className="size-3 shrink-0" aria-hidden />
          <span className="truncate">{p.authors || ''}</span>
        </span>
      </div>
      {(p.influence || p.venue) && (
        <div className="space-y-1.5 px-6 pb-5 text-xs leading-relaxed text-paper-muted sm:px-10">
          {p.influence && (
            <div className="flex items-start gap-1.5">
              <Star className="mt-0.5 size-3 shrink-0 text-paper-accent" aria-hidden />
              <span>{p.influence}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
