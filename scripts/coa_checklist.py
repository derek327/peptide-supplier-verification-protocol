#!/usr/bin/env python3
"""
CoA verification checklist — CLI.

Checks a Certificate of Analysis (entered interactively or via fields) against
a research-grade acceptance baseline and prints a pass/warn/fail report.

Usage:
    python3 coa_checklist.py                     # interactive
    python3 coa_checklist.py --json coa.json     # from JSON fields

JSON schema example:
{
  "lot": "HP-2409-018",
  "vial_lot": "HP-2409-018",
  "purity": 98.2,
  "purity_threshold": 95.0,
  "identity_method": "LC-MS",
  "detection_wavelength_nm": 214,
  "method_stated": true,
  "dated": true,
  "lab_named": true
}

Exit code: 0 = pass, 1 = warn (review), 2 = fail, 3 = usage error.
"""
import argparse
import json
import sys

MIN_PURITY_DEFAULT = 95.0
REQUIRED_FIELDS = ["lot", "purity"]
WARN_MESSAGES: list[str] = []
FAIL_MESSAGES: list[str] = []


def check(fields: dict) -> int:
    FAIL_MESSAGES.clear()
    WARN_MESSAGES.clear()

    for f in REQUIRED_FIELDS:
        if fields.get(f) in (None, ""):
            FAIL_MESSAGES.append(f"missing required field: {f}")
            return 2

    lot = str(fields["lot"]).strip()
    vial_lot = str(fields.get("vial_lot", "") or "").strip()
    if vial_lot and vial_lot != lot:
        FAIL_MESSAGES.append(
            f"lot mismatch: CoA {lot} vs vial label {vial_lot}"
        )

    threshold = float(fields.get("purity_threshold", MIN_PURITY_DEFAULT))
    purity = float(fields["purity"])
    if purity < threshold:
        FAIL_MESSAGES.append(
            f"purity {purity}% below threshold {threshold}%"
        )
    elif purity < threshold + 2:
        WARN_MESSAGES.append(
            f"purity {purity}% within 2pt of threshold {threshold}%"
        )

    identity = str(fields.get("identity_method", "") or "").lower()
    if identity:
        if "ms" not in identity and "mass" not in identity:
            WARN_MESSAGES.append(
                "identity method is not mass spectrometry: "
                f"{fields['identity_method']}"
            )
    else:
        WARN_MESSAGES.append("identity method not stated on CoA")

    wave = fields.get("detection_wavelength_nm")
    if wave:
        try:
            if int(wave) not in (214, 215, 220):
                WARN_MESSAGES.append(
                    f"detection at {wave} nm — peptide standard is 214-220 nm"
                )
        except (TypeError, ValueError):
            WARN_MESSAGES.append("detection wavelength not numeric")

    for flag, label in (
        ("method_stated", "HPLC method not stated"),
        ("dated", "CoA not dated"),
        ("lab_named", "testing lab not named"),
    ):
        if fields.get(flag) is False:
            WARN_MESSAGES.append(label)

    if FAIL_MESSAGES:
        return 2
    if WARN_MESSAGES:
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="CoA verification checklist")
    ap.add_argument("--json", help="path to JSON file with CoA fields")
    args = ap.parse_args()

    if args.json:
        with open(args.json, encoding="utf-8") as fh:
            fields = json.load(fh)
    else:
        fields = {}
        fields["lot"] = input("CoA lot number: ").strip()
        fields["vial_lot"] = input("Vial label lot number (blank if same): ").strip()
        try:
            fields["purity"] = float(input("Reported HPLC purity (%): "))
        except ValueError:
            print("purity must be numeric", file=sys.stderr)
            return 3
        fields["identity_method"] = input("Identity method (e.g. LC-MS): ").strip()
        fields["method_stated"] = input("HPLC method stated? (y/N): ").lower() == "y"
        fields["dated"] = input("CoA dated? (y/N): ").lower() == "y"
        fields["lab_named"] = input("Testing lab named? (y/N): ").lower() == "y"

    rc = check(fields)
    for m in FAIL_MESSAGES:
        print(f"[FAIL] {m}")
    for m in WARN_MESSAGES:
        print(f"[WARN] {m}")
    if not FAIL_MESSAGES and not WARN_MESSAGES:
        print("[PASS] CoA meets acceptance baseline")
    print(f"verdict: {'pass' if rc == 0 else 'warn-review' if rc == 1 else 'fail'}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
