# Designing a Solubility Screen: Matrix Choice, Mass Budget, and Reading Rules

*Research documentation note. This describes how to design and read a laboratory
solubility screen for a research peptide, and what the resulting numbers do and do
not support. It contains no result for any compound and no handling, dosing or
storage instruction.*

## 1. The problem with a single solubility figure

A supplier statement that a material is "soluble in water" or "soluble at 10 mg/mL"
is a point measurement with most of its context removed. Four omissions decide
whether the number can be used at all:

1. **Which solvent composition** — water, buffer, saline and co-solvent mixtures are
   not interchangeable, and pH is the single largest variable for an ionisable peptide.
2. **Which concentration** — solubility is a boundary, so a figure without the
   concentration at which the boundary was observed is a category, not a measurement.
3. **Which observation** — "clear", "slightly hazy" and "no visible particles" are
   three different criteria, and the last one is satisfied by a colloidal dispersion.
4. **Which time** — a reading at one hour and a reading at twenty-four hours are two
   different experiments on materials that hydrate, aggregate or slowly precipitate.

A screen is the cheapest way to replace the point with bounds. It does not deliver
"the solubility"; it delivers a map of conditions where the material was in one
phase at a stated concentration at a stated reading time, plus the conditions where
it was not. That is a weaker claim than a number and a much more useful one, because
it can be checked.

This note accompanies a deterministic reference set: a 24-condition buffer-by-pH
design table, a six-rung concentration ladder with its mass budget, a table of ten
observation codes, and a rule engine that turns a series of observations into a
bounded verdict. All values in the tables are exact functions of the stated design
inputs.

## 2. The three axes, and what confounds each

Any screen is a low-resolution sampling of three axes: solvent composition (buffer
species and pH), concentration, and time. Each axis has a failure mode that produces
a plausible but wrong map.

**Buffer species.** Different buffers at the same nominal molarity have very
different capacity at the same pH, because capacity depends on the distance between
the working pH and the buffer's pKa. Comparing "acetate pH 6" with "phosphate pH 6"
compares two solutions, only one of which is holding pH 6.

**pH.** pH is not an independent variable unless it is stabilised. A well that is
nominally pH 7 in a buffer with almost no capacity at pH 7 will move as soon as the
material, the container or the atmosphere perturbs it — and the perturbation caused
by dissolving a peptide is itself part of the experiment.

**Concentration.** Without a ladder there is no boundary, only a pass or a fail.
With a ladder, the spacing determines the resolution: a two-fold series bounds the
answer to within a factor of two, and no further.

**Time.** Hydration, dissolution of a lyophilised cake and aggregation all have
kinetics. A fixed reading time makes the result reproducible; it does not make it
equilibrium.

## 3. The buffer axis: a common pH grid plus an adequacy column

The reference design uses four buffer systems at 20 mM total — acetate (pKa 4.76),
citrate (second pKa 4.76), phosphate (second pKa 7.20) and Tris (pKa 8.06) — read
across a common pH grid of 3.0, 4.0, 5.0, 6.0, 7.0 and 8.0. That is 24 conditions.

The grid is deliberately *not* centred on each buffer's pKa. Centring it would make
every well comfortable and hide the most common design error: a well labelled with a
pH that the buffer cannot hold. Instead, each well carries a computed adequacy band
from the van Slyke expression for a monoprotic buffer:

```
f    = 1 / (1 + 10^(pKa - pH))
beta = ln(10) * C * f * (1 - f)        [mM per pH unit]
```

Capacity peaks at pH = pKa with the value ln(10)/4 × C = 0.5756 × C, and falls to
0.1903 × C at one pH unit away — a third of the peak. At 20 mM the peak is
11.51 mM/pH. Three bands are used:

- **ok**: at least 20 % of peak and at least 3 mM/pH.
- **weak**: 10–20 % of peak, or 2–3 mM/pH absolute.
- **insufficient**: below both. The well cannot be said to be at its nominal pH.

Of the 24 conditions, **8 are `ok`, 3 are `weak` and 13 are `insufficient`**. That
distribution is the point of the design rather than a defect in it: two thirds of
the plate tells you where a buffer must not be trusted. Acetate holds pH 4.0
(5.81 mM/pH, 50.5 % of peak) and pH 5.0 (10.68 mM/pH, 92.7 %), is marginal at pH 6.0
(2.37 mM/pH, 20.6 %) and is effectively absent at pH 7.0 (0.26 mM/pH, 2.3 %). Tris
is the mirror image: at pH 3.0 it retains 0.0035 % of its peak capacity, which is
indistinguishable from unbuffered water.

The practical consequence is quantified by how little acid it takes to move a well
by 0.2 pH units in 1 mL:

| Condition | beta (mM/pH) | Strong acid needed for ΔpH = 0.2 |
|---|---|---|
| Acetate, pH 5.0 | 10.68 | 2.14 µmol |
| Acetate, pH 6.0 | 2.37 | 0.47 µmol |
| Acetate, pH 7.0 | 0.26 | 0.05 µmol |

Fifty nanomoles is a pipetting error, a trace of acidic residue on glass, or the
counterion load of the peptide itself. A haze in that well is a pH observation, not
a solubility observation, and the adequacy column is what lets a reader tell the
difference after the fact.

One further interaction matters and is easy to miss: **the analyte is also a
buffer**. At 2 mg/mL and a molar mass near 1200 g/mol the peptide is present at
about 1.67 mM, and a single ionisable side chain at that concentration contributes up
to 0.96 mM/pH at its own pKa. That is larger than the capacity of the weakest wells
in the grid, which means the material can move the pH of the very well used to
measure it. Screening at a fixed nominal pH without measuring the actual pH after
dissolution leaves this unquantified.

## 4. The concentration axis and the mass budget

Stage one is a single screening concentration: 2 mg/mL in 0.25 mL per well. Stage two
is a six-rung two-fold ladder from 0.25 to 8 mg/mL, run only in the conditions that
survived stage one.

Two arithmetic facts govern how the plate is prepared. First, the stage-one plate
consumes 24 × 0.25 mL × 2 mg/mL = **12.0 mg of net peptide**, or 13.33 mg of material
at 90 % net content, if every well is filled from a common stock. Second, the ladder
should not be weighed rung by rung:

| Rung (mg/mL) | Net peptide (mg) | Weighed at 90 % (mg) | Molarity at 1200 g/mol (µM) |
|---|---|---|---|
| 0.25 | 0.0625 | 0.0694 | 208 |
| 0.50 | 0.1250 | 0.1389 | 417 |
| 1.00 | 0.2500 | 0.2778 | 833 |
| 2.00 | 0.5000 | 0.5556 | 1667 |
| 4.00 | 1.0000 | 1.1111 | 3333 |
| 8.00 | 2.0000 | 2.2222 | 6667 |

Preparing every rung independently costs 4.375 mg (at 90 % content); preparing one
stock at 8 mg/mL and diluting costs 2.222 mg. The ratio is **1.969** — the sum of a
two-fold series divided by its top term. The ladder is therefore built from one
stock, and the stock mass, not the sum of the rungs, is what must be available.

Three corrections sit outside the table and each shifts the mass:

- **Net content.** The weighed mass is divided by net peptide content. At 90 %
  content the 8 mg/mL stock needs 2.22 mg of material to deliver 2.00 mg of peptide.
- **Salt form.** The peptide fraction of a salt is lower than that of the free base;
  a trifluoroacetate form of a small peptide can carry only half its mass as peptide.
  A ladder prepared by mass without this correction is not the ladder that was
  designed.
- **Volumetric tolerance.** At the 0.25 mg/mL rung a few microlitres of diluent
  error is a percent-level concentration error, which is the same order as the
  resolution of the ladder itself.

## 5. Reading the plate: codes, contiguity, and verdicts

The observation vocabulary is fixed before the plate is read, because a vocabulary
invented after the fact encodes the expected answer. Ten codes are defined, each
with a stated optical basis; the decisive split is between "clear", "dispersed but
no discrete particles" and "solid phase present".

- `clear` — no scatter against a dark background under oblique light.
- `opalescent` / `haze` — scatter present, no discrete particles. Dispersed, not clear.
- `particulates` / `precipitate` — discrete particles, or material on the well floor.
- `gel`, `film`, `colour`, `immiscible`, `bubbles` — neither clear nor dispersed;
  each is a different failure and is recorded as such.

Three rules convert a series into a statement:

1. **Maximum clear concentration** is the highest rung of the *contiguous* clear run
   starting at the lowest rung. Contiguity is not a stylistic choice: a clear rung
   above a failed rung has no physical explanation within a monotonic solubility
   series, so it signals an artefact (incomplete wetting, a bubble, contamination,
   a pipetting error) and the series must be repeated rather than averaged.
2. **Dispersed extent** applies the same rule to clear + opalescent + haze. Reporting
   only this number overstates the result, because a hazy well is not a solution;
   reporting only the clear extent understates the range in which the material is at
   least dispersed.
3. **Series verdict** is one of `no_hit` (no clear rung), `floor_only` (only the
   lowest rung clear, so the boundary is below the ladder), `window` (boundary inside
   the ladder) or `beyond_top` (top rung clear, so the ladder is too short). Only
   `window` produces a bounded number.

Aggregated across conditions, the screen verdict distinguishes `single_condition`,
`ph_dependent` (one buffer species, three or more pH), `species_dependent` (two or
more species, fewer than three pH), `broad` (two or more species and three or more
pH) and `no_hit`. The distinction matters in procurement: a `ph_dependent` result
that spans three pH values inside a single buffer species is often a capacity
artefact, because that buffer is only adequate over part of the range.

Two flags void a boundary outright. `screen_saturated` — every series `beyond_top` —
is a ladder problem or a detection problem before it is a solubility result; a
material that looks clear at 8 mg/mL in every condition is more likely below the
visible threshold than unusually soluble. `non_monotonic` is an artefact signal, as
above.

## 6. What a reproducible screen record contains

A screen that cannot be re-read is not evidence. Eight fields make the difference:

1. Buffer species, total molarity and the measured pH of each well after dissolution.
2. Peptide net content and salt form used for the mass calculation, with the source
   of both figures.
3. The concentration ladder, its preparation route (single stock or per-rung) and
   the diluent composition.
4. Well volume, container material and any filter or centrifugation step.
5. Reading time or times, temperature, and the illumination and background used.
6. The observation code assigned to every well, including the wells that failed and
   the wells that were ambiguous.
7. Which conditions were `ok`, `weak` or `insufficient` on buffer capacity, and the
   pKa values used to compute that.
8. Controls: diluent-only wells, and where possible a material of known behaviour,
   read in the same session.

Fields 6 and 7 are the ones usually missing, and they are the two that let a reader
distinguish a solubility boundary from a pH drift and an artefact from a result.

## 7. Seven design errors that survive review

1. **One buffer, one pH, one concentration.** Produces a pass/fail that cannot be
   interpreted and cannot be compared with anything.
2. **A pH grid that leaves the buffer's useful range.** Labels a well pH 7 when the
   buffer has 2 % of peak capacity there. The adequacy column exists to catch this.
3. **Reporting the dispersed extent as solubility.** A colloidal dispersion is not a
   solution; the distinction is a filtration or centrifugation step away.
4. **No diluent-only control.** Without it, a haze from the diluent, the container or
   the water is attributed to the material.
5. **An unfixed reading time.** Two operators reading at one hour and at one day will
   disagree, and both will be right about their own experiment.
6. **Ignoring low-concentration losses.** Adsorption to plastic and loss on filters
   are largest exactly where the ladder is most sensitive, at the bottom rungs.
7. **A ladder that starts too high.** If the lowest rung already fails, the screen
   reports "insoluble" when it has only shown that the material is not soluble at
   0.25 mg/mL.

## 8. Using a screen result in a procurement review

- Ask for the concentration, not the adjective. "Soluble" without a concentration is
  not a specification.
- Ask which buffer and which measured pH, and whether the pH was measured after the
  material dissolved.
- Ask for the reading time and the observation criterion. A "clear" result by a
  particle-count criterion is a different claim from "clear" by eye.
- Compare only results produced under the same buffer, pH, concentration and reading
  time. Two screens with different grids cannot be placed on one axis.
- Regard a single-point result as a bound, not a value. A screen that reports one
  concentration has bounded the answer to within the ladder spacing and no better.
- Where the screen is the only evidence available, prefer the result that states its
  failures: a record listing the wells that precipitated is more informative than one
  that lists only the wells that did not.

## 9. Limits

Clarity is an operator judgement against a background, not a measured concentration;
a clear well can hold material below the visible threshold. The screen bounds and does
not quantify. Reading time is part of the result, and neither the one-hour nor the
twenty-four-hour reading is an equilibrium value. Adsorption and filtration losses are
invisible to a plate read and can dominate the mass balance at the low rungs. Buffer
pKa values used here are tabulated at 25 °C and zero ionic strength and shift with
temperature and ionic strength — Tris most of all. Co-solvent, ionic strength and
temperature all move both the buffer and the material. Nothing in this note is a
handling instruction, a storage condition, a dose, or a statement about any
biological effect.

## 10. Reference set contents

- `screen-design.csv` — 24 conditions with pKa, distance from pKa, computed buffer
  capacity, percentage of peak, adequacy band, target concentration, net and weighed
  mass per well, and molarity at a model molar mass of 1200 g/mol.
- `concentration-ladder.csv` — six rungs from 0.25 to 8 mg/mL with net mass, weighed
  mass at 90 % content, molarity, cumulative direct-weighing cost and single-stock
  mass.
- `observation-codes.csv` — ten codes with definitions and their membership in the
  clear, dispersed and solid-phase sets.
- `screen-eval-cases.json` — eleven reading cases (eight series, three screen
  aggregates) with fixed expected verdicts.
- `solubility_screen.py` — the rule engine and calculator, with `--selftest`
  (32 assertions), `--design`, `--beta`, `--ladder` and `--series`.

Related documentation: quality documentation and certificate-of-analysis structure
for research supply — https://gethelixpeptide.com/quality ; product-level
documentation and batch records — https://gethelixpeptide.com/products .
