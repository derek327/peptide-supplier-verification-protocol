# Purity vs Peptide Content: Net-Peptide Mass Reference Tables

Deterministic reference tables and a calculation script for the arithmetic that relates a
chromatographic purity figure (area-%) to the net peptide in a weighed sample. Every value is
computed from the two formulas below using the stated inputs &mdash; no observed or fitted data
is involved, so every row can be recomputed exactly.

## Contents

| File | Description |
|---|---|
| `net-peptide-content.csv` | 12 samples (10 mg label mass) across free-base, acetate and TFA forms: purity, water by Karl Fischer, counterion and other non-peptide fractions, resulting content, net peptide mass, and the molar overstatement that results from taking the label mass as peptide |
| `content-vs-water.csv` | 7 points: content at constant 98.0 % purity as water content runs 0 &ndash; 12 % |
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
- Product-level documentation and batch records: https://gethelixpeptide.com/products

## Citation

Cite the DOI of this record. Recomputation from the formulas above reproduces every row.

## License

CC BY 4.0
