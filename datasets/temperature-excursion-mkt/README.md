# Temperature Excursion Reference Tables: MKT Profiles and Triage Matrix

Deterministic reference tables for reviewing a shipment temperature trace against a declared
+2 to +8 &deg;C transport range. Every number is computed from the formulas below and a stated
activation energy &mdash; no observed, fitted or measured data is involved, so every row can be
regenerated exactly.

## Contents

| File | Description |
|---|---|
| `mkt-reference.csv` | 24 profiles (48 h transit: a baseline temperature plus one excursion of stated magnitude and duration), with max/min recorded temperature, arithmetic mean, mean kinetic temperature at two activation energies, and hours outside the +2 to +8 &deg;C band |
| `excursion-triage-matrix.csv` | 18 rows: declared product band x peak temperature x duration outside band, mapped to a documentation action |

## Formulas

```
MKT = (dH / R) / ( -ln( SUM( exp(-dH/(R*Ti)) * dti ) / SUM(dti) ) )

dH        assumed activation energy: 83.144 kJ/mol (conventional) or 62.8 kJ/mol
R         8.314462618 J/(mol*K)
Ti        interval temperature, kelvin
dti       interval duration, hours
```

Invariance checks applied before publication: a constant-temperature profile returns that
temperature exactly; a hot spike raises MKT above the arithmetic mean; changing dH changes
MKT.

## What these tables do not say

- They describe arithmetic only. They are not storage instructions, dosing guidance or
  clinical information, and they say nothing about any specific peptide.
- **MKT hides peaks.** A one-hour excursion to 40 &deg;C can produce the same MKT as a flat
  profile. Always report maximum recorded temperature and duration outside band next to MKT.
- **The activation energy is a modelling assumption, not a measured property.** Two
  laboratories using different dH values disagree on MKT for the same trace; state which was
  used. The two columns here exist to make that sensitivity visible.
- Whether a molecule changed (aggregation, oxidation, deamidation, moisture uptake) is an
  assay question. These tables cannot answer it and do not claim to.
- For an illustrated triage walkthrough and the full documentation file specification, see
  the companion protocol document in this repository.

## Related documentation

- GMP-oriented quality documentation and CoA guidance: https://helixgmppeptides.com/coa-guide
- Catalog and shipping documentation: https://helixpeptidesupply.com/catalog

## Citation

Cite the DOI of this record, including the dH value used. Recomputation from the formulas
above reproduces every row.

## License

CC BY 4.0
