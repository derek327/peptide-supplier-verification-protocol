# Sub-visible Particle Limits for Research Peptide Documentation: Limit Table, Fill-Rate Arithmetic, Counting Resolution and Method Boundaries

Arithmetic for the particle statement that appears on a certificate of analysis of a
research peptide. Everything in this package is derived from stated inputs: the compendial
limit tables, the container fill volume, the counted number, the sampled volume and the
dilution factor. No measured particle count is included, no material was tested, and no
value here is a release decision for any product.

## Files

| File | Contents |
|---|---|
| `limit-bands.csv` | 8 limit rows (light obscuration and microscopic, 10 and 25 um bins, large- and small-volume classes) with the same limit converted to a per-mL basis at six fills |
| `fill-sensitivity.csv` | the small-volume per-container limit converted across fills 0.5-500 mL, with its ratio to the 25/mL large-volume line |
| `poisson-bounds.csv` | exact two-sided 95 % Poisson bounds for observed counts 0-125, and the upper bound as a per-mL figure at a 5 mL sample |
| `size-fractions.csv` | a synthetic log-normal size distribution binned 1-1000 um, reported as count fraction and as mass fraction |
| `method-comparison.csv` | five counting methods: practical size floor and ceiling, what each measures, what each cannot see, output unit |
| `particle-cases.json` | 6 decision cases with computed verdicts and flags |
| `particle_math.py` | the module that generates every table; `--selftest` asserts each path |

## The two size conventions

Compendial reporting uses two fixed bins, 10 um and 25 um. They are conventions tied to the
methods and to the evidence base behind the limits, not a threshold below which particles
do not exist. Light obscuration resolves below 1 um, and a reconstituted peptide solution
routinely contains material in the 1-10 um range that no limit row mentions.

Visibility is a separate convention: a particle is expected to be visible under the
described inspection conditions at about 150 um for parenteral products. So the
"sub-visible" range is the range in which a human inspection cannot answer the question,
which is exactly why an instrument is used. There is no physical discontinuity at that
size: visibility depends on illumination, background contrast and the particle's own
refractive index, so a transparent particle can be missed at 200 um while an opaque one is
seen at 50 um.

## Limits are per container or per mL, and that changes the stringency by up to 480.0x

The small-volume class limit is stated per container (6000 particles at 10 um), the
large-volume class limit per mL (25 per mL). Converting the per-container limit with the
fill volume shows how much the per-mL stringency moves:

| Fill | Class | Limit at 10 um as per mL | Ratio to the 25/mL line |
|---|---|---|---|
| 0.5 mL | SVI | 12000 | 480.0x |
| 2 mL | SVI | 3000 | 120x |
| 10 mL | SVI | 600 | 24x |
| 50 mL | SVI | 120 | 4x |
| 100 mL | SVI | 60 | 2.4x |
| 100.001 mL | LVP | 25 | 1x |

Two consequences. First, the same absolute count means different things in a 2 mL vial and
a 100 mL vial: a report that says "6000 particles per container, compliant" describes a
solution at 3000 per mL in the small vial and 60 per mL in the large one. Second, the class
boundary itself is a step: a 100 mL fill is allowed 60 per mL and a 100.001 mL fill is
allowed 25 per mL, a 2.4x difference in strictness for the same volume of liquid.

## Counting resolution: zero is not zero

Particles are Poisson-distributed in a well-mixed sample, so a count carries its own
uncertainty. Exact 95 % upper bounds:

| Observed | Upper 95 % bound | As per mL from a 5 mL sample |
|---|---|---|
| 0 | 2.996 | 0.599 |
| 1 | 4.744 | 0.949 |
| 10 | 16.962 | 3.392 |
| 100 | 118.079 | 23.616 |

A zero count in 5 mL is compatible with a true concentration up to 0.599 per mL. Against
the 25/mL line that is still a 41.7x margin, so a zero count in a 5 mL sample is a
usable statement - but it is a statement about 5 mL. Two further consequences follow. If the
true mean sits exactly on the limit, a single test passes about 52.4 % of the time,
because the observed count scatters around its expectation; passing once is not evidence
that the lot sits below the line. And the resolution improves only with sampled volume: at
25 mL the zero-count bound falls to 0.12 per mL.

## Sampling, dilution and the arithmetic that is easy to get wrong

If an aliquot is diluted D-fold before counting, the concentration in the original solution
is count x D / sampled volume. A count of 900 in 1 mL of a 10-fold dilution is 9000 per mL
of the original, not 900. Dilution has three costs that are not captured by the factor: the
diluent itself contributes particles, the dilution shifts the size distribution if the
particles are not freely suspended, and a diluted sample can no longer be compared with an
undiluted one on the same per-mL basis without stating both.

## What each method can and cannot see

The table in `method-comparison.csv` lists five methods against size floor, size ceiling,
measurand, blind spot and output unit. The differences that matter for a documentation
review: light obscuration counts by extinction and therefore counts silicone oil droplets
and can count air; membrane microscopy sees morphology but loses everything below its
optical floor and adds filter background; flow imaging gives shape but its classifiers are
configured per method; resonant mass measurement is the only routine method that separates
silicone oil from peptide by the sign of the buoyant mass; and visual inspection answers a
different question entirely.

## The lyophilized case

A lyophilized peptide is a powder. It contains no solution to count, so a particle result
on the powder - or an inspection statement about the cake - says nothing about the
reconstituted solution, where undissolved peptide, buffer salt crystals, aggregates, filter
fibres and container or stopper shedding all appear at once. The comparable statement is a
count on the reconstituted solution at a stated concentration, with the method, the sampled
volume, the size bins, the container fill and the limit basis all named.

## What the package does not do

- No particle count, size distribution or image of any material is included. The
  distribution in `size-fractions.csv` is a log-normal model shape chosen to separate count
  fractions from mass fractions: in that model the 10 um and larger bins hold
  7.11 % of the particles by number but 91.79 % of the mass, which is
  the whole point - a number-weighted count and a mass-weighted statement about the same
  sample describe different things.
- The limit values are transcribed from the published compendial tables named in the
  module. They are not derived here and must be re-read against the current revision before
  any release decision.
- Nothing here is a handling instruction, a storage condition, a dose, a safety statement
  or a claim about any biological effect.

## Related documentation

- Catalog and product documentation for research supply:
  https://helixpeptidesupply.com/catalog
- QC failure patterns in bulk peptide supply:
  https://helixpeptidesupply.com/blog/bulk-tirzepatide-peptides-distributor-qc-failures

## License

CC BY 4.0
