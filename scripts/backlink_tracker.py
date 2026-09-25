#!/usr/bin/env python3
"""外链资产校验（每周）

为什么不用 Zenodo API 直接查：zenodo.org 对非浏览器 TLS（curl/urllib）返回 403，
cron 里必然失败。改成三条不依赖 Zenodo 直连的判据：
  1) DOI 是否仍解析（doi.org handle API）        → 来源页还活着
  2) DataCite 元数据是否还在 + relatedIdentifiers 数 → 元数据没被撤回
  3) 目标站页面是否 200                          → 链接落地页没挂
链接在 HTML 里的存在性（dofollow）用浏览器抽查，结果记在台账 link_verified 字段。

台账：仓库根 assets.json（脚本上一级），可用 ASSETS_PATH 覆盖。
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.environ.get("ASSETS_PATH") or os.path.join(os.path.dirname(HERE), "assets.json")
UA = "Mozilla/5.0 (compatible; backlink-check/1.1)"


def get(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as exc:
        return exc.code, ""
    except Exception as exc:
        return 0, str(exc)[:120]


GRACE_DAYS = int(os.environ.get("DOI_GRACE_DAYS", "3"))


def _published_age(asset):
    try:
        return (date.today() - datetime.strptime(asset.get("published", ""), "%Y-%m-%d").date()).days
    except Exception:
        return None


def check_doi(asset):
    doi = asset.get("doi")
    if not doi:
        return False, "台账缺 doi 字段"
    status, body = get(f"https://doi.org/api/handles/{doi}")
    if status != 200:
        age = _published_age(asset)
        if age is not None and age <= GRACE_DAYS:
            # Zenodo 异步向 DataCite 注册 DOI，新记录几小时内 404 属正常
            return True, f"⏳ DOI 注册中（发布 {age} 天，宽限 {GRACE_DAYS} 天）：HTTP {status}"
        return False, f"DOI 解析失败 HTTP {status}（DOI 可能已撤回）"
    try:
        vals = json.loads(body).get("values", [])
        target = next((v.get("data", {}).get("value") for v in vals
                       if v.get("type") == "URL"), None) or "(未返回 URL)"
    except Exception:
        target = "(解析响应异常)"
    st2, body2 = get(f"https://api.datacite.org/dois/{doi}")
    related = None
    if st2 == 200:
        try:
            related = len(json.loads(body2).get("data", {}).get("attributes", {})
                          .get("relatedIdentifiers") or [])
        except Exception:
            related = None
    detail = f"DOI 正常 → {target}"
    if related is not None:
        detail += f" / DataCite related={related}"
    return True, detail


def check_target(url):
    status, _ = get(url)
    if status == 200:
        return True, "HTTP 200"
    if status in (403, 429):
        return True, f"HTTP {status}（反爬拦截，非失效；以浏览器抽查为准）"
    return False, f"HTTP {status}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(ASSETS):
        print(f"台账不存在: {ASSETS}")
        return 1
    assets = json.load(open(ASSETS, encoding="utf-8")).get("assets", [])

    rows, bad, stale = [], [], []
    for asset in assets:
        ok, detail = check_doi(asset) if asset.get("kind") == "zenodo" else (False, "未知类型")
        targets = []
        for url in asset.get("targets", []):
            tok, tdet = check_target(url)
            targets.append({"url": url, "ok": tok, "detail": tdet})
            if not tok:
                ok = False
        verified = asset.get("link_verified")
        age = None
        if verified:
            try:
                age = (date.today() - datetime.strptime(verified, "%Y-%m-%d").date()).days
            except Exception:
                age = None
        if age is None or age > 30:
            stale.append(asset.get("name"))
        row = {"name": asset.get("name"), "url": asset.get("url"), "ok": ok, "detail": detail,
               "targets": targets, "link_verified": verified, "verify_age_days": age}
        rows.append(row)
        if not ok:
            bad.append(row)

    if args.json:
        print(json.dumps({"results": rows, "failures": len(bad), "stale_link_checks": stale},
                         ensure_ascii=False, indent=1))
    else:
        print("外链资产校验")
        print("=" * 56)
        for r in rows:
            print(f"{'✅' if r['ok'] else '❌'} {r['name']}")
            print(f"   {r['detail']}")
            for t in r["targets"]:
                print(f"   目标 {'✓' if t['ok'] else '✗'} {t['url']} ({t['detail']})")
        print("=" * 56)
        print(f"资产 {len(rows)} 条，异常 {len(bad)} 条")
        if stale:
            print(f"待浏览器抽查链接存在性（>30 天或未记录）: {len(stale)} 条")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
