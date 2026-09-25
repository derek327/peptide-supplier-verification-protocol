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
OUT = os.path.join(HERE, "out")

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
    src = os.path.join(HERE, "datasets", "coa-field-taxonomy-v1.json")
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


if __name__ == "__main__":
    d1, fields = build_coa_taxonomy()
    d2, n = build_reconstitution_tables()
    print(f"coa-field-taxonomy: {len(fields)} 字段 → {d1}")
    print(f"reconstitution-tables: {n} 行 → {d2}")
