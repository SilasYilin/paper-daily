import type { Paper } from '../../types/data';
import { Star, Users, MapPin } from 'lucide-react';

export function CoverPage({ p }: { p: Paper }) {
  return (
    <div className="flex flex-1 flex-col px-6 py-10 sm:px-10 sm:py-11">
      <div className="mb-4 text-[11px] font-bold uppercase tracking-[3px] text-paper-accent">
        {p.category || 'PAPER'}
      </div>
      <h1 className="mb-3.5 text-2xl font-extrabold leading-snug tracking-tight text-paper-ink sm:text-[30px] sm:leading-[1.4]">
        {p.titleZh || p.title}
      </h1>
      <div className="mb-5 italic leading-relaxed text-[13px] text-paper-muted">{p.title}</div>
      {p.hook && (
        <div className="mb-6 text-base font-semibold text-paper-accent">「{p.hook}」</div>
      )}
      <div className="mt-auto flex flex-wrap items-center justify-between gap-3 border-t border-paper-line pt-4 text-xs text-paper-muted">
        <span className="flex items-center gap-1.5">
          <Users className="size-3 shrink-0" />
          {p.authors || ''}
        </span>
        <span className="rounded-full bg-paper-soft px-3 py-0.5 font-bold text-paper-accent">
          匹配度 {p.score ?? ''}
        </span>
      </div>
      {p.influence && (
        <div className="mt-3.5 flex items-start gap-1.5 text-xs leading-relaxed text-paper-muted">
          <Star className="mt-0.5 size-3 shrink-0 text-paper-accent" />
          <span>{p.influence}</span>
        </div>
      )}
      {p.venue && (
        <div className="mt-1.5 flex items-center gap-1.5 text-xs text-paper-muted">
          <MapPin className="size-3 shrink-0" />
          <span className="truncate">{p.venue}</span>
        </div>
      )}
    </div>
  );
}
