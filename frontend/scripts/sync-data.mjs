// 构建前同步每日数据与流程图到 public/（dev/build 共用）
import { cpSync, existsSync, mkdirSync, symlinkSync, rmSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, '..');
const repo = resolve(root, '..');

// 1) data.js -> public/data.js（index.html 的 <script src="./data.js">）
const src = resolve(repo, 'web', 'data.js');
if (existsSync(src)) {
  cpSync(src, resolve(root, 'public', 'data.js'));
  console.log('[sync] web/data.js -> public/data.js');
} else {
  // 兜底空数据，页面会显示「今日无精选」
  mkdirSync(resolve(root, 'public'), { recursive: true });
  writeFileSync(
    resolve(root, 'public', 'data.js'),
    'window.PAPER_DAILY_DATA = { empty: true, reason: "web/data.js 尚未生成，请先运行每日管道。" };\n'
  );
  console.warn('[sync] web/data.js 不存在，写入空数据兜底');
}

// 2) figs 软链到 web/figs（dev 模式图片路径一致；build 产物部署回 web/ 后自然命中）
const figLink = resolve(root, 'figs');
const figTarget = resolve(repo, 'web', 'figs');
try {
  rmSync(figLink, { force: true });
  if (existsSync(figTarget)) symlinkSync(figTarget, figLink, 'dir');
} catch {
  console.warn('[sync] figs 软链失败（不影响 build，仅影响 dev 图片显示）');
}
