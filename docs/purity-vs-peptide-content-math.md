# Purity Is Not Content: Area-% and Net Peptide Mass in a Batch Record

*A documentation note for buyers reviewing release data on research-grade peptides.*

**Scope.** Two numbers appear in almost every research-peptide batch record and are routinely taken as interchangeable: the chromatographic purity figure, usually quoted as area-%, and the peptide content of the material as weighed. They answer different questions, are obtained by different methods, and the gap between them is often several percent. This note sets out what each number does and does not measure, gives a reproducible arithmetic model that relates them, and states where that model stops being trustworthy. The subject is document reading, not handling guidance.

---

## 1. Two different questions

- **Purity (area-%)** answers: *of the material that eluted and was detected, what fraction was the target peak?* It is a ratio between chromatographic peaks. Its denominator is the detected organic content of the injected solution, not the mass of powder in the vial.
- **Content (%)** answers: *of the powder weighed on the balance, what fraction is the target peptide molecule?* Its denominator is mass as-is, including water, counterions and residual process solvent.

A vial can be 99.2 % pure by area and still contain substantially less peptide per milligram than a 97.0 % pure vial, if the first is a hygroscopic trifluoroacetate salt and the second is a well-dried acetate or free base. Buyers who plan experiments from the label mass and use the purity figure as an implicit content value therefore work from a number that was never measured.

## 2. What the area-% figure rests on

Five things decide whether an area-% statement means anything, and all five should be visible in the method description accompanying it:

1. **Detection wavelength.** Peptides lacking aromatic residues have weak absorbance near 214 nm; a method running at 280 nm may report a clean main peak precisely because it does not detect much.
2. **Reporting threshold / limit of quantification.** "99.5 %" with a 1.0 % reporting floor means everything below 1.0 % was folded in or ignored; the same data at a 0.05 % floor can read 99.5 % or 98.1 % depending on what is counted.
3. **Gradient and column chemistry.** Different selectivity resolves different impurities; two figures are comparable only when column, mobile phase, gradient and wavelength match.
4. **Integration parameters.** Shoulder handling and baseline assignment are analyst decisions; a manually adjusted baseline is not the same measurement as a software-routed one.
5. **Sample preparation.** Concentration, solvent and injection volume affect peak shape and thus area.

The area-% figure, even when perfectly method-compliant, is a statement about **chromatographic behaviour of the detected fraction**. It carries no mass information.

## 3. The mass balance of the powder

Everything in the vial that is not target peptide falls into a small number of buckets, and a batch record that omits them makes content unverifiable:

| Bucket | Typical method | Order of magnitude |
|---|---|---|
| Water | Karl Fischer coulometric titration | 1–12 % |
| Counterion (acetate, TFA, chloride) | Ion chromatography, or titration | 0 % (free base) to > 12 % for TFA salts |
| Residual process solvent (acetonitrile, DMF, alcohols) | Headspace GC | 0.05–2 % |
| Related substances / impurities | HPLC, from the complement of the purity figure | 0.5–10 % |
| Inorganic residue / non-volatile ash | Residue on ignition, or ICP-MS | usually < 1 % |

As-is mass = peptide + water + counterion + residual solvent + related substances + inorganic residue. Content is that first term expressed as a fraction.

## 4. A reproducible model

Two relations are enough for most documentation review, and both are arithmetic only:

```
content_pct        = purity_pct * (100 - water_pct - counterion_pct - other_nonpeptide_pct) / 100
net_peptide_mg     = label_mass_mg * content_pct / 100
corrected_moles    = (net_peptide_mg / 1000) / molar_mass_g_per_mol      # molar mass of the free peptide
```

Working example — 10 mg label mass, 98.0 % area-%, 5.0 % water, 6.0 % acetate, 0.5 % other:

```
content_pct    = 98.0 * (100 - 5.0 - 6.0 - 0.5) / 100 = 86.73 %
net_peptide_mg = 10 * 86.73 / 100                     = 8.673 mg
```

Taking 10 mg as peptide overstates the molar amount by 10 / 8.673 = 1.153, i.e. **15.3 %**. Move from an acetate to a trifluoroacetate form at 97 % purity, 8 % water, 10 % counterion and 1 % other, and content falls to 78.57 %, so taking the label mass as peptide overstates it by 27 %. For anything where mass and molar amount matter — dry-mass reporting, reconstitution arithmetic, comparative batch work-up — that is not a rounding difference.

The companion dataset for this note contains 12 worked salt/water/purity combinations, a water-content sensitivity table at constant purity, and a small command-line script that performs the calculation from named arguments, so a reviewer can recompute any row without a spreadsheet.

## 5. Where the model breaks down

The multiplicative form is a bookkeeping convention, not a measurement, and it fails in ways worth naming:

- **Purity and content are measured on different fractions.** Area-% refers to the injected, detected material. Multiplying it by a dry-mass fraction assumes impurities distribute proportionally between the weighed powder and the detected peaks — true enough for a first estimate, not a certified result.
- **The method's reporting floor caps the correction.** If the HPLC method cannot see below 1 %, its purity figure cannot account for low-level related substances that still occupy mass.
- **Salt form is not always one-to-one.** A peptide with several basic residues may carry more than one trifluoroacetate per molecule, so counterion percentage derived from a nominal 1:1 stoichiometry under-counts.
- **Water is dynamic.** A hygroscopic solid takes up moisture between the Karl Fischer sample and the actual weighing; the value is a snapshot of the sample as submitted.
- **Correction only goes one way.** Applying content correction cannot increase the amount of peptide present. Any calculation that yields more peptide than the label mass is an arithmetic or assumption error, not a finding.

A useful self-check when auditing someone else's record: recompute content from the reported water, counterion and purity figures and compare with the content value stated. Disagreement beyond round-off usually means one of the input figures came from a different sample, or that one of the buckets was omitted.

## 6. What actually settles content

If a decision depends on content rather than documentation quality, it needs an assay that is independent of the chromatographic purity figure. The common options, each with a different assumption:

- **Quantitative NMR with an internal standard** — compares the target signal against a known amount of standard; needs a resolved, assignable signal and a pure standard.
- **Amino acid analysis after hydrolysis** — reports the peptide backbone composition; needs complete hydrolysis and does not distinguish closely related sequences well.
- **Nitrogen determination (Kjeldahl or combustion)** — reports total nitrogen; needs a nitrogen-per-molecule model, and is confounded by nitrogen-containing counterions and residual solvent.
- **UV absorbance against an extinction coefficient** — fast and non-destructive, but propagates the accuracy of the coefficient and of the sample's own purity.

None of these substitutes for the others; a release package that states content should also state which principle produced it, the standard used, and the acceptance range.

## 7. Procurement checklist

When a batch record or CoA is in front of you, these are the fields that decide whether the purity figure can be carried into any calculation:

1. Purity figure **with** method (column, mobile phase, gradient, wavelength, flow) and reporting threshold.
2. Water content by Karl Fischer, with the date of the analysis.
3. Counterion identity and content, with the analytical method.
4. Residual solvent statement (or an explicit statement that none was tested).
5. Net peptide content **as a stated percentage of as-is mass**, with the assay principle behind it.
6. Molar mass used in the record, and whether it is the free peptide — salt forms change the formula mass, so a molar mass without its salt form is ambiguous.
7. Storage and re-test dates tied to the lot number, since water content and content percentage move with handling.

Where only a purity figure is supplied and the content question matters, the correct reading is that **content is unstated** — not that content equals purity. Most arithmetic errors seen in buyer-side spreadsheets trace back to that single distinction.

## 8. Limits of this note

- It describes documentation arithmetic. It is not handling, storage or dosing guidance and says nothing about any specific peptide's behaviour.
- The model in section 4 is an estimate for review purposes; it does not replace an assay and should not be reported as a measured content.
- Molar masses used in the companion dataset are sequence-derived values for the free peptide; counterion and water add mass, which is precisely why content is measured rather than inferred.
- Figures spanning different HPLC methods are not comparable, however similar they look when typed into the same column.

---

**Related documentation.** Review workflow and quality documentation structure for the main research catalogue: [gethelixpeptide.com/quality](https://gethelixpeptide.com/quality). Product-level documentation, specification fields and batch records: [gethelixpeptide.com/products](https://gethelixpeptide.com/products). Companion reference tables and calculation script: dataset DOI in the repository `datasets/purity-content-math/`.
