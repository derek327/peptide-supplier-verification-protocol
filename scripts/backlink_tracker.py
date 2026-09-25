#!/usr/bin/env python3
"""外链台账 + 每周自动校验

台账 assets.json 记录每条已发布的外链资产（来源、目标页、DOI、发布日期）。
校验：来源记录是否仍公开、我们的域名是否仍在记录元数据里（description/related identifiers）、
目标页是否仍 200。任何一条掉了就报警——外链掉了不查是白做。

用法: python3 backlink_tracker.py [--json]
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets.json")
UA = "Mozilla/5.0 (compatible; backlink-check/1.0)"


def get(url, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as exc:
        return exc.code, ""
    except Exception as exc:
        return 0, str(exc)[:120]


def check_zenodo(asset):
    rec_id = asset["record_id"]
    status, body = get(f"https://zenodo.org/api/records/{rec_id}")
    if status != 200:
        return False, f"记录 API HTTP {status}"
    try:
        data = json.loads(body)
    except Exception:
        return False, "API 返回非 JSON"
    md = data.get("metadata", {})
    blob = json.dumps(md, ensure_ascii=False)
    missing = [u for u in asset["targets"] if u not in blob]
    if missing:
        return False, f"元数据里已丢失链接: {', '.join(missing)}"
    return True, f"公开 / DOI {data.get('doi')} / 链接 {len(asset['targets'])} 条完整"


def check_target(url):
    status, _ = get(url)
    return (status == 200), f"HTTP {status}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    assets = json.load(open(ASSETS, encoding="utf-8"))
    results, bad = [], []
    for asset in assets.get("assets", []):
        kind = asset.get("kind")
        if kind == "zenodo":
            ok, detail = check_zenodo(asset)
        else:
            ok, detail = (False, f"未知资产类型 {kind}")
        targets = []
        for url in asset.get("targets", []):
            tout, tdetail = check_target(url)
            targets.append({"url": url, "ok": tout, "detail": tdetail})
            if not tout:
                ok = False
        row = {"name": asset.get("name"), "kind": kind, "url": asset.get("url"),
               "ok": ok, "detail": detail, "targets": targets}
        results.append(row)
        if not ok:
            bad.append(row)

    if args.json:
        print(json.dumps({"results": results, "failures": len(bad)}, ensure_ascii=False, indent=1))
    else:
        print("外链台账校验")
        print("=" * 52)
        for r in results:
            flag = "✅" if r["ok"] else "❌"
            print(f"{flag} {r['name']}")
            print(f"   来源: {r['url']}")
            print(f"   {r['detail']}")
            for t in r["targets"]:
                print(f"   目标 {'✓' if t['ok'] else '✗'} {t['url']} ({t['detail']})")
        print("=" * 52)
        print(f"合计 {len(results)} 条资产，异常 {len(bad)} 条")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
