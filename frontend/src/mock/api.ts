import type { DataBundle } from '../types/data';

/** 生产环境由 index.html 的 <script src="./data.js"> 先行注入；dev 用 public/ 副本 */
export function fetchDaily(): DataBundle {
  return (typeof window !== 'undefined' && window.PAPER_DAILY_DATA) || {};
}
