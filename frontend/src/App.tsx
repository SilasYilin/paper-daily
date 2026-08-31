import { useEffect, useState } from 'react';
import { Copy } from 'lucide-react';
import type { DataBundle } from './types/data';
import { allPapers, buildCopyText, copyToClipboard, saveFeedback } from './utils/helpers';
import { pagesOf } from './utils/pages';
import { TopBar } from './components/layout/TopBar';
import { Colophon } from './components/layout/Colophon';
import { Selector } from './components/features/Selector';
import { NavBar } from './components/features/NavBar';
import { CoverPage } from './components/features/CoverPage';
import { IntroPage } from './components/features/IntroPage';
import { ContentCardPage } from './components/features/ContentCardPage';
import { FigurePage } from './components/features/FigurePage';
import { FieldsPage } from './components/features/FieldsPage';
import { EndPage } from './components/features/EndPage';
import { EmptyState } from './components/features/EmptyState';
import { useToast } from './hooks/useToast';

export function App({ data }: { data: DataBundle }) {
  const papers = allPapers(data);
  const { show, node: toastNode } = useToast();
  const decks = papers.map(pagesOf);

  const offsets: number[] = [];
  let acc = 0;
  for (const d of decks) { offsets.push(acc); acc += d.length; }
  const total = acc;

  const [flatIdx, setFlatIdx] = useFlatPager(total);

  const meta = `${data.axes || '三维重建 × 世界模型'} · ${data.date || ''} · ${papers.length} 篇`;
  const issue = data.issue || '';

  if (data.empty || papers.length === 0) {
    return (
      <div className="min-h-dvh bg-paper-50 font-sans">
        <TopBar meta="" />
        <EmptyState reason={data.reason} />
        <Colophon axes={data.axes || '三维重建 × 世界模型'} count={0} date={data.date || ''} />
      </div>
    );
  }

  // 由扁平索引定位论文与卡
  let paperIdx = 0;
  for (let i = decks.length - 1; i >= 0; i--) {
    if (flatIdx >= offsets[i]) { paperIdx = i; break; }
  }
  const cardIdx = flatIdx - offsets[paperIdx];
  const page = decks[paperIdx]?.[cardIdx];
  const p = page?.p ?? papers[paperIdx];

  const onCopy = async () => {
    const ok = await copyToClipboard(buildCopyText(data));
    show(ok ? '✓ 已复制全部文案' : '复制失败，请手动复制');
  };

  const onVote = (v: 1 | -1) => {
    saveFeedback(p.title, v);
    show(v > 0 ? '已记录：有帮助 ✓（下次同步给助手）' : '已记录：不对口（用于调低同类）');
  };

  return (
    <div className="min-h-dvh bg-paper-50 font-sans">
      <TopBar meta={meta} issue={issue} />

      <Selector papers={papers} cur={paperIdx} onPick={i => setFlatIdx(offsets[i])} />

      <div className="mx-auto max-w-3xl px-5 pb-10">
        <div key={flatIdx} className="pd-card">
          {page?.t === 'cover' && <CoverPage p={p} />}
          {page?.t === 'intro' && <IntroPage p={p} />}
          {page?.t === 'card' && <ContentCardPage p={p} card={page.card} idx={cardIdx - 1} />}
          {page?.t === 'fig' && <FigurePage p={p} />}
          {page?.t === 'fields' && <FieldsPage p={p} />}
          {page?.t === 'end' && <EndPage p={p} onVote={onVote} />}
        </div>
      </div>

      <div className="mx-auto max-w-3xl px-5">
        <NavBar
          sub={cardIdx}
          total={decks[paperIdx].length}
          isLast={cardIdx === decks[paperIdx].length - 1}
          onPrev={() => setFlatIdx(Math.max(0, flatIdx - 1))}
          onNext={() => setFlatIdx(Math.min(total - 1, flatIdx + 1))}
          onDot={i => setFlatIdx(offsets[paperIdx] + i)}
        />
      </div>

      {/* 复制文案：桌面胶囊 / 移动圆钮 */}
      <div className="fixed right-4 bottom-4 z-40 hidden sm:block">
        <button
          onClick={onCopy}
          className="flex min-h-11 cursor-pointer items-center gap-1.5 rounded-full bg-paper-ink px-4 text-xs font-semibold text-paper-50 shadow-lg transition-colors duration-200 hover:bg-paper-accent"
        >
          <Copy className="size-3.5" aria-hidden />
          复制文案
        </button>
      </div>
      <div className="fixed right-4 bottom-4 z-40 sm:hidden">
        <button
          onClick={onCopy}
          aria-label="复制文案"
          className="flex size-11 cursor-pointer items-center justify-center rounded-full bg-paper-ink text-paper-50 shadow-lg transition-colors duration-200 hover:bg-paper-accent"
        >
          <Copy className="size-4.5" aria-hidden />
        </button>
      </div>

      <Colophon axes={data.axes || '三维重建 × 世界模型'} count={papers.length} date={data.date || ''} />
      {toastNode}
    </div>
  );
}

/** 扁平翻页（键盘/触摸/按钮共用），一张卡 = 一个索引步进 */
function useFlatPager(total: number) {
  const [idx, setIdx] = useState(0);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' || e.key === 'PageDown') {
        e.preventDefault();
        setIdx(i => Math.min(i + 1, total - 1));
      } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
        e.preventDefault();
        setIdx(i => Math.max(i - 1, 0));
      }
    };
    let tx: number | undefined;
    const onTS = (e: TouchEvent) => { tx = e.touches[0].clientX; };
    const onTE = (e: TouchEvent) => {
      if (tx == null) return;
      const dx = e.changedTouches[0].clientX - tx;
      if (dx < -40) setIdx(i => Math.min(i + 1, total - 1));
      else if (dx > 40) setIdx(i => Math.max(i - 1, 0));
      tx = undefined;
    };
    document.addEventListener('keydown', onKey);
    document.addEventListener('touchstart', onTS, { passive: true });
    document.addEventListener('touchend', onTE, { passive: true });
    return () => {
      document.removeEventListener('keydown', onKey);
      document.removeEventListener('touchstart', onTS);
      document.removeEventListener('touchend', onTE);
    };
  }, [total]);

  return [idx, setIdx] as const;
}
