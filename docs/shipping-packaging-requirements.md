# Shipping and Packaging Requirements — Research Peptide Procurement

A vial that passes QC at the manufacturer has only done half the job when it
leaves the loading dock. Lyophilized peptides are moisture- and
temperature-sensitive, and the transit window is where most documented
deviations actually occur. For research and institutional buyers, packaging
and thermal history should be part of the lot record, not an afterthought.

This document is a shipping and packaging specification that a buyer can
attach to a purchase order, so both sides agree on the protection and the
documentation before the parcel is dispatched.

## 1. Scope

Applies to lyophilized (freeze-dried) peptide vials in single- or multi-vial
orders, shipped ambient or temperature-controlled. Receiving-laboratory
handling after arrival (storage conditions, reconstitution) is covered in the
[lyophilized stability notes](lyophilized-stability-notes.md). This document
covers the physical package, the temperature record, and the paperwork that
should travel inside the box.

## 2. Packaging layers — what to specify

| Layer | Function | Minimum to verify |
|---|---|---|
| Primary vial | Holds the lyophilized cake; crimp or flip-off seal is the first moisture and oxygen barrier | Crimp intact, flip-off button not popped, no hairline cracks |
| Moisture barrier | Heat-sealed foil pouch around the vial, with a desiccant sachet | Foil intact and sealed; desiccant present and not saturated |
| Cushioning | Foam or corrugated dividers so vials do not contact each other or the box wall | Vials immobilized; no glass-to-glass contact |
| Insulated shipper | Rigid EPS or vacuum-panel box with taped seams | Box rigid, seams taped, no crush damage before opening |
| Cold elements (if refrigerated) | Phase-change gel packs conditioned to the target temperature | Packs conditioned (not frozen solid when the spec calls for 2–8 °C); separated from vials by a divider so vials never sit directly on the element |

Write the layer list into the purchase order. "Standard shipping" is not a
specification — a supplier that cannot state which layers are used cannot
demonstrate that the material was protected.

## 3. Temperature requirements and recording

- **Match the storage statement.** The shipping temperature should be
  consistent with the supplier's stability-based storage statement (for
  example 2–8 °C, or controlled ambient where stability data supports it).
  If the supplier will not state a shipping temperature, ask why.
- **Data logger for temperature-controlled shipments.** A single-use USB
  logger placed with the vials, started before dispatch, exported after
  delivery. Request the export (PDF or CSV) showing the full profile,
  minimum and maximum readings, and time spent above the agreed limit.
- **Define the acceptance window in advance.** Agree before dispatch on what
  excursion is acceptable — for example, a stated number of hours within a
  stated range — so the receiving lab does not improvise a decision at the
  dock.
- **Seasonal routing.** Freezing risk in winter transit and heat soak in
  summer are both real; the box design and cold-element plan should account
  for the actual route and season, not a generic template.

## 4. Documentation that should travel inside the box

- Packing list: SKU, lot number, fill mass, vial count — matching the order
- Certificate of Analysis for the **exact lot shipped** (see the
  [lot documentation package spec](lot-documentation-package-spec.md))
- Temperature logger export, when the shipment is temperature-controlled
- Material safety data sheet (MSDS)
- Research-use / laboratory-use declaration and any customs paperwork
- Dispatch date and carrier, with the expected transit window

Paperwork sent later by email is not the same as paperwork in the box. The
receiving lab files the shipment as a unit; the CoA that arrives in a
separate message is easy to mismatch against the wrong lot.

## 5. Receiving inspection checklist

- [ ] Outer box intact — no crush, punctures, or water staining
- [ ] Temperature logger reading within the agreed window (if cold chain)
- [ ] Cold elements still conditioned and not in direct contact with vials
- [ ] Foil pouch sealed; desiccant sachet present and not saturated
- [ ] Vials intact; crimps and flip-off seals unbroken
- [ ] Lot numbers on vial labels match the CoA lot
- [ ] Packing list count and SKUs match the order
- [ ] Photograph the unopened shipment before storing
- [ ] Quarantine the lot until inspection is complete and logged

**If the logger shows an excursion beyond the agreed window:** do not discard
the material and do not quietly accept it either. Quarantine, photograph,
notify the supplier with the logger export, and request a written
disposition. A documented excursion is a resolvable event; an undocumented
one becomes a lot-integrity question later.

## 6. Red flags

- No stated shipping temperature — "we ship everything the same way"
- Temperature-controlled shipment without a logger, or refusal to share the export
- Lyophilized vials in a bubble mailer only — no rigid box, no cushioning
- No foil moisture barrier or desiccant in the package
- CoA and paperwork emailed separately instead of packed with the lot
- Vial label lot numbers that do not match the accompanying CoA
- Vials packed in direct contact with frozen gel packs (local freezing risk)

## 7. Where this sits in the Helix protocol

- First-order supplier questions: `docs/supplier-audit-questionnaire.md`
- Minimum lot file set: `docs/lot-documentation-package-spec.md`
- Storage and reconstitution context: `docs/lyophilized-stability-notes.md`
- Field-by-field CoA reading: `docs/coa-field-guide.md`
- Bulk / wholesale ordering context: https://helixpeptidesupply.com

A defensible shipment is one the receiving lab can file without guessing:
every protection stated, every temperature recorded, every document in the
box.

---

*Research and institutional procurement only. Helix Peptide publishes this
packaging standard so receiving labs can request the same protections from
any supplier, including us.*
