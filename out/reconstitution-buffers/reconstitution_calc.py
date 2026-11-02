#!/usr/bin/env python3
"""复溶缓冲化学计算（纯算术 / 可复现）

四个量：
  beta_mM_per_pH        缓冲容量（mM per pH unit）
  ionic_strength_mM     离子强度（mM，0.5*sum(ci*zi^2)）
  osmolarity_mOsm_L     名义渗透浓度（mOsm/L，粒子数求和）
  required_volume_mL    按净肽含量换算的复溶体积

所有公式写在 README 里，每个值都是输入参数的解析函数，没有拟合、没有实测。
边界：这些数字描述溶液的酸碱与电学性质，不描述任何肽在生物体内的行为。
"""
import argparse
import math

LN10 = math.log(10.0)  # 2.302585...


def ka_from_pka(pka):
    return 10.0 ** (-pka)


def beta_mM_per_pH(total_mM, pka, pH):
    """van Slyke 缓冲容量：beta = ln10 * C * Ka*[H+] / (Ka+[H+])^2"""
    ka = ka_from_pka(pka)
    h = 10.0 ** (-pH)
    return LN10 * total_mM * ka * h / (ka + h) ** 2


def beta_peak_mM_per_pH(total_mM):
    """pH = pKa 时的极大值：ln10/4 * C"""
    return LN10 / 4.0 * total_mM


def frac_deprotonated_acid(pka, pH):
    """一元弱酸：A- 占比 = 1/(1+10^(pKa-pH))"""
    return 1.0 / (1.0 + 10.0 ** (pka - pH))


def frac_protonated_base(pka, pH):
    """一元弱碱（共轭酸 pKa）：BH+ 占比 = 1/(1+10^(pH-pKa))"""
    return 1.0 / (1.0 + 10.0 ** (pH - pka))


def ionic_strength_mM(species):
    """species: [(conc_mM, charge_int), ...] -> I = 0.5*sum(c*z^2)"""
    return 0.5 * sum(c * (z ** 2) for c, z in species)


def osmolarity_mOsm_L(particles_mM):
    """particles_mM: 各粒子浓度之和（理想、完全解离）"""
    return float(sum(particles_mM))


def required_volume_mL(label_mass_mg, net_content_pct, target_mg_per_mL):
    """net peptide mass = label mass * net content; volume = peptide / target"""
    if target_mg_per_mL <= 0:
        raise ValueError("target concentration must be > 0")
    peptide_mg = label_mass_mg * net_content_pct / 100.0
    return peptide_mg / target_mg_per_mL


def molarity_uM(mg_per_mL, molar_mass_g_per_mol):
    """mg/mL ÷ (g/mol) 数值上即 mol/L（mg/g 因子与 mL/L 相消）→ ×1e6 得 uM"""
    return (mg_per_mL / molar_mass_g_per_mol) * 1.0e6


# ---------------------------------------------------------------- 配方定义
# 每个配方：(名称, 标称物种 [(conc_mM, charge)] = 完全解离, 强电解质物种 = 排除弱电解质部分,
#           工作 pH 的粒子 [(conc_mM, n_particles)], 弱电解质 (total_mM, pKa, kind) 或 None, pH)
# 标称与有效值的差别就是重点：远离 pKa 时"按盐完全解离"会高估离子强度。
RECIPES = [
    ("water_for_injection", [], [], [], None, None),
    ("saline_0.9pct", [(154.0, +1), (154.0, -1)], [(154.0, +1), (154.0, -1)],
     [(154.0, 2)], None, None),
    ("pbs_1x",
     [(157.0, +1), (4.5, +1), (139.7, -1), (10.0, -2), (1.8, -1)],
     [(157.0, +1), (4.5, +1), (139.7, -1), (10.0, -2), (1.8, -1)],
     [(157.0, 1), (4.5, 1), (139.7, 1), (11.8, 1)], None, None),
    ("acetate_20mM_pH4.5", [(20.0, +1), (20.0, -1)], [(20.0, +1)],
     [(20.0, 1), (20.0, 1)], (20.0, 4.76, "acid"), 4.5),
    ("phosphate_20mM_pH7.4", [(20.0, +1), (20.0, -1)], [(20.0, +1), (20.0, -1)],
     [(20.0, 2)], None, None),
    ("tris_25mM_pH8.0", [(25.0, +1), (25.0, -1)], [],
     [(25.0, 1)], (25.0, 8.06, "base"), 8.0),
    ("tbs_pH7.4", [(137.0, +1), (2.7, +1), (139.7, -1), (25.0, +1), (25.0, -1)],
     [(137.0, +1), (2.7, +1), (139.7, -1)],
     [(137.0, 1), (2.7, 1), (139.7, 1), (25.0, 1)], (25.0, 8.06, "base"), 7.4),
    ("benzyl_alcohol_0.9pct", [], [], [(87.0, 1)], None, None),
]


def recipe_values(name):
    """返回 (I_nominal_mM, I_effective_mM|None, osmolarity_mOsm_L)

    nominal  = 按称量盐完全解离（上界）
    effective= 弱电解质在工作 pH 按 Henderson-Hasselbalch 分布后计算
               （只对一元弱酸/弱碱建模；磷酸盐二质子体系不建模 → None，README 明说）
    osm      = 工作 pH 下的粒子数之和（含未解离分子）
    """
    for rname, nominal, strong, particles, weak, ph in RECIPES:
        if rname != name:
            continue
        i_nom = ionic_strength_mM(nominal)
        osm = osmolarity_mOsm_L([c * n for c, n in particles])
        i_eff = None
        if weak:
            total, pka, kind = weak
            if kind == "acid":
                frac = frac_deprotonated_acid(pka, ph)
                i_eff = ionic_strength_mM(strong + [(total * frac, -1)])
                # 粒子数不变：Na+ 与乙酸(不论是否解离)各算一个粒子
            else:
                frac = frac_protonated_base(pka, ph)
                i_eff = ionic_strength_mM(strong + [(total * frac, +1), (total * frac, -1)])
                osm += total * frac  # 抗衡离子 Cl-（Tris 分子已计入）
        return i_nom, i_eff, osm
    raise KeyError(name)


def selftest():
    # 1. 极大值位置与取值
    for c in (10.0, 20.0, 50.0):
        assert abs(beta_mM_per_pH(c, 4.76, 4.76) - beta_peak_mM_per_pH(c)) < 1e-12
        assert abs(beta_peak_mM_per_pH(c) - 0.5756463 * c) < 1e-6 * c
        # pKa ± 1 处 = 0.1902954*C（ln10*r/(1+r)^2, r=0.1）
        for ph in (4.76 - 1, 4.76 + 1):
            assert abs(beta_mM_per_pH(c, 4.76, ph) - 0.1902954 * c) < 1e-6 * c
        # 峰值两侧严格下降
        assert beta_mM_per_pH(c, 4.76, 4.76) > beta_mM_per_pH(c, 4.76, 5.1) > beta_mM_per_pH(c, 4.76, 5.6)
        assert beta_mM_per_pH(c, 4.76, 4.76) > beta_mM_per_pH(c, 4.76, 4.4) > beta_mM_per_pH(c, 4.76, 3.9)
    # 2. 离子强度：0.9% NaCl = 154 mM，水 = 0
    assert abs(recipe_values("saline_0.9pct")[0] - 154.0) < 1e-9
    assert recipe_values("water_for_injection")[0] == 0.0
    # 3. 离子强度 != 渗透浓度：苯甲醇只有渗透贡献
    i_ba, _, osm_ba = recipe_values("benzyl_alcohol_0.9pct")
    assert i_ba == 0.0 and osm_ba > 80.0
    # 4. 一元酸碱分布
    assert abs(frac_deprotonated_acid(4.76, 4.76) - 0.5) < 1e-12
    assert abs(frac_deprotonated_acid(4.76, 5.76) - 0.9090909) < 1e-6
    assert abs(frac_protonated_base(8.06, 8.0) - 0.534486) < 1e-5
    # 5. 复溶体积：10 mg × 90% / 5 mg/mL = 1.8 mL；浓度翻倍体积减半
    v = required_volume_mL(10.0, 90.0, 5.0)
    assert abs(v - 1.8) < 1e-12
    assert abs(required_volume_mL(10.0, 90.0, 10.0) * 2 - v) < 1e-12
    # 6. 含量降低则体积严格下降（同一目标浓度）
    assert required_volume_mL(10.0, 85.0, 5.0) < v
    # 7. 摩尔浓度：5 mg/mL @1200 g/mol = 4.1667 mM = 4166.7 uM
    assert abs(molarity_uM(5.0, 1200.0) - 4166.6667) < 1e-3
    print("selftest ok")
    return 0


def main():
    ap = argparse.ArgumentParser(description="reconstitution buffer arithmetic")
    ap.add_argument("--beta", nargs=3, type=float, metavar=("TOTAL_mM", "PKA", "PH"))
    ap.add_argument("--ion", nargs="+", metavar="CONC:CHARGE")
    ap.add_argument("--volume", nargs=3, type=float, metavar=("LABEL_mg", "NET_pct", "TARGET_mg_mL"))
    ap.add_argument("--molarity", nargs=2, type=float, metavar=("mg_mL", "MW"))
    ap.add_argument("--recipe", metavar="NAME")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.beta:
        total, pka, ph = a.beta
        print("beta = {:.3f} mM/pH  (peak at this total = {:.3f})".format(
            beta_mM_per_pH(total, pka, ph), beta_peak_mM_per_pH(total)))
    if a.ion:
        sp = [(float(x.split(":")[0]), int(x.split(":")[1])) for x in a.ion]
        print("I = {:.3f} mM".format(ionic_strength_mM(sp)))
    if a.volume:
        m, pct, t = a.volume
        print("volume = {:.4f} mL  (net peptide {:.4f} mg)".format(
            required_volume_mL(m, pct, t), m * pct / 100.0))
    if a.molarity:
        c, mw = a.molarity
        print("molarity = {:.3f} uM".format(molarity_uM(c, mw)))
    if a.recipe:
        i_nom, i_eff, osm = recipe_values(a.recipe)
        print("{}: I_nominal={:.2f} mM  I_effective={}  osmolarity={:.1f} mOsm/L".format(
            a.recipe, i_nom, "n/a" if i_eff is None else "{:.2f} mM".format(i_eff), osm))
    if not any([a.beta, a.ion, a.volume, a.molarity, a.recipe]):
        ap.print_help()
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
