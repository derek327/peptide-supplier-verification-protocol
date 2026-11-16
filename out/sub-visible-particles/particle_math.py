#!/usr/bin/env python3
"""Sub-visible particle arithmetic for research-grade peptide documentation.

Everything here is arithmetic on stated inputs: compendial limit tables, unit
conversions between per-container and per-mL bases, exact Poisson confidence
bounds for a counted number of particles, dilution factors, and a synthetic
size distribution used only to separate number fractions from mass fractions.

No measured particle count, no product result and no handling instruction is
included. Limits are transcribed from the published compendial tables; the
constant block names the source, and the values must be re-read against the
current revision before any release decision.

CLI:
  --limits                     limit table with per-mL equivalents
  --fill                       per-container to per-mL sensitivity across fills
  --poisson N [N ...]          exact two-sided 95 % bounds for observed counts
  --dilution COUNT V_ML DF     concentration from a diluted count
  --size-fractions             synthetic distribution: number vs mass fraction
  --selftest                   assertions on every arithmetic path
"""
import argparse
import math
import sys

# ---- compendial limits -------------------------------------------------------
# USP <788> Table 1 (light obscuration) and Table 2 (microscopic), mirrored in
# Ph. Eur. 2.9.19. Transcribed, not derived: re-read the current revision.
LIMITS = {
    # klass: (bin_um, limit_value, basis)
    "LVP_LO_10": (10, 25.0, "per_mL"),
    "LVP_LO_25": (25, 3.0, "per_mL"),
    "LVP_MICRO_10": (10, 12.0, "per_mL"),
    "LVP_MICRO_25": (25, 2.0, "per_mL"),
    "SVI_LO_10": (10, 6000.0, "per_container"),
    "SVI_LO_25": (25, 600.0, "per_container"),
    "SVI_MICRO_10": (10, 3000.0, "per_container"),
    "SVI_MICRO_25": (25, 300.0, "per_container"),
}

# Container class boundary: large-volume injection is > 100 mL of labeled fill.
LVP_FILL_THRESHOLD_ML = 100.0
# Size at which a particle is expected to be visible under the described
# inspection conditions of the visual-inspection chapter (parenteral products).
VISIBILITY_REFERENCE_UM = 150.0
# Typical upper concentration of a light-obscuration sensor before coincidence
# losses dominate; instrument-specific, used here only as a flag threshold.
LO_COINCIDENCE_FLAG_PER_ML = 10000.0


# ---- basic conversions -------------------------------------------------------
def per_mL(value, basis, fill_mL):
    """Convert a limit or count to a per-mL basis."""
    if basis == "per_mL":
        return float(value)
    if fill_mL <= 0:
        raise ValueError("fill_mL must be positive")
    return float(value) / float(fill_mL)


def per_container(value, basis, fill_mL):
    """Convert a limit or count to a per-container basis."""
    if basis == "per_container":
        return float(value)
    return float(value) * float(fill_mL)


def container_class(fill_mL):
    return "LVP" if fill_mL > LVP_FILL_THRESHOLD_ML else "SVI"


# ---- Poisson bounds ----------------------------------------------------------
def poisson_pmf(k, lam):
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return math.exp(k * math.log(lam) - lam - math.lgamma(k + 1))


def poisson_cdf(k, lam):
    if k < 0:
        return 0.0
    return sum(poisson_pmf(i, lam) for i in range(0, int(k) + 1))


def poisson_bounds(n, alpha=0.05):
    """Exact two-sided Poisson confidence interval for an observed count n.

    Upper: lambda at which P(X <= n) = alpha.  Lower: lambda at which
    P(X >= n) = alpha, i.e. CDF(n-1) = 1 - alpha (0 when n = 0).
    """
    n = int(n)
    hi = n + 3.0 * math.sqrt(n + 1.0) + 10.0
    while poisson_cdf(n, hi) > alpha:
        hi *= 2.0
        if hi > 1e7:
            raise RuntimeError("bisection escaped")
    lo_b, hi_b = float(n), hi
    for _ in range(200):
        mid = (lo_b + hi_b) / 2.0
        if poisson_cdf(n, mid) > alpha:
            lo_b = mid
        else:
            hi_b = mid
    upper = (lo_b + hi_b) / 2.0

    if n == 0:
        return 0.0, upper
    # CDF(n-1, lambda) decreases in lambda: bracket [0, n] puts the 0.95
    # crossing inside, then move the side that still lies above 0.95.
    a, b = 0.0, float(n)
    for _ in range(200):
        mid = (a + b) / 2.0
        if poisson_cdf(n - 1, mid) > 1.0 - alpha:
            a = mid
        else:
            b = mid
    lower = (a + b) / 2.0
    return lower, upper


def pass_probability_at_limit(limit_per_mL, sample_mL):
    """P(pass) when the true mean sits exactly on the limit.

    Passing is modelled as an observed count not exceeding the expected count,
    which is the most generous reading of a single test.
    """
    lam = float(limit_per_mL) * float(sample_mL)
    return poisson_cdf(int(math.floor(lam)), lam)


def resolution_per_mL(sample_mL, alpha=0.05):
    """Upper 95 % bound in per-mL when zero particles are counted."""
    _, upper = poisson_bounds(0, alpha)
    return upper / float(sample_mL)


# ---- dilution ----------------------------------------------------------------
def concentration_after_dilution(count, sampled_mL, dilution_factor):
    """Particles/mL in the original solution from a count on a diluted sample.

    A D-fold dilution means the sampled volume corresponds to sampled_mL / D of
    the original solution.
    """
    if sampled_mL <= 0 or dilution_factor <= 0:
        raise ValueError("sampled_mL and dilution_factor must be positive")
    original_volume = float(sampled_mL) / float(dilution_factor)
    return float(count) / original_volume


# ---- synthetic size distribution --------------------------------------------
# Log-normal number distribution, geometric median 2 um, sigma_ln 1.0. This is a
# model shape for arithmetic only: it is not a measurement of any material.
SIZE_MEDIAN_UM = 2.0
SIZE_SIGMA_LN = 1.0
SIZE_BINS = [
    (1.0, 2.0), (2.0, 5.0), (5.0, 10.0), (10.0, 25.0),
    (25.0, 50.0), (50.0, 100.0), (100.0, 150.0), (150.0, 1000.0),
]
SIZE_SAMPLES_PER_DECADE = 4000


def _lognormal_cdf(d, median=SIZE_MEDIAN_UM, sigma=SIZE_SIGMA_LN):
    if d <= 0:
        return 0.0
    return 0.5 * (1.0 + math.erf((math.log(d) - math.log(median)) / (sigma * math.sqrt(2.0))))


def size_fractions():
    """Per-bin count fraction and mass fraction (mass ~ d^3 within the bin)."""
    rows = []
    total_n = 0.0
    total_m = 0.0
    for lo, hi in SIZE_BINS:
        n_frac = _lognormal_cdf(hi) - _lognormal_cdf(lo)
        # integrate d^3 over the bin on a log grid
        steps = max(50, int(SIZE_SAMPLES_PER_DECADE * math.log10(max(hi / lo, 1.0001))))
        mass = 0.0
        for i in range(steps):
            d1 = lo * (hi / lo) ** (i / steps)
            d2 = lo * (hi / lo) ** ((i + 1) / steps)
            d = math.sqrt(d1 * d2)
            w = (_lognormal_cdf(d2) - _lognormal_cdf(d1))
            mass += w * d ** 3
        rows.append({"lo_um": lo, "hi_um": hi, "count_fraction": n_frac, "mass_proxy": mass})
        total_n += n_frac
        total_m += mass
    for r in rows:
        r["count_pct"] = 100.0 * r["count_fraction"] / total_n
        r["mass_pct"] = 100.0 * r["mass_proxy"] / total_m
        r.pop("count_fraction")
        r.pop("mass_proxy")
    return rows


# ---- decision engine ---------------------------------------------------------
def limit_per_mL(klass_key, container_fill_mL):
    """Compendial limit expressed per mL, for a container of the stated fill."""
    _bin, value, basis = LIMITS[klass_key]
    return per_mL(value, basis, container_fill_mL)


def check_limit(count, sample_mL, klass_key, container_fill_mL=None):
    """Compare a count against one compendial limit row.

    For a per-container limit the container fill must be stated, because the
    same count means a different thing in a 2 mL vial and a 100 mL vial.
    """
    bin_um, limit_value, basis = LIMITS[klass_key]
    fill = float(container_fill_mL if container_fill_mL is not None else sample_mL)
    observed_per_mL = float(count) / float(sample_mL)
    line = limit_per_mL(klass_key, fill)
    observed_fraction = observed_per_mL / line
    return {
        "klass": klass_key,
        "bin_um": bin_um,
        "limit_value": limit_value,
        "limit_basis": basis,
        "container_fill_mL": fill,
        "observed_count": count,
        "sample_mL": sample_mL,
        "observed_per_mL": round(observed_per_mL, 6),
        "limit_per_mL": round(line, 6),
        "fraction_of_limit": round(observed_fraction, 6),
        "verdict": "pass" if observed_fraction <= 1.0 else "fail",
        "coincidence_flag": "yes" if observed_per_mL > LO_COINCIDENCE_FLAG_PER_ML else "no",
    }


def evaluate_case(case):
    """Multi-part decision for one documentation case.

    case keys: count, sample_mL (of the counted liquid), container_fill_mL,
    klass, dilution_factor (default 1).
    """
    sampled = float(case["sample_mL"])
    fill = float(case["container_fill_mL"])
    df = float(case.get("dilution_factor", 1.0))
    count = float(case["count"])
    conc = concentration_after_dilution(count, sampled, df)
    line = limit_per_mL(case["klass"], fill)
    primary = "pass" if conc <= line else "fail"

    flags = []
    if primary == "fail":
        flags.append("exceeds_limit")
    lvp_ref = LIMITS["LVP_LO_10"][1]
    ratio = conc / lvp_ref
    if case["klass"].startswith("SVI") and ratio > 5.0:
        flags.append("per_container_basis_hides_per_mL_ratio")
    _, upper = poisson_bounds(int(count))
    upper_per_mL = upper / sampled * df
    if upper_per_mL > line:
        flags.append("upper_bound_exceeds_limit")
    if df > 1.0:
        flags.append("diluted_sample")
    if conc > LO_COINCIDENCE_FLAG_PER_ML:
        flags.append("coincidence_range")
    return {
        "case": case["case"],
        "concentration_per_mL": round(conc, 6),
        "limit_per_mL": round(line, 6),
        "expected_in_container": round(conc * fill, 3),
        "ratio_to_LVP_10um_limit": round(ratio, 6),
        "poisson_upper_per_mL": round(upper_per_mL, 6),
        "verdict": primary,
        "flags": sorted(flags),
    }


CASES = [
    {
        "case": "SVI 2 mL vial, LO, 8 particles >=10 um: 4/mL, well inside 6000/container",
        "count": 8, "sample_mL": 2.0, "container_fill_mL": 2.0, "klass": "SVI_LO_10",
        "expected": {"verdict": "pass", "flags": []},
    },
    {
        "case": "SVI 2 mL vial, 5000 particles: passes 6000/container but is 2500/mL",
        "count": 5000, "sample_mL": 2.0, "container_fill_mL": 2.0, "klass": "SVI_LO_10",
        "expected": {"verdict": "pass",
                     "flags": ["per_container_basis_hides_per_mL_ratio"]},
    },
    {
        "case": "LVP 200 mL container, LO, 4200 particles >=10 um: 21/mL",
        "count": 4200, "sample_mL": 200.0, "container_fill_mL": 200.0, "klass": "LVP_LO_10",
        "expected": {"verdict": "pass", "flags": []},
    },
    {
        "case": "same 20/mL passes the LO line 25 but fails the microscopy line 12",
        "count": 20, "sample_mL": 1.0, "container_fill_mL": 200.0, "klass": "LVP_MICRO_10",
        "expected": {"verdict": "fail",
                     "flags": ["exceeds_limit", "upper_bound_exceeds_limit"]},
    },
    {
        "case": "10-fold diluted 1 mL aliquot, 900 particles in a 2 mL SVI vial",
        "count": 900, "sample_mL": 1.0, "container_fill_mL": 2.0, "klass": "SVI_LO_10",
        "dilution_factor": 10.0,
        "expected": {"verdict": "fail",
                     "flags": ["diluted_sample", "exceeds_limit",
                               "per_container_basis_hides_per_mL_ratio",
                               "upper_bound_exceeds_limit"]},
    },
    {
        "case": "zero count in 5 mL against the 25/mL line, 200 mL container",
        "count": 0, "sample_mL": 5.0, "container_fill_mL": 200.0, "klass": "LVP_LO_10",
        "expected": {"verdict": "pass", "flags": []},
    },
]


# ---- CLI ---------------------------------------------------------------------
def _fmt(x, nd=4):
    return ("%." + str(nd) + "f") % x


def print_limits():
    print("klass,bin_um,limit_value,basis,per_mL@1mL,per_mL@2mL,per_mL@5mL,per_mL@10mL,"
          "per_mL@50mL,per_mL@100mL")
    fills = [1.0, 2.0, 5.0, 10.0, 50.0, 100.0]
    for key in ("LVP_LO_10", "LVP_LO_25", "LVP_MICRO_10", "LVP_MICRO_25",
                "SVI_LO_10", "SVI_LO_25", "SVI_MICRO_10", "SVI_MICRO_25"):
        bin_um, value, basis = LIMITS[key]
        cells = ",".join(_fmt(per_mL(value, basis, f), 3) for f in fills)
        print("%s,%d,%s,%s,%s" % (key, bin_um, value, basis, cells))


def print_fill():
    lvp = LIMITS["LVP_LO_10"][1]
    print("fill_mL,container_class,SVI_per_mL,ratio_to_LVP_25_per_mL")
    for f in (0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 100.001, 250.0, 500.0):
        cls = container_class(f)
        if cls == "SVI":
            v = per_mL(LIMITS["SVI_LO_10"][1], "per_container", f)
            print("%s,%s,%s,%s" % (f, cls, _fmt(v, 3), _fmt(v / lvp, 4)))
        else:
            print("%s,%s,%s,%s" % (f, cls, lvp, "1.0000"))


def print_poisson(counts):
    print("observed,lower_95,upper_95,upper_per_mL@5mL")
    for n in counts:
        lo, hi = poisson_bounds(n)
        print("%d,%s,%s,%s" % (n, _fmt(lo, 4), _fmt(hi, 4), _fmt(hi / 5.0, 4)))


def print_size():
    print("bin_um,count_pct,mass_pct")
    for r in size_fractions():
        print("%g-%g,%s,%s" % (r["lo_um"], r["hi_um"], _fmt(r["count_pct"], 4),
                               _fmt(r["mass_pct"], 4)))


# ---- selftest ---------------------------------------------------------------
def selftest():
    # unit conversions
    assert per_mL(6000.0, "per_container", 2.0) == 3000.0
    assert per_mL(6000.0, "per_container", 100.0) == 60.0
    assert per_container(25.0, "per_mL", 4.0) == 100.0
    assert container_class(100.0) == "SVI" and container_class(100.5) == "LVP"

    # the 2.4x step at the container-class boundary
    assert abs(per_mL(6000.0, "per_container", 100.0) / 25.0 - 2.4) < 1e-12
    # SVI per-container limit loosens as fill shrinks: 120x the LVP line at 2 mL
    assert abs(per_mL(6000.0, "per_container", 2.0) / 25.0 - 120.0) < 1e-12
    # microscopy limits are about half the light-obscuration limits
    assert abs(LIMITS["LVP_MICRO_10"][1] / LIMITS["LVP_LO_10"][1] - 0.48) < 1e-12
    assert abs(LIMITS["SVI_MICRO_25"][1] / LIMITS["SVI_LO_25"][1] - 0.5) < 1e-12

    # Poisson pmf/cdf identities
    assert abs(poisson_pmf(0, 0.0) - 1.0) < 1e-15
    assert abs(sum(poisson_pmf(k, 4.2) for k in range(0, 60)) - 1.0) < 1e-9
    assert abs(poisson_cdf(0, 3.0) - math.exp(-3.0)) < 1e-12

    # exact bounds verified semantically: CDF(n, upper) = alpha, CDF(n-1, lower) = 1-alpha
    for n in (0, 1, 2, 5, 10, 100, 4200):
        lo, hi = poisson_bounds(n)
        assert abs(poisson_cdf(n, hi) - 0.05) < 1e-4, (n, hi, poisson_cdf(n, hi))
        if n > 0:
            assert abs(poisson_cdf(n - 1, lo) - 0.95) < 1e-4, (n, lo, poisson_cdf(n - 1, lo))
        else:
            assert lo == 0.0
    # anchor values that can be checked by hand
    assert abs(poisson_bounds(0)[1] - 2.9957) < 1e-3
    assert abs(poisson_bounds(1)[1] - 4.7439) < 1e-3
    assert abs(poisson_bounds(1)[0] - 0.0513) < 1e-3
    assert abs(poisson_bounds(10)[1] - 16.962) < 0.02

    # monotonicity
    prev = -1.0
    for n in range(0, 30):
        _, h = poisson_bounds(n)
        assert h > prev
        prev = h

    # zero count in 5 mL resolves to 0.6/mL, 40x below the 25/mL line
    assert abs(resolution_per_mL(5.0) - 0.5992) < 0.002, resolution_per_mL(5.0)
    assert abs((25.0 / resolution_per_mL(5.0)) - 41.7) < 0.5

    # a true mean sitting on the limit passes about half the time
    p = pass_probability_at_limit(25.0, 5.0)
    assert 0.45 < p < 0.56, p
    p2 = pass_probability_at_limit(25.0, 20.0)
    assert 0.40 < p2 < 0.60, p2

    # dilution: 900 counted in 1 mL of a 10-fold dilution = 9000/mL original
    assert abs(concentration_after_dilution(900, 1.0, 10.0) - 9000.0) < 1e-9
    assert abs(concentration_after_dilution(30, 5.0, 1.0) - 6.0) < 1e-9

    # size fractions: sums to 100, mass fraction above 10 um far exceeds count
    fr = size_fractions()
    assert abs(sum(r["count_pct"] for r in fr) - 100.0) < 1e-6
    assert abs(sum(r["mass_pct"] for r in fr) - 100.0) < 1e-6
    above10 = [r for r in fr if r["lo_um"] >= 10.0]
    count_above10 = sum(r["count_pct"] for r in above10)
    mass_above10 = sum(r["mass_pct"] for r in above10)
    assert 5.0 < count_above10 < 9.0, count_above10
    assert mass_above10 > 85.0, mass_above10
    # the >=10 um count is dominated by the 10-25 um bin, the >=150 um bin is a trace
    assert fr[3]["count_pct"] > 6.0 and fr[7]["count_pct"] < 0.01

    # decision cases
    for case in CASES:
        got = evaluate_case(case)
        exp = case["expected"]
        assert got["verdict"] == exp["verdict"], (case["case"], got["verdict"], exp["verdict"])
        assert got["flags"] == sorted(exp["flags"]), (case["case"], got["flags"], exp["flags"])

    print("selftest ok")


def main(argv=None):
    ap = argparse.ArgumentParser(description="sub-visible particle arithmetic")
    ap.add_argument("--limits", action="store_true")
    ap.add_argument("--fill", action="store_true")
    ap.add_argument("--poisson", nargs="*", type=int)
    ap.add_argument("--dilution", nargs=3, metavar=("COUNT", "SAMPLED_ML", "DF"))
    ap.add_argument("--size-fractions", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    if a.selftest:
        selftest()
        return 0
    if a.limits:
        print_limits()
    if a.fill:
        print_fill()
    if a.poisson is not None:
        print_poisson(a.poisson or [0, 1, 2, 3, 5, 10, 25, 50, 100])
    if a.dilution:
        c, v, df = float(a.dilution[0]), float(a.dilution[1]), float(a.dilution[2])
        print("concentration_per_mL = %s" % _fmt(concentration_after_dilution(c, v, df), 4))
    if a.size_fractions:
        print_size()
    if not any([a.limits, a.fill, a.poisson, a.dilution, a.size_fractions]):
        ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
