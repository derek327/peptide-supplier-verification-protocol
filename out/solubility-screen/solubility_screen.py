#!/usr/bin/env python3
"""Solubility screen design and reading engine (deterministic, no measured data).

Three things this module does, all as exact functions of stated inputs:

1. Buffer adequacy on a common pH grid
   beta(pH) = ln(10) * C * f * (1 - f),  f = 1 / (1 + 10^(pKa - pH))
   Peak at pH = pKa is ln(10)/4 * C = 0.575646 * C. A condition is called
   adequate only if it retains at least 20 % of peak capacity and at least
   3 mM/pH in absolute terms; 10-20 % / 2-3 mM is "weak"; below that it is
   "insufficient" and its observation cannot be attributed to solubility
   alone, because the pH is not held.

2. Mass budget
   net peptide mass per well = target concentration * well volume
   weighed mass = net mass / (net content / 100)
   Direct weighing every rung of a ladder costs sum(c_i * V); preparing one
   stock at the top rung and diluting costs c_top * V. The ratio is reported.

3. Reading a series of observations
   Observation codes that count as "in solution" are declared explicitly in
   OBSERVATION_CODES. The maximum clear concentration is the highest rung of
   the contiguous clear run that starts at the lowest rung: a clear rung above
   a failed rung is a non-monotonic series (an artefact signal), not a data
   point to be averaged.

CLI:
  python3 solubility_screen.py --selftest
  python3 solubility_screen.py --design
  python3 solubility_screen.py --beta 20 4.76 4.0
  python3 solubility_screen.py --ladder 0.25,0.5,1,2,4,8 --volume 0.25 --content 90
  python3 solubility_screen.py --series 0.5:clear,2:clear,5:haze,10:particulates
"""
import argparse
import math
import sys

LN10 = math.log(10.0)

# ---- declared design constants (identical to the published tables) ----
BUFFERS = [
    # name, pKa at 25 C (zero ionic strength), total concentration mM, form note
    ("acetate", 4.76, 20.0, "monoprotic acid, sodium salt"),
    ("citrate", 4.76, 20.0, "second pKa of a triprotic acid"),
    ("phosphate", 7.20, 20.0, "second pKa of a triprotic acid"),
    ("tris", 8.06, 20.0, "monoprotic base, hydrochloride salt"),
]
PH_GRID = [3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
SCREEN_CONC_MG_PER_ML = 2.0
WELL_VOLUME_ML = 0.25
NET_CONTENT_PCT = 90.0
PEPTIDE_MW = 1200.0

# ---- observation codes ----
# counts_as_clear: passes the "no visible scatter" criterion
# counts_as_dispersed: no discrete particles (Tyndall scatter allowed)
OBSERVATION_CODES = {
    "clear":        (True,  True,  "No scatter against a dark background under oblique light"),
    "opalescent":   (False, True,  "Tyndall scatter visible, no discrete particles"),
    "haze":         (False, True,  "Uniform cloudiness, no settling at the reading time"),
    "particulates": (False, False, "Discrete particles or flakes visible"),
    "precipitate":  (False, False, "Material settled on the well floor"),
    "gel":          (False, False, "No meniscus movement on inversion"),
    "film":         (False, False, "Residue on the wall above the liquid line"),
    "colour":       (False, False, "Colour change relative to the diluent control"),
    "immiscible":   (False, False, "Two liquid phases"),
    "bubbles":      (False, False, "Entrained air; read again after standing"),
}
SOLUBLE_CODES = {k for k, v in OBSERVATION_CODES.items() if v[0]}
DISPERSED_CODES = {k for k, v in OBSERVATION_CODES.items() if v[1]}

# Adequacy thresholds
ADEQUATE_PCT = 20.0
WEAK_PCT = 10.0
ADEQUATE_ABS = 3.0
WEAK_ABS = 2.0


def fraction_deprotonated(pka, ph):
    """f = 1 / (1 + 10^(pKa - pH)); the fraction in the basic form."""
    return 1.0 / (1.0 + 10.0 ** (pka - ph))


def beta_mM_per_pH(total_mM, pka, ph):
    """Van Slyke buffer capacity for a monoprotic buffer, mM per pH unit."""
    f = fraction_deprotonated(pka, ph)
    return LN10 * total_mM * f * (1.0 - f)


def beta_peak_mM_per_pH(total_mM):
    return LN10 / 4.0 * total_mM


def adequacy(beta, peak):
    pct = 100.0 * beta / peak if peak else 0.0
    if pct < WEAK_PCT or beta < WEAK_ABS:
        return "insufficient", pct
    if pct < ADEQUATE_PCT or beta < ADEQUATE_ABS:
        return "weak", pct
    return "ok", pct


def design_rows():
    rows = []
    well_no = 0
    for bname, pka, total, form in BUFFERS:
        peak = beta_peak_mM_per_pH(total)
        for ph in PH_GRID:
            well_no += 1
            beta = beta_mM_per_pH(total, pka, ph)
            verdict, pct = adequacy(beta, peak)
            net_ug = SCREEN_CONC_MG_PER_ML * WELL_VOLUME_ML * 1000.0
            weighed_ug = net_ug / (NET_CONTENT_PCT / 100.0)
            rows.append({
                "well": "A%d" % well_no,
                "buffer": bname,
                "buffer_total_mM": total,
                "pKa_25C": pka,
                "target_pH": ph,
                "dpH_from_pKa": round(ph - pka, 2),
                "beta_mM_per_pH": round(beta, 3),
                "beta_vs_peak_pct": round(pct, 1),
                "buffer_adequacy": verdict,
                "form_note": form,
                "target_conc_mg_per_mL": SCREEN_CONC_MG_PER_ML,
                "well_volume_mL": WELL_VOLUME_ML,
                "net_peptide_ug": round(net_ug, 2),
                "weighed_mass_ug_at_content": round(weighed_ug, 2),
                "molarity_uM_at_MW1200": round(molarity_uM(SCREEN_CONC_MG_PER_ML, PEPTIDE_MW), 1),
            })
    return rows


def weighed_mass_mg(target_conc_mg_per_ml, volume_ml, content_pct=100.0):
    """Mass to weigh for a target concentration, correcting for net peptide content."""
    if content_pct <= 0:
        raise ValueError("content_pct must be positive")
    return target_conc_mg_per_ml * volume_ml / (content_pct / 100.0)


def molarity_uM(target_conc_mg_per_ml, mw):
    """mg/mL is numerically g/L, so uM = (mg/mL) / (g/mol) * 1e6."""
    return target_conc_mg_per_ml / mw * 1e6


def ladder_budget(concentrations, volume_ml, content_pct=100.0):
    """Direct weighing per rung versus one stock at the top rung.

    Returns dict with per-rung weighed mass, direct total, stock total, ratio.
    """
    concentrations = sorted(float(c) for c in concentrations)
    if not concentrations:
        raise ValueError("empty ladder")
    rungs = []
    for c in concentrations:
        rungs.append({"conc_mg_per_mL": c,
                      "net_mg": round(c * volume_ml, 4),
                      "weighed_mg": round(weighed_mass_mg(c, volume_ml, content_pct), 4)})
    direct = sum(r["weighed_mg"] for r in rungs)
    stock = rungs[-1]["weighed_mg"]
    return {"rungs": rungs, "direct_total_mg": round(direct, 4),
            "stock_total_mg": round(stock, 4),
            "ratio": round(direct / stock, 3) if stock else None}


def parse_series(text):
    """'0.5:clear,2:haze' -> [(0.5,'clear'), (2.0,'haze')] sorted ascending."""
    out = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        conc, _, code = part.partition(":")
        code = code.strip().lower()
        if code not in OBSERVATION_CODES:
            raise SystemExit("unknown observation code: %s" % code)
        out.append((float(conc), code))
    if not out:
        raise SystemExit("empty series")
    return sorted(out)


def read_series(pairs):
    """Read one concentration series (one buffer at one pH).

    Returns max_clear (highest member of the contiguous clear run from the
    bottom), max_dispersed under the same contiguity rule, a verdict and flags.
    """
    pairs = sorted(pairs)
    flags = []
    max_clear = None
    max_dispersed = None
    run_clear = True
    run_dispersed = True
    for conc, code in pairs:
        is_clear = code in SOLUBLE_CODES
        is_disp = code in DISPERSED_CODES
        if run_clear and is_clear:
            max_clear = conc
        else:
            run_clear = False
        if run_dispersed and is_disp:
            max_dispersed = conc
        else:
            run_dispersed = False
        if code == "bubbles":
            flags.append("re_read_after_standing")
    # a clear rung above a failed rung is an artefact signal
    seen_fail = False
    for conc, code in pairs:
        ok = code in SOLUBLE_CODES
        if not ok:
            seen_fail = True
        elif seen_fail:
            flags.append("non_monotonic")
            break
    top_conc = pairs[-1][0]
    bottom_conc = pairs[0][0]
    if max_clear is None:
        verdict = "no_hit"
    elif max_clear == top_conc:
        verdict = "beyond_top"
    elif max_clear == bottom_conc:
        verdict = "floor_only"
    else:
        verdict = "window"
    if max_clear is not None and max_clear != max_dispersed:
        flags.append("scatter_only_extent")
    if any(code in ("particulates", "precipitate") for _c, code in pairs):
        flags.append("solid_phase_observed")
    return {
        "n_rungs": len(pairs),
        "max_clear_mg_per_mL": max_clear,
        "max_dispersed_mg_per_mL": max_dispersed,
        "verdict": verdict,
        "flags": sorted(set(flags)),
    }


def read_screen(series):
    """Aggregate series reads.

    series: list of dicts with buffer, pH, pairs.
    Returns screen-level verdict, hit count and coverage.
    """
    hits = []
    saturated = 0
    artefact = 0
    for s in series:
        r = read_series(s["pairs"])
        rec = dict(r, buffer=s["buffer"], pH=s["pH"])
        if r["max_clear_mg_per_mL"] is not None:
            hits.append(rec)
        if r["verdict"] == "beyond_top":
            saturated += 1
        if "non_monotonic" in r["flags"]:
            artefact += 1
    buffers = sorted({h["buffer"] for h in hits})
    phs = sorted({h["pH"] for h in hits})
    if not hits:
        verdict = "no_hit"
    elif len(hits) == 1:
        verdict = "single_condition"
    elif len(buffers) >= 2 and len(phs) >= 3:
        verdict = "broad"
    elif len(buffers) >= 2:
        verdict = "species_dependent"
    elif len(phs) >= 3:
        verdict = "ph_dependent"
    else:
        verdict = "narrow"
    flags = []
    if saturated == len(series) and series:
        flags.append("screen_saturated")
    if artefact:
        flags.append("non_monotonic_series:%d" % artefact)
    if not any(h["verdict"] in ("window", "beyond_top") for h in hits) and hits:
        flags.append("upper_bound_not_established")
    return {
        "verdict": verdict,
        "hits": len(hits),
        "n_series": len(series),
        "buffers_hit": buffers,
        "pH_hit": phs,
        "saturated_series": saturated,
        "flags": flags,
    }


def selftest():
    ok = []

    def check(name, cond):
        if not cond:
            raise AssertionError(name)
        ok.append(name)

    # 1. capacity identities
    peak = beta_peak_mM_per_pH(20.0)
    check("peak = ln10/4*C", abs(peak - 0.575646 * 20.0) < 1e-4)
    check("beta at pKa equals peak", abs(beta_mM_per_pH(20.0, 4.76, 4.76) - peak) < 1e-9)
    check("beta at pKa+1 = 0.1903*C",
          abs(beta_mM_per_pH(20.0, 4.76, 5.76) - 0.190259 * 20.0) < 1e-2)

    # 2. adequacy: Tris at pH 3 cannot hold pH
    tris_low = beta_mM_per_pH(20.0, 8.06, 3.0)
    v, pct = adequacy(tris_low, beta_peak_mM_per_pH(20.0))
    check("Tris at pH 3 insufficient", v == "insufficient")
    check("Tris at pH 3 below 0.01 % of peak", pct < 0.01)
    v2, _ = adequacy(beta_mM_per_pH(20.0, 8.06, 8.0), beta_peak_mM_per_pH(20.0))
    check("Tris at pH 8 adequate", v2 == "ok")

    # 3. mass arithmetic
    check("weighed mass 2 mg/mL 0.25 mL at 90 %",
          abs(weighed_mass_mg(2.0, 0.25, 90.0) - 0.555556) < 1e-5)
    check("molarity 2 mg/mL MW 1200 = 1.667 mM",
          abs(molarity_uM(2.0, 1200.0) - 1666.667) < 1e-2)

    # 4. ladder budget: direct weighing is strictly more expensive
    b = ladder_budget([0.25, 0.5, 1, 2, 4, 8], 0.25, 90.0)
    check("direct total = stock * ratio", abs(b["direct_total_mg"] - b["stock_total_mg"] * b["ratio"]) < 1e-3)
    check("direct/stock ratio = 1.969 for a 2-fold ladder", abs(b["ratio"] - 1.969) < 1e-3)
    check("top rung weighed mass", abs(b["stock_total_mg"] - 8.0 * 0.25 / 0.9) < 1e-3)

    # 5. series reading
    s1 = read_series([(0.5, "clear"), (2.0, "clear"), (5.0, "haze"), (10.0, "particulates")])
    check("window max clear = 2", s1["max_clear_mg_per_mL"] == 2.0)
    check("window verdict", s1["verdict"] == "window")
    check("scatter extends further than clear", s1["max_dispersed_mg_per_mL"] == 5.0)

    s2 = read_series([(0.5, "clear"), (2.0, "clear"), (5.0, "clear")])
    check("top rung clear -> beyond_top", s2["verdict"] == "beyond_top")

    s3 = read_series([(0.5, "particulates"), (2.0, "clear"), (5.0, "clear")])
    check("non-monotonic flagged", "non_monotonic" in s3["flags"])
    check("non-monotonic has no contiguous clear run", s3["max_clear_mg_per_mL"] is None)
    check("non-monotonic verdict no_hit", s3["verdict"] == "no_hit")

    s4 = read_series([(0.5, "opalescent"), (2.0, "opalescent"), (5.0, "particulates")])
    check("dispersed series has no clear rung", s4["max_clear_mg_per_mL"] is None)
    check("dispersed extent = 2", s4["max_dispersed_mg_per_mL"] == 2.0)
    check("solid phase recorded when the top rung has particles", "solid_phase_observed" in s4["flags"])

    s5 = read_series([(0.5, "bubbles"), (2.0, "clear")])
    check("bubbles forces re-read", "re_read_after_standing" in s5["flags"])

    # 6. screen aggregation
    broad = [
        {"buffer": "acetate", "pH": 4.0, "pairs": [(0.5, "clear"), (2.0, "haze")]},
        {"buffer": "acetate", "pH": 5.0, "pairs": [(0.5, "clear"), (2.0, "clear")]},
        {"buffer": "acetate", "pH": 6.0, "pairs": [(0.5, "clear"), (2.0, "haze")]},
        {"buffer": "phosphate", "pH": 6.0, "pairs": [(0.5, "clear"), (2.0, "clear")]},
        {"buffer": "phosphate", "pH": 7.0, "pairs": [(0.5, "clear"), (2.0, "haze")]},
    ]
    vb = read_screen(broad)
    check("broad screen verdict", vb["verdict"] == "broad")
    check("broad screen 5 hits", vb["hits"] == 5)

    satu = [{"buffer": "acetate", "pH": p, "pairs": [(0.5, "clear"), (2.0, "clear")]}
            for p in (4.0, 5.0)]
    vs = read_screen(satu)
    check("saturated screen flagged", "screen_saturated" in vs["flags"])

    empty = [{"buffer": "water", "pH": 7.0, "pairs": [(0.5, "particulates"), (2.0, "precipitate")]}]
    ve = read_screen(empty)
    check("no-hit screen verdict", ve["verdict"] == "no_hit")

    arte = [{"buffer": "acetate", "pH": 4.0, "pairs": [(0.5, "precipitate"), (2.0, "clear")]}]
    va = read_screen(arte)
    check("artefact counted", "non_monotonic_series:1" in va["flags"])

    # 7. the design table itself must be exhaustive and well labelled
    rows = design_rows()
    check("design has 24 conditions", len(rows) == 24)
    check("every well id unique", len({r["well"] for r in rows}) == 24)
    check("all 4 buffers present", len({r["buffer"] for r in rows}) == 4)
    check("acetate at pH 3 is insufficient",
          [r for r in rows if r["buffer"] == "acetate" and r["target_pH"] == 3.0][0]["buffer_adequacy"]
          == "insufficient")
    check("acetate at pH 5 is ok",
          [r for r in rows if r["buffer"] == "acetate" and r["target_pH"] == 5.0][0]["buffer_adequacy"]
          == "ok")

    print("selftest ok (%d assertions)" % len(ok))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--design", action="store_true")
    ap.add_argument("--beta", nargs=3, type=float, metavar=("C_mM", "pKa", "pH"))
    ap.add_argument("--ladder")
    ap.add_argument("--volume", type=float, default=0.25)
    ap.add_argument("--content", type=float, default=100.0)
    ap.add_argument("--series")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.design:
        for r in design_rows():
            print("%s %-9s pH %.1f  beta %7.3f mM/pH  %5.1f %% peak  %-12s %s"
                  % (r["well"], r["buffer"], r["target_pH"], r["beta_mM_per_pH"],
                     r["beta_vs_peak_pct"], r["buffer_adequacy"], r["form_note"]))
        return 0
    if args.beta:
        c, pka, ph = args.beta
        b = beta_mM_per_pH(c, pka, ph)
        v, pct = adequacy(b, beta_peak_mM_per_pH(c))
        print("C = %g mM, pKa = %g, pH = %g" % (c, pka, ph))
        print("f(deprotonated) = %.4f" % fraction_deprotonated(pka, ph))
        print("beta = %.3f mM/pH (%.1f %% of peak %.3f) -> %s"
              % (b, pct, beta_peak_mM_per_pH(c), v))
        return 0
    if args.ladder:
        ladder = [float(x) for x in args.ladder.split(",")]
        b = ladder_budget(ladder, args.volume, args.content)
        for r in b["rungs"]:
            print("%6.2f mg/mL -> net %7.4f mg, weigh %7.4f mg"
                  % (r["conc_mg_per_mL"], r["net_mg"], r["weighed_mg"]))
        print("direct total %.4f mg / single stock %.4f mg = %.3fx"
              % (b["direct_total_mg"], b["stock_total_mg"], b["ratio"]))
        return 0
    if args.series:
        for conc, code in parse_series(args.series):
            print("  %.3f mg/mL  %s" % (conc, code))
        print(read_series(parse_series(args.series)))
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
