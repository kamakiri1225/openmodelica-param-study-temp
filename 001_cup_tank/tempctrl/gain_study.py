# -*- coding: utf-8 -*-
"""温度管理ゲイン ctrl_k を振ったスタディ（水温の追従挙動）。

  omc run_gain_study.mos  ->  g0/g50/g150/g500/g1500/g3000 _res.csv
  python gain_study.py    ->  gain_study.png

PI制御なので ctrl_k>0 ならどれも最終的に目標(外気24.5℃)へ収束するが、
ゲインが小さいほど一度高く上がってからゆっくり戻り、大きいほど最初から張り付く。
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
Ttarget = 24.5


def load(f):
    rr = list(csv.reader(open(f, encoding="utf-8")))
    hd = rr[0]
    a = np.array([[float(x) for x in row] for row in rr[1:] if row])
    return a[:, hd.index("time")], a[:, hd.index("y_sim_T")]


gains = [("g0", 0, "0 (OFF=管理なし)", "0.4"),
         ("g50", 50, "50", "tab:purple"),
         ("g150", 150, "150", "tab:blue"),
         ("g500", 500, "500", "tab:green"),
         ("g1500", 1500, "1500", "tab:orange"),
         ("g3000", 3000, "3000 (既定)", "tab:red")]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.4))
for pre, k, lab, col in gains:
    f = os.path.join(HERE, "%s_res.csv" % pre)
    if not os.path.exists(f):
        continue
    t, T = load(f)
    ax1.plot(t / 3600, T, "-", color=col, linewidth=2.0, label="ctrl_k=%s" % lab)
    ax2.plot(t / 3600, T, "-", color=col, linewidth=2.0, label="ctrl_k=%s" % lab)

for ax in (ax1, ax2):
    ax.axhline(Ttarget, color="gray", ls="--", linewidth=1.0)
    ax.set_xlabel("時間 [h]", fontsize=12)
    ax.set_ylabel("タンク水温 [℃]", fontsize=12)
    ax.grid(True, color="lightgray", linewidth=0.8)
    ax.set_axisbelow(True)
ax1.set_title("全体（ゲインが小さいほど一度上がって戻る）", fontsize=12)
ax1.set_ylim(22, 38)
ax1.legend(fontsize=9, loc="center right")
ax2.set_title("目標付近の拡大（最終は全て24.5℃に収束）", fontsize=12)
ax2.set_ylim(23.5, 27)
ax2.annotate("目標=外気 24.5℃", (ax2.get_xlim()[1] * 0.55, Ttarget + 0.1), fontsize=10, color="gray")
fig.suptitle("温度管理ゲイン ctrl_k のスタディ（PI制御, 目標=外気24.5℃）", fontsize=13)
plt.tight_layout()
out = os.path.join(HERE, "gain_study.png")
plt.savefig(out, dpi=150, bbox_inches="tight")

print("最終水温(60000s):")
for pre, k, lab, col in gains:
    f = os.path.join(HERE, "%s_res.csv" % pre)
    if os.path.exists(f):
        _, T = load(f)
        peak = T.max()
        print("  ctrl_k=%-5d 最終%.2f℃ / 最高%.2f℃" % (k, T[-1], peak))
print("saved:", out)
