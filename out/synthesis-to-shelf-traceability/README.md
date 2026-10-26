# Traceability from Synthesis to Shelf — record linkage reference set

Companion data for the note *Traceability from Synthesis to Shelf: Record Linkage Across Five
Handover Boundaries*. Everything here is documentation arithmetic: an identifier scheme, a record
schema, and an audit that tests five properties of a batch record set. No handling instructions,
no storage guidance, no biological claims.

## Lot identifier scheme

`HLX-OEM-2604-A7-W` — issuer, site, year-month of synthesis, base-36 sequence, check character.
The check character is computed over the hyphen-free payload:

```
check = ALPHABET[ sum(value(char_i) * (i+1) for i in 0..n-1) mod 36 ]
ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
```

`lot-id-scheme.csv` documents each segment and its rule.

## The five audit rules

| Rule | Test | Finding code |
|---|---|---|
| R1 | Lot identifier well formed, check character valid, site code matches the document | `id_invalid:<stage>` / `id_site_mismatch:<stage>` |
| R2 | All five stages present; every mandatory field non-empty (empty = absent) | `missing_stage:<stage>` / `missing_field:<stage>.<field>` |
| R3 | Stage dates non-decreasing in synthesis → purification → release → fill → dispatch | `stage_order:<from>-><to>` |
| R4 | Recorded mass non-increasing; fill mass computed as units x mass per unit | `mass_gain:<from>-><to>:<prev>-><cur>` |
| R5 | Retention deadline inside the reference horizon | `retention_soon:<stage>:<deadline>` |

Verdict is `complete` only when there are no findings. That means *documentarily complete*, not
authentic: a coherently fabricated record set passes all five rules.

## Files

| File | Contents |
|---|---|
| `lot-id-scheme.csv` | Identifier segments, alphabets, and the check-character rule |
| `traceability-record-schema.csv` | 21 mandatory fields across the five stages, with evidence type |
| `sample-lot-events.csv` | One worked lot in long format (21 field rows), all five stages |
| `audit-demo-lots.json` | Seven demonstration lots with expected verdicts (complete, missing stage, over-unity mass, inverted dates, invalid identifier, empty field, retention horizon) |
| `traceability_audit.py` | Validator and audit CLI with `--selftest` |

## Usage

```
python3 traceability_audit.py --lot-id HLX-OEM-2604-A7-W
python3 traceability_audit.py --audit audit-demo-lots.json --as-of 2026-10-26
python3 traceability_audit.py --selftest
```

The worked lot in `sample-lot-events.csv` gives purification yield 76.0 %, fill yield 90.0 %
and overall yield 68.0 % (crude 5000 mg, purified 3800 mg, 90 units x 38.0 mg, dispatched
3400 mg). Those figures are arithmetic on the stated masses, not benchmarks.

## Limits

- The audit detects omission and internal contradiction, not authenticity.
- The identifier format is an example design, not a standard; a real scheme must have its checksum
  recomputed, not assumed.
- Retention periods (60 months production/release, 36 months dispatch) are an example policy input
  chosen to make the horizon arithmetic visible. They are not regulatory constants and carry no
  legal meaning.
- Yields in the demo lots are illustrative arithmetic; purification performance varies with
  sequence, scale and method.

## Related documentation

- OEM services and private-label supply: https://helixpeptideoem.com/services
- Product-level documentation and batch records: https://helixpeptideoem.com/products

## License

CC BY 4.0
