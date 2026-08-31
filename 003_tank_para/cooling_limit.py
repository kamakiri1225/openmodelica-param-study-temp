# -*- coding: utf-8 -*-
"""温度管理あり + 冷却能力の上限（例: ダイキン3.5kW=3500W）の考察グラフ。

集中定数（フィット状態, UA=ua(8.79,0.0755)）で:
  - 冷却量 = min(Q, Qcool_max)（目標=外気温を保つのに必要な除熱, ただし上限あり）
  - 温度上昇 ΔT = max(0, (Q - Qcool_max)/UA)   （上限超過分が水温を上げる）
無制限時の実機OM点（OM/_cooling_vs_Q.csv, 冷却量=Q）も重ねる。

  python cooling_limit.py   -> docs/img/cooling_limit.png
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
IMG = os.path.join(HERE, "docs", "img")

# UA（フィット点 heatCeffToAir=8.79, level=0.0755）
th = 2.3 / 1000
Lx1_1, Ly1_1 = 0.903, 0.479
Lx2_1, Lx2_2, Ly2_1, Ly2_2 = 1.191, 0.478, 1.670, 0.337
Lx3_1, Ly3_1 = 0.573, 1.191
A1 = Lx1_1 * Ly1_1; A2 = Lx2_1 * Ly2_1 + Lx2_2 * Ly2_2; A3 = Lx3_1 * Ly3_1


def ua(h_air, level, h_in=10.0, kground=80.0):
    UA_air = h_air * (A1 + A2 + A3)

    def g(Ain, Ac, Ag):
        return 1 / (1 / (h_in * Ain) + 1 / (Ac * kground / th) + 1 / (h_air * Ag))
    u1 = g(A1 + Ly1_1 * level, A1 + Lx1_1 * level + Ly1_1 * level, A1 + Ly1_1 * level)
    a2 = A2 + (Ly2_1 + Lx2_1) * level
    u2 = g(a2, A2 + (Lx2_1 + Ly2_1) * level, a2)
    a3 = A3 + (Lx3_1 + Ly3_1) * level
    u3 = g(a3, a3, a3)
    return UA_air + u1 + u2 + u3


UA = ua(8.79, 0.0755)
Tamb = 24.5
Qcap = 3500.0   # ダイキン3.5kW

Q = np.linspace(0, 6000, 400)
cool = np.minimum(Q, Qcap)                 # 冷却量[W]
dT = np.maximum(0.0, (Q - Qcap) / UA)       # 温度上昇[K]
Tw = Tamb + dT

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 8), sharex=True)

# 上: 冷却量
ax1.plot(Q, cool, "-", color="tab:blue", linewidth=2.6, label="冷却量（上限3500Wで頭打ち）")
ax1.plot([0, 6000], [0, 6000], "--", color="gray", linewidth=1.3, label="上限なしなら 冷却量=発熱量")
# 実機OM(無制限)点
csvf = os.path.join(HERE, "OM", "_cooling_vs_Q.csv")
if os.path.exists(csvf):
    rows = list(csv.DictReader(open(csvf)))
    qi = [float(r["Q_in"]) for r in rows]; qc = [abs(float(r["Q_cool"])) for r in rows]
    ax1.plot(qi, qc, "ks", markersize=7, label="実機OM(無制限)")
ax1.axvline(Qcap, color="tab:red", ls=":", linewidth=1.8)
ax1.axhline(Qcap, color="tab:red", ls=":", linewidth=1.2)
ax1.set_ylabel("冷却量 [W]", fontsize=13); ax1.grid(True, alpha=0.4); ax1.legend(fontsize=10)
ax1.set_title("温度管理あり＋冷却能力上限3500W(ダイキン3.5kW)の影響", fontsize=13)

# 下: 水温
ax2.plot(Q, Tw, "-", color="tab:red", linewidth=2.6)
ax2.axhline(Tamb, color="gray", ls="--", linewidth=1.2, label="外気温 %.1f℃" % Tamb)
ax2.axvline(Qcap, color="tab:red", ls=":", linewidth=1.8, label="冷却上限 %.0f W" % Qcap)
ax2.annotate("Q≤3500: 水温=外気温(制御成立)", (1500, Tamb + 0.6), fontsize=10, color="tab:blue")
ax2.annotate("Q>3500: 冷却飽和→水温上昇\nΔT=(Q-3500)/UA", (3800, Tamb + 8), fontsize=10, color="tab:red")
ax2.set_xlabel("発熱量 Q [W]", fontsize=13); ax2.set_ylabel("水温 [degC]", fontsize=13)
ax2.grid(True, alpha=0.4); ax2.legend(fontsize=10)

plt.tight_layout()
out = os.path.join(IMG, "cooling_limit.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print("UA=%.1f W/K, 上限3500W → Q=4000で水温=%.1f℃, Q=5000で%.1f℃" %
      (UA, Tamb + max(0, (4000 - Qcap) / UA), Tamb + max(0, (5000 - Qcap) / UA)))
print("saved:", out)
