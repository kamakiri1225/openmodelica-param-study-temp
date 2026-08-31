# -*- coding: utf-8 -*-
"""2つのモデルの比較（温度管理なし NoTemp モデル vs 温度管理あり cyclononly モデル）。

事前に両モデルを OM で回して以下を用意:
  OM/_cmp_notemp.csv    ... ana003_Tank3blocks_cyclononly_NoTemp
  OM/_cmp_withtemp.csv  ... ana001_Tank3blocks_004_test (cyclononly, PID)
出力: docs/img/002/compare_models.png
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
ROOT = os.path.dirname(HERE)
H = 3600.0


def tank_mean_C(csv_path):
    rows = list(csv.reader(open(csv_path)))
    hdr = rows[0]
    data = np.array([[float(x) for x in r] for r in rows[1:]])
    t = data[:, hdr.index("time")]
    cols = [i for i, c in enumerate(hdr) if c.endswith("medium.T")]
    K = data[:, cols]
    return t, K.mean(axis=1) - 273.15


# 実測 なし (eva5, 2026-07-09): 4センサ平均が 37.7℃ まで上昇
eva5_t = np.array([0, 5263, 10526, 15789, 21053, 26316, 31579, 36842, 42105, 47368,
                   52632, 57895, 63158, 68421, 73684, 78947, 84211, 89474, 94737, 100000], float)
eva5 = np.array([
    [23.8, 27.8, 29.8, 31.2, 32.4, 33.4, 34.3, 35.0, 35.5, 36.0, 36.4, 36.7, 37.0, 37.2, 37.35, 37.40, 37.50, 37.60, 37.65, 37.70],
    [24.0, 28.0, 30.1, 31.5, 32.7, 33.7, 34.5, 35.2, 35.8, 36.2, 36.6, 36.9, 37.15, 37.35, 37.50, 37.55, 37.60, 37.70, 37.75, 37.80],
    [24.2, 28.4, 30.5, 31.9, 33.0, 34.0, 34.8, 35.5, 36.0, 36.4, 36.8, 37.1, 37.35, 37.55, 37.70, 37.65, 37.75, 37.80, 37.85, 37.90],
    [23.7, 27.6, 29.6, 31.0, 32.2, 33.2, 34.1, 34.8, 35.4, 35.8, 36.2, 36.5, 36.8, 37.0, 37.15, 37.20, 37.30, 37.40, 37.45, 37.50]]).mean(0)
# 実測 あり (eva4, 2026-07-08): 温度管理で 24℃前後に保持
eva4_t = np.array([0, 1326, 2653, 3979, 5305, 6632, 7958, 9284, 10611, 11937,
                   13263, 14589, 15916, 17242, 18568, 19895, 21221, 22547, 23874, 25200], float)
eva4 = np.array([
    [23.73, 23.84, 23.86, 23.87, 24.21, 24.10, 24.13, 24.19, 24.22, 24.26, 24.28, 24.29, 24.32, 24.35, 24.38, 24.37, 24.36, 24.40, 24.41, 24.44],
    [24.02, 24.13, 24.06, 24.11, 24.18, 24.15, 24.15, 24.20, 24.23, 24.26, 24.29, 24.30, 24.33, 24.36, 24.39, 24.38, 24.36, 24.40, 24.42, 24.45],
    [24.00, 24.14, 24.05, 24.10, 24.15, 24.16, 24.16, 24.21, 24.23, 24.26, 24.29, 24.30, 24.34, 24.37, 24.40, 24.38, 24.36, 24.41, 24.42, 24.44],
    [23.42, 23.59, 23.69, 23.78, 24.05, 24.15, 24.15, 24.19, 24.21, 24.25, 24.27, 24.29, 24.31, 24.34, 24.37, 24.36, 24.30, 24.34, 24.35, 24.36]]).mean(0)

fig, ax = plt.subplots(figsize=(10, 6))
# 温度管理なし: フィット後のOMがあればそれを、無ければ基準を使う
no_fit = os.path.join(ROOT, "OM", "_cmp_notemp_fit.csv")
no = no_fit if os.path.exists(no_fit) else os.path.join(ROOT, "OM", "_cmp_notemp.csv")
yes = os.path.join(ROOT, "OM", "_cmp_withtemp.csv")
tag = "（フィット後）" if os.path.exists(no_fit) else ""
# 温度管理なし: OM(赤線) と 実測eva5(赤四角)
if os.path.exists(no):
    t, T = tank_mean_C(no)
    ax.plot(t / H, T, "-", color="tab:red", linewidth=2.4,
            label="OM 温度管理なし%s  終値%.1f℃" % (tag, T[-1]))
ax.plot(eva5_t / H, eva5, "s", color="darkred", markersize=6, label="実測 温度管理なし (eva5)")
# 温度管理あり: OM(青線) と 実測eva4(青三角)
if os.path.exists(yes):
    t, T = tank_mean_C(yes)
    ax.plot(t / H, T, "-", color="tab:blue", linewidth=2.4,
            label="OM 温度管理あり  終値%.1f℃" % T[-1])
ax.plot(eva4_t / H, eva4, "^", color="navy", markersize=6, label="実測 温度管理あり (eva4)")
ax.set_xlim(0, 40)
ax.set_xlabel("Time [h]", fontsize=13)
ax.set_ylabel("水温 (tank1/2/3 平均) [degC]", fontsize=13)
ax.set_title("温度管理あり／なし の比較（実機OM ＋ 実測 eva4=あり / eva5=なし）", fontsize=13)
ax.grid(True, alpha=0.4)
ax.legend(fontsize=12)
plt.tight_layout()
out = os.path.join(HERE, "img", "002", "compare_models.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print("saved:", out)
