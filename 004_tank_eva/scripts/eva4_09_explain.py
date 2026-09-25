"""eva4_09 の解説図
出力: eva4/docs/img/eva4_09_concept.png (分ける前/後の概念図)
      eva4/docs/img/eva4_09_body_vs_zone.png (本体とよどみ部の水温)
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mp
import matplotlib.font_manager as fm
for fp in ["/home/kamakiri/.fonts/NotoSansCJKjp-Regular.otf", r"C:\Windows\Fonts\meiryo.ttc"]:
    if os.path.exists(fp):
        fm.fontManager.addfont(fp); plt.rcParams["font.family"] = fm.FontProperties(fname=fp).get_name(); break
plt.rcParams["axes.unicode_minus"] = False
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E4 = os.path.join(ROOT, "eva4")

# ---- 概念図 ----
def box(ax, x, y, w, h, fc, text, fs=10):
    ax.add_patch(mp.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02", fc=fc, ec="k", lw=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)

def arrow(ax, p, q, c, text="", fs=9, off=(0, 0.25)):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color=c, lw=2))
    if text:
        ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], text, ha="center", fontsize=fs, color=c)

fig, axs = plt.subplots(1, 2, figsize=(14, 5.6))
for k, ax in enumerate(axs):
    ax.set_xlim(-0.3, 10); ax.set_ylim(0, 7.2); ax.axis("off")
    box(ax, 4.2, 1.0, 2.2, 2.0, "#d6e9f8", "tank2\n162 kg")
    box(ax, 7.4, 1.0, 1.8, 2.0, "#d6e9f8", "tank3\n46 kg")
    box(ax, 5.3, 3.7, 2.6, 1.1, "#e8f6ef", "温度管理（冷却）\n目標 24.5℃\ntank2 の水で判断", 9)
    arrow(ax, (5.3, 3.0), (5.9, 3.7), "tab:green", "25 L/min 引く", 8, (-1.0, 0.0))
    arrow(ax, (7.9, 3.7), (8.3, 3.0), "tab:green", "冷やして返す", 8, (0.9, 0.0))
    box(ax, 1.8, 5.6, 2.4, 1.0, "#fdebd0", "ポンプ（サイクロン）\n発熱 610W", 9)
    x1 = 2.6 if k else 1.9  # tank1(本体) の中心
    ax.annotate("", xy=(2.2, 5.6), xytext=(x1, 3.0), arrowprops=dict(arrowstyle="-|>", color="tab:orange", lw=2))
    ax.annotate("", xy=(8.9, 3.0), xytext=(4.2, 6.1), arrowprops=dict(arrowstyle="-|>", color="tab:orange", lw=2, connectionstyle="angle,angleA=0,angleB=90"))
    ax.text(6.6, 6.3, "110 L/min で tank3 へ", fontsize=9, color="tab:orange", ha="center")
    arrow(ax, (7.4, 2.0), (6.4, 2.0), "tab:blue", "戻り", 8, (0, 0.2))
    arrow(ax, (4.2, 2.0), (3.3 if k else 3.2, 2.0), "tab:blue", "戻り", 8, (0, 0.2))
    if k == 0:
        box(ax, 0.6, 1.0, 2.6, 2.0, "#d6e9f8", "tank1\n33 kg\n(全部よく混ざる)")
        ax.set_title("eva4_07：tank1 は1つ（全体が同じ温度）", fontsize=12)
    else:
        box(ax, 2.1, 1.0, 1.2, 2.0, "#d6e9f8", "本体\n10 kg\n(30%)", 9)
        box(ax, 0.0, 1.0, 1.8, 2.0, "#9fc3e0", "よどみ部\nzone1\n23 kg (70%)", 9)
        ax.annotate("", xy=(2.1, 2.0), xytext=(1.8, 2.0), arrowprops=dict(arrowstyle="<|-|>", color="tab:red", lw=2))
        ax.text(1.6, 0.3, "本体と よどみ部 の水の入れ替わりは\n0.15 L/min だけ（熱のやり取り 約10 W/K）", ha="center", fontsize=9, color="tab:red")
        ax.plot(0.9, 1.3, "k*", ms=12); ax.text(1.25, 1.25, "測定点?", fontsize=8, va="center")
        ax.set_title("eva4_09：tank1 を「本体」と「よどみ部」に分ける", fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(E4, "docs", "img", "eva4_09_concept.png"), dpi=130)

# ---- 本体とよどみ部の水温 ----
d = pd.read_csv(os.path.join(E4, "data", "temperature_20points_without_NC_T7.csv"), encoding="utf-8-sig")
te = d["Time [s]"].values / 3600
Te = d[["4-16", "4-17", "4-18", "4-19"]].mean(axis=1).values
r = pd.read_csv(os.path.join(E4, "results", "eva4_09_loop2to3_split_res.csv"))
t = r["time"].values / 3600
fig, ax = plt.subplots(figsize=(9, 4.8))
ax.plot(te, Te, "ko", ms=5, label="実測（4点平均）")
ax.plot(t, r["tank1.medium.T"] - 273.15, "-", color="tab:blue", lw=2, label="tank1 本体（よく混ざる）")
ax.plot(t, r["tank2.medium.T"] - 273.15, ":", color="tab:cyan", lw=2, label="tank2（温度管理が見ている水）")
ax.plot(t, r["zone1.zone.T"] - 273.15, "-", color="tab:purple", lw=2.5, label="tank1 よどみ部 zone1")
ax.axhline(24.5, color="gray", ls="--", lw=1, label="目標 24.5℃")
ax.annotate("本体は約15分で24.5℃", xy=(0.3, 24.5), xytext=(1.0, 24.62), fontsize=10,
            arrowprops=dict(arrowstyle="->"))
ax.annotate("よどみ部は約2.5時間の遅れで\nゆっくり追いつく", xy=(3.0, 24.27), xytext=(3.6, 23.95), fontsize=10,
            arrowprops=dict(arrowstyle="->"))
ax.set_xlim(0, 8); ax.set_ylim(23.7, 24.7)
ax.set_xlabel("経過時間 [h]"); ax.set_ylabel("水温 [℃]")
ax.set_title("eva4_09：本体とよどみ部の水温")
ax.grid(True, alpha=0.3); ax.legend(fontsize=9, loc="lower right")
fig.tight_layout()
fig.savefig(os.path.join(E4, "docs", "img", "eva4_09_body_vs_zone.png"), dpi=130)
print("done")
