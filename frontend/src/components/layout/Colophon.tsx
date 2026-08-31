export function Colophon({ axes, count, date }: { axes: string; count: number; date: string }) {
  return (
    <footer className="px-4 pb-12 pt-2 text-center text-xs leading-relaxed text-paper-muted">
      <div className="mx-auto mb-3 h-px max-w-24 bg-paper-line" aria-hidden />
      <span className="font-display italic">Paper卡片</span>
      {' · '}{axes}{' · '}每篇论文一组卡片 · 键盘 ←→ 或滑动翻页
      <br />
      {count} 篇 · {date}
    </footer>
  );
}
