# Temperature Excursion Protocol for Research Peptide Shipments

*A documentation and disposition workflow for buyers of research-grade peptides.
Research context only — this document describes how to handle documentation when a
shipment's temperature logger shows an out-of-range period. It is not storage advice,
dosing guidance, or a stability claim for any specific sequence.*

---

## 1. What counts as an excursion

An **excursion** is any interval during transport or interim storage in which the recorded
temperature leaves the range the supplier declared for that product. Three parameters define
it, and all three must be recorded, because "it got warm" is not a reportable event:

| Parameter | Why it must be stated | Typical source |
|---|---|---|
| Deviation magnitude | Band entered (e.g. +2 to +8 °C product reaching 22 °C) | Logger trace |
| Duration | Time spent outside the band, not total transit time | Logger trace |
| Physical state at the time | Lyophilised powder vs reconstituted solution differ by orders of magnitude in sensitivity | Packing list + photos |

A shipment can therefore be *in band* the whole way and still be undocumented (no logger),
and it can be *out of band* for twenty minutes and be a non-event. The protocol exists to
separate those two from the case that actually needs analytical follow-up.

The declared range is part of the purchase specification, not a suggestion. If the
specification sheet does not state one, that omission is the first finding — request it in
writing before the next order (see the lot documentation package in
[helixgmppeptides.com/coa-guide](https://helixgmppeptides.com/coa-guide)).

## 2. Data capture: what the logger must give you

A single maximum-reading indicator (a "temperature dot" that turns colour) answers only
*magnitude*, and only at one moment. For a reviewable file you want a time-series device,
and the following must be stated on the report or its certificate:

1. **Device model and serial** — so readings can be traced to a calibration record.
2. **Calibration status and date** — an uncalibrated trace is an anecdote.
3. **Accuracy / resolution** — ±0.5 °C resolution cannot evidence a ±0.3 °C claim.
4. **Logging interval** — a 30-minute interval can miss a short excursion entirely; this
   blind spot must be declared, not glossed over.
5. **Placement** — inside the payload next to the vials, or taped to the outer carton? An
   ambient logger on the box wall records the corridor, not the goods.
6. **Start and stop timestamps with timezone**, and whether the trace covers the full
   handover chain (origin warehouse → carrier → customs hold → your receipt).

A trace missing items 1–4 cannot support a disposition decision in either direction: it
cannot clear the shipment and it cannot condemn it. Regard it as a documentation gap and
request a replacement evaluation.

## 3. Triage matrix

Triage is deliberately coarse. It decides *what to do next*, not whether material is
acceptable — that is what analytical re-check is for.

| Band entered | ≤ 2 h | 2–24 h | > 24 h |
|---|---|---|---|
| +2 to +8 °C product, peak < 15 °C | Record, release | Record, release | Record, quarantine, request analytical re-check |
| +2 to +8 °C product, peak 15–25 °C | Record, release | Record, quarantine | Quarantine, request re-check + replacement assessment |
| +2 to +8 °C product, peak > 25 °C | Quarantine | Quarantine | Reject on documentation grounds |
| −20 °C product, peak < 0 °C | Record, release | Record, release | Record, release |
| −20 °C product, peak 0–25 °C | Record, quarantine | Quarantine, re-check | Reject on documentation grounds |
| −20 °C product, peak > 25 °C | Quarantine | Reject | Reject |

Two rules override the grid:

- **Physical indicators trump the grid.** If vials show melt-back, collapsed cake, visible
  moisture, or a broken seal, the shipment is quarantined regardless of what the logger
  says — a logger that agrees with visible damage adds nothing, and a logger that disagrees
  is broken or misplaced.
- **Reconstituted material is not triaged on this grid at all.** Once in solution the
  handling question is different in kind and belongs to the supplier's own documentation
  for that presentation.

## 4. Mean kinetic temperature: one number, and its limits

The standard way to collapse a varying trace into a single comparable figure is the **mean
kinetic temperature (MKT)**, an Arrhenius-weighted mean rather than an arithmetic one:

```
MKT = (ΔH / R) / ( -ln( ( Σ exp(-ΔH/(R·Ti)) · Δti ) / Σ Δti ) )
```

with ΔH the assumed activation energy (83.144 kJ/mol is the conventional value in
pharmaceutical practice; 62.8 kJ/mol is also used), R = 8.314462618 J/(mol·K), Ti in kelvin,
and Δti the time spent in interval i.

MKT is useful precisely because it is non-linear: a short hot interval moves it far more
than a long mildly-warm one, which is the behaviour you want when comparing two traces.

Its limits matter more than its usefulness:

- **It hides peaks.** A profile that spikes to 40 °C for one hour can produce the same MKT
  as a flat 8 °C profile. Never report MKT without also reporting the maximum recorded
  temperature and the excursion duration.
- **It carries a baked-in assumption.** ΔH is a modelling constant, not a measured property
  of your peptide. Two laboratories using different ΔH values will disagree on MKT for the
  same trace. Always state the ΔH used.
- **It is not a stability result.** MKT summarises a log file; it does not measure whether
  a molecule changed. The directions of change in this domain (aggregation, oxidation,
  deamidation, moisture uptake) are assay questions, not arithmetic ones.

Worked reference values for common excursions, computed from the formula above, are
published alongside this document as a dataset so that a reviewer can reproduce any row.

## 5. The disposition file

For every excursion, the file that travels with the material should contain:

- the raw logger export (CSV, unedited) plus the device certificate;
- the packing list and photos of the received goods, taken before opening;
- the declared range for each line item, quoted verbatim from the specification;
- MKT, maximum recorded temperature, and duration outside band, each with the ΔH used;
- the triage decision and its date, signed by whoever made it;
- if quarantined, the analytical re-check requested (HPLC purity re-run, identity
  confirmation, moisture) and its result, referenced by lot.

The purpose of the file is asymmetric: it matters most in the case you later need to argue
about a lot — with a supplier, an auditor, or your own records. A reviewer who cannot see
the raw trace cannot distinguish a handled excursion from a hidden one.

## 6. Buyer checklist

- [ ] Declared transport range is stated in the specification, not inferred from the label.
- [ ] A calibrated time-series logger is inside the payload, not on the carton.
- [ ] Logging interval and accuracy are stated on the report.
- [ ] Trace covers the whole chain including customs hold.
- [ ] Raw export is received on arrival, not summarised by the supplier.
- [ ] MKT reported together with peak and duration, with ΔH stated.
- [ ] Triage decision recorded with a date and a name.
- [ ] Quarantined lots have a named analytical re-check and a result on file.

## 7. Related documentation

- GMP-oriented quality documentation and CoA guidance:
  [helixgmppeptides.com/coa-guide](https://helixgmppeptides.com/coa-guide)
- Catalog and shipping documentation:
  [helixpeptidesupply.com/catalog](https://helixpeptidesupply.com/catalog)
- Companion dataset (triage matrix + MKT reference tables, reproducible arithmetic):
  see the dataset record accompanying this document.

## License

CC BY 4.0. Adapt the grid to your own quality system; where the two differ, your system
governs.
