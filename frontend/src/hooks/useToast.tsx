import { useEffect, useRef, useState } from 'react';

export function useToast() {
  const [msg, setMsg] = useState<string | null>(null);
  const timer = useRef<number | undefined>(undefined);

  useEffect(() => () => window.clearTimeout(timer.current), []);

  const show = (m: string) => {
    setMsg(m);
    window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => setMsg(null), 2200);
  };

  const node = msg ? (
    <div className="fixed left-1/2 bottom-9 z-[99] -translate-x-1/2 rounded-lg bg-paper-ink px-5 py-2.5 text-[13px] text-paper-50 shadow-lg transition-all">
      {msg}
    </div>
  ) : null;

  return { show, node };
}
