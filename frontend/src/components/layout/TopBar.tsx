import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../../hooks/useTheme';

export function TopBar({ meta }: { meta: string }) {
  const { theme, toggle } = useTheme();
  return (
    <header className="sticky top-0 z-50 border-b border-paper-line bg-paper-50/90 backdrop-blur px-5 py-3">
      <div className="mx-auto flex max-w-3xl items-baseline gap-3">
        <span className="text-[15px] font-bold tracking-wide text-paper-ink">
          Paper<span className="text-paper-accent">卡片</span>
        </span>
        <span className="truncate text-xs text-paper-muted">{meta}</span>
        <span className="flex-1" />
        <button
          onClick={toggle}
          aria-label="切换主题"
          className="flex items-center gap-1.5 rounded-md border border-paper-line bg-transparent px-3 py-1 text-xs text-paper-ink2 transition-colors hover:border-paper-accent hover:text-paper-accent"
        >
          {theme === 'dark' ? <Sun className="size-3.5" /> : <Moon className="size-3.5" />}
          {theme === 'dark' ? '浅色' : '暗色'}
        </button>
      </div>
    </header>
  );
}
