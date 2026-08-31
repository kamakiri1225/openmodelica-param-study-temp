# -*- coding: utf-8 -*-
"""
002 パラメータスタディ（集中定数モデル版）。

設計因子 Q・heatCeffToAir・level_start・size(タンク寸法倍率) を LHS で振り、
応答 τ(時定数) と Tmax(最大温度) を計算して
  - vary_size.png … タンク寸法を 1.0→1.3 倍にしたときの水温カーブ（容量増の効果）
  - pairplot.png  … 4設計因子の散布（点の色 = Tmax）
  - objective_map.png … 目的空間 τ–Tmax（色 = size, ★=実験値は参考）
を描く。目標値は設けず、因子→応答の影響を可視化する（パレート強調はしない）。

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

# ---- 実験データ (eva5) と参考の (Tmax, τ) ----
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

# ---- 集中定数モデル (size = 水平寸法 Lx,Ly の倍率) ----
rho_w, cp_w = 1000.0, 4186.0
th = 2.3 / 1000
Q0 = 610.0
Lx1_1, Ly1_1 = 0.903, 0.479
Lx2_1, Lx2_2, Ly2_1, Ly2_2 = 1.191, 0.478, 1.670, 0.337
Lx3_1, Ly3_1 = 0.573, 1.191


def UA_of(h_air, level, size=1.0, h_in=10.0, kground=80.0):
    s = size
    a1 = Lx1_1 * s * Ly1_1 * s
    a2 = (Lx2_1 * Ly2_1 + Lx2_2 * Ly2_2) * s * s
    a3 = Lx3_1 * s * Ly3_1 * s
    UA_air = h_air * (a1 + a2 + a3)

    def g(Ain, Ac, Ag):
        return 1 / (1 / (h_in * Ain) + 1 / (Ac * kground / th) + 1 / (h_air * Ag))
    u1 = g(a1 + Ly1_1 * s * level, a1 + Lx1_1 * s * level + Ly1_1 * s * level, a1 + Ly1_1 * s * level)
    a2in = a2 + (Ly2_1 + Ly2_2 + Lx2_1) * s * level
    u2 = g(a2in, Lx2_1 * Ly2_1 * s * s + (Lx2_1 + Ly2_1) * s * level, a2in)
    a3g = a3 + (Lx3_1 + Ly3_1) * s * level
    u3 = g(a3g, a3g, a3g)
    return UA_air + u1 + u2 + u3


def C_of(level, size=1.0):
    s = size
    a1 = Lx1_1 * s * Ly1_1 * s
    a2 = (Lx2_1 * Ly2_1 + Lx2_2 * Ly2_2) * s * s
    a3 = Lx3_1 * s * Ly3_1 * s
    return (a1 * level + a2 * level + a3 * 0.9 * level) * rho_w * cp_w


def responses(Q, h_air, level, size=1.0):
    UA = UA_of(h_air, level, size)
    return Tair + Q / UA, C_of(level, size) / UA / 3600.0   # Tmax[degC], tau[h]


def temp_curve(t, Q, h_air, level, size=1.0):
    UA = UA_of(h_air, level, size)
    C = C_of(level, size)
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
    """タンク寸法倍率 size を 1.0→1.3 にしたときの水温カーブ。"""
    H = 3600.0
    tt = np.linspace(0, 200000, 500)
    fig, ax = plt.subplots(figsize=(9.5, 6))
    ax.plot(time_s / H, exp_mean, "ks", markersize=5, label="実験 4センサ平均")
    for s, c in zip([1.0, 1.1, 1.2, 1.3], ["tab:blue", "tab:green", "tab:orange", "tab:red"]):
        Tm, ta = responses(QF, HF, LF, s)
        ax.plot(tt / H, temp_curve(tt, QF, HF, LF, s), "-", color=c, linewidth=2.2,
                label="size=%.1f 倍 (Tmax=%.1f℃, τ=%.1fh)" % (s, Tm, ta))
    ax.set_xlabel("Time [h]"); ax.set_ylabel("Temperature [degC]")
    ax.set_xlim(0, 200000 / H); ax.set_ylim(23, 40); ax.grid(True, alpha=0.4)
    ax.legend(fontsize=11, loc="lower right")
    ax.set_title("タンク寸法(Lx,Ly)を拡大した場合の水温（Q・h_air・level はフィット値固定）")
    plt.tight_layout()
    out = os.path.join(IMG2, "vary_size.png")
    plt.savefig(out, dpi=150, bbox_inches="tight"); plt.close()
    print("saved:", out)


def influence_grid(path):
    """因子ごとの影響: 2行(Tmax, τ) × 4列(Q,heatCeffToAir,level,size)。
    各列はその因子だけを振り、他はフィット値に固定した1本の曲線。"""
    facs = [("Q [W]", 550, 720, QF, "Q"),
            ("heatCeffToAir", 5, 12, HF, "h"),
            ("level_start [m]", 0.05, 0.16, LF, "level"),
            ("size (寸法倍率)", 0.9, 1.3, 1.0, "size")]
    fig, ax = plt.subplots(2, 4, figsize=(18, 8.5))
    for j, (lab, lo, hi, fitv, key) in enumerate(facs):
        xs = np.linspace(lo, hi, 120)
        Tm, ta = [], []
        for x in xs:
            kw = dict(Q=QF, h_air=HF, level=LF, size=1.0)
            kw[{"Q": "Q", "h": "h_air", "level": "level", "size": "size"}[key]] = x
            T, t = responses(kw["Q"], kw["h_air"], kw["level"], kw["size"])
            Tm.append(T); ta.append(t)
        Tf, tf = responses(QF, HF, LF, 1.0)
        # 上段: Tmax
        ax[0, j].plot(xs, Tm, "-", color="tab:red", linewidth=2.6)
        ax[0, j].axhline(Tmax_exp, color="gray", ls="--", lw=1.2)
        ax[0, j].plot(fitv, Tf, "ko", ms=8)
        ax[0, j].set_title(lab, fontsize=16)
        ax[0, j].grid(True, alpha=0.4); ax[0, j].tick_params(labelsize=12)
        # 下段: τ
        ax[1, j].plot(xs, ta, "-", color="tab:blue", linewidth=2.6)
        ax[1, j].axhline(tau_exp, color="gray", ls="--", lw=1.2)
        ax[1, j].plot(fitv, tf, "ko", ms=8)
        ax[1, j].set_xlabel(lab, fontsize=16)
        ax[1, j].grid(True, alpha=0.4); ax[1, j].tick_params(labelsize=12)
    ax[0, 0].set_ylabel("最大温度 Tmax [degC]", fontsize=16)
    ax[1, 0].set_ylabel("時定数 τ [h]", fontsize=16)
    ax[0, 3].legend(["応答", "実験値", "フィット点"], fontsize=11, loc="upper right")
    fig.suptitle("因子の影響（各列＝その因子だけを変化, 他はフィット値固定／灰破線＝実験値・黒点＝フィット点）",
                 fontsize=18, y=1.0)
    plt.tight_layout()
    plt.savefig(path, dpi=140, bbox_inches="tight")
    plt.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300)
    args = ap.parse_args()

    # まず「容量を増やした場合」の直接比較
    fig_vary_size()

    # 因子の影響グリッド（pairplot より読みやすい）
    influence_grid(os.path.join(IMG2, "influence.png"))
    print("saved:", os.path.join(IMG2, "influence.png"))

    # LHS: Q, heatCeffToAir, level, size （目的空間の分布用）
    ranges = [(550.0, 720.0), (5.0, 12.0), (0.05, 0.16), (0.9, 1.3)]
    X = lhs(args.n, ranges)
    Q, h_air, level, size = X[:, 0], X[:, 1], X[:, 2], X[:, 3]
    Tmax = np.empty(args.n); tau = np.empty(args.n)
    for k in range(args.n):
        Tmax[k], tau[k] = responses(Q[k], h_air[k], level[k], size[k])
    print("実験 参考: Tmax=%.2f degC, tau=%.2f h" % (Tmax_exp, tau_exp))
    print("size 範囲 %.1f-%.1f 倍 -> Tmax %.1f-%.1f℃, tau %.1f-%.1fh"
          % (size.min(), size.max(), Tmax.min(), Tmax.max(), tau.min(), tau.max()))

    # 目的空間 τ–Tmax, 色 = size
    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    sc = ax.scatter(tau, Tmax, c=size, cmap="plasma", s=28, alpha=0.85)
    ax.plot(tau_exp, Tmax_exp, "k*", markersize=22, label="実験値（参考）")
    ax.set_xlabel("時定数 τ [h]", fontsize=15)
    ax.set_ylabel("最大温度 Tmax [degC]", fontsize=15)
    ax.set_title("目的空間 τ–Tmax（点の色 = タンク寸法倍率 size）", fontsize=15)
    cbar = plt.colorbar(sc); cbar.set_label("size (倍)", fontsize=15)
    ax.grid(True, alpha=0.4); ax.legend(fontsize=12)
    ax.tick_params(labelsize=12)
    plt.tight_layout()
    out = os.path.join(IMG2, "objective_map.png")
    plt.savefig(out, dpi=140, bbox_inches="tight"); plt.close()
    print("saved:", out)


if __name__ == "__main__":
    main()
