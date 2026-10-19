# Counterion and Salt Form: Mass-Balance Reference Tables

Deterministic reference tables for the arithmetic that connects a peptide's salt form to the
peptide mass and molar quantity in a weighed sample. Every value is computed from the formula
below and the stated inputs &mdash; no observed or fitted data is involved, so every row can be
regenerated exactly.

## Contents

| File | Description |
|---|---|
| `salt-form-mass-balance.csv` | 10 rows: GHK (three protonatable basic centres) and BPC-157 (two) as free base, acetate, chloride, trifluoroacetate and trifluoroacetate dihydrate &mdash; salt molar mass, peptide mass fraction, mg of salt per &micro;mol of peptide, net peptide in a 10 mg label |
| `label-mass-drift.csv` | 6 rows: the same 10 mg weighed mass expressed as acetate, chloride and TFA, with net peptide mass, molar amount and percentage change against the acetate form |
| `counterion-sensitivity.csv` | 5 rows: a 1200 g/mol backbone with 0&ndash;4 protonatable centres, acetate versus TFA, showing how the counterion penalty scales with charge count |
| `salt_form_calc.py` | Command-line calculator for any input set, with a `--selftest` |

## Formula

```
salt_molar_mass       = peptide_molar_mass + n * counterion_molar_mass + w * 18.015
peptide_mass_fraction = peptide_molar_mass / salt_molar_mass
net_peptide_mg        = weighed_mg * peptide_mass_fraction
moles                 = (net_peptide_mg / 1000) / peptide_molar_mass
```

Counterion molar masses used: acetate 59.044, chloride 35.453, trifluoroacetate 113.023
g/mol; water 18.015 g/mol.

## Invariance checks applied before publication

A free base with no bound water returns exactly 100 % peptide fraction; the salt molar mass
equals the free peptide plus the stated counterion and water masses; the peptide fraction falls
strictly as the number of bound counterions rises; at equal charge count the TFA fraction is
lower than the acetate fraction; and no salt row yields more peptide than the label mass.
The GHK tri-TFA fraction is asserted to lie between 49 and 51 %, and the TFA-versus-acetate
peptide-mass difference for GHK to within one percentage point of 23.8 %.

## What these tables do not say

- They are documentation arithmetic. They are not handling, storage, analytical or dosing
  guidance and say nothing about the behaviour of any peptide in any biological system.
- **Integral stoichiometry is a modelling assumption.** Real materials can carry fractional or
  mixed counterion loads, and the number bound depends on the isolation pH and ion-pairing
  conditions. The certificate should state the actual counterion content; substitute it for
  `n` rather than assuming the maximum.
- The peptide molar mass must refer to the free peptide, not the salt. Using a salt molar mass
  in the denominator double-counts the counterion.
- Water content moves with handling. A value measured at release is a snapshot, not a constant.
- The tables do not predict purity, stability, solubility or chromatographic behaviour; they
  only convert a stated composition into mass and moles.

## Related documentation

- Catalog and product documentation: https://helixpeptidesupply.com/catalog
- Product-level documentation and batch records: https://helixpeptidesupply.com/products

## Citation

Cite the DOI of this record. Recomputation from the formula above reproduces every row.

## License

CC BY 4.0
