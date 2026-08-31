# -*- coding: utf-8 -*-
"""
タンク水温モデルのパラメータスタディ支援ツール。

サブコマンド:
  gen     : ラテン超方格(LHS)で設計因子の実験計画(doe.csv)を生成し、
            OpenModelica 用の -override 文字列も出力する。
  pareto  : OM 実行後の結果表(results.csv)を読み、目的関数を計算して
            pairplot とパレート図を描き、パレート最適解を表示する。

使い方:
  python param_study.py gen   --n 60
  python param_study.py pareto --csv results.csv

results.csv に必要な列:
  case, Q, h_air, h_in, kground, level, T_final, tau, rmse
  (先頭6列= doe.csv、後半3列= 各OM実行から取得した応答)

詳細は docs/parameter_study_plan.md を参照。
"""

import sys
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# 設計因子とその範囲 (基準値は元モデルの値)
#   Q       : サイクロン投入熱量 [W]   (要: モデルで Q_cyclone をパラメータ化)
#   h_air   : 外気側熱伝達率     [W/m2K] = heatCeffToAir
#   h_in    : タンク内側熱伝達率 [W/m2K] = heatCefftTank2in
#   kground : 地面熱伝導         [W/mK]  = kground
#   level   : 初期水位           [m]     = level_start
# ============================================================
FACTORS = {
    "Q":       (500.0, 750.0, 610.0),
    "h_air":   (5.0,   20.0,  10.0),
    "h_in":    (5.0,   20.0,  10.0),
    "kground": (20.0,  160.0, 80.0),
    "level":   (0.090, 0.160, 0.128),
}

# 実験の目標値 (eva5: 2026-07-09)
EXP_TFINAL = 37.7   # degC : 4センサ平均の飽和温度
EXP_TAU = 23000.0   # s    : 時定数(63.2%到達)の目安


def cmd_gen(args):
    """LHS で doe.csv を生成する。"""
    rng = np.random.default_rng(args.seed)
    n = args.n
    keys = list(FACTORS.keys())
    d = len(keys)

    # ラテン超方格サンプリング
    lhs = np.zeros((n, d))
    for j in range(d):
        perm = rng.permutation(n)
        lhs[:, j] = (perm + rng.random(n)) / n
    # 各因子の範囲へスケール
    design = np.zeros((n, d))
    for j, k in enumerate(keys):
        lo, hi, _ = FACTORS[k]
        design[:, j] = lo + lhs[:, j] * (hi - lo)

    df = pd.DataFrame(design, columns=keys)
    df.insert(0, "case", np.arange(1, n + 1))
    df.to_csv("doe.csv", index=False)
    print(f"doe.csv を出力しました (N={n})")

    # OM 用の -override 文字列例 (先頭3ケース)
    print("\n-override 例 (simulate の simflags に渡す):")
    for _, row in df.head(3).iterrows():
        ov = (f"Q_cyclone={row.Q:.1f},heatCeffToAir={row.h_air:.3f},"
              f"heatCefftTank2in={row.h_in:.3f},kground={row.kground:.2f},"
              f"level_start={row.level:.4f}")
        print(f"  case {int(row.case):>3}:  -override {ov}")


def pareto_front(points):
    """最小化 2 目的のパレート前線 index を返す。points shape=(n,2)。"""
    n = len(points)
    dominated = np.zeros(n, dtype=bool)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            # j が i を支配 (両目的で j<=i, 片方で j<i)
            if (points[j] <= points[i]).all() and (points[j] < points[i]).any():
                dominated[i] = True
                break
    return np.where(~dominated)[0]


def cmd_pareto(args):
    """results.csv から目的関数・pairplot・パレート図を作る。"""
    df = pd.read_csv(args.csv)
    df["err_Tfinal"] = (df["T_final"] - EXP_TFINAL).abs()
    df["err_tau"] = (df["tau"] - EXP_TAU).abs()

    pts = df[["err_Tfinal", "err_tau"]].to_numpy()
    front = pareto_front(pts)
    df["pareto"] = False
    df.loc[df.index[front], "pareto"] = True

    print("=== パレート最適解 (err_Tfinal, err_tau 最小化) ===")
    cols = ["case", "Q", "h_air", "h_in", "kground", "level",
            "T_final", "tau", "rmse", "err_Tfinal", "err_tau"]
    print(df.loc[df["pareto"], cols].sort_values("rmse").to_string(index=False))

    # --- pairplot (seaborn があれば seaborn、無ければ pandas scatter_matrix) ---
    plot_cols = ["Q", "h_air", "h_in", "kground", "level", "rmse"]
    try:
        import seaborn as sns
        g = sns.pairplot(df[plot_cols + ["pareto"]], hue="pareto",
                         diag_kind="hist", corner=False,
                         plot_kws=dict(s=25, alpha=0.7))
        g.fig.suptitle("Parameter study pairplot (hue=Pareto)", y=1.02)
        g.savefig("pairplot.png", dpi=150, bbox_inches="tight")
        print("\npairplot.png を出力")
    except ModuleNotFoundError:
        print("\n[注意] seaborn 未導入のため pandas.scatter_matrix で代替します。")
        print("       綺麗な pairplot が必要なら: pip install seaborn")
        from pandas.plotting import scatter_matrix
        ax = scatter_matrix(df[plot_cols], figsize=(11, 11),
                            diagonal="hist", alpha=0.7, s=20)
        plt.suptitle("Parameter study scatter matrix")
        plt.savefig("pairplot.png", dpi=150, bbox_inches="tight")
        print("pairplot.png を出力")

    # --- 目的空間のパレート図 ---
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(df["err_Tfinal"], df["err_tau"], c="tab:blue",
               s=25, alpha=0.5, label="all cases")
    pf = df.loc[df["pareto"]].sort_values("err_Tfinal")
    ax.plot(pf["err_Tfinal"], pf["err_tau"], "-o", color="tab:red",
            markersize=7, label="Pareto front")
    for _, r in pf.iterrows():
        ax.annotate(f"#{int(r.case)}", (r.err_Tfinal, r.err_tau),
                    fontsize=8, xytext=(3, 3), textcoords="offset points")
    ax.set_xlabel("|T_final - exp| [degC]", fontsize=12)
    ax.set_ylabel("|tau - exp| [s]", fontsize=12)
    ax.set_title("Pareto front (multi-objective)")
    ax.grid(True, alpha=0.4)
    ax.legend()
    plt.tight_layout()
    plt.savefig("pareto.png", dpi=150, bbox_inches="tight")
    print("pareto.png を出力")
    plt.show()


def main():
    p = argparse.ArgumentParser(description="タンク水温モデル パラメータスタディ支援")
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen", help="LHS で doe.csv を生成")
    g.add_argument("--n", type=int, default=60)
    g.add_argument("--seed", type=int, default=0)
    g.set_defaults(func=cmd_gen)
    pa = sub.add_parser("pareto", help="results.csv からパレート解析")
    pa.add_argument("--csv", default="results.csv")
    pa.set_defaults(func=cmd_pareto)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
