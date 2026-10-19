#!/usr/bin/env python3
"""Salt-form / counterion arithmetic (documentation arithmetic only).

Usage:
  python3 salt_form_calc.py --mw 340.38 --sites 3 --counterion tfa --mass 10
  python3 salt_form_calc.py --mw 340.38 --sites 3 --counterion tfa --water 2 --mass 10
  python3 salt_form_calc.py --selftest

salt_mw               = mw + sites * counterion_mw + water * 18.015
peptide_mass_fraction = mw / salt_mw
net_peptide_mg        = mass * peptide_mass_fraction
umol                  = (net_peptide_mg / 1000) / mw * 1e6
"""
import argparse
import sys

COUNTERIONS = {"none": 0.0, "acetate": 59.044, "chloride": 35.453, "tfa": 113.023}
WATER_MW = 18.015


def salt_mass(mw, sites, counterion, water=0):
    if counterion not in COUNTERIONS:
        raise ValueError("counterion must be one of: " + ", ".join(COUNTERIONS))
    if sites < 0 or water < 0:
        raise ValueError("sites and water must be non-negative")
    return mw + sites * COUNTERIONS[counterion] + water * WATER_MW


def report(mw, sites, counterion, water, mass):
    sm = salt_mass(mw, sites, counterion, water)
    frac = mw / sm
    net = mass * frac
    umol = (net / 1000.0) / mw * 1e6
    print(f"salt form                 : {counterion} x {sites}, water x {water}")
    print(f"salt molar mass           : {sm:.2f} g/mol")
    print(f"peptide mass fraction     : {frac * 100:.2f} %")
    print(f"net peptide in {mass:g} mg label : {net:.3f} mg")
    print(f"molar amount              : {umol:.3f} umol")
    print(f"mg salt per umol peptide  : {sm / 1000.0:.4f} mg")


def selftest():
    assert abs(salt_mass(340.38, 0, "none") - 340.38) < 1e-9
    assert abs(salt_mass(340.38, 3, "acetate") - (340.38 + 3 * 59.044)) < 1e-9
    assert abs(salt_mass(100.0, 1, "tfa", 2) - (100.0 + 113.023 + 2 * 18.015)) < 1e-9
    f_acetate = 340.38 / salt_mass(340.38, 3, "acetate")
    f_tfa = 340.38 / salt_mass(340.38, 3, "tfa")
    assert f_tfa < f_acetate < 1.0
    assert 0.49 < f_tfa < 0.51
    assert 100.0 * 340.38 / salt_mass(340.38, 0, "none") == 100.0
    try:
        salt_mass(100.0, 1, "formate")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown counterion must raise")
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mw", type=float)
    ap.add_argument("--sites", type=int, default=0)
    ap.add_argument("--counterion", default="none", choices=list(COUNTERIONS))
    ap.add_argument("--water", type=int, default=0)
    ap.add_argument("--mass", type=float, default=10.0)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.mw is None:
        print("--mw is required (or use --selftest)", file=sys.stderr)
        sys.exit(2)
    else:
        report(a.mw, a.sites, a.counterion, a.water, a.mass)
