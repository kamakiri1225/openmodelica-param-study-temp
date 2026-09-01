# -*- coding: utf-8 -*-
"""温度管理あり/なし のエネルギー内訳を棒グラフ化（同一モデル, ctrl_k 切替の定常）。

定常のエネルギー収支（入力=出力）:
  管理なし(ctrl_k=0, 水温37.7℃): 発熱610W = 上面→外気 + 側壁→外気 + 底面→地面
  管理あり(ctrl_k>0, 水温24.5℃=外気): 発熱610W = 冷却(制御除熱) + 自然放熱≒0
集中定数の熱コンダクタンスから解析的に算出。

  python heat_breakdown.py   -> heat_breakdown.png
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

# --- 幾何(等価単一矩形 Lx×Ly)・熱伝達率 ---
Lx, Ly = 1.764, 1.829
A_top = Lx * Ly
A_bot = A_top
peri = 2 * (Lx + Ly)
level = 0.0755
A_side = peri * level
h, h_top, h_l = 9.0, 11.2, 200.0
k_air, t_airgap = 0.026, 0.015     # 底面は15mm浮いている→空気層の伝導
h_bot = k_air / t_airgap           # ≒1.73 W/m2K (断熱的)
Q = 610.0

# --- 管理なし(定常)の放熱内訳 ---
Gtop = h_top * A_top
Gl = h_l * A_side
Gside = h * A_side
Gbot = h_bot * A_bot
Gwall = Gside + Gbot
UA = Gtop + 1.0 / (1.0 / Gl + 1.0 / Gwall)
dTw = Q / UA
Qtop = Gtop * dTw
Qwall = Q - Qtop
dTwall = Qwall / Gwall
Qside = Gside * dTwall
Qbot = Gbot * dTwall
# --- 管理あり(定常, 水温=外気): 自然放熱≒0, 冷却=Q ---
Qcool = Q
Qnat = 0.0
print("なし: 上面%.0f 側壁%.0f 底面%.0f =%.0fW" % (Qtop, Qside, Qbot, Qtop + Qside + Qbot))
print("あり: 冷却%.0f 自然放熱%.0f" % (Qcool, Qnat))

# --- 棒グラフ（管理なし / あり を横並び, 出力内訳） ---
fig, ax = plt.subplots(figsize=(7.5, 6))
x = [0, 1]
labels = ["温度管理なし\n(水温37.7℃)", "温度管理あり\n(水温24.5℃=外気)"]
top = [Qtop, 0]
side = [Qside, 0]
bot = [Qbot, 0]
cool = [0, Qcool]
ax.bar(x, top, width=0.5, color="tab:orange", label="上面→外気")
ax.bar(x, side, width=0.5, bottom=top, color="tab:green", label="側壁→外気")
ax.bar(x, bot, width=0.5, bottom=np.add(top, side), color="tab:brown", label="底面→地面(空気層15mm)")
ax.bar(x, cool, width=0.5, color="tab:blue", label="冷却(温度管理で除熱)")
ax.axhline(Q, color="red", ls="--", linewidth=1.5, label="発熱 Q=610W")
for xi, t, s, b, c in zip(x, top, side, bot, cool):
    if t > 5: ax.text(xi, t / 2, "%.0fW" % t, ha="center", va="center", color="white", fontsize=10)
    if s > 5: ax.text(xi, t + s / 2, "%.0fW" % s, ha="center", va="center", color="white", fontsize=10)
    if b > 5: ax.text(xi, t + s + b / 2, "%.0fW" % b, ha="center", va="center", color="white", fontsize=10)
    if c > 5: ax.text(xi, c / 2, "%.0fW" % c, ha="center", va="center", color="white", fontsize=10)
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=11)
ax.set_ylabel("熱量 [W]", fontsize=12)
ax.set_title("タンク 定常エネルギー内訳（同一モデル, ctrl_k 切替, 入力=出力）", fontsize=12)
ax.set_ylim(0, 680)
ax.legend(fontsize=9, loc="upper left", bbox_to_anchor=(1.02, 1.0), borderaxespad=0)
ax.grid(True, axis="y", alpha=0.4)
plt.tight_layout()
out = os.path.join(HERE, "heat_breakdown.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print("saved:", out)
