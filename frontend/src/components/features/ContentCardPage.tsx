import type { Card as CardData, Paper } from '../../types/data';
import { PageHeader, RichText } from './IntroPage';

export function ContentCardPage({ p, card }: { p: Paper; card: CardData }) {
  return (
    <div className="flex flex-1 flex-col">
      <PageHeader tag={p.titleZh || ''} title={card.title || ''} emoji={card.emoji || '◆'} />
      <div className="px-6 sm:px-10">
        <RichText
          text={card.body || ''}
          className="whitespace-pre-line text-[14.5px] leading-[1.85] text-paper-ink2"
        />
      </div>
    </div>
  );
}
