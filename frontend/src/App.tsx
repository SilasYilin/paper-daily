import { useCallback, useEffect, useState } from 'react';
import { Copy, Share2, Keyboard, ArrowLeft } from 'lucide-react';
import type { DataBundle } from './types/data';
import { allPapers, buildCopyText, copyToClipboard, saveFeedback, sharePaper, canShare } from './utils/helpers';
import { pagesOf } from './utils/pages';
import { TopBar, type ViewMode } from './components/layout/TopBar';
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
import { Overview } from './components/features/Overview';
import { useToast } from './hooks/useToast';
import { useTheme } from './hooks/useTheme';

export function App({ data }: { data: DataBundle }) {
  const papers = allPapers(data);
  const { show, node: toastNode } = useToast();
  const { toggle: toggleTheme } = useTheme();
  const [helpOpen, setHelpOpen] = useState(false);
  const decks = papers.map(pagesOf);

  const offsets: number[] = [];
  let acc = 0;
  for (const d of decks) { offsets.push(acc); acc += d.length; }
  const total = acc;

  // 深链：#read/<n> 直接进入第 n 篇的精读视图（可分享）
  const [view, setView] = useState<ViewMode>(() =>
    /^#read\/\d+/.test(window.location.hash) ? 'read' : 'overview',
  );
  const [flatIdx, setFlatIdx] = useFlatPager(total, view === 'read', () => {
    const m = /^#read\/(\d+)/.exec(window.location.hash);
    if (!m) return 0;
    const i = Math.max(0, Math.min(papers.length - 1, Number(m[1]) - 1));
    return offsets[i] ?? 0;
  });

  // 顶栏只留方向名（期号/日期已在 Hero 展示，避免小字重复）
  const meta = data.axes || '稀疏视角 4DGS · 新视角合成';
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

  const onCopy = useCallback(async () => {
    const ok = await copyToClipboard(buildCopyText(data));
    show(ok ? '✓ 已复制全部文案' : '复制失败，请手动复制');
  }, [data, show]);

  const onShare = useCallback(async () => {
    const ok = await sharePaper(p);
    if (!ok) show('分享未完成（已取消或浏览器不支持）');
  }, [p, show]);

  const onVote = (v: 1 | -1) => {
    saveFeedback(p.title, v);
    show(v > 0 ? '已记录：有帮助 ✓（下次同步给助手）' : '已记录：不对口（用于调低同类）');
  };

  /** 从概览进入精读：定位到指定论文的首张卡 */
  const goRead = useCallback((i: number) => {
    setFlatIdx(offsets[i] ?? 0);
    setView('read');
    history.replaceState(null, '', `#read/${i + 1}`);
    window.scrollTo({ top: 0, behavior: 'auto' });
  }, [offsets, setFlatIdx]);

  const goOverview = useCallback(() => {
    setView('overview');
    history.replaceState(null, '', window.location.pathname + window.location.search);
    window.scrollTo({ top: 0, behavior: 'auto' });
  }, []);

  // 浏览器标签页标题跟随当前论文
  useEffect(() => {
    const cur = papers[paperIdx];
    const name = cur ? (cur.titleZh || cur.title) : '';
    document.title = `Paper卡片 · ${data.axes || '三维重建 × 世界模型'}${name ? ` · ${name.slice(0, 30)}` : ''}`;
  }, [paperIdx, papers, data.axes]);

  // 深链同步：#read/<n> 跟随当前论文，便于分享单篇
  useEffect(() => {
    if (view !== 'read') return;
    const h = `#read/${paperIdx + 1}`;
    if (window.location.hash !== h) history.replaceState(null, '', h);
  }, [view, paperIdx]);

  // 全局快捷键：G 切视图、Home/End 首末卡、T 切主题、C 复制、? 帮助、Esc 返回/关闭
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement | null;
      if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return;
      if (e.key === 'Escape') {
        if (helpOpen) { setHelpOpen(false); return; }
        if (view === 'read') { goOverview(); }
        return;
      }
      if ((e.key === 'g' || e.key === 'G') && !e.ctrlKey && !e.metaKey && !e.altKey) {
        e.preventDefault();
        if (view === 'read') goOverview(); else setView('read');
        return;
      }
      if (e.key === '?' || (e.key === '/' && e.shiftKey)) { e.preventDefault(); setHelpOpen(v => !v); return; }
      if (view !== 'read') return;   // 以下仅精读视图生效
      if (e.key === 'Home') { e.preventDefault(); setFlatIdx(0); return; }
      if (e.key === 'End') { e.preventDefault(); setFlatIdx(total - 1); return; }
      if ((e.key === 't' || e.key === 'T') && !e.ctrlKey && !e.metaKey && !e.altKey) { toggleTheme(); return; }
      if ((e.key === 'c' || e.key === 'C') && !e.ctrlKey && !e.metaKey && !e.altKey) { e.preventDefault(); onCopy(); }
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [total, toggleTheme, onCopy, setFlatIdx, view, helpOpen, goOverview]);

  const shareable = canShare();

  /* ============ 概览（仪表盘）视图 ============ */
  if (view === 'overview') {
    return (
      <div className="min-h-dvh bg-paper-50 font-sans">
        <TopBar
          meta={meta}
          issue={issue}
          wide
          view={view}
          onView={setView}
        />
        <Overview data={data} onRead={goRead} />
        {helpOpen && <HelpOverlay onClose={() => setHelpOpen(false)} view={view} />}
        <div className="fixed right-4 bottom-4 z-40 flex gap-2">
          <button
            onClick={onCopy}
            aria-label="复制全部文案"
            title="复制全部文案（快捷键 C）"
            className="flex size-11 cursor-pointer items-center justify-center rounded-full bg-paper-ink text-paper-50 shadow-lg transition-colors duration-200 hover:bg-paper-accent sm:min-h-11 sm:w-auto sm:rounded-full sm:px-4"
          >
            <Copy className="size-4" aria-hidden />
            <span className="ml-1.5 hidden text-xs font-semibold sm:inline">复制文案</span>
          </button>
        </div>
        {toastNode}
      </div>
    );
  }

  /* ============ 精读（翻卡）视图 ============ */
  return (
    <div className="min-h-dvh bg-paper-50 font-sans">
      {/* 阅读进度条 */}
      <div className="pd-progress-track" aria-hidden>
        <div className="pd-progress-bar" style={{ width: `${((flatIdx + 1) / total) * 100}%` }} />
      </div>

      <TopBar meta={meta} issue={issue} view={view} onView={setView} />

      <div className="mx-auto mt-6 flex max-w-3xl items-center gap-3 px-5">
        <button
          onClick={goOverview}
          className="flex h-8 cursor-pointer items-center gap-1.5 rounded-lg border border-paper-line bg-paper-card px-2.5 text-xs text-paper-ink2 transition-colors duration-200 hover:border-paper-accent hover:text-paper-accent"
        >
          <ArrowLeft className="size-3.5" aria-hidden />
          返回概览
        </button>
        <div className="min-w-0 flex-1">
          <Selector papers={papers} cur={paperIdx} onPick={i => setFlatIdx(offsets[i])} />
        </div>
      </div>

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

      {/* 复制 / 分享：桌面胶囊组 / 移动圆钮组 */}
      <div className="fixed right-4 bottom-4 z-40 hidden gap-2 sm:flex">
        {shareable && (
          <button
            onClick={onShare}
            className="flex min-h-11 cursor-pointer items-center gap-1.5 rounded-full bg-paper-ink px-4 text-xs font-semibold text-paper-50 shadow-lg transition-colors duration-200 hover:bg-paper-accent"
          >
            <Share2 className="size-3.5" aria-hidden />
            分享本篇
          </button>
        )}
        <button
          onClick={onCopy}
          className="flex min-h-11 cursor-pointer items-center gap-1.5 rounded-full bg-paper-ink px-4 text-xs font-semibold text-paper-50 shadow-lg transition-colors duration-200 hover:bg-paper-accent"
        >
          <Copy className="size-3.5" aria-hidden />
          复制文案
        </button>
      </div>
      <div className="fixed right-4 bottom-4 z-40 flex gap-2 sm:hidden">
        {shareable && (
          <button
            onClick={onShare}
            aria-label="分享本篇"
            className="flex size-11 cursor-pointer items-center justify-center rounded-full bg-paper-ink text-paper-50 shadow-lg transition-colors duration-200 hover:bg-paper-accent"
          >
            <Share2 className="size-4.5" aria-hidden />
          </button>
        )}
        <button
          onClick={onCopy}
          aria-label="复制文案"
          className="flex size-11 cursor-pointer items-center justify-center rounded-full bg-paper-ink text-paper-50 shadow-lg transition-colors duration-200 hover:bg-paper-accent"
        >
          <Copy className="size-4.5" aria-hidden />
        </button>
      </div>

      {helpOpen && <HelpOverlay onClose={() => setHelpOpen(false)} view={view} />}

      <Colophon axes={data.axes || '三维重建 × 世界模型'} count={papers.length} date={data.date || ''} />
      {toastNode}
    </div>
  );
}

/** 快捷键帮助浮层 */
function HelpOverlay({ onClose, view }: { onClose: () => void; view: ViewMode }) {
  const rows: [string[], string][] = [
    [['G'], '在「概览」与「精读」之间切换'],
    [['Esc'], view === 'read' ? '返回概览 / 关闭浮层' : '关闭浮层'],
    [['←', '→'], '精读：上一张 / 下一张卡'],
    [['PageUp', 'PageDown'], '精读：翻卡（同方向键）'],
    [['Home', 'End'], '精读：跳到本期第一张 / 最后一张'],
    [['T'], '切换浅色 / 暗色主题'],
    [['C'], '复制全部文案（公众号粘贴友好）'],
    [['?'], '打开 / 关闭本帮助'],
  ];
  return (
    <div
      className="fixed inset-0 z-[70] flex items-center justify-center bg-black/40 p-4 backdrop-blur-[2px]"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="快捷键帮助"
    >
      <div
        className="pd-card w-full max-w-sm !min-h-0 p-6"
        onClick={e => e.stopPropagation()}
      >
        <div className="mb-4 flex items-center gap-2">
          <Keyboard className="size-4 text-paper-accent" aria-hidden />
          <h2 className="font-display text-lg font-bold text-paper-ink">快捷键</h2>
          <span className="flex-1" />
          <button
            onClick={onClose}
            aria-label="关闭"
            className="min-h-11 cursor-pointer rounded-md px-2 text-xs text-paper-muted transition-colors hover:text-paper-accent"
          >
            关闭
          </button>
        </div>
        <ul className="space-y-2.5">
          {rows.map(([keys, desc]) => (
            <li key={desc} className="flex items-center justify-between gap-4 text-sm text-paper-ink2">
              <span>{desc}</span>
              <span className="flex shrink-0 gap-1">
                {keys.map(k => <kbd key={k} className="pd-kbd">{k}</kbd>)}
              </span>
            </li>
          ))}
        </ul>
        <p className="mt-5 border-t border-paper-line pt-3 text-[11px] text-paper-muted">
          触屏设备：左右滑动翻卡。概览页点击「精读」直达该篇。
        </p>
      </div>
    </div>
  );
}

/** 扁平翻页（键盘/触摸/按钮共用），一张卡 = 一个索引步进 */
function useFlatPager(total: number, enabled: boolean, initial: () => number = () => 0) {
  const [idx, setIdx] = useState(initial);

  useEffect(() => {
    if (!enabled) return;
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
  }, [total, enabled]);

  return [idx, setIdx] as const;
}
