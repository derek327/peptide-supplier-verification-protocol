#!/usr/bin/env python3
"""构建 Zenodo 数据集包（真数据，可复现）

产出到 out/<record>/：数据文件 + README.md（含方法说明与站点链接）
1) coa-field-taxonomy : CoA 字段分类法（JSON→CSV）
2) reconstitution-tables : 复溶/浓度/剂量换算参考表（纯算术，可复现）
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "out")
DATASETS = os.path.join(ROOT, "datasets")

# 每个记录链接的真实页面（已验证 200）
LINKS = {
    "main": "https://gethelixpeptide.com/products",
    "oem": "https://helixpeptideoem.com/services",
    "supply": "https://helixpeptidesupply.com/catalog",
    "gmp": "https://helixgmppeptides.com/coa-guide",
    "kete": "https://ketebio.com/quality",
    "ruitai": "https://ruitailab.com/quality",
    "jie": "https://jiepeptide.com/quality",
}


def build_coa_taxonomy():
    d = os.path.join(OUT, "coa-field-taxonomy")
    os.makedirs(d, exist_ok=True)
    src = os.path.join(DATASETS, "coa-field-taxonomy-v1.json")
    tax = json.load(open(src, encoding="utf-8"))

    # JSON 副本
    with open(os.path.join(d, "coa-field-taxonomy-v1.json"), "w", encoding="utf-8") as fh:
        json.dump(tax, fh, ensure_ascii=False, indent=2)

    # CSV 扁平化
    rows = []
    for sec in tax["sections"]:
        for f in sec["fields"]:
            rows.append({
                "section_id": sec["id"],
                "section": sec["name"],
                "code": f["code"],
                "label": f["label"],
                "requirement": "required" if f.get("required") else "optional",
                "units": f.get("units") or "",
                "notes": f.get("notes") or "",
            })
    with open(os.path.join(d, "coa-fields.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # 罚分表
    with open(os.path.join(d, "coa-scoring-penalties.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["code", "condition", "penalty_points"])
        w.writeheader()
        for p in tax["scoring"]["penalties"]:
            w.writerow({"code": p["code"], "condition": p["condition"], "penalty_points": p["penalty"]})

    required = sum(1 for r in rows if r["requirement"] == "required")
    readme = f"""# Research Peptide Certificate of Analysis (CoA) Field Taxonomy v1.0

A machine-readable coding scheme for the fields that appear on a research-grade peptide
Certificate of Analysis, with a completeness-scoring rule set.

## Contents

| File | Description |
|---|---|
| `coa-field-taxonomy-v1.json` | Full taxonomy: 5 sections, {len(rows)} fields, scoring rules, banding, and a list of common omissions |
| `coa-fields.csv` | Flattened field list (section, code, label, requirement, units, notes) |
| `coa-scoring-penalties.csv` | Inconsistency penalties applied on top of the completeness count |

## Method

1. Fields were enumerated from the structure of buyer-grade peptide CoA documents
   (identity, purity/assay, identity confirmation, residuals/safety, storage & traceability).
2. Each field is marked `required` ({required} of {len(rows)}) or `optional`, based on whether a buyer
   can verify identity, purity and batch traceability without it.
3. Five internal-consistency penalties are applied on top of completeness, because a CoA can
   be complete and still not auditable (for example, a declared molecular weight that does not
   match the stated sequence).
4. Completeness minus penalties is banded into four procurement interpretations.

## Intended use

- Normalising CoA documents before a procurement review
- Scoring documentation completeness across suppliers on a comparable basis
- Feeding automated extraction / parsing pipelines

## Related work

- Documentation review workflow and worked examples: {LINKS['kete']}
- GMP-oriented CoA guide: {LINKS['gmp']}

## Citation

If you use this taxonomy, cite the DOI of this record. Field naming follows common
pharmaceutical documentation practice; adapt labels to your own QMS where they differ.

## License

CC BY 4.0
"""
    open(os.path.join(d, "README.md"), "w", encoding="utf-8").write(readme)
    return d, rows


def build_reconstitution_tables():
    d = os.path.join(OUT, "reconstitution-tables")
    os.makedirs(d, exist_ok=True)

    vial_mg = [2, 5, 10, 15, 20, 30, 50]
    water_ml = [0.5, 1, 2, 3, 5, 10]
    rows = []
    for mg in vial_mg:
        for ml in water_ml:
            conc_mg_ml = mg / ml
            rows.append({
                "vial_mass_mg": mg,
                "diluent_volume_ml": ml,
                "concentration_mg_per_ml": f"{conc_mg_ml:.4f}",
                "concentration_ug_per_ul": f"{conc_mg_ml:.4f}",   # 1 mg/mL == 1 ug/uL
                "volume_for_100ug_ul": f"{100 / (conc_mg_ml * 1000):.4f}",
                "volume_for_250ug_ul": f"{250 / (conc_mg_ml * 1000):.4f}",
                "volume_for_500ug_ul": f"{500 / (conc_mg_ml * 1000):.4f}",
            })
    with open(os.path.join(d, "reconstitution-reference.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # 单位换算表（纯净数学）
    conv = [
        {"from": "1 mg/mL", "to": "1 ug/uL", "factor": 1, "note": "mass-per-volume equality"},
        {"from": "1 mg", "to": "1000 ug", "factor": 1000, "note": ""},
        {"from": "1 mL", "to": "1000 uL", "factor": 1000, "note": ""},
        {"from": "1 % (w/v)", "to": "10 mg/mL", "factor": 10, "note": "1 g per 100 mL"},
        {"from": "IU (peptide)", "to": "not convertible", "factor": "", "note": "IU requires a substance-specific bioassay definition; do not convert to mass"},
        {"from": "1 Da", "to": "1 g/mol", "factor": 1, "note": ""},
    ]
    with open(os.path.join(d, "unit-conversions.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["from", "to", "factor", "note"])
        w.writeheader()
        w.writerows(conv)

    readme = f"""# Peptide Reconstitution and Unit-Conversion Reference Tables

Deterministic reference tables for laboratory reconstitution arithmetic. Every value is
computed from the two inputs (vial mass, diluent volume) by the formulas below — no fitted
or observed data is involved, so the tables can be regenerated exactly.

## Contents

| File | Description |
|---|---|
| `reconstitution-reference.csv` | {len(rows)} combinations: vial mass 2-50 mg x diluent volume 0.5-10 mL, with concentration and the volume needed for 100/250/500 ug |
| `unit-conversions.csv` | Mass/volume unit conversions, including the case that must *not* be converted |

## Formulas

```
concentration (mg/mL) = vial mass (mg) / diluent volume (mL)
concentration (ug/uL) = concentration (mg/mL)          # 1 mg/mL == 1 ug/uL
volume (uL) for dose D (ug) = D / concentration (ug/uL)
```

## Limits of these tables

- They describe arithmetic only. They are not dosing guidance and carry no clinical meaning.
- Concentration assumes complete dissolution and a diluent that does not change the peptide's
  solubility; bacteriostatic vs sterile water changes preservative content, not this arithmetic.
- IU cannot be converted to mass without a substance-specific bioassay definition; the
  conversion table marks this explicitly rather than supplying a factor.
- Reconstituted stability depends on the peptide, the diluent and storage temperature and is
  outside the scope of these tables.

## Related tools and documentation

- Catalog and product documentation: {LINKS['supply']}
- Research catalog: {LINKS['main']}

## Citation

Cite the DOI of this record. Recomputation from the formulas above is sufficient to reproduce
every row.

## License

CC BY 4.0
"""
    open(os.path.join(d, "README.md"), "w", encoding="utf-8").write(readme)
    return d, len(rows)


def mkt(profile, dH_kj):
    """Mean kinetic temperature of a [(temp_C, hours), ...] profile."""
    import math
    R = 8.314462618
    dH = dH_kj * 1000.0
    num = 0.0
    den = 0.0
    for temp_c, hours in profile:
        k = temp_c + 273.15
        num += math.exp(-dH / (R * k)) * hours
        den += hours
    return dH / R / (-math.log(num / den)) - 273.15


def build_temperature_excursion():
    """温度偏移：MKT 参考表 + 分诊矩阵（全部由公式算出，无实测/拟合数据）"""
    import csv as _csv
    d = os.path.join(OUT, "temperature-excursion-mkt")
    os.makedirs(d, exist_ok=True)

    BASE_H = 48.0          # 运输时长 48 h
    band = (2.0, 8.0)      # 声明运输温度带
    profiles = [
        # (id, base_C, exc_C, exc_h)
        ("C01", 5.0, None, 0.0),
        ("C02", 5.0, 10.0, 6.0),
        ("C03", 5.0, 15.0, 1.0),
        ("C04", 5.0, 15.0, 6.0),
        ("C05", 5.0, 15.0, 24.0),
        ("C06", 5.0, 22.0, 1.0),
        ("C07", 5.0, 22.0, 6.0),
        ("C08", 5.0, 22.0, 24.0),
        ("C09", 5.0, 22.0, 48.0),
        ("C10", 5.0, 30.0, 1.0),
        ("C11", 5.0, 30.0, 6.0),
        ("C12", 5.0, 30.0, 24.0),
        ("C13", 5.0, 40.0, 1.0),
        ("C14", 5.0, 40.0, 6.0),
        ("F01", -20.0, None, 0.0),
        ("F02", -20.0, -5.0, 6.0),
        ("F03", -20.0, 0.0, 6.0),
        ("F04", -20.0, 5.0, 2.0),
        ("F05", -20.0, 5.0, 24.0),
        ("F06", -20.0, 22.0, 2.0),
        ("F07", -20.0, 22.0, 24.0),
        ("F08", -20.0, 30.0, 6.0),
        ("F09", 5.0, -10.0, 6.0),
        ("F10", 5.0, -20.0, 24.0),
    ]

    rows = []
    for pid, base, exc, exc_h in profiles:
        prof = [(base, BASE_H - exc_h)]
        if exc is not None and exc_h:
            prof.append((exc, exc_h))
        temps = [t for t, _ in prof]
        oob = sum(h for t, h in prof if not (band[0] <= t <= band[1]))
        mean = sum(t * h for t, h in prof) / BASE_H
        rows.append({
            "profile_id": pid,
            "base_temp_c": f"{base:g}",
            "excursion_temp_c": "" if exc is None else f"{exc:g}",
            "excursion_hours": f"{exc_h:g}",
            "total_hours": f"{BASE_H:g}",
            "max_temp_c": f"{max(temps):g}",
            "min_temp_c": f"{min(temps):g}",
            "arithmetic_mean_c": f"{mean:.2f}",
            "mkt_dH83_144_kJ_mol_c": f"{mkt(prof, 83.144):.2f}",
            "mkt_dH62_8_kJ_mol_c": f"{mkt(prof, 62.8):.2f}",
            "hours_outside_2_8_band": f"{oob:g}",
        })

    with open(os.path.join(d, "mkt-reference.csv"), "w", newline="", encoding="utf-8") as fh:
        w = _csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # 分诊矩阵（与协议文档同表）
    triage = [
        ("+2 to +8 C product", "< 15", "<= 2", "record, release"),
        ("+2 to +8 C product", "< 15", "2-24", "record, release"),
        ("+2 to +8 C product", "< 15", "> 24", "record, quarantine, request analytical re-check"),
        ("+2 to +8 C product", "15-25", "<= 2", "record, release"),
        ("+2 to +8 C product", "15-25", "2-24", "record, quarantine"),
        ("+2 to +8 C product", "15-25", "> 24", "quarantine, request re-check + replacement assessment"),
        ("+2 to +8 C product", "> 25", "<= 2", "quarantine"),
        ("+2 to +8 C product", "> 25", "2-24", "quarantine"),
        ("+2 to +8 C product", "> 25", "> 24", "reject on documentation grounds"),
        ("-20 C product", "< 0", "<= 2", "record, release"),
        ("-20 C product", "< 0", "2-24", "record, release"),
        ("-20 C product", "< 0", "> 24", "record, release"),
        ("-20 C product", "0-25", "<= 2", "record, quarantine"),
        ("-20 C product", "0-25", "2-24", "quarantine, re-check"),
        ("-20 C product", "0-25", "> 24", "reject on documentation grounds"),
        ("-20 C product", "> 25", "<= 2", "quarantine"),
        ("-20 C product", "> 25", "2-24", "reject"),
        ("-20 C product", "> 25", "> 24", "reject"),
    ]
    with open(os.path.join(d, "excursion-triage-matrix.csv"), "w", newline="", encoding="utf-8") as fh:
        w = _csv.DictWriter(fh, fieldnames=["declared_product_band", "peak_temp_c",
                                            "duration_outside_band_h", "documentation_action"])
        w.writeheader()
        for decl, peak, dur, act in triage:
            w.writerow({"declared_product_band": decl, "peak_temp_c": peak,
                        "duration_outside_band_h": dur, "documentation_action": act})

    # 常识自检（纯算术，跑不过就不出版）
    const = mkt([(5.0, 48.0)], 83.144)
    assert abs(const - 5.0) < 1e-6, const
    spike = next(r for r in rows if r["profile_id"] == "C12")
    assert float(spike["mkt_dH83_144_kJ_mol_c"]) > float(spike["arithmetic_mean_c"]), spike
    warm_dh_hi = next(r for r in rows if r["profile_id"] == "C11")
    assert float(warm_dh_hi["mkt_dH83_144_kJ_mol_c"]) != float(warm_dh_hi["mkt_dH62_8_kJ_mol_c"])

    readme = f"""# Temperature Excursion Reference Tables: MKT Profiles and Triage Matrix

Deterministic reference tables for reviewing a shipment temperature trace against a declared
+2 to +8 &deg;C transport range. Every number is computed from the formulas below and a stated
activation energy &mdash; no observed, fitted or measured data is involved, so every row can be
regenerated exactly.

## Contents

| File | Description |
|---|---|
| `mkt-reference.csv` | {len(rows)} profiles (48 h transit: a baseline temperature plus one excursion of stated magnitude and duration), with max/min recorded temperature, arithmetic mean, mean kinetic temperature at two activation energies, and hours outside the +2 to +8 &deg;C band |
| `excursion-triage-matrix.csv` | {len(triage)} rows: declared product band x peak temperature x duration outside band, mapped to a documentation action |

## Formulas

```
MKT = (dH / R) / ( -ln( SUM( exp(-dH/(R*Ti)) * dti ) / SUM(dti) ) )

dH        assumed activation energy: 83.144 kJ/mol (conventional) or 62.8 kJ/mol
R         8.314462618 J/(mol*K)
Ti        interval temperature, kelvin
dti       interval duration, hours
```

Invariance checks applied before publication: a constant-temperature profile returns that
temperature exactly; a hot spike raises MKT above the arithmetic mean; changing dH changes
MKT.

## What these tables do not say

- They describe arithmetic only. They are not storage instructions, dosing guidance or
  clinical information, and they say nothing about any specific peptide.
- **MKT hides peaks.** A one-hour excursion to 40 &deg;C can produce the same MKT as a flat
  profile. Always report maximum recorded temperature and duration outside band next to MKT.
- **The activation energy is a modelling assumption, not a measured property.** Two
  laboratories using different dH values disagree on MKT for the same trace; state which was
  used. The two columns here exist to make that sensitivity visible.
- Whether a molecule changed (aggregation, oxidation, deamidation, moisture uptake) is an
  assay question. These tables cannot answer it and do not claim to.
- For an illustrated triage walkthrough and the full documentation file specification, see
  the companion protocol document in this repository.

## Related documentation

- GMP-oriented quality documentation and CoA guidance: {LINKS['gmp']}
- Catalog and shipping documentation: {LINKS['supply']}

## Citation

Cite the DOI of this record, including the dH value used. Recomputation from the formulas
above reproduces every row.

## License

CC BY 4.0
"""
    open(os.path.join(d, "README.md"), "w", encoding="utf-8").write(readme)
    return d, len(rows), len(triage)


def build_purity_content_math():
    """纯度 vs 肽净含量：质量平衡换算表 + 含水量敏感性表 + 可复算脚本。

    全部由输入参数经公式算出，无实测/拟合数据；出版前做不变量自检。
    """
    d = os.path.join(OUT, "purity-content-math")
    os.makedirs(d, exist_ok=True)

    LABEL_MG = 10.0
    # (id, peptide, free-peptide molar mass g/mol, area-%, water-%, counterion-%, counterion, other non-peptide %)
    samples = [
        ("P01", "GHK (free peptide)",   340.38, 99.5, 2.0,  0.0,  "none",     0.0),
        ("P02", "GHK (free peptide)",   340.38, 99.5, 4.0,  0.0,  "none",     0.0),
        ("P03", "BPC-157",             1419.53, 98.0, 5.0,  6.0,  "acetate",  0.5),
        ("P04", "BPC-157",             1419.53, 98.0, 6.0,  8.0,  "acetate",  0.5),
        ("P05", "BPC-157",             1419.53, 97.0, 8.0, 10.0,  "TFA",      1.0),
        ("P06", "Semaglutide",         4113.58, 95.0, 5.0,  6.0,  "acetate",  0.5),
        ("P07", "Semaglutide",         4113.58, 92.0, 5.0,  6.0,  "acetate",  0.5),
        ("P08", "Retatrutide",         4731.30, 99.0, 0.5,  0.0,  "none",     0.0),
        ("P09", "Tirzepatide",         4813.51, 99.0, 3.0, 12.0,  "TFA",      0.0),
        ("P10", "Tirzepatide",         4813.51, 99.0, 10.0, 0.0,  "none",     0.0),
        ("P11", "reference peptide",   1000.00, 90.0, 10.0, 10.0, "TFA",      2.0),
        ("P12", "reference peptide",   1000.00, 98.5, 3.0,  4.0,  "acetate",  0.2),
    ]

    def content_pct(purity, water, counterion, other):
        return purity * (100.0 - water - counterion - other) / 100.0

    rows = []
    for sid, name, mw, purity, water, ci, ci_name, other in samples:
        content = content_pct(purity, water, ci, other)
        net_mg = LABEL_MG * content / 100.0
        naive_umol = (LABEL_MG / 1000.0) / mw * 1e6
        corr_umol = (net_mg / 1000.0) / mw * 1e6
        rows.append({
            "sample_id": sid,
            "peptide": name,
            "free_peptide_molar_mass_g_per_mol": f"{mw:.2f}",
            "label_mass_mg": f"{LABEL_MG:g}",
            "hplc_area_pct": f"{purity:.1f}",
            "water_pct_kf": f"{water:.1f}",
            "counterion": ci_name,
            "counterion_pct": f"{ci:.1f}",
            "other_nonpeptide_pct": f"{other:.1f}",
            "peptide_content_pct_as_is": f"{content:.2f}",
            "net_peptide_mg": f"{net_mg:.3f}",
            "umol_if_label_taken_as_peptide": f"{naive_umol:.3f}",
            "umol_after_content_correction": f"{corr_umol:.3f}",
            "overstatement_factor": f"{naive_umol / corr_umol:.3f}",
        })

    with open(os.path.join(d, "net-peptide-content.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # 含水量敏感性：固定纯度 98.0 %、无抗衡离子，含水量 0→12 %
    sens = []
    for water in [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0]:
        content = content_pct(98.0, water, 0.0, 0.0)
        sens.append({
            "water_pct_kf": f"{water:.1f}",
            "hplc_area_pct": "98.0",
            "peptide_content_pct_as_is": f"{content:.2f}",
            "net_peptide_mg_per_10mg_label": f"{LABEL_MG * content / 100.0:.3f}",
        })
    with open(os.path.join(d, "content-vs-water.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(sens[0].keys()))
        w.writeheader()
        w.writerows(sens)

    # 出版前不变量自检（跑不过就不产出）
    assert abs(content_pct(100.0, 0.0, 0.0, 0.0) - 100.0) < 1e-9
    assert abs(content_pct(99.0, 0.5, 0.0, 0.0) - 98.505) < 1e-9
    contents = [float(r["peptide_content_pct_as_is"]) for r in sens]
    assert all(b < a for a, b in zip(contents, contents[1:])), contents
    for r in rows:
        assert float(r["net_peptide_mg"]) < LABEL_MG
        assert float(r["overstatement_factor"]) > 1.0
        assert abs(round(float(r["peptide_content_pct_as_is"]), 2)
                   - round(content_pct(float(r["hplc_area_pct"]), float(r["water_pct_kf"]),
                                      float(r["counterion_pct"]), float(r["other_nonpeptide_pct"])), 2)) < 1e-6

    script = '''#!/usr/bin/env python3
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
'''
    open(os.path.join(d, "net_peptide_calc.py"), "w", encoding="utf-8").write(script)

    readme = f"""# Purity vs Peptide Content: Net-Peptide Mass Reference Tables

Deterministic reference tables and a calculation script for the arithmetic that relates a
chromatographic purity figure (area-%) to the net peptide in a weighed sample. Every value is
computed from the two formulas below using the stated inputs &mdash; no observed or fitted data
is involved, so every row can be recomputed exactly.

## Contents

| File | Description |
|---|---|
| `net-peptide-content.csv` | {len(rows)} samples (10 mg label mass) across free-base, acetate and TFA forms: purity, water by Karl Fischer, counterion and other non-peptide fractions, resulting content, net peptide mass, and the molar overstatement that results from taking the label mass as peptide |
| `content-vs-water.csv` | {len(sens)} points: content at constant 98.0 % purity as water content runs 0 &ndash; 12 % |
| `net_peptide_calc.py` | Command-line calculator for any input set, with a `--selftest` that checks the invariance rules below |

## Formulas

```
content_pct    = purity_pct * (100 - water_pct - counterion_pct - other_nonpeptide_pct) / 100
net_peptide_mg = label_mass_mg * content_pct / 100
umol           = (net_peptide_mg / 1000) / molar_mass_g_per_mol * 1e6   # free-peptide molar mass
```

## Invariance checks applied before publication

A material at 100 % purity with no water, counterion or other non-peptide fraction returns
exactly 100 % content; the dry free-base case 99.0 % purity / 0.5 % water returns 98.505 %;
content falls strictly as water content rises at constant purity; and every published row yields
less peptide than the label mass, so the overstatement factor exceeds 1 in every case.

## What these tables do not say

- They describe documentation arithmetic. They are not handling, storage or dosing guidance and
  say nothing about any specific peptide.
- The multiplicative model assumes impurities distribute proportionally between the weighed
  powder and the detected chromatographic peaks. It is a review estimate, **not a measured
  content**; a stated content should come from an independent assay (quantitative NMR, amino
  acid analysis, nitrogen determination or UV against a stated coefficient).
- The method's reporting threshold caps the correction: a purity method that cannot see below
  1 % cannot account for low-level related substances that still occupy mass.
- Counterion stoichiometry is not necessarily one-to-one; a polybasic peptide may carry more
  than one trifluoroacetate per molecule.
- Water content is a snapshot. A hygroscopic solid takes up moisture between analysis and
  weighing, so the correction drifts with handling.
- Molar masses are sequence-derived values for the free peptide; counterion and water add mass,
  which is exactly why content is measured rather than inferred from the label.

## Related documentation

- Quality documentation structure, specification fields and review workflow: https://gethelixpeptide.com/quality
- Product-level documentation and batch records: {LINKS['main']}

## Citation

Cite the DOI of this record. Recomputation from the formulas above reproduces every row.

## License

CC BY 4.0
"""
    open(os.path.join(d, "README.md"), "w", encoding="utf-8").write(readme)
    return d, len(rows), len(sens)


COUNTERIONS = {
    # name: (molar mass of the counterion moiety, label)
    "none": (0.0, "free base"),
    "acetate": (59.044, "acetate"),
    "chloride": (35.453, "chloride"),
    "tfa": (113.023, "trifluoroacetate"),
}
WATER_MW = 18.015


def _salt_mass(peptide_mw, sites, counterion, water=0):
    return peptide_mw + sites * COUNTERIONS[counterion][0] + water * WATER_MW


def build_counterion_salt_forms():
    """盐型/反离子：盐摩尔质量、肽质量分数、标签质量漂移表（纯算术，可复算）。"""
    d = os.path.join(OUT, "counterion-salt-forms")
    os.makedirs(d, exist_ok=True)

    # (id, peptide, free-peptide molar mass, protonatable basic centres)
    # 碱基数按序列中 N 端 + Arg/Lys/His 侧链计；盐形成条件下实际结合数由工艺决定，
    # 表内按整数化学计量建模（见 README 局限）。
    molecules = [
        ("GHK", "GHK (Gly-His-Lys)", 340.38, 3),
        ("BPC157", "BPC-157", 1419.53, 2),
    ]
    forms = [
        ("free base", "none", 0, 0),
        ("acetate", "acetate", None, 0),          # None = 按位点数满结合
        ("chloride", "chloride", None, 0),
        ("trifluoroacetate", "tfa", None, 0),
        ("trifluoroacetate dihydrate", "tfa", None, 2),
    ]

    rows = []
    for mid, name, mw, sites in molecules:
        for form_label, ci, bound, water in forms:
            n = 0 if ci == "none" else (sites if bound is None else bound)
            salt_mw = _salt_mass(mw, n, ci, water)
            frac = mw / salt_mw
            rows.append({
                "case_id": mid,
                "peptide": name,
                "free_peptide_molar_mass_g_per_mol": f"{mw:.2f}",
                "protonatable_basic_centres": sites,
                "salt_form": form_label,
                "counterion": COUNTERIONS[ci][1],
                "counterions_bound": n,
                "water_molecules": water,
                "salt_molar_mass_g_per_mol": f"{salt_mw:.2f}",
                "peptide_mass_fraction_pct": f"{frac * 100:.2f}",
                "mg_salt_per_umol_peptide": f"{salt_mw / 1000.0:.4f}",
                "net_peptide_mg_per_10mg_label": f"{10.0 * frac:.3f}",
            })
    with open(os.path.join(d, "salt-form-mass-balance.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # 标签质量漂移：同样 10 mg 称量，换盐型后肽质量/摩尔量变化（以醋酸盐为基准）
    drift = []
    for mid, name, mw, sites in molecules:
        base_peptide = 10.0 * mw / _salt_mass(mw, sites, "acetate")
        for _, ci in (("acetate form", "acetate"), ("chloride form", "chloride"),
                      ("TFA form", "tfa")):
            salt_mw = _salt_mass(mw, sites, ci)
            peptide_mg = 10.0 * mw / salt_mw
            umol = (peptide_mg / 1000.0) / mw * 1e6
            drift.append({
                "case_id": mid,
                "peptide": name,
                "salt_form": ci,
                "label_mass_mg": "10",
                "salt_molar_mass_g_per_mol": f"{salt_mw:.2f}",
                "net_peptide_mg": f"{peptide_mg:.3f}",
                "umol_peptide": f"{umol:.3f}",
                "peptide_mg_change_vs_acetate_pct": f"{(peptide_mg / base_peptide - 1) * 100:+.1f}",
            })
    with open(os.path.join(d, "label-mass-drift.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(drift[0].keys()))
        w.writeheader()
        w.writerows(drift)

    # 位点数敏感性：同一 1200 g/mol 骨架，0-4 个位点，醋酸盐 vs TFA
    sens = []
    for n in range(0, 5):
        row = {"protonatable_basic_centres": n, "free_peptide_molar_mass_g_per_mol": "1200.00"}
        for ci in ("acetate", "tfa"):
            salt_mw = _salt_mass(1200.0, n, ci)
            row[f"{ci}_salt_molar_mass_g_per_mol"] = f"{salt_mw:.2f}"
            row[f"{ci}_peptide_mass_fraction_pct"] = f"{1200.0 / salt_mw * 100:.2f}"
        row["tfa_fraction_relative_to_acetate_pct"] = (
            f"{(1200.0 / _salt_mass(1200.0, n, 'tfa')) / (1200.0 / _salt_mass(1200.0, n, 'acetate')) * 100:.1f}"
        )
        sens.append(row)
    with open(os.path.join(d, "counterion-sensitivity.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(sens[0].keys()))
        w.writeheader()
        w.writerows(sens)

    # 出版前不变量自检
    assert abs(_salt_mass(340.38, 0, "none") - 340.38) < 1e-9
    assert abs(_salt_mass(340.38, 3, "acetate") - (340.38 + 3 * 59.044)) < 1e-9
    ghk_tfa = 340.38 / _salt_mass(340.38, 3, "tfa") * 100
    assert 49.0 < ghk_tfa < 51.0, ghk_tfa
    ghk_ac = 340.38 / _salt_mass(340.38, 3, "acetate") * 100
    assert ghk_tfa < ghk_ac, (ghk_tfa, ghk_ac)
    prev = 101.0
    for n in range(0, 5):
        frac = 1200.0 / _salt_mass(1200.0, n, "tfa") * 100
        assert frac < prev, (n, frac)
        prev = frac
    assert all(float(r["peptide_mass_fraction_pct"]) <= 100.0 for r in rows)
    assert all(float(r["net_peptide_mg_per_10mg_label"]) <= 10.0 for r in rows)
    for mid, _name, _mw, _sites in molecules:
        tfa = next(float(r["peptide_mass_fraction_pct"]) for r in rows
                   if r["case_id"] == mid and r["salt_form"] == "trifluoroacetate")
        di = next(float(r["peptide_mass_fraction_pct"]) for r in rows
                  if r["case_id"] == mid and r["salt_form"] == "trifluoroacetate dihydrate")
        assert di < tfa, (mid, di, tfa)
    # 漂移表：TFA 在同样称量下肽质量必须低于醋酸盐，GHK 降幅应为两位数
    ghk_drift = {r["salt_form"]: float(r["net_peptide_mg"]) for r in drift if r["case_id"] == "GHK"}
    assert ghk_drift["tfa"] < ghk_drift["acetate"] < ghk_drift["chloride"]
    assert abs((ghk_drift["tfa"] / ghk_drift["acetate"] - 1) * 100 + 23.7) < 1.0

    script = '''#!/usr/bin/env python3
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
'''
    open(os.path.join(d, "salt_form_calc.py"), "w", encoding="utf-8").write(script)

    readme = f"""# Counterion and Salt Form: Mass-Balance Reference Tables

Deterministic reference tables for the arithmetic that connects a peptide's salt form to the
peptide mass and molar quantity in a weighed sample. Every value is computed from the formula
below and the stated inputs &mdash; no observed or fitted data is involved, so every row can be
regenerated exactly.

## Contents

| File | Description |
|---|---|
| `salt-form-mass-balance.csv` | {len(rows)} rows: GHK (three protonatable basic centres) and BPC-157 (two) as free base, acetate, chloride, trifluoroacetate and trifluoroacetate dihydrate &mdash; salt molar mass, peptide mass fraction, mg of salt per &micro;mol of peptide, net peptide in a 10 mg label |
| `label-mass-drift.csv` | {len(drift)} rows: the same 10 mg weighed mass expressed as acetate, chloride and TFA, with net peptide mass, molar amount and percentage change against the acetate form |
| `counterion-sensitivity.csv` | {len(sens)} rows: a 1200 g/mol backbone with 0&ndash;4 protonatable centres, acetate versus TFA, showing how the counterion penalty scales with charge count |
| `salt_form_calc.py` | Command-line calculator for any input set, with a `--selftest` |

## Formula

```
salt_molar_mass       = peptide_molar_mass + n * counterion_molar_mass + w * 18.015
peptide_mass_fraction = peptide_molar_mass / salt_molar_mass
net_peptide_mg        = weighed_mg * peptide_mass_fraction
moles                 = (net_peptide_mg / 1000) / peptide_molar_mass
```

Counterion molar masses used: acetate 59.044, chloride 35.453, trifluoroacetate 113.023
g/mol; water 18.015 g/mol.

## Invariance checks applied before publication

A free base with no bound water returns exactly 100 % peptide fraction; the salt molar mass
equals the free peptide plus the stated counterion and water masses; the peptide fraction falls
strictly as the number of bound counterions rises; at equal charge count the TFA fraction is
lower than the acetate fraction; and no salt row yields more peptide than the label mass.
The GHK tri-TFA fraction is asserted to lie between 49 and 51 %, and the TFA-versus-acetate
peptide-mass difference for GHK to within one percentage point of 23.8 %.

## What these tables do not say

- They are documentation arithmetic. They are not handling, storage, analytical or dosing
  guidance and say nothing about the behaviour of any peptide in any biological system.
- **Integral stoichiometry is a modelling assumption.** Real materials can carry fractional or
  mixed counterion loads, and the number bound depends on the isolation pH and ion-pairing
  conditions. The certificate should state the actual counterion content; substitute it for
  `n` rather than assuming the maximum.
- The peptide molar mass must refer to the free peptide, not the salt. Using a salt molar mass
  in the denominator double-counts the counterion.
- Water content moves with handling. A value measured at release is a snapshot, not a constant.
- The tables do not predict purity, stability, solubility or chromatographic behaviour; they
  only convert a stated composition into mass and moles.

## Related documentation

- Catalog and product documentation: {LINKS['supply']}
- Product-level documentation and batch records: https://helixpeptidesupply.com/products

## Citation

Cite the DOI of this record. Recomputation from the formula above reproduces every row.

## License

CC BY 4.0
"""
    open(os.path.join(d, "README.md"), "w", encoding="utf-8").write(readme)
    return d, len(rows), len(drift), len(sens)


SCRIPT_CORE = r'''
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
'''

SCRIPT_CLI = r'''

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
'''


def build_synthesis_to_shelf_traceability():
    """合成→货架溯源：lot ID 方案、五段记录 schema、示例批次事件、可跑审计与不变量自检。"""
    d = os.path.join(OUT, "synthesis-to-shelf-traceability")
    os.makedirs(d, exist_ok=True)

    ns = {}
    exec(SCRIPT_CORE, ns)  # 与发布脚本共用同一份逻辑源，避免断言与交付物漂移
    compose = ns["compose_lot_id"]
    audit_lot = ns["audit_lot"]
    check_char = ns["check_char"]
    from datetime import date as _date

    # ---- 1. lot ID 方案
    example_payload = "HLXOEM2604A7"
    chk = check_char(example_payload)
    scheme_rows = [
        ("issuer", "HLX", 3, "A-Z0-9", "Identifier issuer (supplier or brand owner)", "Fixed per issuer, never reused"),
        ("site", "OEM", 3, "A-Z0-9", "Manufacture or fill site code", "Must equal the site named on the record"),
        ("yymm", "2604", 4, "0-9", "Year and month of synthesis", "MM must be 01-12"),
        ("seq", "A7", 2, "A-Z0-9", "Per-month sequence, base 36", "Never re-used; re-work appends .R<n>"),
        ("check", chk, 1, "A-Z0-9", "Position-weighted base-36 check character", "sum(value(char_i)*(i+1)) mod 36 over issuer+site+yymm+seq"),
    ]
    with open(os.path.join(d, "lot-id-scheme.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["segment", "example", "length", "alphabet", "meaning", "rule"])
        w.writeheader()
        for seg, ex, ln, al, mean, rule in scheme_rows:
            w.writerow({"segment": seg, "example": ex, "length": ln, "alphabet": al,
                        "meaning": mean, "rule": rule})

    # ---- 2. 五段记录 schema
    labels = {
        "lot_id": "Lot identifier", "crude_mass_mg": "Crude mass (mg)",
        "sequence_ref": "Sequence reference", "operator": "Operator ID",
        "method": "Purification method", "purified_mass_mg": "Purified mass (mg)",
        "analyst": "Analyst ID", "coa_ref": "CoA document reference",
        "purity_result_pct": "Reported purity (%)", "released_by": "Release approver ID",
        "units": "Units filled", "mass_per_unit_mg": "Mass per unit (mg)",
        "label_version": "Label document version", "carrier": "Carrier",
        "waybill_ref": "Waybill reference", "quantity_mg": "Dispatched quantity (mg)",
        "receipt_signed_by": "Receipt signature ID",
    }
    evidence = {
        "SYN": "production record", "PUR": "production record", "QC": "CoA / release record",
        "FILL": "packaging record", "SHIP": "logistics document",
    }
    schema_rows = []
    for spec in ns["STAGES"]:
        for f in spec["fields"]:
            schema_rows.append({
                "stage": spec["stage"], "stage_name": spec["name"],
                "date_field": spec["date_field"], "field_code": f,
                "field_label": labels[f], "requirement": "required",
                "evidence_type": evidence[spec["stage"]],
                "retention_months_example": spec["retention_months"],
            })
    with open(os.path.join(d, "traceability-record-schema.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(schema_rows[0].keys()))
        w.writeheader()
        w.writerows(schema_rows)

    # ---- 3. 示例批次（长格式）
    def events(lot_id, dsyn, dpur, dqc, dfill, dship, mcrude, mpur, units, mpu, qty):
        return [
            {"stage": "SYN", "lot_id": lot_id, "synthesis_date": dsyn, "crude_mass_mg": mcrude,
             "sequence_ref": "SEQ-GHK-01", "operator": "OP-114"},
            {"stage": "PUR", "lot_id": lot_id, "purification_date": dpur,
             "method": "RP-HPLC, C18, linear acetonitrile gradient", "purified_mass_mg": mpur,
             "analyst": "AN-27"},
            {"stage": "QC", "lot_id": lot_id, "release_date": dqc,
             "coa_ref": "CoA-{}-QC".format(lot_id), "purity_result_pct": 98.4, "released_by": "QA-05"},
            {"stage": "FILL", "lot_id": lot_id, "fill_date": dfill, "units": units,
             "mass_per_unit_mg": mpu, "label_version": "LBL-v3"},
            {"stage": "SHIP", "lot_id": lot_id, "dispatch_date": dship, "carrier": "DHL Express",
             "waybill_ref": "WB-88213", "quantity_mg": qty, "receipt_signed_by": "RCPT-01"},
        ]

    lot_ok = compose("HLX", "OEM", "2604", "A7")
    ok_events = events(lot_ok, "2026-04-08", "2026-04-12", "2026-04-20", "2026-04-27",
                       "2026-05-04", 5000, 3800, 90, 38.0, 3400)

    long_rows = []
    for spec in ns["STAGES"]:
        ev = next(e for e in ok_events if e["stage"] == spec["stage"])
        for f in spec["fields"]:
            long_rows.append({"stage": spec["stage"], "stage_name": spec["name"],
                              "event_date": ev[spec["date_field"]], "lot_id": ev["lot_id"],
                              "field": f, "value": ev[f]})
    with open(os.path.join(d, "sample-lot-events.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["stage", "stage_name", "event_date", "lot_id", "field", "value"])
        w.writeheader()
        w.writerows(long_rows)

    # ---- 4. 审计演示批次（含期望判定）
    import copy

    def variant(lot_id, **over):
        evs = events(lot_id, over.get("dsyn", "2026-04-08"), over.get("dpur", "2026-04-12"),
                     over.get("dqc", "2026-04-20"), over.get("dfill", "2026-04-27"),
                     over.get("dship", "2026-05-04"), over.get("mcrude", 5000),
                     over.get("mpur", 3800), over.get("units", 90), over.get("mpu", 38.0),
                     over.get("qty", 3400))
        return evs

    lots = []

    lots.append({"lot_id": lot_ok, "site_code": "OEM", "expected_verdict": "complete",
                 "expected_findings": [], "events": ok_events,
                 "note": "All five stages present, dates ordered, mass monotonically decreasing"})

    no_qc = [e for e in variant(compose("HLX", "OEM", "2604", "B2")) if e["stage"] != "QC"]
    lots.append({"lot_id": compose("HLX", "OEM", "2604", "B2"), "site_code": "OEM",
                 "expected_verdict": "broken", "expected_findings": ["missing_stage:QC"],
                 "events": no_qc,
                 "note": "Release record absent: four stages present but the CoA stage is missing"})

    gain = variant(compose("HLX", "OEM", "2604", "C5"), mpur=5300)
    lots.append({"lot_id": compose("HLX", "OEM", "2604", "C5"), "site_code": "OEM",
                 "expected_verdict": "broken", "expected_findings": ["mass_gain:SYN->PUR"],
                 "events": gain,
                 "note": "Purified mass 5300 mg exceeds crude mass 5000 mg: over-unity yield"})

    inverted = variant(compose("HLX", "OEM", "2604", "D9"), dship="2026-04-25")
    lots.append({"lot_id": compose("HLX", "OEM", "2604", "D9"), "site_code": "OEM",
                 "expected_verdict": "broken", "expected_findings": ["stage_order:FILL->SHIP"],
                 "events": inverted,
                 "note": "Dispatch precedes fill by two days: retrospective fill date"})

    bad_id_lot = compose("HLX", "OEM", "2604", "E3")
    tampered = variant(bad_id_lot)
    bad_char = "0" if tampered[0]["lot_id"][-1] != "0" else "1"
    tampered[0]["lot_id"] = tampered[0]["lot_id"][:-1] + bad_char
    lots.append({"lot_id": bad_id_lot, "site_code": "OEM", "expected_verdict": "broken",
                 "expected_findings": ["id_invalid:SYN"], "events": tampered,
                 "note": "Synthesis record carries a lot number whose check character fails"})

    no_label = variant(compose("HLX", "OEM", "2604", "F4"))
    for e in no_label:
        if e["stage"] == "FILL":
            e["label_version"] = ""
    lots.append({"lot_id": compose("HLX", "OEM", "2604", "F4"), "site_code": "OEM",
                 "expected_verdict": "broken", "expected_findings": ["missing_field:FILL.label_version"],
                 "events": no_label,
                 "note": "Fill record present but the label version field is empty: stage counts as absent"})

    aged = variant(compose("HLX", "OEM", "2112", "G6"), dsyn="2021-12-01", dpur="2021-12-06",
                   dqc="2021-12-10", dfill="2021-12-15", dship="2021-12-20")
    lots.append({"lot_id": compose("HLX", "OEM", "2112", "G6"), "site_code": "OEM",
                 "expected_verdict": "broken", "expected_findings": ["retention_soon:SYN"],
                 "events": aged,
                 "note": "60-month retention on the 2021-12 records expires 2026-12, inside the 90-day horizon"})

    with open(os.path.join(d, "audit-demo-lots.json"), "w", encoding="utf-8") as fh:
        json.dump({
            "note": "Seven demonstration lots. verdict/expected_findings are asserted at build time "
                    "and again by traceability_audit.py --selftest.",
            "as_of": "2026-10-26", "horizon_days": 90,
            "retention_policy_example_months": {"SYN": 60, "PUR": 60, "QC": 60, "FILL": 60, "SHIP": 36},
            "lots": lots,
        }, fh, ensure_ascii=False, indent=2)

    # ---- 5. 审计脚本
    script = ('#!/usr/bin/env python3\n'
              '"""Lot identifier validation and traceability chain audit (documentation only).\n\n'
              'Usage:\n'
              '  python3 traceability_audit.py --lot-id HLX-OEM-2604-A7-' + chk + '\n'
              '  python3 traceability_audit.py --audit audit-demo-lots.json --as-of 2026-10-26\n'
              '  python3 traceability_audit.py --selftest\n\n'
              'Rules: R1 identifier validity, R2 stage coverage and mandatory fields, R3 stage ordering,\n'
              'R4 mass continuity (mass may not increase), R5 retention horizon.\n'
              '"""\n' + SCRIPT_CORE + SCRIPT_CLI)
    open(os.path.join(d, "traceability_audit.py"), "w", encoding="utf-8").write(script)

    # ---- 出版前不变量自检（全部对已解析数值断言，不对格式化文本断言）
    # 1) 合法 ID 通过；任一单字符替换必须失效
    assert ns["is_valid_lot_id"](lot_ok), lot_ok
    for i in range(len(lot_ok)):
        if lot_ok[i] == "-":
            continue
        repl = "0" if lot_ok[i] != "0" else "1"
        assert not ns["is_valid_lot_id"](lot_ok[:i] + repl + lot_ok[i + 1:]), (lot_ok, i)
    # 2) 七条演示批次的判定必须与期望一致
    for lot in lots:
        res = audit_lot(lot, as_of=_date(2026, 10, 26))
        assert res["verdict"] == lot["expected_verdict"], (lot["lot_id"], res["findings"])
        if lot["expected_verdict"] == "complete":
            assert res["findings"] == [], res["findings"]
        for prefix in lot["expected_findings"]:
            assert any(f.startswith(prefix) for f in res["findings"]), (lot["lot_id"], prefix, res["findings"])
    # 3) 完整批次的收率必须等于手算值
    y = audit_lot(lots[0], as_of=_date(2026, 10, 26))["yields"]
    assert abs(y["SYN_to_PUR_pct"] - 76.0) < 1e-9, y      # 3800/5000
    assert abs(y["PUR_to_FILL_pct"] - 90.0) < 1e-9, y     # 90 x 38.0 = 3420 / 3800
    assert abs(y["FILL_to_SHIP_pct"] - 99.42) < 0.01, y   # 3400/3420
    assert abs(y["overall_pct"] - 68.0) < 1e-9, y         # 3400/5000
    # 4) 零容差：0.5 mg 的质量增量也必须被抓到（否则质量规则形同不存在）
    tiny = variant(compose("HLX", "OEM", "2604", "H8"), mpur=5000.5)
    tiny_res = audit_lot({"lot_id": tiny[0]["lot_id"], "site_code": "OEM", "events": tiny},
                         as_of=_date(2026, 10, 26))
    assert any(f.startswith("mass_gain:SYN->PUR") for f in tiny_res["findings"]), tiny_res["findings"]
    # 5) 保留期算术：跨年加月必须落在正确日历日
    assert ns["add_months"](_date(2021, 12, 1), 60) == _date(2026, 12, 1)
    assert ns["add_months"](_date(2024, 1, 31), 1) == _date(2024, 2, 29)   # 闰年末日收敛
    assert ns["add_months"](_date(2021, 12, 15), 36) == _date(2024, 12, 15)
    # 6) 交付脚本必须可编译且与断言用的是同一份逻辑源
    compile(script, "traceability_audit.py", "exec")
    assert SCRIPT_CORE in script

    readme = """# Traceability from Synthesis to Shelf — record linkage reference set

Companion data for the note *Traceability from Synthesis to Shelf: Record Linkage Across Five
Handover Boundaries*. Everything here is documentation arithmetic: an identifier scheme, a record
schema, and an audit that tests five properties of a batch record set. No handling instructions,
no storage guidance, no biological claims.

## Lot identifier scheme

`HLX-OEM-2604-A7-%s` — issuer, site, year-month of synthesis, base-36 sequence, check character.
The check character is computed over the hyphen-free payload:

```
check = ALPHABET[ sum(value(char_i) * (i+1) for i in 0..n-1) mod 36 ]
ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
```

`lot-id-scheme.csv` documents each segment and its rule.

## The five audit rules

| Rule | Test | Finding code |
|---|---|---|
| R1 | Lot identifier well formed, check character valid, site code matches the document | `id_invalid:<stage>` / `id_site_mismatch:<stage>` |
| R2 | All five stages present; every mandatory field non-empty (empty = absent) | `missing_stage:<stage>` / `missing_field:<stage>.<field>` |
| R3 | Stage dates non-decreasing in synthesis → purification → release → fill → dispatch | `stage_order:<from>-><to>` |
| R4 | Recorded mass non-increasing; fill mass computed as units x mass per unit | `mass_gain:<from>-><to>:<prev>-><cur>` |
| R5 | Retention deadline inside the reference horizon | `retention_soon:<stage>:<deadline>` |

Verdict is `complete` only when there are no findings. That means *documentarily complete*, not
authentic: a coherently fabricated record set passes all five rules.

## Files

| File | Contents |
|---|---|
| `lot-id-scheme.csv` | Identifier segments, alphabets, and the check-character rule |
| `traceability-record-schema.csv` | %d mandatory fields across the five stages, with evidence type |
| `sample-lot-events.csv` | One worked lot in long format (%d field rows), all five stages |
| `audit-demo-lots.json` | Seven demonstration lots with expected verdicts (complete, missing stage, over-unity mass, inverted dates, invalid identifier, empty field, retention horizon) |
| `traceability_audit.py` | Validator and audit CLI with `--selftest` |

## Usage

```
python3 traceability_audit.py --lot-id HLX-OEM-2604-A7-%s
python3 traceability_audit.py --audit audit-demo-lots.json --as-of 2026-10-26
python3 traceability_audit.py --selftest
```

The worked lot in `sample-lot-events.csv` gives purification yield 76.0 %%, fill yield 90.0 %%
and overall yield 68.0 %% (crude 5000 mg, purified 3800 mg, 90 units x 38.0 mg, dispatched
3400 mg). Those figures are arithmetic on the stated masses, not benchmarks.

## Limits

- The audit detects omission and internal contradiction, not authenticity.
- The identifier format is an example design, not a standard; a real scheme must have its checksum
  recomputed, not assumed.
- Retention periods (60 months production/release, 36 months dispatch) are an example policy input
  chosen to make the horizon arithmetic visible. They are not regulatory constants and carry no
  legal meaning.
- Yields in the demo lots are illustrative arithmetic; purification performance varies with
  sequence, scale and method.

## Related documentation

- OEM services and private-label supply: https://helixpeptideoem.com/services
- Product-level documentation and batch records: https://helixpeptideoem.com/products

## License

CC BY 4.0
""" % (chk, len(schema_rows), len(long_rows), chk)
    open(os.path.join(d, "README.md"), "w", encoding="utf-8").write(readme)

    return d, len(schema_rows), len(lots)


if __name__ == "__main__":
    d1, fields = build_coa_taxonomy()
    print(f"coa-field-taxonomy: {len(fields)} 字段 → {d1}")
    d2, n = build_reconstitution_tables()
    print(f"reconstitution-tables: {n} 行 → {d2}")
    d3, m, t = build_temperature_excursion()
    print(f"temperature-excursion-mkt: {m} 剖面 + {t} 分诊行 → {d3}")
    d4, r4, s4 = build_purity_content_math()
    print(f"purity-content-math: {r4} 样品 + {s4} 敏感性行 → {d4}")
    d5, r5, r5b, r5c = build_counterion_salt_forms()
    print(f"counterion-salt-forms: {r5} 盐型行 + {r5b} 漂移行 + {r5c} 位点行 → {d5}")
    d6, s6, l6 = build_synthesis_to_shelf_traceability()
    print(f"synthesis-to-shelf-traceability: {s6} 字段 + {l6} 演示批次 → {d6}")
