# Counterion and Salt Form: Why the Weighed Mass Is Not the Peptide

*A documentation note for buyers reconciling salt form, label mass and molar quantity on research-grade peptides.*

**Scope.** A vial label states a mass. Almost nothing on that label states what the mass is made of. For a peptide supplied as a salt — acetate, trifluoroacetate, chloride, or a hydrated form of any of these — a material fraction of the weighed powder is counterion and water, not peptide. The fraction is not small, it is not constant between suppliers, and it changes when a supplier changes salt form without changing the label. This note sets out the arithmetic that connects salt form to peptide mass and molar quantity, works through realistic examples, and lists what a specification has to state before the arithmetic can be done at all. It is a documentation note: it contains no handling instructions and makes no biological claims.

---

## 1. What "salt form" means on a batch record

A peptide is a polyelectrolyte. It carries protonatable basic centres — the N-terminal α-amine, lysine ε-amines, arginine guanidinium groups, histidine imidazoles — and acidic centres. When it is isolated from an acidic or ion-pairing mobile phase, the basic centres retain an equivalent of acid, and the resulting solid is a salt: peptide cation plus counterion.

The common counterions in research-peptide supply differ in molar mass by nearly a factor of two:

| Counterion | Formula | Molar mass (g/mol) | Charge | Notes for documentation |
|---|---|---|---|---|
| Acetate | CH₃COO⁻ | 59.04 (acetic acid 60.05) | −1 | Volatile; weak UV absorbance; common default |
| Trifluoroacetate (TFA) | CF₃COO⁻ | 113.02 (TFA 114.02) | −1 | Volatile; no useful chromophore at 214 nm; strong ion-pairing character |
| Chloride | Cl⁻ | 35.45 (HCl 36.46) | −1 | Non-volatile; mass stays with the solid |
| Water (hydrate) | H₂O | 18.02 | — | Moves with handling and storage humidity |

Because the counterion sits on the peptide's ionisable sites, the number bound is set by the number of those sites and by the pH and ion-pairing conditions at isolation. It is **not** necessarily one per molecule. A peptide with three protonatable basic centres can carry up to three acetates; a supplier's process may leave it with two, or with a mixture, and the specification should say which.

## 2. The arithmetic

Two relations cover the documentation review:

```
salt_molar_mass = peptide_molar_mass + n × counterion_molar_mass + w × 18.015
peptide_mass_fraction = peptide_molar_mass / salt_molar_mass
```

where `n` is the number of bound counterions and `w` the number of bound waters per peptide molecule. The peptide mass in a weighed quantity follows directly:

```
net_peptide_mg = weighed_mg × peptide_mass_fraction
moles          = (net_peptide_mg / 1000) / peptide_molar_mass
```

The second equation is the one that matters when an experiment is specified in moles. Note that the molar quantity is **independent of the salt form** once the net peptide mass is known — which is precisely why the salt form has to be known. If a protocol says "1 µmol of peptide" and the material is a tri-trifluoroacetate salt, weighing the free-peptide molar mass in milligrams delivers roughly half the intended molar amount.

## 3. Worked cases

Two molecules are enough to show the size of the effect. GHK (Gly-His-Lys, free-peptide molar mass 340.38 g/mol) has three protonatable basic centres: the N-terminus, the histidine imidazole and the lysine ε-amine. BPC-157 (1419.53 g/mol) has two: the N-terminus and one lysine.

| Case | n | Counterion | Salt molar mass | Peptide mass fraction |
|---|---|---|---|---|
| GHK | 3 | none (free base) | 340.38 | 100.0 % |
| GHK | 3 | acetate | 517.51 | 65.8 % |
| GHK | 3 | chloride | 446.74 | 76.2 % |
| GHK | 3 | TFA | 679.45 | 50.1 % |
| BPC-157 | 2 | none (free base) | 1419.53 | 100.0 % |
| BPC-157 | 2 | acetate | 1537.62 | 92.3 % |
| BPC-157 | 2 | chloride | 1490.44 | 95.2 % |
| BPC-157 | 2 | TFA | 1645.58 | 86.3 % |

A small, highly basic peptide is dominated by its counterion; a large peptide is not. On a 10 mg label mass, GHK as the tri-TFA salt contains 5.01 mg of peptide, against 6.58 mg as the tri-acetate — a 23.8 % difference in peptide mass and in molar quantity at identical label mass. For BPC-157 the same substitution moves peptide mass from 9.23 mg to 8.63 mg, 6.6 %. The magnitude scales with the ratio of counterion mass to peptide mass, so it is largest exactly where peptide molar mass is smallest.

This is the point at which "same peptide, same milligram label" stops being a meaningful comparison between two batches.

## 4. Why the trifluoroacetate case deserves separate treatment

TFA is not simply "a heavier acetate". Four documentation-relevant properties separate it:

1. **Mass.** At 113 g/mol per charge it is nearly twice the mass of acetate. For a polybasic peptide the counterion can outweigh the peptide's own contribution to the label.
2. **Invisibility in the purity assay.** Trifluoroacetate has no useful chromophore at the wavelengths used for peptide detection. An area-% purity figure therefore says nothing about how much TFA is present, and a "99 % pure" TFA salt can still be half counterion by mass.
3. **Ion pairing and chromatography.** TFA is a strong ion-pairing acid; it changes peak shape and retention relative to acetate or formate systems. Purity values obtained in a TFA mobile phase are not automatically comparable with values obtained in an acetate or formate system, even on the same column.
4. **Volatility and instability of the stated mass.** TFA is volatile. A solid described as a TFA salt can lose counterion on prolonged drying or change its water and counterion content on storage, so the peptide fraction derived from a historical certificate drifts. Chloride, by contrast, does not evaporate; the mass stays with the solid.

None of these is a defect of TFA as a counterion — it is a legitimate and widely used isolation form. The defect is a batch record that quotes a mass and a purity figure without naming the salt form and its stoichiometry.

## 5. Water is part of the same problem

Hydrate water enters the same denominator. A di-hydrate adds 36.03 g/mol per peptide molecule regardless of counterion; on a 340 g/mol peptide that is a further 9.6 % of the mass. Karl Fischer water content is therefore not an optional field on a certificate — without it, neither content nor peptide fraction can be reconstructed, and a mass that was correct at release drifts as a hygroscopic solid picks up moisture in the buyer's own store.

## 6. What a specification must state

For the arithmetic above to be checkable, a lot release should carry all of the following. Each item exists because without it a specific number cannot be reproduced:

1. **Salt form by name** — acetate, TFA, chloride, free base — not merely "peptide".
2. **Counterion stoichiometry or content** — moles counterion per mole peptide, or mass-% by a named method (ion chromatography, titration, elemental analysis).
3. **Water content by Karl Fischer**, with the method (coulometric or volumetric).
4. **Content basis** — as-is, anhydrous, or anhydrous-and-counterion-free. The three differ by several percent and are not interchangeable.
5. **Assay method for content**, if content is quoted — quantitative NMR, amino-acid analysis, nitrogen determination or UV against a stated coefficient. An area-% figure is not an assay.
6. **Peptide molar mass used**, and whether it refers to the free peptide or the salt.
7. **Residual TFA or acetate limit**, with the analytical method, if the material is a salt of that acid.
8. **Stability of the stated form** — whether the certificate's water and counterion values are release values or a snapshot.

## 7. Review checklist for a buyer

- If the label mass is used in any calculation, convert it to peptide mass and to moles before use; record the salt form and the conversion factor in the batch file.
- Regard a change of salt form between two batches as a specification change, not a packaging detail. Ask for the new stoichiometry and water content, and re-derive the masses.
- When comparing two suppliers' "10 mg", check whether both are the same salt and the same content basis. A 10 mg acetate and a 10 mg TFA vial are not the same quantity of peptide.
- If a certificate quotes area-% purity but no content, water or counterion data, the material's peptide mass is unknown; that is a documentation gap, not a quality judgement.
- If ion-pairing chromatography is used for purity, record the mobile-phase acid. Purity values from TFA and acetate systems are not directly comparable.

## 8. Limits of this note

The model is arithmetic on stated inputs. It assumes integral counterion stoichiometry, which is a simplification: real materials can carry mixed or fractional counterion loads, and a specification may report an average. It assumes the counterion is fully associated with the peptide rather than partly free acid. It assumes the molar mass of the free peptide is known and correct. None of these assumptions is guaranteed, which is why the input values must come from the certificate rather than from a default. The note says nothing about the behaviour of any peptide in any biological system, and the numerical examples are documentation arithmetic, not handling or dosing guidance.
