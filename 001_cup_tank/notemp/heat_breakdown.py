# -*- coding: utf-8 -*-
"""温度管理なしタンク(定常, 水温37.7℃)のエネルギー内訳を棒グラフ化。

定常のエネルギー収支（入力=出力）:
  発熱 Q=610W = 上面→外気 + 側壁→外気 + 底面→地面
集中定数の熱コンダクタンスから各放熱を解析的に算出（OM実測とも整合）。

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

# --- 幾何(等価単一矩形 Lx×Ly) ---
Lx, Ly = 1.764, 1.829
A_top = Lx * Ly
A_bot = A_top
peri = 2 * (Lx + Ly)
level = 0.0755
A_side = peri * level
# --- 熱伝達率 ---
h, h_top, h_l = 9.0, 11.2, 200.0
k_air, t_airgap = 0.026, 0.015     # 底面は15mm浮いている→空気層の伝導
h_bot = k_air / t_airgap           # ≒1.73 W/m2K (断熱的)
Q, Tamb = 610.0, 24.5

# --- 集中定数の定常解 ---
Gtop = h_top * A_top          # 上面→外気(自然対流)
Gl = h_l * A_side             # 水→壁
Gside = h * A_side            # 壁→外気(側)
Gbot = h_bot * A_bot          # 壁→地面(底, 空気層で断熱的)
Gwall = Gside + Gbot          # 壁→外気/地面 合計
UA = Gtop + 1.0 / (1.0 / Gl + 1.0 / Gwall)
dTw = Q / UA                  # 水温上昇
Qtop = Gtop * dTw
Qwall = Q - Qtop              # 壁経由(側+底)
dTwall = Qwall / Gwall
Qside = Gside * dTwall
Qbot = Gbot * dTwall
print("水温=%.1f℃, 上面=%.0fW, 側壁=%.0fW, 底面=%.0fW, 計=%.0fW" %
      (Tamb + dTw, Qtop, Qside, Qbot, Qtop + Qside + Qbot))

# --- 棒グラフ(入力 / 出力内訳) ---
fig, ax = plt.subplots(figsize=(6.5, 6))
x = [0, 1]
ax.bar(0, Q, width=0.5, color="tab:red", label="発熱 Q=610W (サイクロン)")
b1 = ax.bar(1, Qtop, width=0.5, color="tab:orange", label="上面→外気")
b2 = ax.bar(1, Qside, width=0.5, bottom=Qtop, color="tab:green", label="側壁→外気")
b3 = ax.bar(1, Qbot, width=0.5, bottom=Qtop + Qside, color="tab:brown", label="底面→地面(空気層15mm)")
for yv, hh, lab in [(Qtop / 2, Qtop, "上面 %.0fW" % Qtop),
                    (Qtop + Qside / 2, Qside, "側壁 %.0fW" % Qside),
                    (Qtop + Qside + Qbot / 2, Qbot, "底面 %.0fW" % Qbot)]:
    ax.text(1, yv, lab, ha="center", va="center", color="white", fontsize=10)
ax.text(0, Q / 2, "発熱\n610W", ha="center", va="center", color="white", fontsize=11)
ax.set_xticks(x)
ax.set_xticklabels(["入力", "出力(放熱)内訳"], fontsize=12)
ax.set_ylabel("熱量 [W]", fontsize=12)
ax.set_title("温度管理なし(水温37.7℃) 定常エネルギー内訳", fontsize=12)
ax.set_ylim(0, 680)
ax.legend(fontsize=9, loc="upper left", bbox_to_anchor=(1.02, 1.0), borderaxespad=0)
ax.grid(True, axis="y", alpha=0.4)
plt.tight_layout()
out = os.path.join(HERE, "heat_breakdown.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print("saved:", out)
