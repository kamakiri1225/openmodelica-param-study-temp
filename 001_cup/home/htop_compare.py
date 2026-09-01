# -*- coding: utf-8 -*-
"""上面熱伝達率 h_top の影響（55=蒸発込み vs 10=対流のみ）を実験と比較。
事前に _build/htop_55.csv, _build/htop_10.csv を OM で作成しておく
（simulate(..., simflags="-override h_top=55" / "=10")）。
  python plot_htop_compare.py
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


def load(f):
    r = list(csv.reader(open(f)))
    h = r[0]
    d = np.array([[float(x) for x in row] for row in r[1:]])
    return d[:, h.index("time")], d[:, h.index("y_sim_T")]


exp = []
with open(os.path.join(HERE, "data", "water_heating_temperature_measurement.csv"), encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        exp.append((float(row["time_s"]), float(row["temperature_C"])))
exp = np.array(exp)

t55, y55 = load(os.path.join(HERE, "_build", "htop_55.csv"))
t10, y10 = load(os.path.join(HERE, "_build", "htop_10.csv"))


def rmse(t, y):
    return float(np.sqrt(np.mean((np.interp(exp[:, 0], t, y) - exp[:, 1]) ** 2)))


fig, ax = plt.subplots(figsize=(9.5, 5.8))
ax.plot(exp[:, 0] / 60, exp[:, 1], "ks", markersize=7, label="実験")
ax.plot(t55 / 60, y55, "-", color="tab:red", linewidth=2.4,
        label="OM h_top=55 (蒸発込み) 飽和%.0f℃ RMSE=%.2f" % (y55[-1], rmse(t55, y55)))
ax.plot(t10 / 60, y10, "-", color="tab:blue", linewidth=2.4,
        label="OM h_top=10 (対流のみ) 飽和%.0f℃ RMSE=%.2f" % (y10[-1], rmse(t10, y10)))
ax.set_xlabel("時間 [min]", fontsize=13)
ax.set_ylabel("桶の水温 [degC]", fontsize=13)
ax.set_title("上面熱伝達率 h_top の影響（15W, 160×90mm, 水20mm）", fontsize=13)
ax.grid(True, alpha=0.4)
ax.legend(fontsize=11, loc="lower right")
plt.tight_layout()
out = os.path.join(HERE, "CupHotWater_15W_home_htop_compare.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print("saved:", out)
