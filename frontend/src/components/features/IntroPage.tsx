import type { Paper } from '../../types/data';

/** 行内 `code` 转高亮 + 换行 */
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

export function IntroPage({ p }: { p: Paper }) {
  return (
    <div className="flex flex-1 flex-col">
      <PageHeader tag="导读 · 通俗版" title="这篇在讲什么" emoji="✨" />
      <div className="px-6 sm:px-10">
        <RichText
          text={p.summary || ''}
          className="pd-intro text-[15.5px] leading-[1.85] text-paper-ink"
        />
      </div>
      <div className="mt-auto border-t border-dashed border-paper-line px-6 py-3.5 text-[11.5px] text-paper-muted sm:px-10">
        导读为通俗版，便于快速理解；后续卡片为专业表述。
      </div>
    </div>
  );
}

export function PageHeader({ tag, title, emoji }: { tag: string; title: string; emoji?: string }) {
  return (
    <div className="px-6 pt-9 pb-0 sm:px-10 sm:pt-10">
      <div className="mb-1.5 text-[11px] uppercase tracking-[2px] text-paper-muted">{tag}</div>
      <h2 className="text-xl font-extrabold text-paper-ink">
        {emoji && <span className="mr-2.5">{emoji}</span>}
        {title}
      </h2>
      <div className="my-3 h-[3px] w-8.5 rounded bg-paper-accent" />
    </div>
  );
}
