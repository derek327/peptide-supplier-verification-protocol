# Extractables and Leachables from Container Closure Systems: Geometry, Exposure Arithmetic, Extraction Depth and Migration Kinetics

Reference arithmetic for the numbers that appear in an extractables/leachables (E&L)
statement for a research peptide in a vial. Nothing here is a measured extractable, a
measured leachable, or a toxicological conclusion: every row is a closed-form function of
a stated input (geometry, extraction fraction, rate constant, activation energy, or an
example exposure tier), so the tables regenerate exactly.

## Contents

| File | Description |
|---|---|
| `container-geometry.csv` | 9 container/fill combinations: wetted area, surface-to-volume ratio, concentration and per-container mass per 1 ug/cm2 |
| `extractable-to-exposure.csv` | 36 rows: surface load (0.05-2.0 ug/cm2) x 3 containers x 1 and 4 containers/day -> ug/mL, ug/container, ug/day and percent of three example tiers |
| `sequential-extraction.csv` | cumulative fraction removed by 1-4 successive extractions at 0.4/0.6/0.8 per step, with the understatement factor of a single step |
| `migration-kinetics.csv` | first-order approach to plateau for 5 rate constants, fraction at 0/30/90/180/365/730 days, half-life, t90 and the 730-day extrapolation factor |
| `arrhenius-acceleration.csv` | acceleration factor for 20-100 kJ/mol between 25 C and 30/40/50 C, and the 25 C time equivalent of 90 days at 40 C |
| `el-cases.json` | 10 fixed decision cases with computed verdicts and qualifying flags |
| `el_math.py` | the module that generates every value, with `--selftest` |
| `README.md` | this file |

## Formulas

Surface-to-volume ratio of a cylindrical fill (bottom disc plus wall):

```
S/V = 4/D + 1/h          [cm2/mL],  h = 4V/(pi D^2)
```

Surface load to concentration and to per-container mass:

```
c [ug/mL] = E [ug/cm2] * S/V [cm2/mL]
m [ug/container] = E * A = c * V          A = pi D^2/4 + pi D h
exposure [ug/day] = m * (containers/day)
E_allowable [ug/cm2] = tier [ug/day] / (A * containers/day)
```

Successive extractions, each removing a fraction f of what remains:

```
cumulative(n) = 1 - (1-f)^n
```

First-order approach to a plateau C_inf:

```
C(t) = C_inf * (1 - exp(-k t))      t_half = ln2/k      t_p = -ln(1-p)/k
```

Arrhenius acceleration between two absolute temperatures:

```
AF = exp( -(Ea/R) * (1/T_acc - 1/T_ref) )      R = 8.314462618 J/(mol K)
```

## What the tables show

1. **One surface load, three different answers.** 0.50 ug/cm2 in a 2 mL fill of a 2R vial
   is 1.95 ug/mL, 3.90 ug per container and 3.90 ug/day at one container per day. The same
   surface load in a 20 mL fill of a 20R vial is 20.08 ug per container, because the wetted
   area is 5.15 times larger. At four containers per day the 2R case becomes 15.60 ug/day.
2. **Fill volume moves the concentration without changing the load.** S/V = 4/D + 1/h, so a
   0.5 mL fill of the same 2R vial has an S/V 1.435 times the 2 mL fill: the same ug/cm2
   gives 1.435 times the ug/mL.
3. **A single extraction is a fraction of the total.** If one extraction removes 60 % of what
   is removable, the reported value must be divided by 0.60 to state the total; three
   successive extractions reach 93.6 %. Reporting the first extract as "the extractables"
   understates by 1.67 times.
4. **Migration is a curve, not a number.** At k = 0.001/day the half-life is 693 days, so a
   24-month timepoint sits at 51.8 % of the plateau and the plateau is 1.93 times the measured
   value. A T0 result is not a scaled-down version of the plateau.
5. **The acceleration factor is an assumption.** Between 25 C and 40 C the factor is 2.63 at
   50 kJ/mol and 4.69 at 80 kJ/mol: identical test conditions, 1.79 times different
   interpretation. Arrhenius extrapolation transfers a rate constant, not a mechanism.
6. **Identified compounds are not the whole residue.** With 0.10 ug/cm2 identified against
   0.42 ug/cm2 of non-volatile residue, the identified fraction is 23.8 %; an exposure figure
   built only from identified peaks is 4.2 times lower than the residue-based one.
7. **Extractables set an upper bound, not an exposure.** An exhaustive extractable study
   describes what the material can release under forcing conditions. A leachable study
   describes what is present in the product. The first is used as a worst case; treating it
   as the second overstates, and treating a single leachable timepoint as the plateau
   understates. Both directions appear in the cases file.

## Boundaries

- The container dimensions are idealised cylinders with round-number dimensions. They are
  not drawings of any catalogue vial, and real vials have shoulders, neck geometry, coatings
  and closure surfaces that this model does not represent.
- The three exposure tiers (0.15, 5 and 50 ug/day) are example inputs chosen to span three
  orders of magnitude. They are not regulatory limits and must not be quoted as such. Any
  real programme uses its own threshold basis, route and duration.
- The extraction fractions and rate constants are illustrative inputs. The arithmetic shows
  how sensitive a conclusion is to them; it does not supply them.
- No toxicological, clinical, handling, storage or dosing statement is made or implied.
  Passing an arithmetic comparison is not a safety determination.
- A container closure system includes the stopper, any coating or laminate, the adhesive and
  the ink. This dataset models the wetted area of the glass only, and uses it as the
  normalising area for the whole system.

## Links

Review workflow and documentation structure for research supply:
<https://gethelixpeptide.com/quality>
Product-level documentation and batch records:
<https://gethelixpeptide.com/products>

## License

CC BY 4.0
