# -*- coding: utf-8 -*-
"""桶水加熱 CupHotWater_15W_001 の OM 結果と実験データを比較して画像化。

手順:
  1) このフォルダで OM を実行して結果CSVを作る:
       omc.exe run_cup.mos           (-> CupHotWater_15W_001_res.csv)
  2) python plot_cup_compare.py      (-> CupHotWater_15W_compare.png)
"""
import os
import glob
import csv
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

# 実験データ
exp = []
with open(os.path.join(HERE, "water_heating_temperature_measurement.csv"), encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        exp.append((float(row["time_s"]), float(row["temperature_C"])))
exp = np.array(exp)

# OM 結果
res = os.path.join(HERE, "CupHotWater_15W_001_res.csv")
rows = list(csv.reader(open(res)))
hdr = rows[0]
data = np.array([[float(x) for x in r] for r in rows[1:]])
t = data[:, hdr.index("time")]
sim = data[:, hdr.index("y_sim_T")]

rmse = float(np.sqrt(np.mean((np.interp(exp[:, 0], t, sim) - exp[:, 1]) ** 2)))

fig, ax = plt.subplots(figsize=(9, 5.5))
ax.plot(exp[:, 0] / 60, exp[:, 1], "ks", markersize=7, label="実験")
ax.plot(t / 60, sim, "-", color="tab:red", linewidth=2.2, label="OM シミュレーション")
ax.set_xlabel("時間 [min]", fontsize=13)
ax.set_ylabel("桶の水温 [degC]", fontsize=13)
ax.set_title("桶の水加熱（15W, 160×90mm, 水20mm）OM vs 実験  RMSE=%.2f℃" % rmse, fontsize=13)
ax.grid(True, alpha=0.4)
ax.legend(fontsize=12)
plt.tight_layout()
out = os.path.join(HERE, "CupHotWater_15W_compare.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print("RMSE=%.2f degC  ->  %s" % (rmse, out))
