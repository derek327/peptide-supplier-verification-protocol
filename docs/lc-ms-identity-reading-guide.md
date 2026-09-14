# LC-MS Identity Reading Guide — How to Read a Mass Confirmation Report

An HPLC purity figure tells you how much of the material eluted as a single
peak. It does not tell you *what* that peak is. Identity is established by
mass spectrometry, and for research peptide lots the LC-MS report is the
document that carries that claim. This guide covers what the numbers on such
a report mean and what to check before accepting it.

## 1. Why purity and identity are separate claims

A 98% HPLC area figure is consistent with a well-made lot of the correct
construct — and equally consistent with a 98%-pure lot of a different
construct that happens to elute in the same window. The two questions are
answered by two different methods:

| Question | Method | Field on the CoA |
|---|---|---|
| How much of the material is the main component? | RP-HPLC (UV) | Purity (area %) |
| Is the main component the claimed molecule? | LC-MS / ESI-MS | Identity / mass confirmation |

A CoA that reports purity but states identity as "pass" without an observed
mass is an incomplete document, regardless of the purity number.

## 2. The four numbers that matter on an LC-MS report

1. **Observed m/z** — the mass-to-charge values of the detected ions.
2. **Charge state (z)** — the multiplier applied during deconvolution.
3. **Deconvoluted (reconstructed) mass** — the neutral mass the software
   calculates from the m/z series.
4. **Theoretical / expected mass** — the calculated monoisotopic or average
   mass for the stated construct, with its salt and modification form.

Acceptance is decided by comparing (3) against (4) in **ppm or Da**, not by
eyeballing whether the spectrum "looks right".

## 3. Reading charge states

Electrospray of a peptide produces a series of multiply charged ions. For a
peptide of neutral mass *M*, an ion at charge *z* appears at:

```
m/z = (M + z·1.00794) / z
```

So a single component appears as a ladder of peaks spaced roughly `1/z` apart
in m/z. A ~3,000 Da peptide typically shows +2, +3 and +4 ions; longer
sequences and PEGylated or otherwise larger constructs spread further.

Practical checks:

- Do the peaks form a consistent ladder, or is there a single isolated ion?
  A single ion with no series is weak evidence and should be questioned.
- Are the spacing and the deconvoluted mass arithmetically consistent with
  the stated charge assignment? Mislabelled charge states are the most common
  error in hand-written mass reports.

## 4. Adducts, counterions and the "wrong mass" that is not wrong

The neutral mass of the construct and the mass of the *material as supplied*
are two different things. Common shifts seen on legitimate reports:

| Species / modification | Approximate Δ (Da) |
|---|---|
| Sodium adduct (+Na, replaces H) | +21.98 |
| Potassium adduct (+K, replaces H) | +37.96 |
| Trifluoroacetate adduct (TFA) | +113.99 |
| N-terminal acetylation | +42.01 |
| C-terminal amidation (vs free acid) | −0.98 |
| Methionine oxidation | +15.99 |
| Deamidation (Asn/Gln → Asp/Glu) | +0.98 |
| Disulfide formation (per bridge) | −2.02 |
| Copper(II) complexed (e.g. GHK-Cu) | +62.93 |

Two consequences for purchasing decisions:

- A mass that is off by ~+22, +38 or ~+114 may be an adduct of the correct
  construct rather than a different construct. Ask the lab to state whether
  the reported mass is the neutral construct or an adduct sum.
- A mass that matches a **different salt or modification form** of your
  target is still not your target for documentation purposes. This is the
  core issue with acetate vs TFA lots, and with free-acid vs amidated
  C-termini — both are frequently listed under one catalog name.

## 5. Monoisotopic vs average mass

For small molecules the two are nearly identical; for peptides above roughly
1,500 Da they diverge by a few Da because of natural ^13C content. Reports are
consistent only if they declare which convention they used. A reported
deviation of two or three Da on a 4,000 Da peptide is usually a convention
mismatch, not a synthesis error — but it must be resolved on paper before
acceptance.

## 6. Document integrity for the mass report

- Is the **construct** stated in full (sequence or at minimum the declared
  mass and modification/salt form)?
- Is the **instrument and ionisation mode** named (e.g. ESI, column, LC
  gradient if LC-MS rather than infusion)?
- Is the **calibration** stated, and is a calibrant or lock-mass used?
- Is the **deconvolution software** named, with the charge-state range used?
- Is the **actual spectrum** attached, or only a table of numbers? A table
  without a spectrum cannot be reviewed.
- Is the mass report tied to the **same lot number** as the CoA and the vial
  label?

## 7. Red flags

- Identity stated as "pass" or "conforms" with no observed mass value
- Observed mass reported with no theoretical value, or vice versa
- No charge state or deconvolution parameters given
- Spectrum present but with unlabelled peaks, or a mass axis too coarse to
  judge ppm-level agreement
- A single trace shown for a product that should give a multi-charge ladder
- Mass shift of one adduct unit described as "within specification" with no
  adduct assignment

## 8. Practical acceptance flow

1. Request the mass confirmation for the **exact lot**, together with the CoA.
2. Confirm the declared construct and its modification/salt form.
3. Compare deconvoluted mass against theoretical — expect ppm-level
   agreement for a well-controlled lot; flag anything exceeding 0.1%.
4. Account for any adduct or counterion explicitly in your lot file.
5. File the spectrum with the lot — identity evidence is part of the lot
   record, not an optional attachment.

---

*Reference document for institutional and laboratory buyers. Published by
Helix Peptide (gethelixpeptide.com) as part of a documentation-first
procurement standard. See also the CoA verification guide at
[gethelixgmppeptides.com/coa-guide](https://gethelixgmppeptides.com/coa-guide).*
