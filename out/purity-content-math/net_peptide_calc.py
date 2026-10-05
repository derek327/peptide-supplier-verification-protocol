#!/usr/bin/env python3
"""Net peptide content calculator (documentation arithmetic only).

Usage:
  python3 net_peptide_calc.py --mass 10 --purity 98 --water 5 --counterion 6 --other 0.5 --mw 1419.53
  python3 net_peptide_calc.py --selftest

content_pct    = purity_pct * (100 - water - counterion - other) / 100
net_peptide_mg = label_mass_mg * content_pct / 100
"""
import argparse
import sys

LABEL_MG = 10.0


def content_pct(purity, water, counterion, other):
    non_peptide = water + counterion + other
    if non_peptide < 0 or non_peptide > 100:
        raise ValueError("non-peptide fractions must lie in 0-100 %")
    return purity * (100.0 - non_peptide) / 100.0


def report(mass, purity, water, counterion, other, mw):
    content = content_pct(purity, water, counterion, other)
    net_mg = mass * content / 100.0
    naive = (mass / 1000.0) / mw * 1e6
    corrected = (net_mg / 1000.0) / mw * 1e6
    print(f"peptide content (as-is) : {content:.2f} %")
    print(f"net peptide in {mass:g} mg label mass : {net_mg:.3f} mg")
    print(f"umol if label mass taken as peptide  : {naive:.3f}")
    print(f"umol after content correction        : {corrected:.3f}")
    print(f"overstatement factor                 : {naive / corrected:.3f}")


def selftest():
    assert abs(content_pct(100.0, 0.0, 0.0, 0.0) - 100.0) < 1e-9
    assert abs(content_pct(98.0, 5.0, 6.0, 0.5) - 86.73) < 1e-9
    assert abs(content_pct(100.0, 0.0, 0.0, 0.0)) >= abs(content_pct(99.0, 10.0, 0.0, 0.0))
    try:
        content_pct(98.0, 60.0, 50.0, 0.0)
    except ValueError:
        pass
    else:
        raise AssertionError("non-peptide sum over 100 % must raise")
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mass", type=float, default=LABEL_MG)
    ap.add_argument("--purity", type=float)
    ap.add_argument("--water", type=float)
    ap.add_argument("--counterion", type=float)
    ap.add_argument("--other", type=float, default=0.0)
    ap.add_argument("--mw", type=float)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest or None in (a.purity, a.water, a.counterion, a.mw):
        if not a.selftest:
            print("purity / water / counterion / mw are required (or use --selftest)", file=sys.stderr)
            sys.exit(2)
        selftest()
    else:
        report(a.mass, a.purity, a.water, a.counterion, a.other, a.mw)
