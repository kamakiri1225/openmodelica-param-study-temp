# -*- coding: utf-8 -*-
"""
002 パラメータスタディ（集中定数モデル版）。

時間の指標は「整定時間 5τ」(= 5×C/UA, 99.3%到達) を用いる（001 の fit 図と統一）。

図:
  - vary_size.png     … タンク寸法(Lx,Ly)を一律 1.0→1.3 倍にしたときの水温
  - influence.png     … 因子ごとの影響 2行(Tmax, 5τ) × 4列(Q,heatCeffToAir,level,size)
  - objective_map.png … 目的空間 5τ–Tmax（色 = size）
  - pairplot.png      … タンク別 Lx を個別に変えたスタディの pairplot（色 = Tmax）

  python docs/study_pareto_demo.py [--n 300]
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
             "C:/Windows/Fonts/meiryo.ttc", "C:/Windows/Fonts/YuGothR.ttc",
             "C:/Windows/Fonts/msgothic.ttc"]:
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

HERE = os.path.dirname(__file__)
IMG2 = os.path.join(HERE, "img", "002")
os.makedirs(IMG2, exist_ok=True)

# ---- 実験データ (eva5) と参考の (Tmax, 5τ) ----
time_s = np.array([0, 5263, 10526, 15789, 21053, 26316, 31579, 36842, 42105, 47368,
                   52632, 57895, 63158, 68421, 73684, 78947, 84211, 89474, 94737, 100000], float)
sensors = np.array([
    [23.8, 27.8, 29.8, 31.2, 32.4, 33.4, 34.3, 35.0, 35.5, 36.0, 36.4, 36.7, 37.0, 37.2, 37.35, 37.40, 37.50, 37.60, 37.65, 37.70],
    [24.0, 28.0, 30.1, 31.5, 32.7, 33.7, 34.5, 35.2, 35.8, 36.2, 36.6, 36.9, 37.15, 37.35, 37.50, 37.55, 37.60, 37.70, 37.75, 37.80],
    [24.2, 28.4, 30.5, 31.9, 33.0, 34.0, 34.8, 35.5, 36.0, 36.4, 36.8, 37.1, 37.35, 37.55, 37.70, 37.65, 37.75, 37.80, 37.85, 37.90],
    [23.7, 27.6, 29.6, 31.0, 32.2, 33.2, 34.1, 34.8, 35.4, 35.8, 36.2, 36.5, 36.8, 37.0, 37.15, 37.20, 37.30, 37.40, 37.45, 37.50]])
exp_mean = sensors.mean(0)
Tair = 24.5
Tmax_exp = float(exp_mean[-1])
tau_exp = float(np.interp(Tair + 0.632 * (Tmax_exp - Tair), exp_mean, time_s)) / 3600.0
tset_exp = 5 * tau_exp   # 整定時間 5τ [h]

# ---- 集中定数モデル ----
# size    : Lx,Ly を一律にスケール
# s1,s2,s3: 各タンクの Lx (Lx1_1 / Lx2_1,Lx2_2 / Lx3_1) を個別スケール
rho_w, cp_w = 1000.0, 4186.0
th = 2.3 / 1000
Lx1_1, Ly1_1 = 0.903, 0.479
Lx2_1, Lx2_2, Ly2_1, Ly2_2 = 1.191, 0.478, 1.670, 0.337
Lx3_1, Ly3_1 = 0.573, 1.191


def _dims(size, s1, s2, s3):
    lx1 = Lx1_1 * s1 * size; ly1 = Ly1_1 * size
    lx2 = Lx2_1 * s2 * size; lx2b = Lx2_2 * s2 * size; ly2 = Ly2_1 * size; ly2b = Ly2_2 * size
    lx3 = Lx3_1 * s3 * size; ly3 = Ly3_1 * size
    a1 = lx1 * ly1
    a2 = lx2 * ly2 + lx2b * ly2b
    a3 = lx3 * ly3
    return (lx1, ly1, lx2, ly2, lx3, ly3, a1, a2, a3)


def ua(h_air, level, size=1.0, s1=1.0, s2=1.0, s3=1.0, h_in=10.0, kground=80.0):
    lx1, ly1, lx2, ly2, lx3, ly3, a1, a2, a3 = _dims(size, s1, s2, s3)
    UA_air = h_air * (a1 + a2 + a3)

    def g(Ain, Ac, Ag):
        return 1 / (1 / (h_in * Ain) + 1 / (Ac * kground / th) + 1 / (h_air * Ag))
    u1 = g(a1 + ly1 * level, a1 + lx1 * level + ly1 * level, a1 + ly1 * level)
    a2in = a2 + (ly2 + lx2) * level
    u2 = g(a2in, a2 + (lx2 + ly2) * level, a2in)
    a3g = a3 + (lx3 + ly3) * level
    u3 = g(a3g, a3g, a3g)
    return UA_air + u1 + u2 + u3


def cap(level, size=1.0, s1=1.0, s2=1.0, s3=1.0):
    _, _, _, _, _, _, a1, a2, a3 = _dims(size, s1, s2, s3)
    return (a1 * level + a2 * level + a3 * 0.9 * level) * rho_w * cp_w


def responses(Q, h_air, level, size=1.0, s1=1.0, s2=1.0, s3=1.0):
    UA = ua(h_air, level, size, s1, s2, s3)
    Tmax = Tair + Q / UA
    tset = 5 * cap(level, size, s1, s2, s3) / UA / 3600.0   # 整定時間 5τ [h]
    return Tmax, tset


def temp_curve(t, Q, h_air, level, size=1.0):
    UA = ua(h_air, level, size)
    C = cap(level, size)
    return Tair + (Q / UA) * (1 - np.exp(-t / (C / UA)))


def lhs(n, ranges, seed=1):
    rng = np.random.default_rng(seed)
    out = np.zeros((n, len(ranges)))
    for j, (lo, hi) in enumerate(ranges):
        perm = rng.permutation(n)
        out[:, j] = lo + ((perm + rng.random(n)) / n) * (hi - lo)
    return out


# フィット点（001）
QF, HF, LF = 610.0, 8.79, 0.0755


def fig_vary_size():
    H = 3600.0
    tt = np.linspace(0, 200000, 500)
    fig, ax = plt.subplots(figsize=(9.5, 6))
    ax.plot(time_s / H, exp_mean, "ks", markersize=5, label="実験 4センサ平均")
    for s, c in zip([1.0, 1.1, 1.2, 1.3], ["tab:blue", "tab:green", "tab:orange", "tab:red"]):
        Tm, ts = responses(QF, HF, LF, size=s)
        ax.plot(tt / H, temp_curve(tt, QF, HF, LF, s), "-", color=c, linewidth=2.2,
                label="size=%.1f 倍 (Tmax=%.1f℃, 5τ=%.0fh)" % (s, Tm, ts))
    ax.set_xlabel("Time [h]"); ax.set_ylabel("Temperature [degC]")
    ax.set_xlim(0, 200000 / H); ax.set_ylim(23, 40); ax.grid(True, alpha=0.4)
    ax.legend(fontsize=11, loc="lower right")
    ax.set_title("タンク寸法(Lx,Ly)を拡大した場合の水温（Q・h_air・level はフィット値固定）")
    plt.tight_layout()
    out = os.path.join(IMG2, "vary_size.png")
    plt.savefig(out, dpi=150, bbox_inches="tight"); plt.close()
    print("saved:", out)


def fig_influence():
    facs = [("Q [W]", 550, 720, QF, "Q"),
            ("heatCeffToAir", 5, 12, HF, "h"),
            ("level_start [m]", 0.05, 0.16, LF, "level"),
            ("size (寸法倍率)", 0.9, 1.3, 1.0, "size")]
    fig, ax = plt.subplots(2, 4, figsize=(18, 8.5))
    for j, (lab, lo, hi, fitv, key) in enumerate(facs):
        xs = np.linspace(lo, hi, 120)
        Tm, ts = [], []
        for x in xs:
            kw = dict(Q=QF, h_air=HF, level=LF, size=1.0)
            kw[{"Q": "Q", "h": "h_air", "level": "level", "size": "size"}[key]] = x
            T, t = responses(kw["Q"], kw["h_air"], kw["level"], size=kw["size"])
            Tm.append(T); ts.append(t)
        Tf, tf = responses(QF, HF, LF)
        ax[0, j].plot(xs, Tm, "-", color="tab:red", linewidth=2.6)
        ax[0, j].axhline(Tmax_exp, color="gray", ls="--", lw=1.2)
        ax[0, j].plot(fitv, Tf, "ko", ms=8)
        ax[0, j].set_title(lab, fontsize=16); ax[0, j].grid(True, alpha=0.4); ax[0, j].tick_params(labelsize=12)
        ax[1, j].plot(xs, ts, "-", color="tab:blue", linewidth=2.6)
        ax[1, j].axhline(tset_exp, color="gray", ls="--", lw=1.2)
        ax[1, j].plot(fitv, tf, "ko", ms=8)
        ax[1, j].set_xlabel(lab, fontsize=16); ax[1, j].grid(True, alpha=0.4); ax[1, j].tick_params(labelsize=12)
    ax[0, 0].set_ylabel("最大温度 Tmax [degC]", fontsize=16)
    ax[1, 0].set_ylabel("整定時間 5τ [h]", fontsize=16)
    fig.suptitle("因子の影響（各列＝その因子だけ変化, 他はフィット値固定／灰破線＝実験値・黒点＝フィット点）",
                 fontsize=18, y=1.0)
    plt.tight_layout()
    out = os.path.join(IMG2, "influence.png")
    plt.savefig(out, dpi=140, bbox_inches="tight"); plt.close()
    print("saved:", out)


def pairplot(data, labels, cvals, clabel, path, title):
    """下三角のみ・正方形パネルの pairplot。点の色 = cvals。"""
    m = len(labels)
    fig, axes = plt.subplots(m, m, figsize=(3.3 * m, 3.3 * m))
    sc = None
    for i in range(m):
        for j in range(m):
            ax = axes[i, j]
            ax.set_box_aspect(1)
            if j > i:
                ax.axis("off"); continue
            if i == j:
                ax.hist(data[:, i], bins=18, color="0.75", edgecolor="w")
            else:
                sc = ax.scatter(data[:, j], data[:, i], c=cvals, cmap="viridis",
                                s=24, alpha=0.85, edgecolor="none")
            if i == m - 1:
                ax.set_xlabel(labels[j], fontsize=15)
            else:
                ax.set_xticklabels([])
            if j == 0 and i != 0:
                ax.set_ylabel(labels[i], fontsize=15)
            elif j != 0:
                ax.set_yticklabels([])
            ax.tick_params(labelsize=11)
    fig.subplots_adjust(wspace=0.08, hspace=0.08, right=0.9)
    cax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
    cbar = fig.colorbar(sc, cax=cax); cbar.set_label(clabel, fontsize=16); cbar.ax.tick_params(labelsize=12)
    fig.suptitle(title, fontsize=19, y=0.93)
    plt.savefig(path, dpi=140, bbox_inches="tight"); plt.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300)
    args = ap.parse_args()

    fig_vary_size()
    fig_influence()

    # 目的空間マップ用 LHS (Q, heatCeffToAir, level, size)
    X = lhs(args.n, [(550.0, 720.0), (5.0, 12.0), (0.05, 0.16), (0.9, 1.3)])
    Q, h_air, level, size = X.T
    Tmax = np.empty(args.n); tset = np.empty(args.n)
    for k in range(args.n):
        Tmax[k], tset[k] = responses(Q[k], h_air[k], level[k], size=size[k])
    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    scn = ax.scatter(tset, Tmax, c=size, cmap="plasma", s=28, alpha=0.85)
    ax.plot(tset_exp, Tmax_exp, "k*", markersize=22, label="実験値（参考）")
    ax.set_xlabel("整定時間 5τ [h]", fontsize=15); ax.set_ylabel("最大温度 Tmax [degC]", fontsize=15)
    ax.set_title("目的空間 5τ–Tmax（点の色 = タンク寸法倍率 size）", fontsize=15)
    cb = plt.colorbar(scn); cb.set_label("size (倍)", fontsize=15)
    ax.grid(True, alpha=0.4); ax.legend(fontsize=12); ax.tick_params(labelsize=12)
    plt.tight_layout()
    out = os.path.join(IMG2, "objective_map.png")
    plt.savefig(out, dpi=140, bbox_inches="tight"); plt.close()
    print("saved:", out)

    # ---- タンク別 Lx 個別スタディの pairplot ----
    Xd = lhs(args.n, [(0.7, 1.4), (0.7, 1.4), (0.7, 1.4)], seed=7)
    sL1, sL2, sL3 = Xd.T
    Tm = np.empty(args.n); tsd = np.empty(args.n)
    for k in range(args.n):
        Tm[k], tsd[k] = responses(QF, HF, LF, s1=sL1[k], s2=sL2[k], s3=sL3[k])
    data = np.column_stack([sL1, sL2, sL3, Tm, tsd])
    labels = ["Lx1 倍率", "Lx2 倍率", "Lx3 倍率", "Tmax [degC]", "5τ [h]"]
    pairplot(data, labels, Tm, "Tmax [degC]",
             os.path.join(IMG2, "pairplot.png"),
             "タンク別 Lx を個別に変えたスタディ pairplot（色 = Tmax, 時間指標 = 5τ）")
    print("saved:", os.path.join(IMG2, "pairplot.png"))
    print("Lx2(tank2) を 0.7->1.4 倍: Tmax %.1f->%.1f℃" %
          (responses(QF, HF, LF, s2=1.4)[0], responses(QF, HF, LF, s2=0.7)[0]))


if __name__ == "__main__":
    main()
