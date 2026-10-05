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


if __name__ == "__main__":
    d1, fields = build_coa_taxonomy()
    print(f"coa-field-taxonomy: {len(fields)} 字段 → {d1}")
    d2, n = build_reconstitution_tables()
    print(f"reconstitution-tables: {n} 行 → {d2}")
    d3, m, t = build_temperature_excursion()
    print(f"temperature-excursion-mkt: {m} 剖面 + {t} 分诊行 → {d3}")
    d4, r4, s4 = build_purity_content_math()
    print(f"purity-content-math: {r4} 样品 + {s4} 敏感性行 → {d4}")
