# Sub-visible particle limits: what a particle statement on a peptide CoA can and cannot establish

*Research documentation note. Procurement and documentation-comparability framing only.
No handling instruction, dose, storage condition or biological claim is made here, and no
material is assessed.*

## 1. The number that looks comparable and is not

A certificate of analysis for a research peptide sometimes carries a line like
"particulate matter: complies" or "sub-visible particles: < 6000/container". Those two
strings are not the same measurement, not on the same basis, and in most cases not
reproducible without three pieces of information that the line omits: the method, the
sampled volume, and the container fill.

The underlying compendial frame is small and old. Two size bins (10 µm and 25 µm), two
container classes (large volume above 100 mL of labelled fill, small volume at or below
it), two counting methods (light obscuration and membrane microscopy), and a separate
visual-inspection chapter that answers a different question at a different size. Every
number in a particle statement sits inside that frame. The arithmetic below is what turns a
count into a comparison, and where it goes wrong when one of the three inputs is missing.

## 2. Two size conventions that are not physics

The 10 µm and 25 µm reporting bins are conventions. They exist because the methods and the
evidence base behind the limits were built around those cut-offs, not because particles
below 10 µm do not exist or do not matter. Light obscuration resolves well below 1 µm, and
a reconstituted peptide solution routinely carries material in the 1–10 µm range that no
limit row mentions at all. A report that says "no particles detected" almost always means
"no particles above the reporting threshold", which is a different sentence.

The second convention is visibility. Under the described inspection conditions, a particle
is expected to be visible at roughly 150 µm for parenteral products. "Sub-visible" therefore
means the range in which a human inspection cannot answer the question — which is exactly
why an instrument is used. There is no physical discontinuity at 150 µm: visibility depends
on illumination, background contrast, and the particle's own refractive index. A transparent
particle can be missed at 200 µm while an opaque one is seen at 50 µm. Any supplier
statement that treats "visible: none" as covering the sub-visible range has confused two
methods, not reported two results.

## 3. Limits move with the container, not only with the concentration

The large-volume class limit is stated per millilitre (25/mL at 10 µm, 3/mL at 25 µm). The
small-volume class limit is stated per container (6000/container at 10 µm, 600/container at
25 µm). Converting the per-container figure to a per-mL basis with the fill volume shows how
far the strictness moves:

| Fill | Class | 10 µm limit as per mL | Ratio to the 25/mL line |
|---|---|---|---|
| 0.5 mL | small volume | 12000 | 480× |
| 1 mL | small volume | 6000 | 240× |
| 2 mL | small volume | 3000 | 120× |
| 5 mL | small volume | 1200 | 48× |
| 10 mL | small volume | 600 | 24× |
| 50 mL | small volume | 120 | 4.8× |
| 100 mL | small volume | 60 | 2.4× |
| 100.001 mL | large volume | 25 | 1× |

Two consequences follow, and both matter commercially.

First, the same absolute count means completely different things in different containers.
"6000 particles per container, compliant" describes a solution at 3000/mL in a 2 mL vial and
at 60/mL in a 100 mL bottle. A buyer comparing two suppliers who both report "compliant"
may be comparing numbers that differ by a factor of 120 in the quantity they care about —
and neither report is wrong.

Second, the class boundary is a step function of labelled fill, not a smooth function of
quality. A 100 mL fill is allowed 60/mL and a 100.001 mL fill is allowed 25/mL: a 2.4×
change in strictness for the same volume of liquid. The step is a property of the standard,
so it will not appear in any supplier's marketing, but it is visible in one line of
arithmetic.

## 4. The method sets the line, so the method is part of the result

The two compendial methods carry different limits for the same class and the same size bin:

| Class | Bin | Light obscuration | Membrane microscopy | Ratio |
|---|---|---|---|---|
| Large volume | ≥10 µm | 25/mL | 12/mL | 0.48 |
| Large volume | ≥25 µm | 3/mL | 2/mL | 0.67 |
| Small volume | ≥10 µm | 6000/container | 3000/container | 0.50 |
| Small volume | ≥25 µm | 600/container | 300/container | 0.50 |

The microscopic limits are roughly half the light-obscuration limits. So a result of
20 particles/mL at 10 µm passes the light-obscuration line (25) and fails the microscopic
line (12) — same sample, same size bin, opposite verdicts. This is not a paradox and not a
sign that one method is wrong; it reflects different detection physics and different
historical evidence. But it does mean that a particle number without its method is not a
result. It is a number looking for a context.

## 5. Counting resolution: zero is not zero

Particles in a well-mixed sample are Poisson-distributed, so any count carries its own
uncertainty. Exact two-sided 95 % bounds for a handful of observed counts:

| Observed count | Lower 95 % | Upper 95 % | Upper as per mL from a 5 mL sample |
|---|---|---|---|
| 0 | 0 | 3.00 | 0.60 |
| 1 | 0.05 | 4.74 | 0.95 |
| 2 | 0.36 | 6.30 | 1.26 |
| 3 | 0.82 | 7.75 | 1.55 |
| 10 | 5.43 | 16.96 | 3.39 |
| 25 | 17.38 | 34.92 | 6.98 |
| 100 | 84.14 | 118.08 | 23.62 |

A zero count in 5 mL is fully compatible with a true concentration as high as 0.6/mL, and a
count of 100 is compatible with anything from 84 to 118. Three practical consequences:

1. **Zero counts still say something, but only about the sampled volume.** At 5 mL, zero
   gives a margin of about 42× against the 25/mL line, which is a usable statement. At
   25 mL the zero-count bound falls to 0.12/mL and the margin becomes about 209×.
2. **Being on the limit is not a passing position.** If the true mean sits exactly on the
   limit, a single test passes about 52 % of the time, because the observed count scatters
   around its expectation. One passing test is not evidence that a lot sits below the line;
   it is evidence that the lot is not far above it.
3. **Repeat counts on the same sample are not independent evidence** unless the sample was
   re-homogenised and re-sampled; counting the same aliquot twice narrows instrument noise,
   not sampling noise.

## 6. Sampling and dilution arithmetic

Counting a diluted aliquot is normal practice, and the conversion is trivial as long as it
is stated: concentration in the original solution = count × dilution factor / sampled
volume. A count of 900 in 1 mL of a 10-fold dilution is 9000/mL of the original, not 900.
In a 2 mL vial that extrapolates to 18000 particles per container — three times the
6000/container line — while the raw number "900" looks modest.

Three costs of dilution are not captured by the factor:

- The diluent contributes its own particles. A diluent with 1/mL at 10 µm contributes
  10/mL to the original after a 10-fold dilution, which is 40 % of the 25/mL line by itself.
- Dilution changes the size distribution if particles are not freely suspended: aggregates
  can dissociate, and large particles can settle out of the aliquot taken.
- A diluted result and an undiluted result are not comparable on the same per-mL basis
  without stating both the factor and the sampled volume.

There is also an instrument-side ceiling. Light-obscuration sensors have a maximum
concentration above which two particles in the sensing zone are counted as one, typically
around ten thousand per millilitre. Above that, the raw count is biased low and dilution is
mandatory — but then the dilution costs above apply, and a validated particle-free diluent
becomes part of the method.

## 7. What each method cannot see

The differences that matter for reading a report:

- **Light obscuration** counts by extinction cross-section and reports an equivalent
  circular diameter. It counts silicone oil droplets as particles, and it can count air
  bubbles. It cannot tell you what the particle is.
- **Membrane microscopy** shows morphology on a filter, so it can separate fibres, crystals
  and spheres. It loses everything below its optical floor (practically around 5 µm), adds
  filter background, and loses material that dissolves during filter preparation.
- **Flow imaging** gives size plus shape and can flag spheres as probable silicone oil. Its
  classifiers are configured per method and per product; a classifier tuned on protein
  aggregates will mislabel something else.
- **Resonant mass measurement** is the only routine method that separates silicone oil from
  peptide by the sign of the buoyant mass, because oil is less dense than water and peptide
  is more dense. Its usable size window is narrow and its sizing depends on an assumed
  density.
- **Visual inspection** answers a different question: visible or not, at a stated
  illumination. It produces a judgement, not a count, and it does not cover the sub-visible
  range at all.

A single "particles/mL" number is therefore compatible with several different physical
situations: mostly silicone oil, mostly peptide aggregate, mostly undissolved salt. The
number alone cannot distinguish them, which is why morphology or density information is
worth asking for when the number is near a limit.

## 8. Number fraction and mass fraction point in opposite directions

Counts are number-weighted; almost every practical concern is mass- or volume-weighted. In
a log-normal model size distribution (median 2 µm, σ_ln = 1, chosen only to make the
arithmetic explicit), the 10 µm and larger bins hold 7.1 % of the particles by number but
91.8 % of the mass. Within that tail, the 25–50 µm bin holds 0.68 % of the count and 26.9 %
of the mass; the 150 µm and larger bin holds 0.001 % of the count and 9.3 % of the mass.

So "the count is dominated by fines below 10 µm" and "the mass is dominated by particles
above 25 µm" are both true of the same sample. A report built on counts alone will always
look as if the small particles are the story, and a report built on mass or visual
appearance will always look as if the large ones are. Neither is a mistake; they are two
different questions, and the model shows how far apart the answers can sit.

## 9. The lyophilized case: the powder has no particles to count

A lyophilized research peptide is a powder. There is no solution in the vial to count, so a
particle result on the powder — or a statement that the cake was inspected and is uniform —
says nothing about the reconstituted solution. Particles appear at reconstitution: undissolved
peptide, buffer salt crystals that were cosolubilised in the fill, aggregates formed during
freeze-drying or on wetting, filter fibres from the fill line, and material shed from the
vial and the stopper.

The comparable statement is therefore a count on the reconstituted solution at a stated
concentration, with method, sampled volume, size bins, container fill and limit basis all
named. A supplier who reports a particle figure on a lyophilized product without stating the
reconstitution volume has reported a number whose unit is unknown.

## 10. Six failure modes, and the arithmetic that exposes each

1. **Basis swap.** "6000/container" in a 2 mL vial is 3000/mL, 120× the large-volume line.
   Check: divide the per-container figure by the fill volume.
2. **Bin omission.** Only the 10 µm bin is reported, no 25 µm figure. The 25 µm line is
   8.3× stricter in per-mL terms (3 vs 25), so its absence is not a detail.
3. **Method silence.** The same 20/mL passes light obscuration and fails microscopy. Check:
   the method must be named, together with the instrument class.
4. **Dilution silence.** A count taken on a diluted aliquot without the factor understates
   by exactly the factor. Check: 900 in 1 mL of a 10-fold dilution is 9000/mL.
5. **Single-unit sampling.** A figure from one vial presented as a lot result. Check: how
   many containers were sampled, and whether the value is a maximum or a mean.
6. **Detection-limit claim.** "No particles detected" at a sampled volume too small to
   resolve the limit in question. Check: zero in 1 mL resolves only to 3.0/mL, so it cannot
   speak to a 25/mL line with any margin; zero in 25 mL resolves to 0.12/mL.

## 11. What to put in the request, in order

1. The method and instrument class (light obscuration, membrane microscopy, flow imaging,
   resonant mass), with the size bins and the reporting threshold.
2. The sampled volume and the number of containers, plus whether the reported value is a
   maximum or a mean.
3. The container fill volume and the limit basis (per mL or per container), stated
   explicitly.
4. For a lyophilized product: the reconstitution volume and the concentration at which the
   count was taken.
5. Whether the sample was diluted, and if so the factor and the diluent's own particle
   count.
6. Whether silicone oil was excluded, and by which method — the answer changes the
   interpretation of an elevated count near a limit.
7. Continuity with previous lots: the same method, the same bins, the same sampled volume.
   A method change between lots makes trend comparison meaningless even when both results
   are individually compliant.
8. The raw count alongside the verdict, so the margin can be recomputed rather than taken
   on trust.

## 12. Boundaries

Nothing here states a safe or unsafe particle level, a release decision for any product, a
storage condition, a dose, or a biological effect. The limit values are transcribed from the
published compendial tables and must be re-read against the current revision before any
release decision; the Poisson bounds, the fill conversions, the dilution arithmetic and the
size fractions are computations on stated inputs, reproducible from the accompanying module.
The size distribution is a model shape chosen to separate number weighting from mass
weighting, not a measurement of any material.

Worked tables, the decision cases and the module that generates them:
`sub-visible-particles/` in this repository. Catalog and product documentation for research
supply: <https://helixpeptidesupply.com/catalog>. QC failure patterns in bulk peptide
supply: <https://helixpeptidesupply.com/blog/bulk-tirzepatide-peptides-distributor-qc-failures>.
