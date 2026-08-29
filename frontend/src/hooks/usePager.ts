import { useCallback, useEffect, useState } from 'react';

/** 主题无关的基础状态 + 全局键盘 / 触摸翻页 */
export function usePager(total: number) {
  const [cur, setCur] = useState(0);

  const next = useCallback(() => setCur(c => Math.min(c + 1, total - 1)), [total]);
  const prev = useCallback(() => setCur(c => Math.max(c - 1, 0)), [total]);
  const goto = useCallback((i: number) => setCur(Math.max(0, Math.min(i, total - 1))), [total]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' || e.key === 'PageDown') { e.preventDefault(); next(); }
      else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); prev(); }
    };
    const onTS = (e: TouchEvent) => { (window as unknown as { __pdTx?: number }).__pdTx = e.touches[0].clientX; };
    const onTE = (e: TouchEvent) => {
      const tx = (window as unknown as { __pdTx?: number }).__pdTx;
      if (tx == null) return;
      const dx = e.changedTouches[0].clientX - tx;
      if (dx < -40) next(); else if (dx > 40) prev();
      (window as unknown as { __pdTx?: number }).__pdTx = undefined;
    };
    document.addEventListener('keydown', onKey);
    document.addEventListener('touchstart', onTS, { passive: true });
    document.addEventListener('touchend', onTE, { passive: true });
    return () => {
      document.removeEventListener('keydown', onKey);
      document.removeEventListener('touchstart', onTS);
      document.removeEventListener('touchend', onTE);
    };
  }, [next, prev]);

  return { cur, next, prev, goto };
}
