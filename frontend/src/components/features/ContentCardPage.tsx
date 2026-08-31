import type { Card as CardData, Paper } from '../../types/data';
import { PageHeader, RichText } from './IntroPage';

const CARD_NOS = ['II', 'III', 'IV', 'V', 'VI', 'VII'];

export function ContentCardPage({ p, card, idx }: { p: Paper; card: CardData; idx?: number }) {
  return (
    <div className="flex flex-1 flex-col">
      <PageHeader tag={p.titleZh || ''} title={card.title || ''} no={CARD_NOS[idx ?? 0] || '·'} />
      <div className="px-6 sm:px-10">
        <RichText
          text={card.body || ''}
          className="whitespace-pre-line text-[14.5px] leading-[1.85] text-paper-ink2"
        />
      </div>
    </div>
  );
}
