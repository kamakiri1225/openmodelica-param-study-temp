"""eva4 実測から「モデルに足りない点」を確認する図を作る
出力: eva4/docs/img/eva4_measured_points.png, eva4/docs/img/eva4_heat_removal.png
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
for fp in ["/home/kamakiri/.fonts/NotoSansCJKjp-Regular.otf", r"C:\Windows\Fonts\meiryo.ttc"]:
    if os.path.exists(fp):
        fm.fontManager.addfont(fp); plt.rcParams["font.family"] = fm.FontProperties(fname=fp).get_name(); break
plt.rcParams["axes.unicode_minus"] = False

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "eva4", "docs", "img")
d = pd.read_csv(os.path.join(ROOT, "eva4", "data", "temperature_20points_without_NC_T7.csv"), encoding="utf-8-sig")
t = d["Time [s]"].values / 3600
cols = ["4-16", "4-17", "4-18", "4-19"]
T = d[cols].values
Tm = T.mean(axis=1)

# 図1: 測定点ごとの温度
fig, ax = plt.subplots(figsize=(8, 4.5))
for c in cols:
    ax.plot(t, d[c], "o-", ms=3, label=c)
ax.plot(t, Tm, "k--", lw=2, label="4点平均")
ax.axhline(24.5, color="gray", ls=":", label="目標 24.5℃")
ax.fill_between(t, T.min(axis=1), T.max(axis=1), color="orange", alpha=0.2, label="測定点のばらつき")
ax.set_xlabel("経過時間 [h]"); ax.set_ylabel("水温 [℃]")
ax.set_title("eva4 実測：開始から約2時間は測定点で温度が最大0.6℃違う")
ax.grid(True, alpha=0.3); ax.legend(fontsize=9, loc="lower right")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "eva4_measured_points.png"), dpi=130)

# 図2: 実測から逆算した除熱量
cp, Q, UA_tank, Tamb, G = 4186, 610, 46, 24.5, 25 / 60 * 4186
p = np.polyfit(t, Tm, 3)
Ts = np.polyval(p, t)
dTdt = np.polyval(np.polyder(p), t) / 3600
fig, ax = plt.subplots(figsize=(8, 4.5))
for m, ls in [(246, "-"), (415, "--")]:
    Qrem = Q + UA_tank * (Tamb - Ts) - m * cp * dTdt
    ax.plot(t, Qrem, "b" + ls, lw=2, label=f"実測から逆算した除熱量（水 {m} kg）")
ax.plot(t, G * (Ts - 24.5), "r-", lw=2, label="24.5℃の水を25L/minで完全混合した場合")
ax.axhline(0, color="k", lw=0.8)
ax.set_xlabel("経過時間 [h]"); ax.set_ylabel("タンクから取られる熱 [W]（正＝冷却）")
ax.set_title("水温が24.5℃より低い間も、実機は約500Wを除熱している")
ax.grid(True, alpha=0.3); ax.legend(fontsize=9, loc="lower right")
fig.tight_layout(); fig.savefig(os.path.join(IMG, "eva4_heat_removal.png"), dpi=130)
print("done")
