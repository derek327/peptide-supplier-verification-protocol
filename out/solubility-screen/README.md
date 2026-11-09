# Solubility Screen Design Set: Buffer-by-pH Matrix, Concentration Ladder and Reading Rules

A reference design for a solubility screen of a research peptide, plus the rule set
that turns the observations into a bounded statement. Every number in the tables is
an exact function of the stated design inputs; no measured, fitted or literature
solubility value is included, and the set contains no result for any compound.

## Design inputs

| Parameter | Value |
|---|---|
| Buffers | acetate, citrate, phosphate, Tris (all 20 mM total) |
| pH grid | 3.0, 4.0, 5.0, 6.0, 7.0, 8.0 |
| Screening concentration | 2.0 mg/mL |
| Well volume | 0.25 mL |
| Net peptide content assumed | 90 % |
| Model peptide molar mass | 1200 g/mol |
| Conditions (stage 1) | 4 buffers x 6 pH = 24 |

The pH grid is deliberately common across buffers rather than centred on each pKa.
That is what makes the buffer-adequacy column necessary: a condition can fail because
the peptide is insoluble, or because the buffer cannot hold the pH it claims. The
adequacy screen separates the two before any interpretation.

## Buffer adequacy

Buffer capacity is the van Slyke expression for a monoprotic buffer:

    f  = 1 / (1 + 10^(pKa - pH))
    beta = ln(10) * C * f * (1 - f)        [mM per pH unit]

The maximum is at pH = pKa and equals ln(10)/4 * C = 0.5756 * C. At pKa +/- 1 the
value falls to 0.1903 * C, i.e. a third of the peak. The adequacy bands used here:

| Band | Rule | Reading |
|---|---|---|
| ok | >= 20 % of peak and >= 3 mM/pH | pH is held; observation is interpretable |
| weak | 10-20 % of peak or 2-3 mM/pH | observation kept, flagged, not used to set a boundary |
| insufficient | < 10 % of peak or < 2 mM/pH | pH not held; the well cannot support a solubility statement |

Worked points from `screen-design.csv` (all 20 mM):

| Buffer | pH | beta (mM/pH) | % of peak | Band |
|---|---|---|---|---|
| acetate | 3.0 | 0.773 | 6.7 | insufficient |
| acetate | 5.0 | 10.677 | 92.7 | ok |
| acetate | 6.0 | 2.369 | 20.6 | weak |
| phosphate | 7.0 | 10.923 | 94.9 | ok |
| Tris | 3.0 | 0.000 | 0.0 | insufficient |
| Tris | 8.0 | 11.458 | 99.5 | ok |

Tris at pH 3 retains 0.0035 % of its peak capacity: the well is effectively
unbuffered, and a haze there is a pH-drift observation rather than a solubility one.
Across the 24 conditions, 13 are `insufficient` and 3 are
`weak`, so two thirds of the grid exists to show where a buffer must not be trusted.

## Concentration axis and mass budget

One concentration gives a pass/fail, not a boundary. A six-rung two-fold ladder
(0.25 to 8 mg/mL) at 0.25 mL per well is used here.

Direct weighing every rung costs the sum of the rung masses; preparing one stock at
the top rung and diluting costs only the top rung. For this ladder the ratio is
**1.969** (total 4.3750 mg versus 2.2222 mg at 90 % net content),
so the ladder is prepared from one stock, and the stock mass is what has to be
available in the vial.

The mass column is net peptide; the weighing column divides by net content. At
90 % content the top rung needs 2.2222 mg of material to deliver 2.0000 mg
of peptide in 0.25 mL. Two further corrections matter and are not in the table:
salt form changes the peptide fraction of the weighed mass, and volumetric flasks
carry a tolerance that matters at the low rungs.

## Reading rules

Observation codes are declared in `observation-codes.csv`. Only `clear` counts as
clear; `opalescent` and `haze` count as dispersed (no discrete particles) but not
clear; `particulates`, `precipitate`, `gel`, `film`, `colour`, `immiscible` and
`bubbles` count as neither.

1. **Maximum clear concentration** = the highest rung of the contiguous clear run
   that starts at the lowest rung. A clear rung above a failed rung does not extend
   the run; the series is flagged `non_monotonic`.
2. **Dispersed extent** = the same rule applied to `clear + opalescent + haze`.
   Reporting only this number overstates what was established, because scatter at a
   rung means the material is not fully in solution at that concentration.
3. **Series verdict**: `no_hit` (no clear rung), `floor_only` (only the lowest rung
   clear, so the boundary lies below the ladder), `window` (boundary inside the
   ladder), `beyond_top` (top rung clear, so the ladder is too short).
4. **Screen verdict** over hit series: `single_condition`, `ph_dependent` (one
   buffer, three or more pH), `species_dependent` (two or more buffers, fewer than
   three pH), `broad` (two or more buffers and three or more pH), or `no_hit`.
5. **Flags that void a boundary**: `non_monotonic` (repeat before using the series),
   `re_read_after_standing` (air), `solid_phase_observed` (record the solid, do not
   report only the clear rungs), `scatter_only_extent` (clear and dispersed extents
   differ), and `screen_saturated` (every series `beyond_top`, which is a ladder
   problem or a detection-insensitivity problem before it is a solubility result).

`screen-eval-cases.json` contains 11 reading cases with fixed expected
verdicts; the builder asserts every one of them, and `solubility_screen.py --selftest`
asserts the same rules plus the arithmetic identities.

## What the screen does not establish

- Clarity is an operator judgement against a background, not a measured concentration.
  A "clear" well can still contain material below the visible threshold; the screen
  bounds, it does not quantify.
- Reading time is part of the result. A rung that is clear at one hour and hazy at
  twenty-four has two different answers, and neither is the equilibrium value.
- Adsorption to the container and loss through filters are not visible in a plate
  read; at the low rungs they can dominate the mass balance.
- Temperature, ionic strength and co-solvent change both the buffer pKa and the
  material's behaviour. A screen run at one temperature does not transfer to another.
- No value here is a handling instruction, a storage condition, a dose, or a
  statement about any biological effect.

## Related documentation

- Quality documentation and certificate-of-analysis structure for research supply:
  https://gethelixpeptide.com/quality
- Product-level documentation and batch records:
  https://gethelixpeptide.com/products

## License

CC BY 4.0
