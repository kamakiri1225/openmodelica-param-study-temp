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


fig, ax = plt.subplots(figsize=(10, 6))
no = os.path.join(ROOT, "OM", "_cmp_notemp.csv")
yes = os.path.join(ROOT, "OM", "_cmp_withtemp.csv")
if os.path.exists(no):
    t, T = tank_mean_C(no)
    ax.plot(t / H, T, "-", color="tab:red", linewidth=2.4,
            label="温度管理なし (NoTempモデル)  終値%.1f℃" % T[-1])
if os.path.exists(yes):
    t, T = tank_mean_C(yes)
    ax.plot(t / H, T, "-", color="tab:blue", linewidth=2.4,
            label="温度管理あり (cyclononly+PIDモデル)  終値%.1f℃" % T[-1])
ax.set_xlabel("Time [h]", fontsize=13)
ax.set_ylabel("水温 (tank1/2/3 平均) [degC]", fontsize=13)
ax.set_title("温度管理あり／なし モデル比較（実機OM, 各モデルのデフォルト設定）", fontsize=13)
ax.grid(True, alpha=0.4)
ax.legend(fontsize=12)
plt.tight_layout()
out = os.path.join(HERE, "img", "002", "compare_models.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print("saved:", out)
