# -*- coding: utf-8 -*-
"""
002 パラメータスタディの実演（集中定数モデル版）。

合わせこみ(001)後のベースラインを中心に、設計因子 Q・heatCeffToAir・level_start を
LHS で振り、目的関数 τ（時定数）と Tmax（最大温度）を計算して
  - pairplot   (docs/img/002/pairplot.png)   … 因子×応答の総当たり（seaborn風）
  - pareto     (docs/img/002/pareto.png)      … 実験目標への近さでパレート前線
を描く。OM を Windows で回す場合は data/run_study.py が同じ流れを omc.exe で実行する。

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

HERE = os.path.dirname(__file__)
IMG2 = os.path.join(HERE, "img", "002")
os.makedirs(IMG2, exist_ok=True)

# ============================================================
# 実験データ (eva5) と目標 (Tmax, τ)
# ============================================================
time_s = np.array([0, 5263, 10526, 15789, 21053, 26316, 31579, 36842, 42105, 47368,
                   52632, 57895, 63158, 68421, 73684, 78947, 84211, 89474, 94737, 100000], float)
sensors = np.array([
    [23.8, 27.8, 29.8, 31.2, 32.4, 33.4, 34.3, 35.0, 35.5, 36.0, 36.4, 36.7, 37.0, 37.2, 37.35, 37.40, 37.50, 37.60, 37.65, 37.70],
    [24.0, 28.0, 30.1, 31.5, 32.7, 33.7, 34.5, 35.2, 35.8, 36.2, 36.6, 36.9, 37.15, 37.35, 37.50, 37.55, 37.60, 37.70, 37.75, 37.80],
    [24.2, 28.4, 30.5, 31.9, 33.0, 34.0, 34.8, 35.5, 36.0, 36.4, 36.8, 37.1, 37.35, 37.55, 37.70, 37.65, 37.75, 37.80, 37.85, 37.90],
    [23.7, 27.6, 29.6, 31.0, 32.2, 33.2, 34.1, 34.8, 35.4, 35.8, 36.2, 36.5, 36.8, 37.0, 37.15, 37.20, 37.30, 37.40, 37.45, 37.50]])
exp_mean = sensors.mean(0)
Tair = 24.5
Tmax_exp = float(exp_mean[-1])                       # ≈ 37.65
tgt = Tair + 0.632 * (Tmax_exp - Tair)
tau_exp = float(np.interp(tgt, exp_mean, time_s)) / 3600.0   # h (63.2%到達)

# ============================================================
# 集中定数モデル
# ============================================================
rho_w, cp_w = 1000.0, 4186.0
th = 2.3 / 1000
Lx1_1, Ly1_1 = 0.903, 0.479
Lx2_1, Lx2_2, Ly2_1, Ly2_2 = 1.191, 0.478, 1.670, 0.337
Lx3_1, Ly3_1 = 0.573, 1.191
A1 = Lx1_1 * Ly1_1
A2 = Lx2_1 * Ly2_1 + Lx2_2 * Ly2_2
A3 = Lx3_1 * Ly3_1


def UA_of(h_air, level, h_in=10.0, kground=80.0):
    UA_air = h_air * (A1 + A2 + A3)

    def g(Ain, Ac, Ag):
        return 1 / (1 / (h_in * Ain) + 1 / (Ac * kground / th) + 1 / (h_air * Ag))
    u1 = g(A1 + Ly1_1 * level, A1 + Lx1_1 * level + Ly1_1 * level, A1 + Ly1_1 * level)
    A2in = A2 + Ly2_1 * level + Ly2_2 * level + Lx2_1 * level
    u2 = g(A2in, Lx2_1 * Ly2_1 + Lx2_1 * level + Ly2_1 * level, A2in)
    A3g = A3 + Lx3_1 * level + Ly3_1 * level
    u3 = g(A3g, A3g, A3g)
    return UA_air + u1 + u2 + u3


def C_of(level):
    return (A1 * level + A2 * level + A3 * 0.9 * level) * rho_w * cp_w


def responses(Q, h_air, level):
    UA = UA_of(h_air, level)
    Tmax = Tair + Q / UA
    tau = C_of(level) / UA / 3600.0   # h
    return Tmax, tau


# ============================================================
# LHS 設計 (フィット点中心)
# ============================================================
def lhs(n, ranges, seed=1):
    rng = np.random.default_rng(seed)
    d = len(ranges)
    out = np.zeros((n, d))
    for j, (lo, hi) in enumerate(ranges):
        perm = rng.permutation(n)
        out[:, j] = lo + ((perm + rng.random(n)) / n) * (hi - lo)
    return out


def pareto_front(P):
    n = len(P)
    dom = np.zeros(n, bool)
    for i in range(n):
        for j in range(n):
            if i != j and (P[j] <= P[i]).all() and (P[j] < P[i]).any():
                dom[i] = True
                break
    return ~dom


# ============================================================
# 自前 pairplot (seaborn風): 対角=ヒスト, 下三角=散布(パレート強調)
# ============================================================
def pairplot(data, labels, pareto, path):
    m = len(labels)
    fig, axes = plt.subplots(m, m, figsize=(3.4 * m, 3.4 * m))
    for i in range(m):
        for j in range(m):
            ax = axes[i, j]
            if i == j:
                ax.hist(data[:, i], bins=25, color="tab:blue", alpha=0.7)
            else:
                ax.scatter(data[~pareto, j], data[~pareto, i], s=16, alpha=0.35,
                           color="tab:blue", label="全ケース")
                ax.scatter(data[pareto, j], data[pareto, i], s=55, alpha=0.95,
                           color="tab:red", edgecolor="k", linewidth=0.5,
                           label="パレート最適（実験目標に最も近い）")
            if i == m - 1:
                ax.set_xlabel(labels[j], fontsize=16)
            if j == 0:
                ax.set_ylabel(labels[i], fontsize=16)
            ax.tick_params(labelsize=12)
    axes[0, m - 1].legend(fontsize=14, loc="upper right", markerscale=1.4)
    fig.suptitle("パラメータスタディ pairplot（赤=パレート最適点, 目的: τ・Tmax を実験に一致）",
                 fontsize=20, y=1.005)
    plt.tight_layout()
    plt.savefig(path, dpi=140, bbox_inches="tight")
    plt.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300)
    args = ap.parse_args()

    ranges = [(550.0, 720.0),   # Q  (fit 610)
              (5.0, 12.0),      # heatCeffToAir (fit 8.79)
              (0.05, 0.16)]     # level_start   (fit 0.0755)
    X = lhs(args.n, ranges)
    Q, h_air, level = X[:, 0], X[:, 1], X[:, 2]
    Tmax = np.empty(args.n)
    tau = np.empty(args.n)
    for k in range(args.n):
        Tmax[k], tau[k] = responses(Q[k], h_air[k], level[k])

    # 目的: 実験の (Tmax, τ) に近づける (両方最小化)
    err_T = np.abs(Tmax - Tmax_exp)
    err_t = np.abs(tau - tau_exp)
    pf = pareto_front(np.column_stack([err_T, err_t]))

    print("実験目標 : Tmax=%.2f degC,  tau=%.2f h" % (Tmax_exp, tau_exp))
    print("試行数   : %d,  パレート点: %d" % (args.n, pf.sum()))
    best = np.argmin(err_T + err_t)
    print("最良近似 : Q=%.0f  heatCeffToAir=%.2f  level=%.4f  -> Tmax=%.2f tau=%.2fh"
          % (Q[best], h_air[best], level[best], Tmax[best], tau[best]))

    # ---- pairplot ----
    data = np.column_stack([Q, h_air, level, Tmax, tau])
    labels = ["Q [W]", "heatCeffToAir", "level [m]", "Tmax [degC]", "tau [h]"]
    pairplot(data, labels, pf, os.path.join(IMG2, "pairplot.png"))
    print("saved:", os.path.join(IMG2, "pairplot.png"))

    # ---- pareto (目的空間) ----
    fig, ax = plt.subplots(figsize=(7.5, 6))
    sc = ax.scatter(tau, Tmax, c=err_T + err_t, cmap="viridis_r", s=20, alpha=0.8)
    ax.scatter(tau[pf], Tmax[pf], s=45, facecolor="none", edgecolor="red",
               linewidth=1.5, label="パレート最適")
    ax.plot(tau_exp, Tmax_exp, "r*", markersize=20, label="実験目標")
    ax.set_xlabel("時定数 τ [h]", fontsize=12)
    ax.set_ylabel("最大温度 Tmax [degC]", fontsize=12)
    ax.set_title("目的空間 τ–Tmax（色=実験への総誤差, 星=実験目標）", fontsize=12)
    plt.colorbar(sc, label="|ΔTmax|+|Δτ|")
    ax.grid(True, alpha=0.4)
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(IMG2, "pareto.png"), dpi=140, bbox_inches="tight")
    plt.close()
    print("saved:", os.path.join(IMG2, "pareto.png"))


if __name__ == "__main__":
    main()
