# -*- coding: utf-8 -*-
"""変更後の CupHotWater_15W_001.mo(OM結果) と cup_data_mz.csv(実験) を比較。

  omc で _work/CupHotWater_15W_001_res.csv を作った後:
  python compare_cup_mz.py   -> CupHotWater_15W_mz_compare.png

実験CSVは6センサ。U4-3/U4-4 はほぼ一定(≒外気/参照)なので、
水温センサ U4-1, U4-2, U1-2, U1-4 を実測とみなし、その平均も重ねる。
"""
import os
import csv
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

# --- 実験データ (cup_data_mz.csv) ---
expf = os.path.join(HERE, "data", "cup_data_mz.csv")
with open(expf, encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))
SHIFT = 7 * 60   # 実験はOMより420s(7分)遅れ -> -420sシフトしてOM(加熱開始t=0)に合わせる
te = np.array([float(r["time_s"]) for r in rows]) - SHIFT
sensors = ["U4-1", "U4-2", "U4-3", "U4-4", "U1-2", "U1-4"]
exp = {s: np.array([float(r[s]) for r in rows]) for s in sensors}
water_sensors = ["U4-1", "U4-2", "U1-2", "U1-4"]     # 昇温するセンサ=水温
# 実測↔モデル対応: U4-1=水温(cup.medium.T), U4-2=桶壁(thermalConductor2.port_b), U4-3=外気温
REF_WATER = "U4-1"    # 水温基準 <-> OM y_sim_T
REF_WALL = "U4-2"     # 桶壁基準 <-> OM y_wall_T
AMB = "U4-3"          # 外気温(参照)
exp_water = exp[REF_WATER]
exp_wall = exp[REF_WALL]

# --- OM 結果 ---
resf = os.path.join(HERE, "CupHotWater_15W_company_res.csv")
with open(resf, encoding="utf-8") as f:
    rr = list(csv.reader(f))
head = rr[0]
arr = np.array([[float(x) for x in row] for row in rr[1:] if row])
ts = arr[:, head.index("time")]
Tsim = arr[:, head.index("y_sim_T")]     # 水温
Twall = arr[:, head.index("y_wall_T")]   # 桶壁

# OM を実験時刻へ内挿して RMSE（シフト後 t>=0 の点のみ）
mask = te >= 0
rmse_w = float(np.sqrt(np.mean((np.interp(te, ts, Tsim)[mask] - exp_water[mask]) ** 2)))
rmse_wall = float(np.sqrt(np.mean((np.interp(te, ts, Twall)[mask] - exp_wall[mask]) ** 2)))

# --- プロット ---
# シフトで t<0 になった点(画面外の初期27.5℃)は描画から除外し、
# 実測を加熱開始(≈25℃, U4-3/ディップ)から始めて OM初期25.0℃と揃える。
pm = te >= 0
fig, ax = plt.subplots(figsize=(9.5, 5.6))
# 背景(その他センサ)
for s in ["U1-2", "U1-4", "U4-4"]:
    ax.plot(te[pm], exp[s][pm], "-", color="0.75", linewidth=0.9, alpha=0.6,
            label="実測 %s (参考)" % s)
# 外気温 U4-3
ax.plot(te[pm], exp[AMB][pm], ":", color="tab:cyan", linewidth=1.6,
        label="実測 %s = 外気温(≈25℃)" % AMB)
# ペア1: 水温
ax.plot(te[pm], exp_water[pm], "s", color="black", markersize=6,
        label="実測 %s = 水温" % REF_WATER)
ax.plot(ts, Tsim, "-", color="red", linewidth=2.6,
        label="OM y_sim_T = 水温  RMSE=%.2f℃" % rmse_w)
# ペア2: 桶壁
ax.plot(te[pm], exp_wall[pm], "o", color="tab:green", markersize=5,
        label="実測 %s = 桶壁" % REF_WALL)
ax.plot(ts, Twall, "--", color="tab:blue", linewidth=2.2,
        label="OM y_wall_T = 桶壁  RMSE=%.2f℃" % rmse_wall)

ax.set_xlabel("時間 [s]（実測は −%ds シフト済）" % SHIFT, fontsize=12)
ax.set_ylabel("温度 [℃]", fontsize=12)
ax.set_xlim(0, 9000)
ax.set_ylim(20, 50)
ax.grid(True, color="lightgray", linewidth=0.8)
ax.set_axisbelow(True)
ax.set_title("桶15W加熱 会社版: OM vs 実測（水温U4-1・桶壁U4-2, 外気U4-3, 実測−%ds）" % SHIFT, fontsize=12)
ax.legend(fontsize=8, ncol=2, loc="lower right")
plt.tight_layout()
out = os.path.join(HERE, "CupHotWater_15W_company_compare.png")
plt.savefig(out, dpi=150, bbox_inches="tight")

# --- 数値サマリ ---
print("時間シフト: 実測 -%ds (OM加熱開始 t=0 に整合)" % SHIFT)
print("水温 : OM y_sim_T  t0=%.1f→%.1f℃ / 実測%s 最終%.1f℃  RMSE=%.2f℃" %
      (Tsim[0], Tsim[-1], REF_WATER, exp_water[-1], rmse_w))
print("桶壁 : OM y_wall_T t0=%.1f→%.1f℃ / 実測%s 最終%.1f℃  RMSE=%.2f℃" %
      (Twall[0], Twall[-1], REF_WALL, exp_wall[-1], rmse_wall))
print("外気 : 実測%s ≈ %.1f℃ (=Tamb)" % (AMB, exp[AMB].mean()))
print("saved:", out)
