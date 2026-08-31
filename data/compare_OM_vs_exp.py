# -*- coding: utf-8 -*-
"""
OpenModelica のタンク水温シミュレーション結果と、実験データ(eva5)を比較する。

前提のワークフロー:
  1) Windows 側で OM/run_sim.mos を実行して CSV を出力
       "C:\\Program Files\\OpenModelica1.26.3-64bit\\bin\\omc.exe" run_sim.mos
     -> ana002_Tank3blocks_002_machineAreaTankMist_NoTemp_res.csv が生成される
  2) この CSV を下の OM_CSV に指定して本スクリプトを実行

使い方:
  python compare_OM_vs_exp.py [OM結果CSVのパス]
  引数を省略した場合は既定パス(../OM/..._res.csv)を探す。
"""

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# 実験データ (eva5.py と同一。2026-07-09 10:00 起点)
# ============================================================
time_s = np.array([
    0, 5263, 10526, 15789, 21053,
    26316, 31579, 36842, 42105, 47368,
    52632, 57895, 63158, 68421, 73684,
    78947, 84211, 89474, 94737, 100000
], dtype=float)

exp = {
    "4-16": [23.8, 27.8, 29.8, 31.2, 32.4, 33.4, 34.3, 35.0, 35.5, 36.0,
             36.4, 36.7, 37.0, 37.2, 37.35, 37.40, 37.50, 37.60, 37.65, 37.70],
    "4-17": [24.0, 28.0, 30.1, 31.5, 32.7, 33.7, 34.5, 35.2, 35.8, 36.2,
             36.6, 36.9, 37.15, 37.35, 37.50, 37.55, 37.60, 37.70, 37.75, 37.80],
    "4-18": [24.2, 28.4, 30.5, 31.9, 33.0, 34.0, 34.8, 35.5, 36.0, 36.4,
             36.8, 37.1, 37.35, 37.55, 37.70, 37.65, 37.75, 37.80, 37.85, 37.90],
    "4-19": [23.7, 27.6, 29.6, 31.0, 32.2, 33.2, 34.1, 34.8, 35.4, 35.8,
             36.2, 36.5, 36.8, 37.0, 37.15, 37.20, 37.30, 37.40, 37.45, 37.50],
}
# 外気温度(参考): 4-9 ~ 24.5 degC 一定 (モデルの Tair_deg=24.5 に対応)
exp = {k: np.array(v, dtype=float) for k, v in exp.items()}

# 4センサの平均を「代表水温」として比較の基準にする
exp_mean = np.mean(np.vstack(list(exp.values())), axis=0)

# ============================================================
# OM 結果 CSV の読み込み
# ============================================================
DEFAULT_OM_CSV = os.path.join(
    os.path.dirname(__file__), "..", "OM", "temp_off",
    "ana003_Tank3blocks_cyclononly_NoTemp_res.csv"
)

om_csv = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OM_CSV

if not os.path.exists(om_csv):
    print("=" * 60)
    print("OM 結果 CSV が見つかりません:")
    print("  ", os.path.abspath(om_csv))
    print()
    print("先に Windows 側で OM/run_sim.mos を実行して CSV を生成してください:")
    print('  "C:\\Program Files\\OpenModelica1.26.3-64bit\\bin\\omc.exe" run_sim.mos')
    print("=" * 60)
    sys.exit(1)

om = pd.read_csv(om_csv)

# time 列とタンク温度列を自動判定
time_col = "time" if "time" in om.columns else om.columns[0]
temp_cols = [c for c in om.columns if c.endswith(".T") or c.endswith("].T")]
if not temp_cols:
    # フォールバック: time 以外の数値列すべて
    temp_cols = [c for c in om.columns if c != time_col]

om_t = om[time_col].to_numpy(dtype=float)


def to_celsius(series):
    """ケルビン(平均>100)なら摂氏へ変換。"""
    arr = np.asarray(series, dtype=float)
    return arr - 273.15 if np.nanmean(arr) > 100 else arr


# ============================================================
# 実験時刻へ内挿して誤差指標を計算
# ============================================================
print("OM 結果 CSV        :", os.path.abspath(om_csv))
print("time 列            :", time_col)
print("タンク温度列       :", temp_cols)
print()

results = {}
for c in temp_cols:
    om_c = to_celsius(om[c])
    om_interp = np.interp(time_s, om_t, om_c)  # 実験時刻に合わせる
    resid = om_interp - exp_mean
    rmse = float(np.sqrt(np.mean(resid ** 2)))
    mae = float(np.mean(np.abs(resid)))
    maxe = float(np.max(np.abs(resid)))
    results[c] = dict(rmse=rmse, mae=mae, maxe=maxe, interp=om_interp)

print("実験4センサ平均を基準にした誤差 [degC]")
print("-" * 60)
print(f"{'変数':40s} {'RMSE':>6s} {'MAE':>6s} {'MAXerr':>7s}")
for c, r in results.items():
    print(f"{c:40s} {r['rmse']:6.2f} {r['mae']:6.2f} {r['maxe']:7.2f}")
print("-" * 60)

best = min(results, key=lambda c: results[c]["rmse"])
best_rmse = results[best]["rmse"]
if best_rmse < 1.0:
    verdict = "良好に一致 (RMSE < 1.0 degC)"
elif best_rmse < 2.0:
    verdict = "おおむね一致 (RMSE < 2.0 degC)"
else:
    verdict = "乖離あり (RMSE >= 2.0 degC) — パラメータ再調整を推奨"
print(f"最良一致: {best}  RMSE={best_rmse:.2f} degC -> {verdict}")

# ============================================================
# グラフ (実験 = マーカー, OM = 実線)
# ============================================================
H = 3600.0  # s -> h
fig, ax = plt.subplots(figsize=(11, 6))

for k, v in exp.items():
    ax.plot(time_s / H, v, marker="o", markersize=4, linewidth=1.0,
            linestyle="--", alpha=0.6, label=f"exp {k}")
ax.plot(time_s / H, exp_mean, color="black", marker="s", markersize=4,
        linewidth=2.0, label="exp mean (基準)")

for c in temp_cols:
    ax.plot(om_t / H, to_celsius(om[c]), linewidth=2.0, label=f"OM {c}")

ax.set_xlabel("Time [h]", fontsize=13)
ax.set_ylabel("Temperature [degC]", fontsize=13)
ax.set_xlim(0, om_t.max() / H if len(om_t) else 100000 / H)
ax.grid(True, which="major", linestyle="-", linewidth=0.6, alpha=0.5)
ax.minorticks_on()
ax.grid(True, which="minor", linestyle=":", linewidth=0.4, alpha=0.3)
ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=9)
ax.set_title(f"OM vs Experiment  (best {best}: RMSE={best_rmse:.2f} degC)")

plt.tight_layout()
out_png = os.path.join(os.path.dirname(__file__), "compare_OM_vs_exp.png")
plt.savefig(out_png, dpi=200, bbox_inches="tight")
print("\nグラフを保存:", os.path.abspath(out_png))
plt.show()
