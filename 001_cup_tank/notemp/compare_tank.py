# -*- coding: utf-8 -*-
"""cup集中定数版タンクモデル(OM) と eva5 実測(温度管理なし) を比較。

  omc run_tank.mos  ->  TankHotWater_cyclone_cup_res.csv を作った後:
  python compare_tank.py   -> TankHotWater_cyclone_cup_compare.png

実測: eva5_tank_data.csv  水温 4-16/4-17/4-18/4-19, 外気 4-9。
OM: y_sim_T(=tank.medium.T) を水温4本の平均に対して RMSE 評価。
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

# --- 実測 (eva5) ---
with open(os.path.join(HERE, "data", "eva5_tank_data.csv"), encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))
te = np.array([float(r["time_s"]) for r in rows])
water = ["4-16", "4-17", "4-18", "4-19"]
exp = {s: np.array([float(r[s]) for r in rows]) for s in water + ["4-9"]}
exp_mean = np.mean([exp[s] for s in water], axis=0)

# --- OM 結果 ---
resf = os.path.join(HERE, "TankHotWater_cyclone_cup_res.csv")
with open(resf, encoding="utf-8") as f:
    rr = list(csv.reader(f))
head = rr[0]
arr = np.array([[float(x) for x in row] for row in rr[1:] if row])
ts = arr[:, head.index("time")]
Tsim = arr[:, head.index("y_sim_T")]

rmse = float(np.sqrt(np.mean((np.interp(te, ts, Tsim) - exp_mean) ** 2)))

# --- プロット ---
fig, ax = plt.subplots(figsize=(10, 5.6))
sc = {"4-16": "tab:blue", "4-17": "tab:orange", "4-18": "tab:green", "4-19": "tab:red"}
for s in water:
    ax.plot(te, exp[s], "o", color=sc[s], markersize=4, alpha=0.55, label="実測 %s" % s)
ax.plot(te, exp_mean, "s-", color="black", markersize=5, linewidth=1.5, label="実測 水温平均")
ax.plot(te, exp["4-9"], ":", color="tab:cyan", linewidth=1.6, label="実測 4-9 = 外気温(≈24.5℃)")
ax.plot(ts, Tsim, "-", color="red", linewidth=2.6,
        label="OM TankHotWater_cyclone_cup (y_sim_T)  RMSE=%.2f℃" % rmse)

ax.set_xlabel("時間 [s]", fontsize=12)
ax.set_ylabel("温度 [℃]", fontsize=12)
ax.set_xlim(0, 100000)
ax.set_ylim(22, 40)
ax.grid(True, color="lightgray", linewidth=0.8)
ax.set_axisbelow(True)
ax.set_title("タンク(cup集中定数版, Q=610W, 蓋あり) OM vs eva5実測(温度管理なし)", fontsize=12)
ax.legend(fontsize=9, ncol=2, loc="lower right")
plt.tight_layout()
out = os.path.join(HERE, "TankHotWater_cyclone_cup_compare.png")
plt.savefig(out, dpi=150, bbox_inches="tight")

print("OM y_sim_T : t=0 %.2f℃ -> t=100000 %.2f℃" % (Tsim[0], Tsim[-1]))
print("実測 水温平均: t=0 %.2f℃ -> 最終 %.2f℃  (外気4-9≈%.1f℃)" % (exp_mean[0], exp_mean[-1], exp["4-9"].mean()))
print("水温平均に対する RMSE = %.2f ℃" % rmse)
print("saved:", out)
