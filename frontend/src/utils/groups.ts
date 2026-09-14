import type { Paper } from '../types/data';

/** 亲和度分层：核心 / 相关 / 泛读（对应晨报的「版块」，顺序即优先级） */
export type Tier = 'core' | 'related' | 'scan';

export interface TierDef {
  key: Tier;
  label: string;
  en: string;
  desc: string;
  /** CSS 变量名（在 index.css 中按亮/暗主题定义） */
  colorVar: string;
}

export const TIERS: TierDef[] = [
  {
    key: 'core',
    label: '核心方向',
    en: 'CORE',
    desc: '稀疏视角新视角合成 · 4DGS · 前馈式几何',
    colorVar: 'var(--pd-tier-core)',
  },
  {
    key: 'related',
    label: '相关方向',
    en: 'RELATED',
    desc: '世界模型 · 视频扩散 · 单目几何 · 3D 感知',
    colorVar: 'var(--pd-tier-related)',
  },
  {
    key: 'scan',
    label: '邻近领域',
    en: 'NEARBY',
    desc: '方法可借鉴，非当前主线',
    colorVar: 'var(--pd-tier-scan)',
  },
];

/** 核心方向关键词（命中即 core）：稀疏视角 NVS / 4DGS / 前馈几何基础模型 */
const CORE_KW = [
  'sparse view', 'sparse-view', 'few view', 'few-view', 'few shot view',
  'novel view synthesis', 'view synthesis', 'nvs',
  '4dgs', '4d gs', '4d gaussian', 'dynamic gaussian', 'dynamic scene',
  'gaussian splatting', '3dgs', '3d gs', 'splatting',
  'feed-forward 3d', 'feedforward 3d', 'vggt', 'dust3r', 'mast3r',
  'pose-free', 'unposed', 'uncalibrated', 'camera pose',
  'nerf', 'radiance field', 'radiance fields',
  '三维重建', '新视角', '稀疏视角', '高斯', '动态场景',
];

/** 相关方向关键词 */
const RELATED_KW = [
  'world model', 'world simulator', 'video diffusion', 'video generation',
  'video world model', '4d world', 'explorable', 'cosmos',
  'monocular depth', 'depth estimation', 'depth anything', 'geometric',
  'point cloud', 'point encoder', '3d perception', '3d llm',
  'scene understanding', 'spatial', 'reconstruction',
  '世界模型', '视频生成', '视频扩散', '深度估计', '点云', '空间',
];

/** 提取用于匹配的文本（分类 + 标题 + 中文标题 + 一句话钩子） */
function haystack(p: Paper): string {
  return [
    p.category || '',
    p.title || '',
    p.titleZh || '',
    p.hook || '',
    (p.fields?.task as string) || '',
  ]
    .join(' ')
    .toLowerCase();
}

/** 判定论文所属亲和度层 */
export function tierOf(p: Paper): Tier {
  const t = haystack(p);
  if (CORE_KW.some(k => t.includes(k))) return 'core';
  if (RELATED_KW.some(k => t.includes(k))) return 'related';
  return 'scan';
}

export interface Group {
  def: TierDef;
  items: { paper: Paper; index: number; n: number }[];
}

/**
 * 分组并保持「全局连续编号」——与晨报口径一致：
 * 编号跨组累加，不在组内重置。
 */
export function groupPapers(papers: Paper[]): Group[] {
  const buckets: Record<Tier, { paper: Paper; index: number }[]> = {
    core: [],
    related: [],
    scan: [],
  };
  papers.forEach((p, i) => buckets[tierOf(p)].push({ paper: p, index: i }));

  let n = 0;
  return TIERS.map(def => ({
    def,
    items: buckets[def.key].map(it => ({ ...it, n: ++n })),
  }));
}

const WEEK = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];

/** 2026-09-10 → 2026年9月10日 星期四（人话，不暴露 ISO 串） */
export function humanDate(iso?: string): string {
  if (!iso) return '';
  const m = /^(\d{4})-(\d{1,2})-(\d{1,2})$/.exec(iso.trim());
  if (!m) return iso;
  const [_, y, mo, d] = m;
  const dt = new Date(Number(y), Number(mo) - 1, Number(d));
  if (Number.isNaN(dt.getTime())) return iso;
  return `${y}年${Number(mo)}月${Number(d)}日 ${WEEK[dt.getDay()]}`;
}

/** 稳定色相：由字符串生成抹茶系色相角，用于分类 chip 的细微区分 */
export function hueOf(s: string): number {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  return h % 360;
}
