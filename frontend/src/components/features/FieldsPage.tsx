import type { Fields, Paper } from '../../types/data';
import { PageHeader } from './IntroPage';

const FIELD_DEFS: ReadonlyArray<[keyof Fields, string, string]> = [
  ['background', 'Background', '背景'],
  ['task', 'Task', '任务'],
  ['insight', 'Insight', '核心洞察'],
  ['pipeline', 'Pipeline', '流程'],
  ['methods', 'Methods', '方法'],
  ['experiment', 'Experiment', '实验'],
  ['limitation', 'Limitation', '局限'],
];

export function FieldsPage({ p }: { p: Paper }) {
  const fl = p.fields || {};
  const items = FIELD_DEFS.map(([k, en, zh], i) => {
    const v = fl[k];
    return v ? (
      <div key={k} className="border-l border-paper-line pl-4">
        <h5 className="text-xs font-extrabold tracking-wide text-paper-ink">
          <span className="font-display mr-2 text-paper-accent">{String(i).padStart(2, '0')}</span>
          {en} · {zh}
        </h5>
        <p className="mt-1 text-[12.8px] leading-[1.75] text-paper-ink2">{v}</p>
      </div>
    ) : null;
  }).filter(Boolean);

  return (
    <div className="flex flex-1 flex-col">
      <PageHeader tag="DEEP READ" title="深读 · 0-6 字段" no="VII" />
      <div className="grid gap-4 px-6 sm:px-10">
        {items.length > 0 ? items : <p className="text-paper-muted">以原文为准。</p>}
      </div>
    </div>
  );
}
