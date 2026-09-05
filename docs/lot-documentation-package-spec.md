# Lot Documentation Package Spec — Research Peptide Procurement

A catalog page and a single CoA PDF are not a documentation package.
Institutional buyers evaluating a white-label or contract-manufactured
research peptide lot should receive a **defined set of files** that can be
filed, compared across lots, and handed to an incoming-QC reviewer.

This spec lists the minimum package, the recommended extras, and how to
reject an incomplete set. It is written for laboratory and procurement use.
It does not describe clinical use.

## 1. Why a package, not a single PDF

A Certificate of Analysis answers “what was measured on this lot.”
It does not, by itself, prove:

- the vial you will receive is that lot
- the construct (sequence, salt, modification) matches the PO
- the method behind the purity number is inspectable
- the pack-out and storage statements match what was shipped

Buyers who only archive a CoA discover the gap when a later lot does not
match the first one and there is nothing else to compare.

## 2. Minimum package (every lot)

| # | Document | Must contain |
|---|---|---|
| 1 | Lot-specific CoA | Lot number, HPLC purity (area %), identity method, date |
| 2 | HPLC chromatogram | Same lot number as the CoA; wavelength stated |
| 3 | Identity report | LC-MS / ESI (or equivalent) with observed vs expected mass |
| 4 | Construct sheet | Sequence or sequence hash, salt / counter-ion, any amidation or modification |
| 5 | Pack-out list | Vial count, fill mass or volume, label artwork revision, lot printed on label |
| 6 | Storage statement | Recommended temperature, light, and moisture conditions for the sealed vial |

If any of items 1–3 is missing, regard the lot as **not released for receiving**.

## 3. Recommended extras (first order or new construct)

| Document | When it matters |
|---|---|
| Method summary (HPLC column, gradient, detection λ) | Comparing purity numbers across suppliers |
| Peptide content / nitrogen or counter-ion assay | Dose-by-weight calculations in the receiving lab |
| Residual solvent or water (KF) where the process uses them | Lyophilized lots stored longer than a few months |
| Label and carton photograph | OEM / private-label lots where artwork is part of the PO |
| Chain-of-custody or ship temperature log | Frozen or cold-pack lanes |

These extras are not a substitute for items 1–3.

## 4. File naming (so lots can be compared)

Use one folder per lot. Suggested names:

```
{sku}_{lot}_coa.pdf
{sku}_{lot}_hplc.pdf
{sku}_{lot}_ms.pdf
{sku}_{lot}_construct.pdf
{sku}_{lot}_packout.pdf
{sku}_{lot}_storage.pdf
```

Do not put “latest” or “generic” in the filename. A later buyer should be
able to tell which file belongs to which lot without opening it.

## 5. Acceptance checklist before payment

- [ ] CoA lot number equals the lot that will be shipped
- [ ] Chromatogram lot number equals the CoA
- [ ] Identity method is mass-based, not “pass” with no method
- [ ] Construct sheet matches the purchase order (sequence / salt / modification)
- [ ] Pack-out list states the same SKU and fill as the quote
- [ ] Storage statement is specific (temperature + moisture), not “store well”

## 6. Red flags

- One PDF reused across SKUs with only the product name changed
- Chromatogram without a lot number
- “Batch range” CoA offered in place of a lot-specific file
- Construct described only as a catalog name (no sequence or CAS)
- Pack-out promised “as usual” with no count or fill mass

## 7. Where this sits in the Helix protocol

- Field-by-field CoA reading: `docs/coa-field-guide.md`
- HPLC method notes: `docs/hplc-method-notes.md`
- First-order supplier questions: `docs/supplier-audit-questionnaire.md`
- OEM / private-label context: https://helixpeptideoem.com/services
- CoA buyer guide: https://helixgmppeptides.com/coa-guide

A complete package is what lets a receiving lab file the lot, not just
read a purity number.

---

*Research and institutional procurement only. Helix Peptide publishes this
spec so buyers can request the same file set from any supplier, including us.*
