# -*- coding: utf-8 -*-
"""003 パラメータスタディ: 温度管理あり／なし を含む pairplot。

設計因子（LHS）: 発熱量Q, 外気側熱伝達率 heatCeffToAir, 水位 level, 外気温 Tair。
各設計点について 2 条件を評価する:
  - 温度管理なし: 水温は Tair + Q/UA まで上昇（温度上昇 ΔT = Q/UA）
  - 温度管理あり: PIDが目標=外気温に保持 → 水温=外気温（ΔT ≒ 0。15℃なら15℃）
pairplot は点を **温度管理あり(青)／なし(赤)** で色分けする。

  python pairplot_control.py [--n 250]

出力: docs/img/pairplot_control.png
時間指標は 5τ（整定時間, 99.3%到達）。
"""
import os
import glob
import argparse
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
matplotlib.rcParams["font.size"] = 13

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "docs", "img")
os.makedirs(IMG, exist_ok=True)

# ---- 集中定数モデル（002 のフィット式と同一）----
rho_w, cp_w = 1000.0, 4186.0
th = 2.3 / 1000
Lx1_1, Ly1_1 = 0.903, 0.479
Lx2_1, Lx2_2, Ly2_1, Ly2_2 = 1.191, 0.478, 1.670, 0.337
Lx3_1, Ly3_1 = 0.573, 1.191
A1 = Lx1_1 * Ly1_1
A2 = Lx2_1 * Ly2_1 + Lx2_2 * Ly2_2
A3 = Lx3_1 * Ly3_1


def ua(h_air, level, h_in=10.0, kground=80.0):
    UA_air = h_air * (A1 + A2 + A3)

    def g(Ain, Ac, Ag):
        return 1 / (1 / (h_in * Ain) + 1 / (Ac * kground / th) + 1 / (h_air * Ag))
    u1 = g(A1 + Ly1_1 * level, A1 + Lx1_1 * level + Ly1_1 * level, A1 + Ly1_1 * level)
    a2in = A2 + (Ly2_1 + Lx2_1) * level
    u2 = g(a2in, A2 + (Lx2_1 + Ly2_1) * level, a2in)
    a3g = A3 + (Lx3_1 + Ly3_1) * level
    u3 = g(a3g, a3g, a3g)
    return UA_air + u1 + u2 + u3


def cap(level):
    return (A1 * level + A2 * level + A3 * 0.9 * level) * rho_w * cp_w


def volume_L(level):
    return (A1 * level + A2 * level + A3 * 0.9 * level) * 1000.0   # m3 -> L


def area_total(level):
    """放熱面積 [m2] = 上面 + 側/底(濡れ面積)。"""
    A_top = A1 + A2 + A3
    A_g = (A1 + Ly1_1 * level) + (A2 + (Ly2_1 + Lx2_1) * level) + (A3 + (Lx3_1 + Ly3_1) * level)
    return A_top + A_g


def lhs(n, ranges, seed=1):
    rng = np.random.default_rng(seed)
    out = np.zeros((n, len(ranges)))
    for j, (lo, hi) in enumerate(ranges):
        perm = rng.permutation(n)
        out[:, j] = lo + ((perm + rng.random(n)) / n) * (hi - lo)
    return out


def pairplot1(data, labels, color, path, title):
    """単色 pairplot。下三角=散布, 対角=ヒスト, 上三角=相関係数(定数列は—)。"""
    m = len(labels)
    fig, axes = plt.subplots(m, m, figsize=(3.3 * m, 3.3 * m))
    for i in range(m):
        for j in range(m):
            ax = axes[i, j]
            ax.set_box_aspect(1)
            if j > i:
                xi, xj = data[:, i], data[:, j]
                if xi.std() < 1e-9 or xj.std() < 1e-9:
                    ax.text(0.5, 0.5, "—", ha="center", va="center", transform=ax.transAxes, fontsize=16)
                else:
                    r = float(np.corrcoef(xj, xi)[0, 1])
                    col = matplotlib.cm.RdBu_r((r + 1) / 2)
                    ax.set_facecolor((col[0], col[1], col[2], 0.25))
                    ax.text(0.5, 0.5, "%.2f" % r, ha="center", va="center",
                            transform=ax.transAxes, fontweight="bold", fontsize=13 + abs(r) * 20)
                ax.set_xticks([]); ax.set_yticks([]); continue
            if i == j:
                ax.hist(data[:, i], bins=18, color=color, alpha=0.7)
            else:
                ax.scatter(data[:, j], data[:, i], c=color, s=16, alpha=0.6, edgecolor="none")
            if i == m - 1:
                ax.set_xlabel(labels[j], fontsize=15)
            else:
                ax.set_xticklabels([])
            if j == 0 and i != 0:
                ax.set_ylabel(labels[i], fontsize=15)
            elif j != 0:
                ax.set_yticklabels([])
            ax.tick_params(labelsize=11)
    fig.suptitle(title, fontsize=20, y=0.93)
    plt.savefig(path, dpi=130, bbox_inches="tight")
    plt.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=250)
    args = ap.parse_args()
    n = args.n

    X = lhs(n, [(550.0, 4000.0), (5.0, 12.0), (0.05, 0.16), (15.0, 35.0)])
    Q, h_air, level, Tair = X.T
    UA = np.array([ua(h_air[k], level[k]) for k in range(n)])
    tau5 = np.array([5 * cap(level[k]) / UA[k] / 3600.0 for k in range(n)])

    # なし: ΔT=Q/UA、あり: ΔT=0（目標=外気温）
    dT_off = Q / UA
    dT_on = np.zeros(n)

    # 2条件を積む
    def stack(a_off, a_on):
        return np.concatenate([a_off, a_on])
    V = np.array([volume_L(level[k]) for k in range(n)])
    Ar = np.array([area_total(level[k]) for k in range(n)])
    labels = ["発熱量Q [W]", "heatCeffToAir", "外気温 [degC]", "体積 [L]",
              "表面積 [m²]", "水位 [m]", "温度上昇 ΔT [K]", "5τ [h]"]

    data_off = np.column_stack([Q, h_air, Tair, V, Ar, level, dT_off, tau5])
    data_on = np.column_stack([Q, h_air, Tair, V, Ar, level, dT_on, tau5])
    pairplot1(data_off, labels, "tab:red", os.path.join(IMG, "pairplot_control_off.png"),
              "温度管理なし pairplot（%d ケース, 上三角=相関係数）" % n)
    pairplot1(data_on, labels, "tab:blue", os.path.join(IMG, "pairplot_control_on.png"),
              "温度管理あり pairplot（目標=外気温, %d ケース／ΔT=0のため相関は—）" % n)
    print("温度管理なし %d ケース, あり %d ケース（計 %d）" % (n, n, 2 * n))
    print("なし: ΔT=%.1f〜%.1f K (Q/UA)  /  あり: ΔT=0 (水温=外気温)" % (dT_off.min(), dT_off.max()))
    print("saved:", os.path.join(IMG, "pairplot_control_off.png"), "/ _on.png")


if __name__ == "__main__":
    main()
