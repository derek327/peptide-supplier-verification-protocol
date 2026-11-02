# Reconstitution Buffer Selection: Reference Tables for Diluent Choice

Arithmetic reference set for the chemistry decisions that sit behind a reconstitution
instruction: which buffer species, at what concentration and pH, with what ionic strength,
and what volume follows from the label mass and the peptide content of the fill.

Every value is an exact function of the stated inputs. No measured, fitted or observed data
is included, and nothing here describes behaviour in any biological system.

## Contents

| File | Contents |
|---|---|
| `buffer-species.csv` | 9 buffer systems: conjugate acid, pKa at 25 C, useful pH window, temperature coefficient, volatility, practical notes |
| `buffer-capacity-curve.csv` | 153 rows: van Slyke buffer capacity for acetate / phosphate / Tris at 10, 20 and 50 mM across pKa -2 to +2 in 0.25 pH steps |
| `diluent-recipes.csv` | 8 diluent recipes with nominal and speciation-adjusted ionic strength and nominal osmolarity |
| `concentration-arithmetic.csv` | 16 rows: label mass x net peptide content x target concentration -> diluent volume, plus the volume that delivers 100 ug |
| `reconstitution_calc.py` | Command-line calculator with `--selftest` |

## Formulas

Buffer capacity, monoprotic buffer of total concentration C:

```
beta = ln(10) * C * Ka * [H+] / (Ka + [H+])^2
beta(pH = pKa) = ln(10)/4 * C = 0.5756 * C
beta(pH = pKa +/- 1) = 0.1903 * C
```

Ionic strength:

```
I = 0.5 * sum(ci * zi^2)
```

Fraction charged (monoprotic acid / base):

```
acid: f(A-)    = 1 / (1 + 10^(pKa - pH))
base: f(BH+)   = 1 / (1 + 10^(pH - pKa))
```

Reconstitution volume from label mass and net peptide content:

```
V(mL) = label_mass(mg) * net_content(%) / 100 / target(mg/mL)
```

## Worked values in this set

| Quantity | Value |
|---|---|
| 20 mM acetate, pH 4.5 | beta = 10.540 mM/pH (peak at 20 mM = 11.513) |
| 20 mM phosphate, pH 7.4 | beta = 10.923 mM/pH |
| 25 mM Tris, pH 8.0 | beta = 14.323 mM/pH |
| 0.9 % NaCl | I = 154 mM, 308 mOsm/L |
| PBS 1x | I = 171.5 mM nominal, 313 mOsm/L |
| 0.9 % benzyl alcohol | I = 0 mM, 87 mOsm/L |
| 20 mM acetate, pH 4.5 (speciation) | I = 13.55 mM effective (20.00 nominal), 40.0 mOsm/L |
| 25 mM Tris, pH 8.0 (speciation) | I = 13.36 mM effective (25.00 nominal), 38.4 mOsm/L |
| 10 mg at 90 % content to 5 mg/mL | 1.800 mL, 9.000 mg peptide |

## Invariance checks applied before release

1. Buffer capacity at pH = pKa equals ln(10)/4 x C for 10, 20 and 50 mM, exactly.
2. Buffer capacity at pKa +/- 1 equals 0.1903 x C, and falls strictly on both sides of the peak.
3. Capacity scales linearly with total concentration at fixed pH.
4. 0.9 % NaCl returns I = 154 mM and 308 mOsm/L; water returns 0 for both.
5. Benzyl alcohol returns I = 0 with 87 mOsm/L, so ionic strength and osmolarity are not
   interchangeable quantities in this set.
6. The speciation-adjusted value falls below the fully-ionised nominal value, which is the
   point of reporting both: acetate 13.55 vs 20.00 mM at pH 4.5, Tris 13.36 vs 25.00 mM at
   pH 8.0. A buffer quoted at nominal ionic strength overstates its ionic strength whenever
   the working pH is more than about one unit from its pKa.
7. Reconstitution volume is inversely proportional to target concentration and falls strictly
   as net peptide content falls.
8. The molarity unit conversion is self-checked: 5 mg/mL at 1200 g/mol is 4.167 mM.

## Limits

- pKa values are tabulated at 25 C and zero ionic strength. Apparent pKa shifts with
  temperature and ionic strength; a working value must be measured at the working condition.
- Ionic strength is computed from the recipe as written. The speciation-adjusted column is
  implemented only for monoprotic weak acids and bases; phosphate is reported as nominal and
  is explicitly not modelled as a diprotic system here.
- Osmolarity is a particle-count estimate, not a measurement. Real osmolarity requires
  freezing-point depression or vapour-pressure measurement.
- Buffer capacity describes resistance of the solution to added acid or base. It says nothing
  about whether a peptide is soluble, stable or unaffected at that pH.
- Aggregation, adsorption and surface loss are physical phenomena that these tables do not
  quantify; they have to be measured on the actual material and container.
- No value in this set is a handling instruction, a dose, or a statement about any
  biological effect.

## Related documentation

- Quality documentation framework for GMP-oriented supply:
  https://helixgmppeptides.com/coa-guide
- Institutional and OEM supply overview: https://helixgmppeptides.com/

## License

CC BY 4.0
