import { Leaf } from 'lucide-react';

export function EmptyState({ reason }: { reason?: string }) {
  return (
    <div className="mx-auto max-w-xl px-6 py-24 text-center">
      <Leaf className="mx-auto mb-4 size-14 text-paper-accent/70" aria-hidden />
      <h2 className="font-display mb-2 text-lg font-bold text-paper-ink">今日无精选</h2>
      <p className="text-sm text-paper-muted">
        {reason || '今日时间窗内无命中偏好方向的合适论文，明天见。'}
      </p>
    </div>
  );
}
