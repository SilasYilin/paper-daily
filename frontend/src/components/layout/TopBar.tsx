import { Moon, Sun, Newspaper } from 'lucide-react';
import { useTheme } from '../../hooks/useTheme';

export function TopBar({ meta, issue }: { meta: string; issue?: string }) {
  const { theme, toggle } = useTheme();
  return (
    <header className="sticky top-0 z-50 border-b border-paper-line bg-paper-50/90 backdrop-blur px-5 py-3">
      <div className="mx-auto flex max-w-3xl items-center gap-3">
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
        <button
          onClick={toggle}
          aria-label="切换主题"
          className="flex min-h-11 cursor-pointer items-center gap-1.5 rounded-md border border-paper-line bg-transparent px-3 text-xs text-paper-ink2 transition-colors duration-200 hover:border-paper-accent hover:text-paper-accent"
        >
          {theme === 'dark' ? <Sun className="size-3.5" /> : <Moon className="size-3.5" />}
          {theme === 'dark' ? '浅色' : '暗色'}
        </button>
      </div>
    </header>
  );
}
