# -*- coding: utf-8 -*-
"""温度管理ありタンク(OM, 基準+制御) と eva4 実測(温度管理あり) を比較。

  omc run_tank_ctrl.mos  ->  TankHotWater_cyclone_cup_TempCtrl_res.csv を作った後:
  python compare_tank_ctrl.py   -> TankHotWater_cyclone_cup_TempCtrl_compare.png

実測 eva4: 4-16/4-17/4-18/4-19（水温, 約24℃保持, 0..25200s, 外気センサなし）。
OM: y_sim_T(=tank.medium.T) を水温4本平均に対して RMSE 評価。冷却量 y_cool[W] も併記。
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

# --- 実測 (eva4, 温度管理あり) ---
with open(os.path.join(HERE, "data", "eva4_tank_data.csv"), encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))
te = np.array([float(r["time_s"]) for r in rows])
water = ["4-16", "4-17", "4-18", "4-19"]
exp = {s: np.array([float(r[s]) for r in rows]) for s in water}
exp_mean = np.mean([exp[s] for s in water], axis=0)

# --- OM 結果 ---
resf = os.path.join(HERE, "TankHotWater_cyclone_cup_TempCtrl_res.csv")
with open(resf, encoding="utf-8") as f:
    rr = list(csv.reader(f))
head = rr[0]
arr = np.array([[float(x) for x in row] for row in rr[1:] if row])
ts = arr[:, head.index("time")]
Tsim = arr[:, head.index("y_sim_T")]
Qcool = arr[:, head.index("y_cool")]

rmse = float(np.sqrt(np.mean((np.interp(te, ts, Tsim) - exp_mean) ** 2)))

# --- プロット (左軸=温度, 右軸=冷却量) ---
fig, ax = plt.subplots(figsize=(10, 5.6))
sc = {"4-16": "tab:blue", "4-17": "tab:orange", "4-18": "tab:green", "4-19": "tab:red"}
for s in water:
    ax.plot(te, exp[s], "o", color=sc[s], markersize=4, alpha=0.55, label="実測 %s" % s)
ax.plot(te, exp_mean, "s-", color="black", markersize=5, linewidth=1.5, label="実測 水温平均")
ax.plot(ts, Tsim, "-", color="red", linewidth=2.6,
        label="OM 管理あり (y_sim_T)  RMSE=%.2f℃" % rmse)
ax.axhline(24.5, color="gray", ls="--", linewidth=1.0, label="目標=外気 24.5℃")
ax.set_xlabel("時間 [s]", fontsize=12)
ax.set_ylabel("温度 [℃]", fontsize=12)
ax.set_xlim(0, 25200)
ax.set_ylim(22, 30)
ax.grid(True, color="lightgray", linewidth=0.8)
ax.set_axisbelow(True)

ax2 = ax.twinx()
ax2.plot(ts, Qcool, "-", color="tab:purple", linewidth=1.6, alpha=0.7, label="OM 冷却量 [W]")
ax2.set_ylabel("冷却量 [W]", color="tab:purple", fontsize=12)
ax2.tick_params(axis="y", labelcolor="tab:purple")
ax2.set_ylim(0, 800)

ax.set_title("タンク 温度管理あり: OM(基準+制御) vs eva4実測（水温 約24℃保持）", fontsize=12)
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, fontsize=9, ncol=2, loc="upper right")
plt.tight_layout()
out = os.path.join(HERE, "TankHotWater_cyclone_cup_TempCtrl_compare.png")
plt.savefig(out, dpi=150, bbox_inches="tight")

print("OM 管理あり水温: t=0 %.2f℃ -> 最終 %.2f℃ (目標24.5℃保持)" % (Tsim[0], Tsim[-1]))
print("実測eva4 水温平均: t=0 %.2f℃ -> 最終 %.2f℃" % (exp_mean[0], exp_mean[-1]))
print("冷却量: 最終 %.0f W (=発熱610Wを除去)" % Qcool[-1])
print("水温平均に対する RMSE = %.2f ℃" % rmse)
print("saved:", out)
