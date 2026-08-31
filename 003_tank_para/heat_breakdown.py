# -*- coding: utf-8 -*-
"""ベース(Q=610W, フィット値)の熱量内訳を温度管理あり/なしで棒グラフ化。

定常状態のエネルギー収支（入力=出力）:
  温度管理なし: 発熱610W = 上面→大気 + 側/底→地面（水温が上がり自然放熱でつり合う）
  温度管理あり: 発熱610W = 冷却(制御)（水温=外気温なので自然放熱≒0, 制御が全部除去）

  python heat_breakdown.py   -> docs/img/heat_breakdown.png
"""
import os
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
IMG = os.path.join(HERE, "docs", "img")

# --- フィット状態の UA を上面/地面に分解 ---
th = 2.3 / 1000
Lx1_1, Ly1_1 = 0.903, 0.479
Lx2_1, Lx2_2, Ly2_1, Ly2_2 = 1.191, 0.478, 1.670, 0.337
Lx3_1, Ly3_1 = 0.573, 1.191
A1 = Lx1_1 * Ly1_1; A2 = Lx2_1 * Ly2_1 + Lx2_2 * Ly2_2; A3 = Lx3_1 * Ly3_1
h_air, level, h_in, kground = 8.79, 0.0755, 10.0, 80.0
Q = 610.0


def g(Ain, Ac, Ag):
    return 1 / (1 / (h_in * Ain) + 1 / (Ac * kground / th) + 1 / (h_air * Ag))


UA_air = h_air * (A1 + A2 + A3)
u1 = g(A1 + Ly1_1 * level, A1 + (Lx1_1 + Ly1_1) * level, A1 + Ly1_1 * level)
a2 = A2 + (Ly2_1 + Lx2_1) * level
u2 = g(a2, A2 + (Lx2_1 + Ly2_1) * level, a2)
a3 = A3 + (Lx3_1 + Ly3_1) * level
u3 = g(a3, a3, a3)
UA_ground = u1 + u2 + u3
UA = UA_air + UA_ground
dT = Q / UA
Q_top = UA_air * dT       # 上面→大気
Q_gnd = UA_ground * dT    # 側/底→地面

print("なし: 上面→大気=%.0fW, 側/底→地面=%.0fW, 計%.0fW (水温上昇ΔT=%.1fK)" % (Q_top, Q_gnd, Q_top + Q_gnd, dT))
print("あり: 冷却(制御)=%.0fW, 自然放熱≒0 (水温=外気温)" % Q)

# --- 棒グラフ（積み上げ, 出力=610Wの内訳） ---
fig, ax = plt.subplots(figsize=(7.5, 6))
x = [0, 1]
labels = ["温度管理なし\n(水温37.8℃)", "温度管理あり\n(水温24.5℃=外気温)"]
# なし: 上面 + 地面, あり: 冷却
top = [Q_top, 0]
gnd = [Q_gnd, 0]
cool = [0, Q]
b1 = ax.bar(x, top, width=0.5, color="tab:orange", label="上面→大気 放熱")
b2 = ax.bar(x, gnd, width=0.5, bottom=top, color="tab:brown", label="側/底→地面 放熱")
b3 = ax.bar(x, cool, width=0.5, bottom=np.add(top, gnd), color="tab:blue", label="冷却(温度管理で除去)")
ax.axhline(Q, color="red", ls="--", linewidth=1.5, label="発熱量 Q=610W")
# 数値ラベル
for xi, t, gg, c in zip(x, top, gnd, cool):
    if t > 1: ax.text(xi, t / 2, "%.0fW" % t, ha="center", va="center", color="white", fontsize=11)
    if gg > 1: ax.text(xi, t + gg / 2, "%.0fW" % gg, ha="center", va="center", color="white", fontsize=11)
    if c > 1: ax.text(xi, c / 2, "%.0fW" % c, ha="center", va="center", color="white", fontsize=11)
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=12)
ax.set_ylabel("熱量 [W]", fontsize=13)
ax.set_title("ベース(Q=610W)の熱量内訳（定常, 入力=出力）", fontsize=13)
ax.set_ylim(0, 720)
ax.legend(fontsize=10, loc="upper right")
ax.grid(True, axis="y", alpha=0.4)
plt.tight_layout()
out = os.path.join(IMG, "heat_breakdown.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print("saved:", out)
