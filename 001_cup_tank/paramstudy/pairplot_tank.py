# -*- coding: utf-8 -*-
"""001_cup_tank 統一モデルのパラメータスタディ（pairplot, 温度管理あり/なし別）。

設計因子(LHSで振る5つ):
  発熱量 Q [W], 上面熱伝達率 h_top, 水位 level [m], Lx倍率 sx, Ly倍率 sy
  ※ Lx と Ly は「個別」に倍率(縦横を別々に)。→ 縦横比も表面積も独立に変わる。
応答(各点から計算して表示):
  表面積倍率(1=実機), 体積 V [L], 5τ [h], 5τ時の温度上昇 ΔT [K](上限100K)
温度管理:
  なし … ΔT = Q/UA (5τで99.3%)
  あり … ダイキン3.5kW仕様(冷却上限3500W)。Q<=3500 は ΔT=0, Q>3500 は ΔT=(Q-3500)/UA
あり/なし で画像を分割。点の色 = 発熱量Q。

列の並び(左→右): 発熱量, 熱伝達率, 水位, Lx倍率, Ly倍率, 表面積倍率, 体積, 5τ, 温度上昇ΔT

  python pairplot_tank.py [--n 300]
出力: pairplot_off.png (温度管理なし), pairplot_on.png (温度管理あり)
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

# ---- 統一モデルと同じ集中定数（001_cup_tank）----
rho_w, cp_w = 1000.0, 4186.0
Lx0, Ly0 = 1.764, 1.829            # 実機の Lx, Ly [m]
h_side = 9.0                       # 側面(固定, 自然対流)
h_bottom = 0.026 / 0.015           # 底面=15mm空気層の伝導(固定, ≒1.73)
h_water_wall = 200.0               # 水↔壁(固定, 壁≒水)
Tamb = 24.5
Qcool_max = 3500.0                 # ダイキン3.5kW(冷却能力上限)
dT_max = 100.0                     # 温度上昇の上限 [K] (沸騰等)


def geom(sx, sy, level):
    """Lx=Lx0*sx, Ly=Ly0*sy （縦横を個別に倍率）。"""
    A_top = (Lx0 * sx) * (Ly0 * sy)
    peri = 2.0 * (Lx0 * sx + Ly0 * sy)
    A_side = peri * level
    A_bot = A_top
    return A_top, A_side, A_bot


def ua(h_top, level, sx, sy):
    A_top, A_side, A_bot = geom(sx, sy, level)
    Gtop = h_top * A_top
    Gside = h_side * A_side
    Gbot = h_bottom * A_bot
    Gl = h_water_wall * A_side
    Gwall = Gside + Gbot
    return Gtop + 1.0 / (1.0 / Gl + 1.0 / Gwall)


def cap(level, sx, sy):
    A_top, _, _ = geom(sx, sy, level)
    return A_top * level * rho_w * cp_w      # 水の熱容量 [J/K]


def volume_L(level, sx, sy):
    A_top, _, _ = geom(sx, sy, level)
    return A_top * level * 1000.0            # m3 -> L


def area_total(level, sx, sy):
    A_top, A_side, A_bot = geom(sx, sy, level)
    return A_top + A_side + A_bot            # 上面+側面+底面 [m2]


def lhs(n, ranges, seed=1):
    rng = np.random.default_rng(seed)
    out = np.zeros((n, len(ranges)))
    for j, (lo, hi) in enumerate(ranges):
        perm = rng.permutation(n)
        out[:, j] = lo + ((perm + rng.random(n)) / n) * (hi - lo)
    return out


def pairplot1(data, labels, cvals, clabel, path, title):
    m = len(labels)
    fig, axes = plt.subplots(m, m, figsize=(3.0 * m, 3.0 * m))
    sc = None
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
                            transform=ax.transAxes, fontweight="bold", fontsize=11 + abs(r) * 16)
                ax.set_xticks([]); ax.set_yticks([]); continue
            if i == j:
                ax.hist(data[:, i], bins=18, color="0.7", alpha=0.8)
            else:
                sc = ax.scatter(data[:, j], data[:, i], c=cvals, cmap="jet", s=14, alpha=0.75, edgecolor="none")
            if i == m - 1:
                ax.set_xlabel(labels[j], fontsize=12)
            else:
                ax.set_xticklabels([])
            if j == 0 and i != 0:
                ax.set_ylabel(labels[i], fontsize=12)
            elif j != 0:
                ax.set_yticklabels([])
            ax.tick_params(labelsize=9)
    fig.subplots_adjust(right=0.9)
    cax = fig.add_axes([0.92, 0.15, 0.014, 0.7])
    cbar = fig.colorbar(sc, cax=cax); cbar.set_label(clabel, fontsize=15)
    fig.suptitle(title, fontsize=18, y=0.92)
    plt.savefig(path, dpi=120, bbox_inches="tight")
    plt.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300)
    args = ap.parse_args()
    n = args.n

    # 設計因子: Q, h_top, level, Lx倍率 sx, Ly倍率 sy （Lx,Ly個別）
    X = lhs(n, [(400.0, 5000.0), (6.0, 100.0), (0.05, 0.22), (0.8, 2.0), (0.8, 2.0)])
    Q, h_top, level, sx, sy = X.T
    UA = np.array([ua(h_top[k], level[k], sx[k], sy[k]) for k in range(n)])
    C = np.array([cap(level[k], sx[k], sy[k]) for k in range(n)])
    tau5 = 5.0 * C / UA / 3600.0                          # 5τ [h]
    V = np.array([volume_L(level[k], sx[k], sy[k]) for k in range(n)])
    A = np.array([area_total(level[k], sx[k], sy[k]) for k in range(n)])
    A_base = area_total(0.0755, 1.0, 1.0)                 # 実機(sx=sy=1, level=0.0755)の表面積
    A_ratio = A / A_base                                  # 表面積倍率(1=実機)

    f5 = 1.0 - np.exp(-5.0)                               # 5τ で 99.3%
    dT_off = Q / UA
    dT_on = np.maximum(0.0, (Q - Qcool_max) / UA)         # ダイキン3.5kW上限
    dT5_off = np.minimum(f5 * dT_off, dT_max)             # 5τ時の温度上昇(上限100K)
    dT5_on = np.minimum(f5 * dT_on, dT_max)

    # 列の並び(左→右): 発熱量, 熱伝達率, 水位, Lx倍率, Ly倍率, 表面積倍率, 体積, 5τ, ΔT
    labels = ["発熱量Q [W]", "熱伝達率 h_top", "水位 [m]", "Lx倍率", "Ly倍率",
              "表面積倍率(1=実機)", "体積 [L]", "5τ [h]", "5τ時 温度上昇 ΔT [K]"]
    data_off = np.column_stack([Q, h_top, level, sx, sy, A_ratio, V, tau5, dT5_off])
    data_on = np.column_stack([Q, h_top, level, sx, sy, A_ratio, V, tau5, dT5_on])

    pairplot1(data_off, labels, Q, "発熱量Q [W]", os.path.join(HERE, "pairplot_off.png"),
              "タンク統一モデル pairplot — 温度管理なし（%d ケース）" % n)
    pairplot1(data_on, labels, Q, "発熱量Q [W]", os.path.join(HERE, "pairplot_on.png"),
              "タンク統一モデル pairplot — 温度管理あり・ダイキン3.5kW上限（%d ケース）" % n)

    n_hold = int(np.sum(Q <= Qcool_max))
    print("実機表面積(倍率1) = %.2f m2" % A_base)
    print("設計点(LHS) N=%d。温度管理なし %d ケース / あり %d ケース（計 %d）" % (n, n, n, 2 * n))
    print("あり: Q<=3500W で保持(ΔT=0)= %d 点, Q>3500W で上昇= %d 点" % (n_hold, n - n_hold))
    print("なし: 5τ時ΔT %.1f〜%.1f K / あり: %.1f〜%.1f K" % (dT5_off.min(), dT5_off.max(), dT5_on.min(), dT5_on.max()))
    print("saved:", os.path.join(HERE, "pairplot_off.png"), "/ pairplot_on.png")


if __name__ == "__main__":
    main()
