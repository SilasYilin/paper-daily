export interface Card {
  emoji: string;
  title: string;
  body: string;
}

export interface Figure {
  file: string;
  caption: string;
  kind?: string;
}

export interface Fields {
  background?: string;
  task?: string;
  insight?: string;
  pipeline?: string;
  methods?: string;
  experiment?: string;
  limitation?: string;
  [key: string]: string | undefined;
}

export interface Paper {
  title: string;
  titleZh?: string;
  hook?: string;
  summary?: string;
  cards?: Card[];
  figures?: Figure[];
  figureNote?: string;
  figure?: string | null;
  fields?: Fields;
  influence?: string;
  github?: string;
  stars?: number | null;
  citedBy?: number | null;
  institutions?: string[];
  authors?: string;
  venue?: string;
  category?: string;
  score?: number | string;
  scores?: { innovation?: number | null; effectiveness?: number | null; note?: string };
  paperUrl?: string;
}

export interface DataBundle {
  issue?: string;
  date?: string;
  axes?: string;
  edNote?: string;
  empty?: boolean;
  reason?: string;
  hero?: Paper;
  papers?: Paper[];
  counts?: { total?: number; new?: number };
}

declare global {
  interface Window {
    PAPER_DAILY_DATA?: DataBundle;
  }
}

export function loadData(): DataBundle {
  return (window as unknown as { PAPER_DAILY_DATA?: DataBundle }).PAPER_DAILY_DATA || {};
}
