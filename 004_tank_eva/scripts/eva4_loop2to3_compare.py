"""eva4_07/08/09(温度管理ループ tank2→tank3) の OpenModelica 結果を実測と比較
入力: eva4/results/eva4_07_loop2to3_res.csv, eva4_08_loop2to3_coil_res.csv, eva4_09_loop2to3_split_res.csv
出力: eva4/docs/img/eva4_07_08_09_vs_exp.png
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
E4 = os.path.join(ROOT, "eva4")
d = pd.read_csv(os.path.join(E4, "data", "temperature_20points_without_NC_T7.csv"), encoding="utf-8-sig")
te = d["Time [s]"].values
Te = d[["4-16", "4-17", "4-18", "4-19"]].mean(axis=1).values

def rmse(t, T):
    return np.sqrt(np.mean((np.interp(te, t, T) - Te) ** 2))

def load(n):
    return pd.read_csv(os.path.join(E4, "results", f"eva4_{n}_res.csv"))

r7, r8, r9 = load("07_loop2to3"), load("08_loop2to3_coil"), load("09_loop2to3_split")
curves = [
    (r7, "tank1.medium.T", "tab:blue", "-", "eva4_07 目標温度制御：tank1"),
    (r8, "tank1.medium.T", "tab:green", "-", "eva4_08 冷却コイル型：tank1"),
    (r9, "tank1.medium.T", "tab:purple", ":", "eva4_09 分割：tank1 本体"),
    (r9, "zone1.zone.T", "tab:purple", "-", "eva4_09 分割：tank1 よどみ部"),
]
fig, axs = plt.subplots(1, 2, figsize=(13, 4.8))
ax = axs[0]
ax.plot(te / 3600, Te, "ko", ms=5, label="eva4 実測（4点平均）")
for r, c, col, ls, lab in curves:
    t = r["time"].values; T = r[c].values - 273.15
    ax.plot(t / 3600, T, ls, color=col, lw=2, label=f"{lab}（RMSE {rmse(t, T):.2f}℃）")
ax.axhline(24.5, color="gray", ls="--", lw=1, label="目標 24.5℃")
ax.set_xlim(0, 8); ax.set_xlabel("経過時間 [h]"); ax.set_ylabel("水温 [℃]")
ax.set_title("水温：温度管理ループ tank2→tank3")
ax.grid(True, alpha=0.3); ax.legend(fontsize=8.5, loc="lower right")

ax = axs[1]
ax.plot(r7["time"] / 3600, -r7["tempControl.cooler.Q_flow"], "-", color="tab:blue", lw=2, label="eva4_07")
ax.plot(r8["time"] / 3600, r8["coilCtrl.coil.Q_flow"], "-", color="tab:green", lw=2, label="eva4_08")
ax.plot(r9["time"] / 3600, -r9["tempControl.cooler.Q_flow"], "--", color="tab:purple", lw=2, label="eva4_09")
ax.axhline(610, color="k", ls="--", lw=1, label="ポンプ発熱 610W")
ax.set_xlim(0, 8); ax.set_xlabel("経過時間 [h]"); ax.set_ylabel("除熱量 [W]")
ax.set_title("温度管理の除熱量")
ax.grid(True, alpha=0.3); ax.legend(fontsize=9, loc="lower right")
fig.tight_layout()
fig.savefig(os.path.join(E4, "docs", "img", "eva4_07_08_09_vs_exp.png"), dpi=130)
print("done")
