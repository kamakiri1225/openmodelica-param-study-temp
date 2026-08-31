# -*- coding: utf-8 -*-
"""003: フィット状態（実測一致）から各因子を振ったときの水温カーブ。

基準＝002 のフィット点（Q=610, heatCeffToAir=8.79, level_start=0.0755）で、この状態が
実測 eva5 に一致する。ここから Q / level / heatCeffToAir / size を個別に振って可視化する。

  python vary_factors.py     -> docs/img/vary_Q.png, vary_level.png, vary_h_air.png, vary_size.png
"""
import os
import glob
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

for cand in ["~/.fonts/NotoSansCJKjp-Regular.otf",
             "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
             "C:/Windows/Fonts/meiryo.ttc"]:
    for p in glob.glob(os.path.expanduser(cand)):
        try:
            fm.fontManager.addfont(p)
            matplotlib.rcParams["font.family"] = fm.FontProperties(fname=p).get_name()
            break
        except Exception:
            pass
    else:
        continue
    break
matplotlib.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "docs", "img")
os.makedirs(IMG, exist_ok=True)
H = 3600.0

# 実測 eva5 (温度管理なし) 平均
eva5_t = np.array([0, 5263, 10526, 15789, 21053, 26316, 31579, 36842, 42105, 47368,
                   52632, 57895, 63158, 68421, 73684, 78947, 84211, 89474, 94737, 100000], float)
eva5 = np.array([
    [23.8, 27.8, 29.8, 31.2, 32.4, 33.4, 34.3, 35.0, 35.5, 36.0, 36.4, 36.7, 37.0, 37.2, 37.35, 37.40, 37.50, 37.60, 37.65, 37.70],
    [24.0, 28.0, 30.1, 31.5, 32.7, 33.7, 34.5, 35.2, 35.8, 36.2, 36.6, 36.9, 37.15, 37.35, 37.50, 37.55, 37.60, 37.70, 37.75, 37.80],
    [24.2, 28.4, 30.5, 31.9, 33.0, 34.0, 34.8, 35.5, 36.0, 36.4, 36.8, 37.1, 37.35, 37.55, 37.70, 37.65, 37.75, 37.80, 37.85, 37.90],
    [23.7, 27.6, 29.6, 31.0, 32.2, 33.2, 34.1, 34.8, 35.4, 35.8, 36.2, 36.5, 36.8, 37.0, 37.15, 37.20, 37.30, 37.40, 37.45, 37.50]]).mean(0)

# ---- 集中定数モデル ----
Tair, T_START = 24.5, 24.5
rho_w, cp_w, th = 1000.0, 4186.0, 2.3 / 1000
Lx1_1, Ly1_1 = 0.903, 0.479
Lx2_1, Lx2_2, Ly2_1, Ly2_2 = 1.191, 0.478, 1.670, 0.337
Lx3_1, Ly3_1 = 0.573, 1.191


def _A(size):
    a1 = Lx1_1 * Ly1_1 * size * size
    a2 = (Lx2_1 * Ly2_1 + Lx2_2 * Ly2_2) * size * size
    a3 = Lx3_1 * Ly3_1 * size * size
    return a1, a2, a3


def ua(h_air, level, size=1.0, h_in=10.0, kground=80.0):
    a1, a2, a3 = _A(size)
    UA_air = h_air * (a1 + a2 + a3)
    s = size

    def g(Ain, Ac, Ag):
        return 1 / (1 / (h_in * Ain) + 1 / (Ac * kground / th) + 1 / (h_air * Ag))
    u1 = g(a1 + Ly1_1 * s * level, a1 + (Lx1_1 + Ly1_1) * s * level, a1 + Ly1_1 * s * level)
    a2in = a2 + (Ly2_1 + Lx2_1) * s * level
    u2 = g(a2in, a2 + (Lx2_1 + Ly2_1) * s * level, a2in)
    a3g = a3 + (Lx3_1 + Ly3_1) * s * level
    u3 = g(a3g, a3g, a3g)
    return UA_air + u1 + u2 + u3


def cap(level, size=1.0):
    a1, a2, a3 = _A(size)
    return (a1 * level + a2 * level + a3 * 0.9 * level) * rho_w * cp_w


def curve(t, Q, h_air, level, size=1.0, Tamb=Tair):
    """水温 [degC]。開始=外気温 Tamb, 到達=Tamb+Q/UA。"""
    UA = ua(h_air, level, size)
    Tinf = Tamb + Q / UA
    return Tinf + (Tamb - Tinf) * np.exp(-t / (cap(level, size) / UA))


# フィット点（実測一致）: Q=610, heatCeffToAir=8.79, level=0.0755, size=1.0, 外気温=24.5
QF, HF, LF, SF, TF = 610.0, 8.79, 0.0755, 1.0, 24.5
tt = np.linspace(0, 200000, 500)
FIXNAME = {"Q": "Q=610W", "h_air": "heatCeffToAir=8.79", "level": "level=0.0755m",
           "size": "size=1.0", "Tamb": "外気温=24.5℃"}


def fig_vary(name, label, values, fmt, kw_key, ymin=23, ymax=42, show_exp=True):
    fig, ax = plt.subplots(figsize=(9.5, 6))
    if show_exp:
        ax.plot(eva5_t / H, eva5, "ks", markersize=5, label="実測 eva5 (温度管理なし)")
    for v, c in zip(values, ["tab:blue", "tab:green", "tab:orange", "tab:red"]):
        kw = dict(Q=QF, h_air=HF, level=LF, size=SF, Tamb=TF)
        kw[kw_key] = v
        ax.plot(tt / H, curve(tt, kw["Q"], kw["h_air"], kw["level"], kw["size"], kw["Tamb"]),
                "-", color=c, linewidth=2.0, label=fmt % v)
    # 温度管理あり（点線, 目標=外気温 → 水温=外気温に保持）
    if kw_key == "Tamb":
        for v, c in zip(values, ["tab:blue", "tab:green", "tab:orange", "tab:red"]):
            ax.axhline(v, ls=":", color=c, linewidth=1.8)
        ax.plot([], [], ls=":", color="gray", linewidth=1.8, label="温度管理あり (=外気温に保持)")
    else:
        ax.axhline(TF, ls=":", color="gray", linewidth=2.2,
                   label="温度管理あり (=外気温%.1f℃に保持)" % TF)
    fixed = [FIXNAME[k] for k in ["Q", "h_air", "level", "size", "Tamb"] if k != kw_key]
    ax.text(0.02, 0.97, "固定（実測フィット値）: " + ", ".join(fixed),
            transform=ax.transAxes, va="top", fontsize=9,
            bbox=dict(boxstyle="round", fc="white", alpha=0.85))
    ax.set_xlabel("Time [h]", fontsize=13); ax.set_ylabel("水温 [degC]", fontsize=13)
    ax.set_xlim(0, 200000 / H); ax.set_ylim(ymin, ymax); ax.grid(True, alpha=0.4)
    ax.legend(fontsize=10, loc="lower right")
    ax.set_title("%s を振る（他は実測フィット値に固定）" % label, fontsize=13)
    plt.tight_layout()
    out = os.path.join(IMG, "vary_%s.png" % name)
    plt.savefig(out, dpi=150, bbox_inches="tight"); plt.close()
    print("saved:", out)


fig_vary("Q", "発熱量 Q [W]", [550, 610, 690, 750], "Q=%.0f W", "Q")
fig_vary("h_air", "heatCeffToAir", [6, 8.79, 11, 14], "h_air=%.2f", "h_air")
fig_vary("level", "水位 level [m]", [0.05, 0.0755, 0.11, 0.16], "level=%.3f m", "level")
fig_vary("size", "タンク寸法倍率 size", [1.0, 1.1, 1.2, 1.3], "size=%.1f 倍", "size")
# 外気温を振る（開始温度も外気温に追従。実測は24.5℃条件なので参考重畳）
fig_vary("Tair", "外気温 [degC]", [15, 24.5, 30, 35], "外気温=%.1f℃", "Tamb", ymin=13, ymax=52)
