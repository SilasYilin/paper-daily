import type { DataBundle, Paper } from '../types/data';

export function allPapers(d: DataBundle): Paper[] {
  return ([] as Paper[]).concat(d.hero ? [d.hero] : [], d.papers || []);
}

/** 与旧版 copyText 完全一致的纯文本（公众号粘贴友好） */
export function buildCopyText(d: DataBundle): string {
  const L: string[] = [];
  L.push(`Paper卡片 · ${d.date || ''} · ${d.counts?.total || 0} 篇`);
  allPapers(d).forEach((p, i) => {
    L.push('');
    L.push(`▍${i + 1}. ${p.titleZh || p.title}`);
    if (p.hook) L.push(`「${p.hook}」`);
    const sc = p.scores || {};
    if (sc.innovation != null || sc.effectiveness != null) {
      L.push(`评分：创新 ${sc.innovation ?? '–'}/10 · 效果 ${sc.effectiveness ?? '–'}/10`);
    }
    L.push(`【导读】${p.summary || ''}`);
    (p.cards || []).forEach(c => L.push(`${c.emoji} ${c.title}：${c.body}`));
    L.push(`原文：${p.paperUrl || ''}`);
  });
  return L.join('\n');
}

export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch { /* fallthrough */ }
  try {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    const ok = document.execCommand('copy');
    document.body.removeChild(ta);
    return ok;
  } catch {
    return false;
  }
}

export function saveFeedback(title: string, v: 1 | -1) {
  try {
    const fb = JSON.parse(localStorage.getItem('pd-feedback') || '[]') as unknown[];
    fb.push({ title, v, at: Date.now() });
    localStorage.setItem('pd-feedback', JSON.stringify(fb));
  } catch { /* ignore */ }
}
