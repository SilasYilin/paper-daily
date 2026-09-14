#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
net.py - 统一网络入口（v1.3）

背景：本机 http_proxy/https_proxy 环境变量长期指向 127.0.0.1:7890，但该端口
并非总是开放（用户未启动梯子时）。早期做法是「一律直连」，但直连无法稳定访问
arXiv / Semantic Scholar（IP 被限流）。

现在的策略是**自适应**：
  1. 若环境变量 PAPER_DAILY_PROXY 指定了代理 -> 用它
  2. 否则依次探测常见本地代理端口（7890/7891/...），端口开放即采用
  3. 都没有 -> 直连
  4. 请求失败时自动在「代理 / 直连」之间切换重试

对外只暴露 open_bytes / get_text / get_json，脚本不再各自维护 opener。
"""
from __future__ import annotations

import json
import os
import socket
import time
import urllib.error
import urllib.request

DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# 常见本地代理端口（HTTP 代理）
_PROBE_PORTS = [7890, 7891, 10809, 10808, 1080, 2080]
_PROBE_HOST = "127.0.0.1"

_proxy_cache: str | None | bool = False  # False = 未探测


def _port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    s = socket.socket()
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        return True
    except Exception:  # noqa: BLE001
        return False
    finally:
        s.close()


def detect_proxy() -> str | None:
    """返回可用的 HTTP 代理 URL；无可用代理返回 None。结果进程内缓存。"""
    global _proxy_cache
    if _proxy_cache is not False:
        return _proxy_cache  # type: ignore[return-value]

    env = os.environ.get("PAPER_DAILY_PROXY")
    if env:
        _proxy_cache = env if _port_open(*_split_hostport(env)) else None
        return _proxy_cache

    for p in _PROBE_PORTS:
        if _port_open(_PROBE_HOST, p):
            _proxy_cache = f"http://{_PROBE_HOST}:{p}"
            return _proxy_cache

    _proxy_cache = None
    return None


def _split_hostport(proxy_url: str):
    body = proxy_url.split("://", 1)[-1].split("@")[-1]
    host, _, port = body.partition(":")
    return host or "127.0.0.1", int(port or 80)


def _opener(proxy: str | None):
    handler = urllib.request.ProxyHandler({"http": proxy, "https": proxy} if proxy else {})
    return urllib.request.build_opener(handler)


def _try_order() -> list[str | None]:
    """尝试顺序：可用代理优先，然后直连兜底。"""
    p = detect_proxy()
    return [p, None] if p else [None]


def open_bytes(url: str, timeout: int = 30, headers: dict | None = None,
               retries: int = 2, backoff: float = 2.0) -> bytes:
    """按「代理→直连」顺序尝试，全部失败抛最后一次异常。"""
    hdrs = {"User-Agent": DEFAULT_UA, "Accept": "*/*"}
    if headers:
        hdrs.update(headers)
    last: Exception | None = None
    for attempt in range(retries + 1):
        for proxy in _try_order():
            try:
                req = urllib.request.Request(url, headers=hdrs)
                with _opener(proxy).open(req, timeout=timeout) as r:
                    return r.read()
            except urllib.error.HTTPError as e:
                last = e
                # 4xx（除 429）通常重试无益；429 限流值得换通道重试
                if e.code < 500 and e.code != 429:
                    continue
            except Exception as e:  # noqa: BLE001
                last = e
        if attempt < retries:
            time.sleep(backoff * (attempt + 1))
    raise last if last else RuntimeError("request failed")


class _Resp:
    """兼容 urllib 的 context-manager 响应对象（供旧代码 `.open(...)` 写法使用）。"""

    __slots__ = ("_data",)

    def __init__(self, data: bytes):
        self._data = data

    def read(self) -> bytes:
        return self._data

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def open(req, timeout: int = 30):  # noqa: A001 - 有意与 urllib 命名保持一致
    """兼容旧代码的 `_OPENER.open(req, timeout=..)` 调用形式。"""
    url = getattr(req, "full_url", None) or str(req)
    hdrs: dict = {}
    try:
        for k, v in (getattr(req, "headers", {}) or {}).items():
            if isinstance(v, str):
                hdrs[k] = v
    except Exception:  # noqa: BLE001
        pass
    return _Resp(open_bytes(url, timeout=timeout, headers=hdrs))


def get_text(url: str, timeout: int = 30, headers: dict | None = None,
             retries: int = 2) -> str:
    return open_bytes(url, timeout=timeout, headers=headers, retries=retries).decode(
        "utf-8", errors="ignore")


def get_json(url: str, timeout: int = 30, headers: dict | None = None,
             retries: int = 2) -> dict:
    hdrs = {"Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    return json.loads(open_bytes(url, timeout=timeout, headers=hdrs, retries=retries)
                      .decode("utf-8", errors="ignore"))


if __name__ == "__main__":
    p = detect_proxy()
    print("detected proxy:", p)
    for u in ("https://api.openalex.org/works?per-page=1",
              "https://arxiv.org/abs/2609.11115"):
        try:
            b = open_bytes(u, timeout=25, retries=1)
            print(f"  {u} -> OK {len(b)}B")
        except Exception as e:  # noqa: BLE001
            print(f"  {u} -> FAIL {type(e).__name__}: {str(e)[:70]}")
