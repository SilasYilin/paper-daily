import { useEffect, useRef, useState } from 'react';
import type { ReactNode } from 'react';
import { ArrowRight, ExternalLink, Code, Star, Quote, Building2 } from 'lucide-react';
import type { DataBundle, Paper } from '../../types/data';
import { groupPapers, humanDate, TIERS, type Group } from '../../utils/groups';
import { allPapers } from '../../utils/helpers';

const SUMMARY_MAX = 60;

/** 卡片摘要：优先用一句话钩子，否则截断长摘要（≤60 字，含省略号） */
function briefOf(p: Paper): string {
  const raw = (p.hook || p.summary || '').replace(/\s+/g, ' ').trim();
  const chars = [...raw];
  return chars.length > SUMMARY_MAX ? chars.slice(0, SUMMARY_MAX).join('') + '…' : raw;
}

/** 元信息行：有则显示，无则整体省略（宁缺毋滥） */
function MetaRow({ p }: { p: Paper }) {
  const bits: { icon: ReactNode; text: string }[] = [];
  if (p.institutions?.length) {
    bits.push({
      icon: <Building2 className="size-3" aria-hidden />,
      text: p.institutions.slice(0, 2).join('、') + (p.institutions.length > 2 ? ' 等' : ''),
    });
  }
  if (p.stars != null) {
    bits.push({ icon: <Star className="size-3" aria-hidden />, text: `${p.stars} star` });
  }
  if (p.citedBy != null) {
    bits.push({ icon: <Quote className="size-3" aria-hidden />, text: `被引 ${p.citedBy}` });
  }
  const sc = p.scores || {};
  if (sc.innovation != null || sc.effectiveness != null) {
    bits.push({
      icon: <span className="text-[10px] font-bold">评</span>,
      text: `创新 ${sc.innovation ?? '–'} · 效果 ${sc.effectiveness ?? '–'}`,
    });
  }
  if (!bits.length) return null;
  return (
    <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-paper-muted">
      {bits.map((b, i) => (
        <span key={i} className="inline-flex items-center gap-1">
          {b.icon}
          {b.text}
        </span>
      ))}
    </div>
  );
}

function PaperCard({
  p,
  n,
  color,
  onRead,
}: {
  p: Paper;
  n: number;
  color: string;
  onRead: () => void;
}) {
  return (
    <article
      className="pd-oc"
      style={{ ['--c' as string]: color }}
    >
      <div className="mb-2.5 flex items-center gap-2">
        <span className="pd-oc-no">{n}</span>
        {p.category && (
          <span className="pd-oc-chip" title={p.category}>
            {p.category}
          </span>
        )}
      </div>

      <h3 className="mb-2 text-[15.5px] leading-[1.45] font-semibold tracking-[-0.005em] text-paper-ink">
        {p.titleZh || p.title}
      </h3>

      <p className="mb-3 text-[13.5px] leading-[1.65] text-paper-ink2">{briefOf(p)}</p>

      <MetaRow p={p} />

      <div className="mt-auto flex items-center gap-3 pt-3">
        <button onClick={onRead} className="pd-oc-go">
          精读 <ArrowRight className="size-3.5" aria-hidden />
        </button>
        {p.paperUrl && (
          <a
            href={p.paperUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="pd-oc-link"
          >
            原文 <ExternalLink className="size-3" aria-hidden />
          </a>
        )}
        {p.github && (
          <a
            href={p.github}
            target="_blank"
            rel="noopener noreferrer"
            className="pd-oc-link"
            aria-label="GitHub 仓库"
            title="GitHub 仓库"
          >
            <Code className="size-3" aria-hidden />
            <span className="text-[12px]">代码</span>
          </a>
        )}
      </div>
    </article>
  );
}

export function Overview({
  data,
  onRead,
}: {
  data: DataBundle;
  onRead: (paperIndex: number) => void;
}) {
  const papers = allPapers(data);
  const groups: Group[] = groupPapers(papers);
  const ids = groups.map(g => 'sec-' + g.def.key);
  const [active, setActive] = useState(ids[0]);
  const mainRef = useRef<HTMLElement | null>(null);

  /* 滚动高亮：取当前视口中最靠上的可见分组 */
  useEffect(() => {
    const secs = ids
      .map(id => document.getElementById(id))
      .filter((el): el is HTMLElement => Boolean(el));
    if (!secs.length) return;
    const io = new IntersectionObserver(
      entries => {
        const visible = entries
          .filter(e => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible[0]) setActive(visible[0].target.id);
      },
      { rootMargin: '-140px 0px -55% 0px', threshold: [0, 0.25, 0.6] },
    );
    secs.forEach(s => io.observe(s));
    return () => io.disconnect();
  }, [ids.join(',')]);

  const total = papers.length;
  const heroDate = humanDate(data.date);

  return (
    <>
      {/* ---------- Hero ---------- */}
      <header className="pd-hero">
        <div className="mx-auto max-w-[1180px] px-5 pt-10 pb-7 sm:pt-12">
          <div className="pd-kicker">
            PAPER DAILY · 每日论文精选
          </div>

          <h1 className="font-display text-[clamp(26px,4.4vw,40px)] leading-[1.18] font-bold tracking-[-0.02em] text-paper-ink">
            本期精选，{total} 篇值得看
          </h1>

          <p className="mt-2.5 mb-5 text-[15px] text-paper-ink2">
            {data.issue && (
              <>
                <b className="font-semibold text-paper-ink">{data.issue}</b>
                {'　·　'}
              </>
            )}
            报道日 <b className="font-semibold text-paper-ink">{heroDate || data.date}</b>
            {data.axes && <>　·　<b className="font-semibold text-paper-ink">{data.axes}</b></>}
            <span className="ml-2 text-[12px] text-paper-muted">（北京时间）</span>
          </p>

          {/* 统计胶囊：总数 + 三档分布 */}
          <div className="flex flex-wrap gap-3">
            <div className="pd-stat">
              <div className="pd-stat-num !text-paper-accent">{total}</div>
              <div className="pd-stat-lbl">Total</div>
            </div>
            {groups.map(g => (
              <div key={g.def.key} className="pd-stat">
                <div className="pd-stat-num" style={{ color: g.def.colorVar }}>
                  {g.items.length}
                </div>
                <div className="pd-stat-lbl">{g.def.label}</div>
              </div>
            ))}
          </div>

          {data.edNote && (
            <div className="pd-lead mt-4">{data.edNote}</div>
          )}
        </div>
      </header>

      {/* ---------- 锚点导航 ---------- */}
      <nav className="pd-nav" aria-label="版块导航">
        <div className="mx-auto flex max-w-[1180px] gap-2 overflow-x-auto px-5 py-2.5 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          {groups.map(g => {
            const on = active === 'sec-' + g.def.key;
            return (
              <a
                key={g.def.key}
                href={'#sec-' + g.def.key}
                onClick={() => setActive('sec-' + g.def.key)}
                className={'pd-nav-a' + (on ? ' is-on' : '') + (g.items.length ? '' : ' is-empty')}
                style={{ ['--c' as string]: g.def.colorVar }}
                aria-current={on ? 'true' : undefined}
              >
                <span className="pd-nav-dot" />
                {g.def.label}
                <span className="pd-nav-cnt">{g.items.length}</span>
              </a>
            );
          })}
        </div>
      </nav>

      {/* ---------- 正文：分组卡片网格 ---------- */}
      <main ref={mainRef} className="mx-auto max-w-[1180px] px-5 pt-7 pb-2">
        {groups.map(g => (
          <section key={g.def.key} id={'sec-' + g.def.key} className="pd-blk">
            <div className="pd-blk-head">
              <h2 className="font-display text-[19px] font-bold tracking-[-0.01em] text-paper-ink">
                {g.def.label}
              </h2>
              <span className="pd-blk-en">{g.def.en}</span>
              <span className="pd-blk-desc">{g.def.desc}</span>
              <span className="pd-blk-n">{g.items.length} 篇</span>
            </div>

            {g.items.length ? (
              <div className="pd-grid">
                {g.items.map(it => (
                  <PaperCard
                    key={it.index}
                    p={it.paper}
                    n={it.n}
                    color={g.def.colorVar}
                    onRead={() => onRead(it.index)}
                  />
                ))}
              </div>
            ) : (
              <div className="pd-blk-empty">本期暂无该层次条目。</div>
            )}
          </section>
        ))}
      </main>

      {/* ---------- 文末 ---------- */}
      <footer className="pd-foot">
        <div className="mx-auto max-w-[1180px] px-5">
          <div>
            本期共 <b className="text-paper-ink">{total}</b> 篇　·　数据源：
            <a href="https://huggingface.co/papers" target="_blank" rel="noopener noreferrer">HF Daily Papers</a>
            {' · '}
            <a href="https://aihot.virxact.com" target="_blank" rel="noopener noreferrer">AI HOT</a>
            {' · '}
            <a href="https://arxiv.org" target="_blank" rel="noopener noreferrer">arXiv</a>
          </div>
          <div className="mt-1.5">
            分层依据：{TIERS.map(t => t.label).join(' / ')}（按你的偏好画像自动判定）　·　摘要为自动归纳，引用请以原文为准。
          </div>
        </div>
      </footer>
    </>
  );
}
