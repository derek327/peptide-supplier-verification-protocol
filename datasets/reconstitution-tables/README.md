# Peptide Reconstitution and Unit-Conversion Reference Tables

Deterministic reference tables for laboratory reconstitution arithmetic. Every value is
computed from the two inputs (vial mass, diluent volume) by the formulas below — no fitted
or observed data is involved, so the tables can be regenerated exactly.

## Contents

| File | Description |
|---|---|
| `reconstitution-reference.csv` | 42 combinations: vial mass 2-50 mg x diluent volume 0.5-10 mL, with concentration and the volume needed for 100/250/500 ug |
| `unit-conversions.csv` | Mass/volume unit conversions, including the case that must *not* be converted |

## Formulas

```
concentration (mg/mL) = vial mass (mg) / diluent volume (mL)
concentration (ug/uL) = concentration (mg/mL)          # 1 mg/mL == 1 ug/uL
volume (uL) for dose D (ug) = D / concentration (ug/uL)
```

## Limits of these tables

- They describe arithmetic only. They are not dosing guidance and carry no clinical meaning.
- Concentration assumes complete dissolution and a diluent that does not change the peptide's
  solubility; bacteriostatic vs sterile water changes preservative content, not this arithmetic.
- IU cannot be converted to mass without a substance-specific bioassay definition; the
  conversion table marks this explicitly rather than supplying a factor.
- Reconstituted stability depends on the peptide, the diluent and storage temperature and is
  outside the scope of these tables.

## Related tools and documentation

- Catalog and product documentation: https://helixpeptidesupply.com/catalog
- Research catalog: https://gethelixpeptide.com/products

## Citation

Cite the DOI of this record. Recomputation from the formulas above is sufficient to reproduce
every row.

## License

CC BY 4.0
