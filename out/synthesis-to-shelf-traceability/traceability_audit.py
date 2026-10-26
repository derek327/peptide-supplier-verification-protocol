#!/usr/bin/env python3
"""Lot identifier validation and traceability chain audit (documentation only).

Usage:
  python3 traceability_audit.py --lot-id HLX-OEM-2604-A7-W
  python3 traceability_audit.py --audit audit-demo-lots.json --as-of 2026-10-26
  python3 traceability_audit.py --selftest

Rules: R1 identifier validity, R2 stage coverage and mandatory fields, R3 stage ordering,
R4 mass continuity (mass may not increase), R5 retention horizon.
"""

import calendar
import json
import os
from datetime import date, datetime

LOT_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

STAGES = [
    {"stage": "SYN", "name": "Synthesis", "date_field": "synthesis_date",
     "fields": ["lot_id", "crude_mass_mg", "sequence_ref", "operator"], "retention_months": 60},
    {"stage": "PUR", "name": "Purification", "date_field": "purification_date",
     "fields": ["lot_id", "method", "purified_mass_mg", "analyst"], "retention_months": 60},
    {"stage": "QC", "name": "QC release", "date_field": "release_date",
     "fields": ["lot_id", "coa_ref", "purity_result_pct", "released_by"], "retention_months": 60},
    {"stage": "FILL", "name": "Fill and packaging", "date_field": "fill_date",
     "fields": ["lot_id", "units", "mass_per_unit_mg", "label_version"], "retention_months": 60},
    {"stage": "SHIP", "name": "Dispatch and receipt", "date_field": "dispatch_date",
     "fields": ["lot_id", "carrier", "waybill_ref", "quantity_mg", "receipt_signed_by"], "retention_months": 36},
]

STAGE_ORDER = [s["stage"] for s in STAGES]
STAGE_BY = {s["stage"]: s for s in STAGES}


def check_char(payload):
    """Position-weighted base-36 check character over the hyphen-free payload."""
    payload = payload.upper()
    total = 0
    for i, ch in enumerate(payload):
        total += LOT_ALPHABET.index(ch) * (i + 1)
    return LOT_ALPHABET[total % 36]


def compose_lot_id(issuer, site, yymm, seq):
    payload = "{}{}{}{}".format(issuer, site, yymm, seq).upper()
    return "{}-{}-{}-{}-{}".format(issuer.upper(), site.upper(), yymm, seq.upper(), check_char(payload))


def lot_id_parts(value):
    value = (value or "").strip().upper()
    parts = value.split("-")
    if len(parts) != 5:
        return None
    issuer, site, yymm, seq, chk = parts
    if (len(issuer), len(site), len(yymm), len(seq), len(chk)) != (3, 3, 4, 2, 1):
        return None
    if not yymm.isdigit() or not 1 <= int(yymm[2:]) <= 12:
        return None
    for group in (issuer, site, seq, chk):
        if any(c not in LOT_ALPHABET for c in group):
            return None
    return {"issuer": issuer, "site": site, "yymm": yymm, "seq": seq, "check": chk}


def is_valid_lot_id(value):
    p = lot_id_parts(value)
    if not p:
        return False
    payload = p["issuer"] + p["site"] + p["yymm"] + p["seq"]
    return check_char(payload) == p["check"]


def add_months(d, months):
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    day = min(d.day, calendar.monthrange(y, m)[1])
    return date(y, m, day)


def parse_date(value):
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except Exception:
        return None


def num(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).strip())
    except Exception:
        return None


def _empty(value):
    return value is None or (isinstance(value, str) and not value.strip())


def audit_lot(lot, as_of=None, horizon_days=90, mass_tol_pct=0.0):
    """Five-rule documentary audit. Returns verdict + findings + yields."""
    as_of = as_of or date.today()
    findings = []
    events = lot.get("events") or []
    by_stage = {}
    for ev in events:
        by_stage.setdefault(ev.get("stage"), []).append(ev)
    site_code = (lot.get("site_code") or "").strip().upper()

    # R1 identifier validity (structure + check character + site code)
    for ev in events:
        lid = ev.get("lot_id")
        parts = lot_id_parts(lid)
        if not parts or not is_valid_lot_id(lid):
            findings.append("id_invalid:{}".format(ev.get("stage")))
        elif site_code and parts["site"] != site_code:
            findings.append("id_site_mismatch:{}".format(ev.get("stage")))

    # R2 stage coverage and mandatory fields
    for spec in STAGES:
        st = spec["stage"]
        if st not in by_stage:
            findings.append("missing_stage:{}".format(st))
            continue
        for ev in by_stage[st]:
            if _empty(ev.get(spec["date_field"])):
                findings.append("missing_field:{}.{}".format(st, spec["date_field"]))
            for f in spec["fields"]:
                if _empty(ev.get(f)):
                    findings.append("missing_field:{}.{}".format(st, f))

    # R3 stage ordering
    dated = []
    for spec in STAGES:
        for ev in by_stage.get(spec["stage"], []):
            d = parse_date(ev.get(spec["date_field"]))
            if d:
                dated.append((STAGE_ORDER.index(spec["stage"]), d, spec["stage"]))
    dated.sort(key=lambda x: x[0])
    for (_i0, d0, s0), (_i1, d1, s1) in zip(dated, dated[1:]):
        if d1 < d0:
            findings.append("stage_order:{}->{}".format(s0, s1))

    # R4 mass continuity (mass may not increase along the chain)
    points = []
    for spec in STAGES:
        for ev in by_stage.get(spec["stage"], []):
            st = spec["stage"]
            v = None
            if st == "SYN":
                v = num(ev.get("crude_mass_mg"))
            elif st == "PUR":
                v = num(ev.get("purified_mass_mg"))
            elif st == "FILL":
                u, m = num(ev.get("units")), num(ev.get("mass_per_unit_mg"))
                v = u * m if (u is not None and m is not None) else None
            elif st == "SHIP":
                v = num(ev.get("quantity_mg"))
            if v is not None:
                points.append((st, v))
    yields = {}
    for (s0, v0), (s1, v1) in zip(points, points[1:]):
        if v1 > v0 * (1 + mass_tol_pct / 100.0):
            findings.append("mass_gain:{}->{}:{:.3f}->{:.3f}".format(s0, s1, v0, v1))
        if v0 > 0:
            yields["{}_to_{}_pct".format(s0, s1)] = round(v1 / v0 * 100.0, 2)
    if points and points[0][1] > 0:
        yields["overall_pct"] = round(points[-1][1] / points[0][1] * 100.0, 2)

    # R5 retention horizon
    for spec in STAGES:
        for ev in by_stage.get(spec["stage"], []):
            d = parse_date(ev.get(spec["date_field"]))
            if not d:
                continue
            deadline = add_months(d, spec["retention_months"])
            delta = (deadline - as_of).days
            if 0 <= delta <= horizon_days:
                findings.append("retention_soon:{}:{}".format(spec["stage"], deadline.isoformat()))

    return {
        "lot_id": lot.get("lot_id"),
        "verdict": "complete" if not findings else "broken",
        "findings": findings,
        "yields": yields,
        "stages_present": [s for s in STAGE_ORDER if s in by_stage],
    }


def _load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Lot identifier validation and traceability chain audit")
    ap.add_argument("--lot-id", help="validate one lot identifier and decode its segments")
    ap.add_argument("--audit", help="audit a JSON file of lots (see audit-demo-lots.json)")
    ap.add_argument("--as-of", help="reference date for the retention horizon (YYYY-MM-DD)")
    ap.add_argument("--horizon-days", type=int, default=90)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.lot_id:
        parts = lot_id_parts(args.lot_id)
        ok = is_valid_lot_id(args.lot_id)
        print("lot id            :", args.lot_id.strip().upper())
        print("well formed       :", bool(parts))
        print("check character ok:", ok)
        if parts:
            payload = parts["issuer"] + parts["site"] + parts["yymm"] + parts["seq"]
            print("issuer/site/yymm/seq :", parts["issuer"], parts["site"], parts["yymm"], parts["seq"])
            print("expected check    :", check_char(payload), "stated:", parts["check"])
        return 0 if ok else 1

    if args.audit:
        data = _load_json(args.audit)
        lots = data.get("lots", data)
        as_of = parse_date(args.as_of) if args.as_of else None
        bad = 0
        for lot in lots:
            res = audit_lot(lot, as_of=as_of, horizon_days=args.horizon_days)
            expected = lot.get("expected_verdict")
            mark = "!" if expected and expected != res["verdict"] else " "
            if expected and expected != res["verdict"]:
                bad += 1
            print("{} {:<24} {:<8} {}".format(mark, str(res["lot_id"]), res["verdict"],
                                              ", ".join(res["findings"]) or "-"))
            if res["yields"]:
                print("    yields: " + ", ".join("{}={}%".format(k, v) for k, v in res["yields"].items()))
        if any(lot.get("expected_verdict") for lot in lots):
            print("mismatches vs expected_verdict: {}".format(bad))
        return 0 if bad == 0 else 2

    if args.selftest:
        return selftest()

    ap.print_help()
    return 1


def selftest():
    good = compose_lot_id("HLX", "OEM", "2604", "A7")
    assert is_valid_lot_id(good), good
    # any single-character substitution must invalidate the identifier
    for i in range(len(good)):
        if good[i] == "-":
            continue
        repl = "0" if good[i] != "0" else "1"
        tampered = good[:i] + repl + good[i + 1:]
        assert not is_valid_lot_id(tampered), tampered
    assert lot_id_parts("HLX-OEM-2613-A7-Z") is None   # month 13
    assert lot_id_parts("HLX-OEM-2604-A77-Z") is None  # sequence must be 2 chars
    assert not is_valid_lot_id("HLX-OEM-2604-A7-Z")
    demo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audit-demo-lots.json")
    if os.path.exists(demo):
        for lot in _load_json(demo)["lots"]:
            res = audit_lot(lot, as_of=date(2026, 10, 26))
            assert res["verdict"] == lot["expected_verdict"], (res["lot_id"], res["findings"])
            for prefix in lot.get("expected_findings", []):
                assert any(f.startswith(prefix) for f in res["findings"]), (res["lot_id"], prefix, res["findings"])
    print("selftest ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
