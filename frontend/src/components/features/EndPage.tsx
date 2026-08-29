import { ExternalLink, ThumbsDown, ThumbsUp } from 'lucide-react';
import type { Paper } from '../../types/data';
import { PageHeader } from './IntroPage';

export function EndPage({
  p,
  onVote,
}: {
  p: Paper;
  onVote: (v: 1 | -1) => void;
}) {
  return (
    <div className="flex flex-1 flex-col">
      <PageHeader tag="LINKS" title="原文与反馈" emoji="📎" />
      <div className="flex flex-1 flex-col px-6 text-[14.5px] leading-[1.85] text-paper-ink2 sm:px-10">
        <p className="break-all">标题：{p.title || ''}</p>
        <p className="break-all">
          原文：
          <a
            href={p.paperUrl || '#'}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-paper-accent hover:underline"
          >
            {p.paperUrl || ''}
            <ExternalLink className="size-3.5 shrink-0" />
          </a>
        </p>
        <p className="mt-4">这篇对你的研究有帮助吗？</p>
        <div className="mt-1.5 flex gap-2.5">
          <button
            onClick={() => onVote(1)}
            className="flex items-center gap-1.5 rounded-lg border border-paper-line bg-paper-card px-4 py-1.5 text-[13px] text-paper-ink2 transition-colors hover:border-paper-accent hover:text-paper-accent"
          >
            <ThumbsUp className="size-4" /> 有帮助
          </button>
          <button
            onClick={() => onVote(-1)}
            className="flex items-center gap-1.5 rounded-lg border border-paper-line bg-paper-card px-4 py-1.5 text-[13px] text-paper-ink2 transition-colors hover:border-paper-accent hover:text-paper-accent"
          >
            <ThumbsDown className="size-4" /> 不对口
          </button>
        </div>
      </div>
      <div className="mt-auto border-t border-dashed border-paper-line px-6 py-3.5 text-[11.5px] text-paper-muted sm:px-10">
        反馈会进入偏好画像，影响后续筛选。
      </div>
    </div>
  );
}
