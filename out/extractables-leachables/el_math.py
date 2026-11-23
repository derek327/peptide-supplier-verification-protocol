#!/usr/bin/env python3
"""W13 extractables & leachables arithmetic (container closure systems).

Every value here is a closed-form function of the stated inputs:
geometry (idealised cylinder), an extraction fraction, a first-order rate
constant, an activation energy, or an example exposure tier. No measured
extractable, leachable or toxicological value is included.

Self-test: python3 el_math.py --selftest
"""
import argparse
import math

R_GAS = 8.314462618  # J/(mol*K)

# Example tiers in ug/day. These are EXAMPLE policy inputs chosen to span
# three orders of magnitude so the arithmetic can be followed; they are not
# regulatory limits and must not be quoted as such.
TIERS = [
    ("tier_low", 0.15),
    ("tier_mid", 5.0),
    ("tier_high", 50.0),
]

# Idealised cylindrical container geometry. Dimensions are example inputs
# (round numbers), not catalogue drawings; the arithmetic is what transfers.
VESSELS = [
    # name, inner diameter cm, nominal fill mL
    ("2R", 1.2, 2.0),
    ("6R", 1.6, 5.0),
    ("10R", 1.8, 10.0),
    ("20R", 2.2, 20.0),
]

REF_VESSEL = "2R"


def fill_height(d_cm, fill_mL):
    """Height of a cylindrical fill: V = (pi*d^2/4)*h  ->  h = 4V/(pi d^2)."""
    return 4.0 * fill_mL / (math.pi * d_cm ** 2)


def sv_ratio(d_cm, fill_mL):
    """Wetted surface-to-volume ratio in cm^2/mL = 4/D + 1/h (bottom + wall)."""
    h = fill_height(d_cm, fill_mL)
    return 4.0 / d_cm + 1.0 / h


def wetted_area(d_cm, fill_mL):
    """Wetted area in cm^2 = bottom disc + cylindrical wall."""
    h = fill_height(d_cm, fill_mL)
    return math.pi * d_cm ** 2 / 4.0 + math.pi * d_cm * h


def vessel(name):
    for n, d, fill in VESSELS:
        if n == name:
            return {"name": n, "d_cm": d, "fill_mL": fill,
                    "height_cm": fill_height(d, fill),
                    "area_cm2": wetted_area(d, fill),
                    "sv_cm2_per_mL": sv_ratio(d, fill)}
    raise KeyError(name)


def conc_from_surface(e_ug_cm2, d_cm, fill_mL):
    """Surface-normalised extractable (ug/cm^2) -> concentration (ug/mL)."""
    return e_ug_cm2 * sv_ratio(d_cm, fill_mL)


def per_container(e_ug_cm2, d_cm, fill_mL):
    """Mass per container in ug = E * wetted area (equivalently conc * fill)."""
    return e_ug_cm2 * wetted_area(d_cm, fill_mL)


def exposure_per_day(e_ug_cm2, d_cm, fill_mL, vials_per_day):
    """Daily exposure in ug/day at a stated number of containers per day."""
    return per_container(e_ug_cm2, d_cm, fill_mL) * vials_per_day


def allowable_surface(tier_ug_day, d_cm, fill_mL, vials_per_day):
    """Reverse: the surface-normalised value that exactly meets a tier."""
    return tier_ug_day / (wetted_area(d_cm, fill_mL) * vials_per_day)


def sequential_total(fraction_per_step, steps):
    """Cumulative fraction removed by n successive extractions: 1-(1-f)^n."""
    if steps < 1:
        raise ValueError("steps must be >= 1")
    return 1.0 - (1.0 - fraction_per_step) ** steps


def sequential_table(fraction_per_step, steps=5):
    return [{"step": n, "cumulative_fraction": sequential_total(fraction_per_step, n)}
            for n in range(1, steps + 1)]


def first_order(k_per_day, t_days, c_inf=1.0):
    """Leachable approach to plateau: C(t) = Cinf*(1-exp(-k t))."""
    return c_inf * (1.0 - math.exp(-k_per_day * t_days))


def t_half(k_per_day):
    return math.log(2.0) / k_per_day


def t_fraction(k_per_day, p):
    """Time to reach fraction p of the plateau."""
    if not 0.0 < p < 1.0:
        raise ValueError("p must be in (0,1)")
    return -math.log(1.0 - p) / k_per_day


def arrhenius_af(ea_kj_mol, t_ref_c, t_acc_c):
    """Acceleration factor k(Tacc)/k(Tref) from the Arrhenius relation."""
    t1 = t_ref_c + 273.15
    t2 = t_acc_c + 273.15
    return math.exp(-ea_kj_mol * 1000.0 / R_GAS * (1.0 / t2 - 1.0 / t1))


def identified_fraction(nvr_ug_cm2, identified_ug_cm2):
    if not nvr_ug_cm2:
        raise ValueError("NVR must be > 0")
    return identified_ug_cm2 / nvr_ug_cm2


CASES = [
    {
        "case": "E01 2R, 0.15 ug/cm2, 1 vial/day, mid tier",
        "e_ug_cm2": 0.15, "vessel": "2R", "vials_per_day": 1,
        "tier_ug_day": 5.0, "basis": "extractable",
        "expected": {"verdict": "pass", "flags": ["exhaustive_upper_bound"]},
    },
    {
        "case": "E02 2R, 0.50 ug/cm2, 1 vial/day, mid tier",
        "e_ug_cm2": 0.50, "vessel": "2R", "vials_per_day": 1,
        "tier_ug_day": 5.0, "basis": "extractable",
        "expected": {"verdict": "pass", "flags": ["exhaustive_upper_bound"]},
    },
    {
        "case": "E03 same value, 4 vials/day",
        "e_ug_cm2": 0.50, "vessel": "2R", "vials_per_day": 4,
        "tier_ug_day": 5.0, "basis": "extractable",
        "expected": {"verdict": "fail", "flags": ["exhaustive_upper_bound"]},
    },
    {
        "case": "E04 same value against low tier",
        "e_ug_cm2": 0.50, "vessel": "2R", "vials_per_day": 1,
        "tier_ug_day": 0.15, "basis": "extractable",
        "expected": {"verdict": "fail", "flags": ["exhaustive_upper_bound"]},
    },
    {
        "case": "E05 same value in a 20R fill (larger contact area)",
        "e_ug_cm2": 0.50, "vessel": "20R", "vials_per_day": 1,
        "tier_ug_day": 5.0, "basis": "extractable",
        "expected": {"verdict": "fail", "flags": ["exhaustive_upper_bound",
                                                  "geometry_sensitive"]},
    },
    {
        "case": "E06 leachable measured 0.08 ug/cm2, low tier",
        "e_ug_cm2": 0.08, "vessel": "2R", "vials_per_day": 1,
        "tier_ug_day": 0.15, "basis": "leachable",
        "expected": {"verdict": "fail", "flags": []},
    },
    {
        "case": "E07 single extraction at f=0.60, mid tier",
        "e_ug_cm2": 0.50, "vessel": "2R", "vials_per_day": 1,
        "tier_ug_day": 5.0, "basis": "extractable",
        "extraction_steps": 1, "fraction_per_step": 0.60,
        "expected": {"verdict": "fail", "flags": ["exhaustive_upper_bound",
                                                  "single_extraction_understates"]},
    },
    {
        "case": "E08 identified 0.10 of NVR 0.42 ug/cm2, mid tier",
        "e_ug_cm2": 0.42, "vessel": "2R", "vials_per_day": 1,
        "tier_ug_day": 5.0, "basis": "extractable",
        "nvr_ug_cm2": 0.42, "identified_ug_cm2": 0.10,
        "expected": {"verdict": "pass", "flags": ["exhaustive_upper_bound",
                                                  "unidentified_majority"]},
    },
    {
        "case": "E09 30-day timepoint at k=0.001/day read as plateau",
        "e_ug_cm2": 0.05, "vessel": "2R", "vials_per_day": 1,
        "tier_ug_day": 5.0, "basis": "leachable",
        "timepoint_days": 30.0, "k_per_day": 0.001,
        "expected": {"verdict": "fail", "flags": ["early_timepoint",
                                                  "extrapolated_to_plateau"]},
    },
    {
        "case": "E10 0.60 ug/cm2 measured leachable, mid tier",
        "e_ug_cm2": 0.60, "vessel": "2R", "vials_per_day": 1,
        "tier_ug_day": 5.0, "basis": "leachable",
        "expected": {"verdict": "pass", "flags": ["near_tier"]},
    },
]


def evaluate_case(case):
    """Turn one record into an exposure verdict plus the flags that qualify it."""
    v = vessel(case["vessel"])
    area = v["area_cm2"]
    fill = v["fill_mL"]
    exposure = per_container(case["e_ug_cm2"], v["d_cm"], fill) * case["vials_per_day"]
    flags = []
    detail = {}

    if case.get("basis") == "extractable":
        flags.append("exhaustive_upper_bound")

    # A single extraction that removes fraction f understates the total by 1/f.
    steps = case.get("extraction_steps")
    if steps is not None:
        f = case["fraction_per_step"]
        total = sequential_total(f, steps)
        detail["reported_exposure_ug_day"] = exposure
        detail["extraction_total_fraction"] = total
        if steps == 1:
            flags.append("single_extraction_understates")
        exposure = exposure / total

    # A single early timepoint is a fraction of the plateau; scale it up.
    if case.get("timepoint_days") and case.get("k_per_day"):
        frac = first_order(case["k_per_day"], case["timepoint_days"])
        detail["timepoint_fraction_of_plateau"] = frac
        flags.append("extrapolated_to_plateau")
        if frac < 0.9:
            flags.append("early_timepoint")
        exposure = exposure / frac

    # Identified compounds rarely account for the whole non-volatile residue.
    if case.get("nvr_ug_cm2") and case.get("identified_ug_cm2") is not None:
        frac_id = identified_fraction(case["nvr_ug_cm2"], case["identified_ug_cm2"])
        detail["identified_fraction"] = frac_id
        detail["identified_only_exposure_ug_day"] = (
            per_container(case["identified_ug_cm2"], v["d_cm"], fill) * case["vials_per_day"])
        if frac_id < 0.5:
            flags.append("unidentified_majority")

    # Geometry: a contact area more than twice the 2R reference changes the answer.
    ref = vessel(REF_VESSEL)
    if area > 2.0 * ref["area_cm2"]:
        flags.append("geometry_sensitive")

    ratio = exposure / case["tier_ug_day"]
    if 0.8 <= ratio <= 1.25:
        flags.append("near_tier")

    verdict = "pass" if exposure <= case["tier_ug_day"] else "fail"
    return {
        "verdict": verdict,
        "flags": sorted(flags),
        "exposure_ug_day": round(exposure, 6),
        "tier_ug_day": case["tier_ug_day"],
        "ratio_to_tier": round(ratio, 4),
        "per_container_ug": round(per_container(case["e_ug_cm2"], v["d_cm"], fill), 6),
        "conc_ug_mL": round(conc_from_surface(case["e_ug_cm2"], v["d_cm"], fill), 6),
        "area_cm2": round(area, 4),
        "sv_cm2_per_mL": round(v["sv_cm2_per_mL"], 4),
        "detail": {k: round(val, 6) for k, val in detail.items()},
    }


def selftest():
    # --- geometry: S/V must equal 4/D + 1/h and area = conc*fill identity
    r = vessel("2R")
    h = fill_height(1.2, 2.0)
    assert abs(sv_ratio(1.2, 2.0) - (4.0 / 1.2 + 1.0 / h)) < 1e-12
    assert abs(r["area_cm2"] - 7.7977) < 5e-4, r["area_cm2"]
    assert abs(r["sv_cm2_per_mL"] - 3.8988) < 5e-4, r["sv_cm2_per_mL"]
    assert abs(conc_from_surface(0.5, 1.2, 2.0) * 2.0
               - per_container(0.5, 1.2, 2.0)) < 1e-12
    # larger formats dilute the same surface load
    ratios = [vessel(n)["sv_cm2_per_mL"] for n, _, _ in VESSELS]
    assert ratios == sorted(ratios, reverse=True)
    assert abs(ratios[0] / ratios[-1] - 1.9412) < 5e-3, ratios[0] / ratios[-1]
    # a smaller fill in the same vial raises S/V
    assert abs(sv_ratio(1.2, 0.5) / sv_ratio(1.2, 2.0) - 1.4351) < 1e-3

    # --- per-day exposure and the reverse calculation agree
    e = exposure_per_day(0.5, 1.2, 2.0, 1)
    assert abs(e - 3.89885) < 1e-4, e
    allow = allowable_surface(5.0, 1.2, 2.0, 4)
    assert abs(allow - 0.160296) < 1e-5, allow
    assert abs(exposure_per_day(allow, 1.2, 2.0, 4) - 5.0) < 1e-12

    # --- sequential extraction: 1-(1-f)^n
    seq = sequential_table(0.6, 4)
    assert [round(r["cumulative_fraction"], 4) for r in seq] == [0.6, 0.84, 0.936, 0.9744]
    assert abs(1.0 / sequential_total(0.6, 1) - 1.6667) < 1e-3

    # --- first order: half life, t90, and the 24-month slow-migrant case
    assert abs(t_half(0.05) - 13.8629) < 1e-3
    assert abs(t_fraction(0.05, 0.9) - 46.0517) < 1e-3
    assert abs(first_order(0.05, t_fraction(0.05, 0.9)) - 0.9) < 1e-12
    frac730 = first_order(0.001, 730.0)
    assert abs(frac730 - 0.5181) < 1e-4, frac730
    assert abs(1.0 / frac730 - 1.9301) < 1e-4

    # --- Arrhenius: the factor is an assumption, not a measurement
    assert abs(arrhenius_af(50, 25, 40) - 2.6279) < 1e-3
    assert abs(arrhenius_af(80, 25, 40) - 4.6920) < 1e-3
    assert abs(arrhenius_af(40, 25, 40) - 2.1662) < 1e-3
    assert arrhenius_af(50, 25, 25) == 1.0

    # --- identified fraction
    assert abs(identified_fraction(0.42, 0.10) - 0.2381) < 1e-4

    # --- every case matches its stated expectation
    for case in CASES:
        got = evaluate_case(case)
        assert got["verdict"] == case["expected"]["verdict"], (case["case"], got)
        assert got["flags"] == sorted(case["expected"]["flags"]), (case["case"], got["flags"])
    # E03 must be exactly four times E02, and E05 must be ~5.15x the 2R area
    e02 = evaluate_case(CASES[1])["exposure_ug_day"]
    e03 = evaluate_case(CASES[2])["exposure_ug_day"]
    assert abs(e03 / e02 - 4.0) < 1e-9
    assert abs(vessel("20R")["area_cm2"] / vessel("2R")["area_cm2"] - 5.1506) < 5e-4
    print("selftest ok (%d cases, %d assertions groups)" % (len(CASES), 9))


def main():
    ap = argparse.ArgumentParser(description="Extractables/leachables arithmetic")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--vessels", action="store_true")
    ap.add_argument("--surface", type=float, help="ug/cm2 to convert")
    ap.add_argument("--vessel", default="2R")
    ap.add_argument("--vials-per-day", type=float, default=1.0)
    ap.add_argument("--tier", type=float, default=5.0)
    ap.add_argument("--kinetics", type=float, help="k per day")
    ap.add_argument("--af", type=float, help="activation energy kJ/mol")
    args = ap.parse_args()

    if args.selftest:
        selftest()
        return
    if args.vessels:
        for name, _, _ in VESSELS:
            v = vessel(name)
            print("%-4s fill %5.1f mL  area %6.3f cm2  S/V %5.3f cm2/mL  h %5.3f cm"
                  % (v["name"], v["fill_mL"], v["area_cm2"], v["sv_cm2_per_mL"], v["height_cm"]))
        return
    if args.surface is not None:
        v = vessel(args.vessel)
        conc = conc_from_surface(args.surface, v["d_cm"], v["fill_mL"])
        per = per_container(args.surface, v["d_cm"], v["fill_mL"])
        day = per * args.vials_per_day
        print("E=%.4f ug/cm2  %s  conc=%.4f ug/mL  per container=%.4f ug  "
              "exposure=%.4f ug/day  vs tier %.3f -> %.2f%%"
              % (args.surface, args.vessel, conc, per, day, args.tier, 100 * day / args.tier))
        print("allowable E at %.1f vials/day = %.5f ug/cm2"
              % (args.vials_per_day,
                 allowable_surface(args.tier, v["d_cm"], v["fill_mL"], args.vials_per_day)))
        return
    if args.kinetics:
        for t in (30, 90, 180, 365, 730):
            print("k=%.4f/day t=%4d d -> %.4f of plateau (t1/2=%.2f d, t90=%.2f d)"
                  % (args.kinetics, t, first_order(args.kinetics, t), t_half(args.kinetics),
                     t_fraction(args.kinetics, 0.9)))
        return
    if args.af:
        for ta in (30, 40, 50):
            af = arrhenius_af(args.af, 25, ta)
            print("Ea=%5.1f kJ/mol  %d C vs 25 C -> AF %.3f  (90 d at %d C = %.1f d at 25 C)"
                  % (args.af, ta, af, ta, 90 * af))
        return
    ap.print_help()


if __name__ == "__main__":
    main()
