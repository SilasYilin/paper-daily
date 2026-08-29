import type { Card, Paper } from '../types/data';

/** 每篇论文的页组：封面 / 导读 / N 张内容卡 / 流程图 / 深读 / 反馈 */
export type PageItem =
  | { t: 'cover'; p: Paper }
  | { t: 'intro'; p: Paper }
  | { t: 'card'; p: Paper; card: Card }
  | { t: 'fig'; p: Paper }
  | { t: 'fields'; p: Paper }
  | { t: 'end'; p: Paper };

export function pagesOf(p: Paper): PageItem[] {
  const pg: PageItem[] = [{ t: 'cover', p }];
  if (p.summary) pg.push({ t: 'intro', p });
  (p.cards || []).forEach(c => pg.push({ t: 'card', p, card: c }));
  if ((p.figures && p.figures.length) || p.figureNote) pg.push({ t: 'fig', p });
  pg.push({ t: 'fields', p });
  pg.push({ t: 'end', p });
  return pg;
}
