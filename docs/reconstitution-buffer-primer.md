# Reconstitution Buffer Selection: A Chemistry Primer for Documentation Review

A reconstitution instruction looks like a single sentence — *dissolve the contents in N mL of
diluent* — but it encodes four separate decisions: which liquid, at what pH resistance, at what
ionic strength, and what the resulting solution actually contains per millilitre. Each of those
decisions is checkable with arithmetic. Most supplier statements carry only one of them, usually
the volume.

This primer sets out the four variables, the formulas that connect them, and the eight items a
statement should contain before a buyer can reproduce what the supplier did. It is written for
procurement and documentation review of research-grade material; it contains no handling
instruction, no dose and no statement about any biological effect.

The accompanying reference set (`out/reconstitution-buffers/`) computes every figure quoted
below from stated inputs, and ships a calculator with a self-test.

## 1. The four variables

| Variable | What it controls | How a reviewer checks it |
|---|---|---|
| pH | Charge state of ionisable groups; solubility; adsorption behaviour | Stated value plus the species used to reach it |
| Buffer capacity | How far pH moves when acid, base or dilution arrives | Total buffer molarity and the distance from its pKa |
| Ionic strength | Electrostatic interactions, aggregation propensity, salting effects | Species list and concentrations, not just "20 mM buffer" |
| Other solutes | Tonicity, assay interference, preservative presence | Each excipient named with its concentration |

A statement that gives a pH without a species, or a species without a molarity, leaves the
reviewer unable to compute the second and third rows of that table.

## 2. Species selection: the pKa window is a hard constraint

A buffer holds pH best within about one unit either side of its pKa. Beyond that the capacity
falls to a third of its peak, and the solution is mostly a salt solution with a pH label.

| Buffer (conjugate acid) | pKa (25 °C) | Useful window | ΔpKa per °C | Volatile |
|---|---|---|---|---|
| Acetate | 4.76 | 3.6–5.6 | +0.0002 | yes |
| Citrate (pKa2) | 4.76 | 3.0–6.2 | −0.0024 | no |
| MES | 6.10 | 5.5–6.7 | −0.011 | no |
| Histidine (imidazole) | 6.04 | 5.5–6.5 | −0.017 | no |
| Phosphate (pKa2) | 7.20 | 6.2–8.2 | −0.0028 | no |
| HEPES | 7.55 | 6.8–8.2 | −0.014 | no |
| Tris | 8.06 | 7.0–9.0 | −0.028 | no |
| Ammonium | 9.25 | 8.2–10.2 | −0.030 | yes |
| Glycine (pKa2) | 9.78 | 8.8–10.6 | −0.025 | no |

The temperature column is not decoration. Tris has the largest coefficient in the table: its pKa
is 8.06 at 25 °C, **8.62 at 5 °C and 7.72 at 37 °C**. A Tris buffer adjusted to pH 8.0 on the
bench is a pH 8.5 buffer in a cold room and a pH 7.7 buffer at 37 °C, and its capacity changes
with it — 14.32 mM/pH at pH 8.0 versus 8.48 mM/pH at pH 7.4 for the same 25 mM preparation.
Phosphate, at −0.0028 per °C, moves roughly ten times less over the same interval. If a
specification states a pH without a temperature, the number is not reproducible.

Volatility matters for documentation in a different way: acetate (as free acid) and ammonium
lose buffer components on repeated opening, so a pH verified at release does not necessarily
describe the material months later.

## 3. Buffer capacity: the number that is never printed

Buffer capacity β is the amount of strong acid or base, in millimoles, needed to move one litre
of solution by one pH unit. For a monoprotic buffer of total concentration C:

```
beta = ln(10) * C * Ka * [H+] / (Ka + [H+])^2
beta (pH = pKa)        = 0.5756 * C
beta (pH = pKa ± 1)    = 0.1903 * C
```

Worked values from the reference set:

| Preparation | β (mM per pH unit) | Share of its own peak |
|---|---|---|
| 20 mM acetate, pH 4.50 | 10.540 | 91.5 % |
| 20 mM acetate, pH 5.76 | 3.806 | 33.1 % |
| 20 mM phosphate, pH 7.40 | 10.923 | 94.9 % |
| 20 mM phosphate, pH 6.20 | 3.806 | 33.1 % |
| 25 mM Tris, pH 8.00 | 14.323 | 99.5 % |
| 25 mM Tris, pH 7.40 | 8.478 | 58.9 % |
| 10 / 20 / 50 mM at peak | 5.758 / 11.513 / 28.782 | 100 % |

Put at vial scale, β = 10.540 mM/pH means that **1.0 mL of the pH 4.5 acetate preparation needs
1.05 µmol of strong acid to move 0.1 pH unit**; 0.5 mL needs 0.53 µmol. That is a very small
absolute amount. A 1–2 mL vial is a small reactor, and anything that carries acid or base into
it — a preservative, an acidic counterion from the peptide itself, dissolved CO₂ from room air —
is a large perturbation relative to that capacity. This is the practical reason the buffer
concentration belongs in the statement and not only the pH.

Note also that capacity is linear in concentration but bounded by the distance from the pKa.
Doubling molarity at pH 5.76 does not bring acetate to its peak value; it only doubles a third
of it.

## 4. Ionic strength and osmolarity are separate dials

Ionic strength weights each species by the square of its charge:

```
I = 0.5 * sum(ci * zi^2)
```

Osmolarity counts particles, charged or not. The two are frequently conflated, and one recipe in
the set shows why that fails: **0.9 % v/v benzyl alcohol has an ionic strength of 0 mM and an
osmolarity of 87 mOsm/L.** It contributes particles and no ions.

| Recipe | I nominal (mM) | I at working pH (mM) | Osmolarity (mOsm/L) |
|---|---|---|---|
| Sterile water | 0.00 | — | 0.0 |
| 0.9 % NaCl | 154.00 | — | 308.0 |
| PBS 1× | 171.50 | — | 313.0 |
| 20 mM sodium acetate, pH 4.5 | 20.00 | 13.55 | 40.0 |
| 20 mM sodium phosphate, pH 7.4 | 20.00 | not modelled | 40.0 |
| 25 mM Tris-HCl, pH 8.0 | 25.00 | 13.36 | 38.4 |
| TBS (25 mM Tris / 137 mM NaCl / 2.7 mM KCl) | 164.70 | 160.21 | 324.9 |
| 0.9 % benzyl alcohol | 0.00 | — | 87.0 |

The nominal column assumes every weighed salt is fully ionised. The working-pH column applies
the actual distribution: at pH 4.5 only 35.5 % of a 20 mM acetate preparation is charged
(7.09 mM), so the effective ionic strength is 13.55 mM, not 20.00. Tris is further from its pKa
at pH 8.0 than the label suggests — 53.4 % protonated, giving 13.36 mM against a nominal 25.00.

Two consequences for review:

- "20 mM buffer" describes molarity, not ionic strength. Two 20 mM preparations at different pH
  values differ by up to a factor of two in ionic strength.
- A statement that lists only salts (NaCl, KCl) and omits the buffer species understates ionic
  strength substantially; TBS is 160 mM effective, not the 140 mM the salt line implies.

Phosphate is reported as nominal here and explicitly not modelled as a diprotic system. That is
a stated limit of the reference set, not a property of phosphate.

## 5. From label mass to concentration: two denominators

The volume that produces a stated concentration follows from the peptide mass, not the label
mass:

```
net peptide (mg)   = label mass (mg) * net content (%) / 100
volume (mL)        = net peptide (mg) / target concentration (mg/mL)
```

A 5 mg fill at 90 % net content contains 4.50 mg of peptide. To reach 2 mg/mL, the volume is
2.250 mL; to reach 5 mg/mL, 0.900 mL. Using the label mass instead of the peptide mass
overstates the delivered concentration by 11 % in this case, and the error grows as content
falls.

Molar concentration needs one more input, the peptide's molar mass: 1 mg/mL of a 1200 g/mol
peptide is 833 µM, and the same mass of a 2400 g/mol peptide is 417 µM. A statement that gives
mg/mL without the construct's molar mass cannot be converted to molarity by the reader.

So the three numbers that make concentration checkable are: **label mass, net peptide content
with its method, and either the target concentration or the volume**. Missing the content value,
the volume cannot be verified at all.

## 6. Losses the arithmetic does not capture

Everything above assumes the peptide all ends up in solution. At low concentration, with a high
surface-to-volume ratio, a measurable fraction can sit on the container wall, on a filter
membrane, or in dead volume. None of that is predictable from the formulas; it has to be
measured on the actual material and container.

What a reviewer can ask for instead of a claim:

- the container type stated in the record (glass vs polymer, and the polymer if relevant);
- if filtration is specified, the membrane material and pore size;
- whether a rinse step is part of the instruction, and what volume it uses;
- a mass-balance basis for any statement that no loss occurs.

A statement that the solution is "complete" without a mass-balance basis is an assertion, not a
result.

## 7. Preservative-containing diluents

Benzyl alcohol at 0.9 % v/v is 87 mM, non-ionic, and contributes osmolarity without ionic
strength. Where it appears in a diluent, three things belong in the documentation: the
concentration, the fact that the diluent is not plain water, and the container/multi-entry
framing that made the preservative relevant in the first place. The word "bacteriostatic" on its
own does not specify a concentration, and compatibility with a given peptide is not implied by
the presence of a preservative.

## 8. What a reviewable reconstitution statement contains

1. Diluent identity, including whether it contains a preservative and at what concentration.
2. Diluent volume, or the target concentration plus the arithmetic that produces the volume.
3. Buffer species, molarity and pH, with the temperature at which the pH was set.
4. The peptide's net content and the method used to determine it.
5. Resulting concentration expressed both as mg/mL and, where the construct mass is known, as
   molarity.
6. Container and, if filtration is specified, membrane material and pore size.
7. A storage statement for the solution that is scoped to what was actually tested — and an
   explicit statement where nothing was tested.
8. The research-use-only framing, kept separate from the physical description.

## 9. Procurement checklist

- [ ] pKa of the stated buffer is within about one unit of the stated pH (if not, ask why).
- [ ] Buffer molarity is stated, not only the pH (capacity is otherwise uncomputable).
- [ ] Buffer species is named, not implied by a trade name.
- [ ] Net content is stated with its method; concentration arithmetic reproduces the stated volume.
- [ ] Ionic strength is either stated or computable from a complete species list.
- [ ] Any preservative is named with its concentration, and its presence is reflected in the
      container and storage framing.

## 10. What these tables cannot tell you

- Whether a given peptide dissolves at a given concentration in a given buffer. Solubility is a
  property of the sequence and the condition, measured, not derived.
- Whether it aggregates, and at what ionic strength or pH. Aggregation is measured.
- Whether it is chemically stable over time in the solution. That is a stability study.
- The true osmolarity. The tables give a particle-count estimate; measurement requires
  freezing-point depression or vapour pressure.
- The true pKa at the working ionic strength and temperature. Tabulated values are at 25 °C and
  zero ionic strength; apparent values shift, and the shift is largest for Tris.
- Anything about behaviour in a biological system. Nothing in this set addresses that.

## Reference set

`out/reconstitution-buffers/` contains `buffer-species.csv` (9 systems), `buffer-capacity-curve.csv`
(153 rows: acetate, phosphate and Tris at 10, 20 and 50 mM across pKa ± 2 in 0.25 steps),
`diluent-recipes.csv` (8 recipes), `concentration-arithmetic.csv` (16 rows) and
`reconstitution_calc.py`, a calculator with `--selftest`. Release checks assert the peak values
(0.5756·C), the pKa ± 1 values (0.1903·C), the saline and PBS values, and the inverse relation
between volume and target concentration, so the published numbers cannot drift from the code.

Documentation framework for GMP-oriented supply: https://helixgmppeptides.com/coa-guide

Institutional supply overview: https://helixgmppeptides.com/

*Published for laboratory and research procurement use. CC BY 4.0.*
