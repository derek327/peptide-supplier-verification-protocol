# Helix Peptide — Research Supplier Verification Protocol

Open reference document for institutional and laboratory buyers evaluating
research-grade peptide suppliers. Published by Helix Peptide as part of our
documentation-first procurement standard.

**Site:** https://gethelixpeptide.com
**CoA / QA standard:** https://gethelixgmppeptides.com/coa-guide
**OEM / private label:** https://helixpeptideoem.com
**Wholesale / bulk:** https://helixpeptidesupply.com

## Repository contents

- `docs/coa-field-guide.md` — field-by-field guide to verifying a Certificate of Analysis
- `docs/hplc-method-notes.md` — how to judge whether an HPLC purity figure is meaningful
- `scripts/coa_checklist.py` — CLI checklist that scores a CoA against a research-grade acceptance baseline (purity threshold, lot match, identity method, method statement)

```bash
python3 scripts/coa_checklist.py --json coa.json   # exit 0 pass / 1 review / 2 fail
```

---

---

## 1. Lot-Specific Documentation

A catalog purity number is not sufficient. For each lot, request:

- Certificate of Analysis (CoA) for the **exact lot** to be shipped
- HPLC purity integration with chromatogram
- Identity confirmation by mass spectrometry (LC-MS or equivalent)
- Lot number printed on the vial **matching** the CoA

## 2. Analytical Acceptance Baseline

| Parameter | Research-grade expectation |
|---|---|
| HPLC purity | ≥ 95% (many buyers specify ≥ 98%) |
| Identity | Mass confirmation, not visual label check |
| Appearance | Documented per lot (color / physical form) |
| Residual solvents | Checked where applicable |

## 3. Verification Checklist Before Ordering

- [ ] CoA is lot-specific (not a generic "batch range")
- [ ] Named analytical lab or in-house method stated
- [ ] Vial label lot number will match CoA lot number
- [ ] Storage / stability statement provided
- [ ] Research-use-only permitted-use statement clear
- [ ] QA contact responsive within one business day

## 4. Construct Precision

Confirm the **exact construct** — sequence, salt/counter-ion form, and any
modification. Examples where catalogs are commonly confused:

- GHK-Cu (copper tripeptide complex) vs AHK-Cu vs Copper Tripeptide-1 (CTP-1)
- BPC-157 vs BPC-157 salts/acetate forms
- TB-500 fragment (Ac-LKKTETQ-NH2) vs full-length Thymosin Beta-4
- Retatrutide (tri-agonist) vs tirzepatide (dual) vs semaglutide (GLP-1)

Sequence confirmation is the first checkpoint before any protocol work.

## 5. Red Flags

- CoA without a matching lot number
- No identity method (HPLC "purity" with no mass confirmation)
- Pressure to order before documentation review
- Vague answers about the analytical lab or method

---

*This document is published for laboratory and research procurement use.
Helix Peptide supplies research-grade catalog peptides with batch
documentation. Buyers are responsible for compliance with local regulations
and permitted-use statements.*

License: CC BY 4.0 — free to cite with attribution.
