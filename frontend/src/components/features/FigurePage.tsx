import type { Paper } from '../../types/data';
import { Puzzle } from 'lucide-react';
import { PageHeader, RichText } from './IntroPage';

export function FigurePage({ p }: { p: Paper }) {
  const fig = p.figures?.[0];
  return (
    <div className="flex flex-1 flex-col">
      <PageHeader tag="PIPELINE" title="流程图" no="VI" />
      <div className="flex min-h-0 flex-1 flex-col px-6 sm:px-10">
        {fig ? (
          <div className="flex flex-col items-center">
            <img
              src={`figs/${fig.file}`}
              alt="论文方法流程图"
              className="max-h-[380px] max-w-full self-center rounded-xl border border-paper-line bg-paper-50 object-contain"
            />
            {fig.caption && (
              <div className="mt-2.5 text-xs leading-relaxed text-paper-muted">{fig.caption}</div>
            )}
          </div>
        ) : (
          <div className="py-10 text-center text-[13px] text-paper-muted">
            <Puzzle className="mx-auto mb-2.5 size-10 opacity-50" aria-hidden />
            本文暂无 HTML 版流程图
          </div>
        )}
        {p.figureNote && (
          <RichText
            text={p.figureNote}
            className="mt-3 text-[13.5px] leading-[1.8] text-paper-ink2"
          />
        )}
      </div>
    </div>
  );
}
