# -*- coding: utf-8 -*-
"""eva5 熱の流れ概念図。熱伝達率がどこに効くかを図示する。
出力: eva5/docs/img/eva5_concept.png"""
import os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

for fp in ["/home/kamakiri/.fonts/NotoSansCJKjp-Regular.otf", r"C:\Windows\Fonts\meiryo.ttc"]:
    if os.path.exists(fp):
        fm.fontManager.addfont(fp); plt.rcParams["font.family"] = fm.FontProperties(fname=fp).get_name(); break
plt.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(12, 7.5), dpi=140)
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

def box(x, y, w, h, text, fc, ec, fs=11, bold=False):
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.6",
                                fc=fc, ec=ec, lw=1.6))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal")

def arrow(x1, y1, x2, y2, color, lw=2.2, style="-|>"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=18, color=color, lw=lw))

# 外気・地面バー
ax.add_patch(plt.Rectangle((5, 90), 90, 7, fc="#eaf2f8", ec="#5499c7"))
ax.text(50, 93.5, "外気  Tair = 24.5 ℃", ha="center", va="center", fontsize=12, color="#21618c")
ax.add_patch(plt.Rectangle((5, 3), 90, 7, fc="#f6ece0", ec="#a6712e"))
ax.text(50, 6.5, "地面  24.5 ℃ (prescribedTemperature)", ha="center", va="center", fontsize=12, color="#7e5109")

# 3タンク(よく混合された水)
tanks = [("tank1", 30), ("tank2", 52), ("tank3", 74)]
for name, x in tanks:
    box(x, 50, 16, 20, f"{name}", "#d6eaf8", "#2471a3", fs=12, bold=True)
ax.text(52, 63, "3槽の水 (循環でほぼ均一)  合計 ≈ 246 kg  C ≈ 1.03 MJ/K", ha="center", fontsize=10.5, color="#1a5276")

# 循環ポンプ(タンク間 + 戻り)
for (x1), (x2) in [(38, 44), (60, 66)]:
    arrow(x1, 46, x2, 46, "#2471a3", lw=2.0)
ax.text(49, 42.5, "循環ポンプ 1.83 kg/s (path_1to2 / 1to21)", ha="center", fontsize=9.5, color="#2471a3")

# 加熱: サイクロン投入熱
box(12, 72, 17, 12, "サイクロン\n投入熱\nQ = 610 W", "#fadbd8", "#c0392b", fs=11, bold=True)
arrow(12, 66, 26, 56, "#c0392b", lw=3.0)
ax.text(15, 60, "加熱源\n(HF_cyclone→pump)", ha="center", fontsize=9, color="#c0392b")

# 上面 → 外気 (heatCeffToAir)
for _, x in tanks:
    arrow(x, 60, x, 89, "#e67e22", lw=2.2)
ax.text(50, 82, "上面から外気へ放熱  ★heatCeffToAir = 8.79 W/m²K  (飽和温度の主ノブ)",
        ha="center", fontsize=10.5, color="#b9770e",
        bbox=dict(boxstyle="round", fc="#fef9e7", ec="#b9770e", alpha=0.9))

# 底面 → 地面 (kground) と 液→内壁(heatCefftTank2in)
for _, x in tanks:
    arrow(x, 40, x, 10.5, "#a6712e", lw=2.2)
ax.text(50, 20, "底面から地面へ伝導  kground = 80 W/m·K / 厚さ2.3mm\n(液→内壁 heatCefftTank2in = 10 W/m²K を経由)",
        ha="center", fontsize=10, color="#7e5109",
        bbox=dict(boxstyle="round", fc="#f6ece0", ec="#a6712e", alpha=0.9))

# 結果
box(90, 50, 15, 16, "定常\n≈ 37.7 ℃\n(実測RMSE\n0.24℃)", "#e8f8f5", "#148f77", fs=10.5, bold=True)
arrow(82, 50, 82.5, 50, "#148f77", lw=0.1, style="-")

ax.set_title("eva5 熱の流れ概念図：加熱610W と 放熱(外気・地面) の釣り合いで定常温度が決まる",
             fontsize=13, pad=12)
fig.tight_layout(); _out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "eva5", "docs", "img", "eva5_concept.png")
os.makedirs(os.path.dirname(_out), exist_ok=True)
fig.savefig(_out)
print("saved eva5_concept.png")
