import { Moon, Sun, Newspaper, LayoutGrid, BookOpen } from 'lucide-react';
import { useTheme } from '../../hooks/useTheme';

export type ViewMode = 'overview' | 'read';

export function TopBar({
  meta,
  issue,
  wide,
  view,
  onView,
}: {
  meta: string;
  issue?: string;
  wide?: boolean;
  view?: ViewMode;
  onView?: (v: ViewMode) => void;
}) {
  const { theme, toggle } = useTheme();
  const box = wide ? 'max-w-[1180px]' : 'max-w-3xl';
  return (
    <header className="sticky top-0 z-50 border-b border-paper-line bg-paper-50/90 px-5 py-3 backdrop-blur">
      <div className={`mx-auto flex ${box} items-center gap-3`}>
        <Newspaper className="size-4 shrink-0 text-paper-accent" aria-hidden />
        <span className="font-display text-[17px] font-bold tracking-tight text-paper-ink">
          Paper<span className="text-paper-accent">卡片</span>
        </span>
        <span className="hidden truncate text-xs text-paper-muted sm:inline">{meta}</span>
        {issue && (
          <span className="hidden rounded-sm border border-paper-line px-1.5 py-0.5 font-display text-[11px] italic text-paper-muted md:inline">
            {issue}
          </span>
        )}
        <span className="flex-1" />

        {view && onView && (
          <div
            className="flex items-center gap-0.5 rounded-lg border border-paper-line p-0.5"
            role="group"
            aria-label="视图切换"
          >
            <button
              onClick={() => onView('overview')}
              aria-pressed={view === 'overview'}
              title="概览（快捷键 G）"
              className={
                (view === 'overview'
                  ? 'bg-paper-ink text-paper-50'
                  : 'text-paper-ink2 hover:text-paper-accent') +
                ' flex h-9 cursor-pointer items-center gap-1.5 rounded-md px-2.5 text-xs transition-colors duration-200'
              }
            >
              <LayoutGrid className="size-3.5" aria-hidden />
              <span className="hidden sm:inline">概览</span>
            </button>
            <button
              onClick={() => onView('read')}
              aria-pressed={view === 'read'}
              title="精读（快捷键 G）"
              className={
                (view === 'read'
                  ? 'bg-paper-ink text-paper-50'
                  : 'text-paper-ink2 hover:text-paper-accent') +
                ' flex h-9 cursor-pointer items-center gap-1.5 rounded-md px-2.5 text-xs transition-colors duration-200'
              }
            >
              <BookOpen className="size-3.5" aria-hidden />
              <span className="hidden sm:inline">精读</span>
            </button>
          </div>
        )}

        <button
          onClick={toggle}
          aria-label="切换主题"
          className="flex min-h-11 cursor-pointer items-center gap-1.5 rounded-md border border-paper-line bg-transparent px-3 text-xs text-paper-ink2 transition-colors duration-200 hover:border-paper-accent hover:text-paper-accent"
        >
          {theme === 'dark' ? <Sun className="size-3.5" /> : <Moon className="size-3.5" />}
          <span className="hidden sm:inline">{theme === 'dark' ? '浅色' : '暗色'}</span>
        </button>
      </div>
    </header>
  );
}
