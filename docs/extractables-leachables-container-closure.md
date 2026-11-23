# Extractables and Leachables from Container Closure Systems: Reading a Number That Has No Basis

A supplier statement that a vial closure contributes "less than 0.5 µg" of extractables is
not a small statement or a large one — it is an incomplete one. The same 0.5 µg/cm² of
surface loading becomes 3.90 µg per container in a 2 mL fill and 20.08 µg per container in a
20 mL fill, because the wetted area differs by a factor of 5.15. Multiplied by four containers
a day, the first case is 15.6 µg/day. The number did not change. Its basis did.

This note sets out the arithmetic behind an extractables and leachables (E&L) statement for a
research peptide in a glass vial with an elastomeric closure: what the geometric term is, how
a surface load converts to an exposure, what a single extraction actually measures, how a
migration curve behaves over a shelf life, and where the usual document fails. Every number
below is computed from stated inputs and can be regenerated; the accompanying dataset
(`container-geometry.csv`, `extractable-to-exposure.csv`, `sequential-extraction.csv`,
`migration-kinetics.csv`, `arrhenius-acceleration.csv`, `el-cases.json`, `el_math.py`) carries
the full tables and a self-test.

## 1. Four qualifiers that a bare mass does not carry

An E&L figure is only interpretable when four things are stated:

| Qualifier | Typical omission | Consequence |
|---|---|---|
| Normalising area or volume | "0.5 µg" with no denominator | cannot be compared to any other container |
| Container and fill | "per vial" without fill volume | concentration and per-container mass diverge |
| Contact time and temperature | "extractables" with no condition set | 30 days at 40 °C and 24 months at 25 °C are different questions |
| Number of containers per day | "per day" exposure with no dose count | a passing figure at one container fails at four |

Passing all four through a single arithmetic chain is the point of the tables. The chain is:
surface load → concentration → per-container mass → daily exposure → comparison against a
threshold, with each arrow carrying a unit conversion that can be checked by hand.

## 2. The geometry term

For a cylindrical fill, the wetted area is a bottom disc plus a wall, and the volume is the
disc area times the fill height. Dividing one by the other collapses to a two-term expression:

```
S/V = 4/D + 1/h        [cm²/mL],   h = 4V/(π D²)
```

Two properties follow immediately and are worth remembering because they explain most
disagreements between two laboratories that used "the same" extraction:

- the ratio falls as the container gets wider (`4/D`), and
- the ratio rises as the fill gets shallower (`1/h`).

The dataset's example geometry (round-number cylinders, not catalogue drawings):

| Format | Fill (mL) | Height (cm) | Wetted area (cm²) | S/V (cm²/mL) | Relative to 2R/2 mL |
|---|---|---|---|---|---|
| 2R | 0.5 | 0.442 | 2.798 | 5.595 | 1.435 |
| 2R | 1.0 | 0.884 | 4.464 | 4.464 | 1.145 |
| 2R | 2.0 | 1.768 | 7.798 | 3.899 | 1.000 |
| 6R | 5.0 | 2.487 | 14.511 | 2.902 | 0.744 |
| 10R | 10.0 | 3.930 | 24.767 | 2.477 | 0.635 |
| 20R | 20.0 | 5.261 | 40.165 | 2.008 | 0.515 |

A half-full 2R vial concentrates the same surface load 1.435 times more than a full one. A
20R fill spreads it over 5.15 times the area, so the per-container mass is 5.15 times higher
at identical µg/cm². If two statements quote the same surface load but different fill volumes,
both are correct and neither is comparable.

## 3. Extractables are an upper bound; leachables are a measurement

The distinction is not terminology. An extractable study puts the material in contact with
aggressive solvents under exaggerated time and temperature to find out what it *can* release.
A leachable study measures what is *present in the product* under its real storage condition.

- Using extractables as the exposure is a deliberate worst case. It overstates, and it is
  defensible precisely because it overstates.
- Using a single leachable timepoint as the plateau understates, and it is not defensible
  without a kinetic argument (section 5).
- Reporting an extractable value in a column labelled "leachables" is a category error that
  arithmetic cannot detect and a reviewer can.

The case file marks every extractable-based exposure with the flag `exhaustive_upper_bound`,
so a reader can see which direction the number is biased.

## 4. Extraction depth: the first extract is a fraction, not a total

Exhaustive extraction is normally done in successive aliquots. If each step removes a fraction
f of what remains, the cumulative fraction after n steps is

```
cumulative(n) = 1 − (1 − f)^n
```

| f per step | 1 step | 2 steps | 3 steps | 4 steps | first step as % of 3-step total |
|---|---|---|---|---|---|
| 0.4 | 40.0 % | 64.0 % | 78.4 % | 87.0 % | 51.0 % |
| 0.6 | 60.0 % | 84.0 % | 93.6 % | 97.4 % | 64.1 % |
| 0.8 | 80.0 % | 96.0 % | 99.2 % | 99.8 % | 80.7 % |

With f = 0.6 the first extract carries 60 % of the total; reporting it as "the extractables"
understates by 1.667 times. This is the most common silent error in a supplier summary,
because the number is real, the method is real, and only the denominator is missing. The
arithmetic correction is trivial: divide by the cumulative fraction, and state the number of steps.

The dataset's case E07 uses exactly this trap. A 0.50 µg/cm² first extract passes a 5 µg/day
comparison at 3.90 µg/day; corrected to the exhaustive total (÷ 0.60) it is 6.50 µg/day and fails.

## 5. Migration over time is a curve

A leachable concentration approaches a plateau rather than growing without limit. A
first-order approach is the simplest defensible model:

```
C(t) = C∞ (1 − e^(−k t))        t½ = ln2/k        t_p = −ln(1−p)/k
```

| k (per day) | t½ (days) | t90 (days) | 30 d | 90 d | 365 d | 730 d | plateau/730 d |
|---|---|---|---|---|---|---|---|
| 0.0005 | 1 386 | 4 605 | 1.5 % | 4.4 % | 16.7 % | 30.6 % | 3.27× |
| 0.001 | 693 | 2 303 | 3.0 % | 8.6 % | 30.6 % | 51.8 % | 1.93× |
| 0.005 | 139 | 461 | 13.9 % | 36.2 % | 83.9 % | 97.4 % | 1.03× |
| 0.02 | 34.7 | 115 | 45.1 % | 83.5 % | 99.9 % | 100 % | 1.00× |
| 0.05 | 13.9 | 46.1 | 77.7 % | 98.9 % | 100 % | 100 % | 1.00× |

Two readings matter for procurement:

1. **A T0 or 30-day value is not a scaled-down plateau.** For the slowest case here, 30 days
   sits at 3 % of the plateau; the plateau is 33 times the measured value.
2. **A 24-month study can still be unfinished.** At k = 0.001/day the 24-month point is 51.8 %
   of plateau, so the extrapolation factor is 1.93 — a 93 % correction on a number that looks
   like a final result.

Which k applies is a property of the migrant and the matrix, not of the container alone:
volatiles and surface residues move in days, polymer additives and adhesive components move
over months to years. The table's purpose is to show the size of the correction, not to
supply a rate constant.

## 6. Temperature: the acceleration factor is an assumption

Accelerated extraction trades time for temperature. The factor between two temperatures is an
Arrhenius expression:

```
AF = exp( −(Ea/R) (1/T_acc − 1/T_ref) ),   R = 8.314462618 J/(mol·K)
```

| Ea (kJ/mol) | 25→30 °C | 25→40 °C | 25→50 °C | 90 d at 40 °C equals (days at 25 °C) |
|---|---|---|---|---|
| 20 | 1.14 | 1.47 | 1.87 | 132 |
| 40 | 1.30 | 2.17 | 3.48 | 195 |
| 50 | 1.39 | 2.63 | 4.76 | 237 |
| 60 | 1.49 | 3.19 | 6.50 | 287 |
| 80 | 1.70 | 4.69 | 12.14 | 422 |
| 100 | 1.95 | 6.91 | 22.66 | 621 |

Between 25 °C and 40 °C the factor runs from 1.47 to 6.91 across this range — a 4.7-fold
spread on identical test conditions. At 50 versus 80 kJ/mol the difference is 1.79 times (the
ratio 4.692/2.628 in the dataset's invariant check). So "90 days at 40 °C" is not a duration;
it is a duration plus an activation energy. If the Ea is not stated, the acceleration has no
interpretable magnitude, and neither does any conclusion drawn from it.

The secondary caution: Arrhenius transfer preserves a rate constant under an assumed single
mechanism. When a closure has several migrants with different mechanisms, one factor cannot
represent all of them, and a ranking of migrants at the accelerated condition need not hold
at the storage condition.

## 7. Identified compounds are not the whole residue

Two aggregate measures commonly accompany a chromatogram: non-volatile residue (NVR, a
gravimetric total) and total organic carbon (TOC, for aqueous extracts), plus the sum of
identified and semi-quantified peaks. They are not interchangeable and the gap is usually
large. In the dataset's example, an NVR of 0.42 µg/cm² with 0.10 µg/cm² identified gives an
identified fraction of 23.8 % — an exposure figure built only from identified peaks is 4.2
times lower than the residue-based one.

Three consequences:

- A mass-balance statement should carry both numbers: total residue and identified fraction.
- An "unidentified" remainder is not automatically harmless; it is unexplained. Unexplained
  is a documentation status, not a toxicological one.
- If the sum of identified peaks exceeds the gravimetric residue, the quantitation or the
  residue method is wrong — that is a check a reviewer can do in one line.

## 8. Comparing against a threshold: the per-day step

Thresholds in E&L programmes are usually expressed per day, because exposure is a daily mass.
The conversion from a surface load is:

```
E_allowable [µg/cm²] = tier [µg/day] / (A [cm²] × containers/day)
```

For a 5 µg/day tier, a 2R vial (7.798 cm²) and four containers a day, the allowable surface
load is 0.160 µg/cm². At one container a day it is 0.641 µg/cm² — four times looser. The same
material therefore passes or fails on dose count alone, which is why a supplier cannot state
compliance without the intended use pattern.

The dataset uses three example tiers (0.15, 5 and 50 µg/day). They are example inputs chosen
to span three orders of magnitude so the arithmetic can be followed; they are not regulatory
limits and must not be quoted as such. Every real programme works from its own threshold
basis, route and duration — the arithmetic is portable, the numbers are not.

## 9. Six failure modes, and the arithmetic that catches each

| # | What the document says | What is missing | Arithmetic check |
|---|---|---|---|
| 1 | "Extractables < 0.5 µg" | no denominator | ask for µg/cm² and the wetted area; recompute per container |
| 2 | "0.5 µg/cm², passes 5 µg/day" | containers per day and fill | multiply by area × containers/day; check the tier basis |
| 3 | "Extractables 0.50 µg/cm², single extract" | number of extraction steps | divide by 1−(1−f)^n; a 0.6 first extract needs ×1.667 |
| 4 | "Leachables at T0 below limit" | time dependence | compare timepoint to plateau; T0 is the least informative point |
| 5 | "Stable at 40 °C for 90 days" | activation energy | state Ea and report the factor; 2.63× and 4.69× are both "90 days at 40 °C" |
| 6 | "Total extractables 0.42 µg/cm² (12 peaks)" | identified fraction, mass balance | sum identified vs NVR; if the sum exceeds NVR the method is wrong |

Each row is a one-line calculation on numbers the document already contains — which is why
these are review items rather than analytical requests. The case file encodes the same logic
as a decision engine returning `pass`/`fail` plus the qualifying flags, with ten fixed cases
asserted in `--selftest`.

## 10. Review checklist for a closure E&L package

1. **Denominator stated** for every extractable and leachable figure (µg/cm², µg/mL,
   µg/container), with the wetted area and fill volume that connect them.
2. **Container closure system defined** — glass, coating or laminate, elastomer, adhesive and
   ink are separate contributors; "the vial" is not a material.
3. **Extraction conditions** stated as solvent, time, temperature and surface-to-volume ratio;
   a change in S/V changes the result at constant surface load.
4. **Extraction depth** stated as number of steps with cumulative fraction, not just the first
   aliquot.
5. **Leachable timepoints** over the intended shelf life, with the kinetic argument for
   extrapolation if the plateau is not reached.
6. **Accelerated conditions** with the activation energy used and the resulting factor.
7. **Mass balance**: gravimetric or TOC total alongside the identified fraction, and a stated
   treatment of the unidentified remainder.
8. **Dose basis**: containers per day and fill volume, so the per-day exposure can be
   recomputed independently.

## 11. Boundaries

- The container dimensions here are idealised cylinders with round-number dimensions. Real
  vials have shoulders, neck geometry, coatings and a closure surface that this model does not
  represent; the arithmetic transfers, the absolute areas do not.
- Extraction fractions, rate constants and activation energies in the tables are illustrative
  inputs. The tables quantify sensitivity to them; they do not measure them.
- The three tiers are example policy inputs, not limits, and passing a comparison is not a
  safety determination. Nothing here addresses toxicology, route of exposure, dose, handling,
  storage or any biological effect.
- No measured extractable or leachable value is included. Every value is a closed-form
  function of a stated input, which is what makes the tables reproducible and also what makes
  them insufficient on their own.

The review workflow and documentation structure these tables support are described at
<https://gethelixpeptide.com/quality>, and product-level documentation at
<https://gethelixpeptide.com/products>.
