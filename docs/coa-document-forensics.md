# CoA Document Forensics — Reading a Certificate of Analysis for Signs of Fabrication

A Certificate of Analysis is a *document*, and documents can be produced
without any analytical work behind them. Fabricated and recycled CoAs are the
most common failure mode institutional buyers encounter in the research
peptide supply chain, because the incentive structure is asymmetric: a
convincing PDF costs the vendor almost nothing, while the buyer's first real
test is a re-assay weeks after payment.

This guide is the technical companion to the field-by-field
[CoA field guide](coa-field-guide.md). Where that document covers *what a CoA
should state*, this one covers *how a CoA gives itself away* when it was
written rather than measured.

## 1. Three families of bad CoA

| Family | How it is produced | Where it fails inspection |
|---|---|---|
| **Recycled** | A genuine CoA from lot A is re-labelled to lot B, or last year's report is reissued under this year's lot number | Lot-number, date and instrument cross-references disagree between document and history |
| **Templated** | Values are typed into a house template with no attached raw data | No chromatogram, no spectrum, no method parameters, generic approval signature |
| **Edited** | A real report has individual numbers or an image altered before export | Internal inconsistencies, PDF metadata anomalies, pixel-level reuse of a known chromatogram |

Recycled documents are the most frequent and the easiest to catch, because the
seller often has only one real report to reuse.

## 2. Cross-reference checks that a recycled CoA cannot survive

Run these before you look at a single analytical value. Each one compares the
CoA against another artifact you already hold.

1. **Lot number on the vial against the CoA.** Photograph the crimp and label
   on arrival. A lot that "matches" only in the invoice line is not matched.
2. **Lot number against the dispatch history.** If you have bought the same
   SKU before, compare. Same lot number, different fill date, different
   appearance — one of the two documents is not real.
3. **Analysis date against shipping date.** Analysis after dispatch is
   impossible for a lot-specific report. Analysis *years* before dispatch
   should be explained, not assumed benign.
4. **Report date against method revision.** If the stated HPLC method has a
   revision quoted on the CoA, that revision must have existed on the analysis
   date.
5. **Instrument and column identifiers.** Serious labs quote them. A column
   serial that is identical across three unrelated suppliers, or an instrument
   ID that changes mid-document, is a copy artifact.
6. **Supplier identity.** Letterhead name, address and QA signatory should be
   the entity you contracted with. Whitelabel reissue is common; the reseller
   should say so rather than present another firm's letterhead as their own.

## 3. File-level forensics (PDF and image metadata)

Non-destructive, takes minutes, and requires only a PDF reader with a
document-properties panel or a CLI utility.

- **Creation vs modification timestamp.** A CoA created the day it was emailed
  for a lot analysed months earlier is normal. A CoA created *before* the
  analysis date it states is not.
- **Producer/author fields.** Reports exported from a house LIMS will name it.
  A "scanned" CoA whose metadata names an image editor or a word processor is
  a re-creation, not the lab's output.
- **Font and layout drift.** Edited rows frequently show a different font,
  a slightly different baseline, or letter spacing that does not match the
  surrounding table. Zoom to 300% on every value you plan to rely on.
- **Embedded image resolution and compression.** A chromatogram pasted from a
  chat application, re-saved twice, or cropped mid-axis will show
  inconsistent compression around the peak region.
- **Digital signature validity.** A "signed" report should show an intact
  signature panel. A cropped signature block is a decoration.
- **Repeated image fingerprints.** Compare chromatograms across lots and
  suppliers. Identical baseline noise is the single strongest signal of reuse:
  real injections never reproduce noise trace-for-trace. Hash or byte-compare
  the embedded image; visually overlay it against a report from a different
  seed.

## 4. Analytical-value checks that a written report usually fails

These are arithmetic and physical-plausibility tests, not opinions about
"looks fine".

| Check | Signal of a written report |
|---|---|
| Retention time identical to 0.01 min across different lots, columns or dates | Copy-paste, not injection |
| Every purity value lands on the same round figure (e.g. 98.5% for all SKUs) | Template fill |
| Area-% values for related peaks do not sum with the main peak to ~100% | Numbers invented independently |
| Impurity profile identical across constructs | Same image reused |
| Baseline noise pattern identical in two chromatograms | Same file reused |
| Reported purity that is internally inconsistent with the stated integration (main peak area vs total area) | Edited cell |
| Detector response far above linear range with no dilution noted | Unusable measurement presented as validated |
| Mass spectrum with no charge-state ladder for a multi-kDa construct | See [LC-MS reading guide](lc-ms-identity-reading-guide.md) |
| Residual solvent / water values quoted with more precision than the method supports | Decorative data |

The general principle: **a real analysis carries its own noise.** When two
documents share noise, they share an origin.

## 5. Triangulation across the document set

A single CoA is weak evidence. Ask for the set and read it as one record:

- CoA (lot-specific, with chromatogram)
- Mass or LC-MS confirmation for the **same lot** ([lot documentation package spec](lot-documentation-package-spec.md))
- Packing list and invoice with matching lot, fill mass and vial count
- Storage/stability statement consistent with the shipping configuration ([shipping and packaging requirements](shipping-packaging-requirements.md))
- MSDS with the construct, form and CAS/sequence data consistent with the CoA
- Available raw data: instrument export (e.g. `.cdf` or `.raw` chromatogram), integration parameters, calibration record

Inconsistency *between* documents is the cheapest thing for a buyer to detect
and the hardest thing for a fabricator to control, because the fabrication is
usually done once, for one document, by one person.

## 6. Requesting raw data — and what refusal means

A legitimate lab can export the raw chromatogram and integration method for a
lot; this is routine file retrieval, not a new analysis.

- Ask for the **instrument export plus integration parameters**, not a
  higher-resolution screenshot.
- If raw data cannot be released, ask for a **re-issued CoA on lab letterhead
  quoting the lot and adding the missing method details**. A lab that performed
  the work can reissue; a reseller who never held the file cannot.
- Ask QA one question with a verifiable answer: *"Which column and method were
  used for lot X, and what was the injection volume?"* Specific answers and
  vague answers are self-sorting.
- Where value justifies it, **split the sample** and commission an independent
  purity and identity assay. Retain the sealed counter-sample as received, with
  photographs and the temperature record.

## 7. Escalation and record keeping

1. Record the finding in the lot file: what was inconsistent, in which
   documents, on what date.
2. Give the supplier one documented opportunity to explain or reissue.
3. If resolved, keep both the original and the reissued document. The
   superseded version is part of the audit trail, not waste.
4. If not resolved, stop the lot from entering your working inventory and
   regard prior lots from that supplier as unverified until re-tested.
5. Feed the pattern back into supplier scoring: documentation integrity is a
   qualification criterion, weighted alongside price and lead time.

## 8. Buyer's quick checklist

- [ ] Lot number on the vial, CoA, packing list and invoice agree
- [ ] Analysis date precedes dispatch and postdates the stated method revision
- [ ] Instrument, column and method parameters are stated
- [ ] A chromatogram is attached, at a resolution where the peak can be judged
- [ ] Chromatogram is not a visual or byte-level duplicate of another report
- [ ] Peak values are internally consistent and not all round figures
- [ ] Identity confirmation for the same lot, with a charge-state ladder
- [ ] PDF metadata is consistent with a lab-issued document
- [ ] Signature block intact and signatory identifiable
- [ ] Raw data or a reissued CoA is available on request

`scripts/coa_checklist.py` in this repository scores a structured CoA record
against a research-grade baseline and flags missing method statements, lot
mismatches and absent identity confirmation.

---

*Reference document for institutional and laboratory buyers. Published by
Helix Peptide (gethelixpeptide.com) as part of a documentation-first
procurement standard. Documented verification practices are collected at
[gethelixpeptide.com/quality](https://gethelixpeptide.com/quality); the CoA
method walkthrough is at
[gethelixgmppeptides.com/coa-guide](https://gethelixgmppeptides.com/coa-guide).*
