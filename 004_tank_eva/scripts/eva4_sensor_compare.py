"""eva4_05(冷却機側の水にセンサ) / eva4_06(ポンプ出口にセンサ) の OpenModelica 結果を実測と比較
入力: eva4/results/eva4_05_localSensor_res.csv, eva4_06_pumpOutSensor_res.csv (run_sim_05/06 の結果)
出力: eva4/docs/img/eva4_05_06_vs_exp.png
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

# eva4_03(冷却コイル型)は集中定数: 平衡24.46℃, 時定数2.77h, 初期23.8℃
t3 = np.linspace(0, 30000, 600)
T3 = 24.46 + (23.8 - 24.46) * np.exp(-t3 / (2.77 * 3600))

fig, axs = plt.subplots(1, 2, figsize=(13, 4.8))
ax = axs[0]
ax.plot(te / 3600, Te, "ko", ms=5, label="eva4 実測（4点平均）")
ax.plot(t3 / 3600, T3, "g-", lw=2, label=f"eva4_03 冷却コイル型（RMSE {rmse(t3, T3):.2f}℃）")
res = {}
for n, c, lab in [("05_localSensor", "tab:blue", "eva4_05 センサ=冷却機側の水"),
                  ("06_pumpOutSensor", "tab:red", "eva4_06 センサ=ポンプ出口")]:
    r = pd.read_csv(os.path.join(E4, "results", f"eva4_{n}_res.csv"))
    t = r["time"].values; T = r["tank1.medium.T"].values - 273.15
    res[n] = r
    ax.plot(t / 3600, T, "-", color=c, lw=2, label=f"{lab}（RMSE {rmse(t, T):.2f}℃）")
ax.axhline(24.5, color="gray", ls=":", label="目標 24.5℃")
ax.set_xlim(0, 8); ax.set_xlabel("経過時間 [h]"); ax.set_ylabel("tank1 水温 [℃]")
ax.set_title("タンク水温：05・06 とも約15分で上がりきる")
ax.grid(True, alpha=0.3); ax.legend(fontsize=9, loc="lower right")

ax = axs[1]
for n, c, lab in [("05_localSensor", "tab:blue", "eva4_05"), ("06_pumpOutSensor", "tab:red", "eva4_06")]:
    r = res[n]
    ax.plot(r["time"] / 3600, -r["sCooler.cooler.Q_flow"], "-", color=c, lw=2, label=f"{lab} 除熱量")
ax.axhline(610, color="k", ls="--", lw=1, label="ポンプ発熱 610W")
ax.set_xlim(0, 2); ax.set_xlabel("経過時間 [h]"); ax.set_ylabel("除熱量 [W]")
ax.set_title("除熱量：センサ温度が24.5℃に届くまで 0W")
ax.grid(True, alpha=0.3); ax.legend(fontsize=9, loc="lower right")
fig.tight_layout()
fig.savefig(os.path.join(E4, "docs", "img", "eva4_05_06_vs_exp.png"), dpi=130)
print("done")
