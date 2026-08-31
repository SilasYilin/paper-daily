import type { Paper } from '../../types/data';

/** 行内 `code` 转高亮 */
export function RichText({ text, className = '' }: { text: string; className?: string }) {
  const parts = text.split(/(`[^`]+`)/g);
  return (
    <div className={className}>
      {parts.map((seg, i) =>
        seg.startsWith('`') && seg.endsWith('`') && seg.length > 2 ? (
          <code key={i} className="rounded bg-paper-tagbg px-1.5 py-0.5 font-mono text-[13px]">
            {seg.slice(1, -1)}
          </code>
        ) : (
          <span key={i}>{seg}</span>
        )
      )}
    </div>
  );
}

/** 杂志化页头：kicker + 衬线大标题 + 分隔短标尺。图标一律走 emoji 之外的语义编号。 */
export function PageHeader({ tag, title, no }: { tag: string; title: string; no?: string }) {
  return (
    <div className="px-6 pt-8 sm:px-10 sm:pt-9">
      <div className="mb-1.5 flex items-baseline justify-between">
        <div className="text-[11px] uppercase tracking-[2px] text-paper-muted">{tag}</div>
        {no && (
          <div className="font-display text-[13px] font-semibold italic text-paper-accent">{no}</div>
        )}
      </div>
      <h2 className="font-display text-[22px] font-bold leading-snug tracking-tight text-paper-ink">
        {title}
      </h2>
      <div className="mt-3 mb-4 flex items-center gap-2">
        <div className="h-[3px] w-9 rounded bg-paper-accent" />
        <div className="h-px flex-1 bg-paper-line" />
      </div>
    </div>
  );
}

export function IntroPage({ p }: { p: Paper }) {
  return (
    <div className="flex flex-1 flex-col">
      <PageHeader tag="导读 · 通俗版" title="这篇在讲什么" no="I" />
      <div className="px-6 sm:px-10">
        <RichText
          text={p.summary || ''}
          className="pd-intro text-[15.5px] leading-[1.9] text-paper-ink"
        />
      </div>
      <div className="mt-auto border-t border-dashed border-paper-line px-6 py-3.5 text-[11.5px] text-paper-muted sm:px-10">
        导读为通俗版，便于快速理解；后续卡片为专业表述。
      </div>
    </div>
  );
}
