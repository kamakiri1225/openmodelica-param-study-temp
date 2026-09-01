# -*- coding: utf-8 -*-
"""同一モデル TankHotWater_cyclone_cup_TempCtrl の温度管理 ON/OFF を1枚に。

  omc run_onoff.mos   ->  _off_res.csv (ctrl_k=0), _on_res.csv (ctrl_k=3000)
  python onoff_compare.py   -> onoff_compare.png

ctrl_k=0 で温度管理なし(37.7℃まで上昇=基準モデルと同一)、
ctrl_k=3000 で温度管理あり(24.5℃保持)。1モデルで両方できることを示す。
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


def load(f):
    rr = list(csv.reader(open(f, encoding="utf-8")))
    hd = rr[0]
    a = np.array([[float(x) for x in row] for row in rr[1:] if row])
    return a[:, hd.index("time")], a[:, hd.index("y_sim_T")]


def exp_mean(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    te = np.array([float(r["time_s"]) for r in rows])
    w = ["4-16", "4-17", "4-18", "4-19"]
    m = np.mean([[float(r[s]) for r in rows] for s in w], axis=0)
    return te, m


t_off, T_off = load(os.path.join(HERE, "_off_res.csv"))
t_on, T_on = load(os.path.join(HERE, "_on_res.csv"))
# 実験データ: OFF=eva5(温度管理なし), ON=eva4(温度管理あり)
te5, m5 = exp_mean(os.path.join(HERE, "..", "notemp", "data", "eva5_tank_data.csv"))
te4, m4 = exp_mean(os.path.join(HERE, "data", "eva4_tank_data.csv"))

# --- 時定数 τ を OFF 曲線から求める(63.2%到達時刻) ---
Tamb = 24.5
Tfin = T_off[-1]                       # ≒最終到達温度(150000s≒6.5τで実質飽和)
dT = Tfin - Tamb
T_at_tau = Tamb + 0.632 * dT           # τ での水温 = 63.2%到達温度
# 逆引き: 「水温が T_at_tau になる時刻」を曲線から読む(温度→時刻)。
# np.interp(x,xp,fp) の xp に温度列 T_off, fp に時刻列 t_off を渡す。
# OFF曲線は単調上昇なので温度→時刻が1対1に決まり内挿できる。
tau = float(np.interp(T_at_tau, T_off, t_off))
t3 = 3 * tau                            # 3τ=95.0%
t5 = 5 * tau                            # 5τ=99.3%到達=整定時間
T_at_3tau = Tamb + (1 - np.exp(-3.0)) * dT
T_at_5tau = Tamb + (1 - np.exp(-5.0)) * dT

fig, ax = plt.subplots(figsize=(10, 5.6))
ax.plot(t_off / 3600, T_off, "-", color="tab:red", linewidth=2.6,
        label="OM OFF (ctrl_k=0) → 37.7℃まで上昇")
ax.plot(te5 / 3600, m5, "o", color="tab:red", markersize=5, alpha=0.6,
        label="実測 eva5 (温度管理なし)")
ax.plot(t_on / 3600, T_on, "-", color="tab:blue", linewidth=2.6,
        label="OM ON (ctrl_k=3000) → 24.5℃保持")
ax.plot(te4 / 3600, m4, "s", color="tab:blue", markersize=5, alpha=0.6,
        label="実測 eva4 (温度管理あり)")
ax.axhline(24.5, color="gray", ls="--", linewidth=1.0, label="目標=外気 24.5℃")

# --- 時定数の線 (τ, 3τ, 5τ) ---
ax.axvline(tau / 3600, color="green", ls="--", linewidth=1.5)
ax.axvline(t3 / 3600, color="darkorange", ls="--", linewidth=1.5)
ax.axvline(t5 / 3600, color="purple", ls="--", linewidth=1.8)
ax.plot([tau / 3600], [T_at_tau], "o", color="green", markersize=7, zorder=5)
ax.plot([t3 / 3600], [T_at_3tau], "o", color="darkorange", markersize=7, zorder=5)
ax.plot([t5 / 3600], [T_at_5tau], "o", color="purple", markersize=7, zorder=5)
ax.annotate("τ=%.1fh (63.2%%)" % (tau / 3600), (tau / 3600, T_at_tau),
            xytext=(tau / 3600 + 1.2, T_at_tau - 3.0), color="green", fontsize=10,
            arrowprops=dict(arrowstyle="->", color="green"))
ax.annotate("3τ=%.1fh (95.0%%)" % (t3 / 3600), (t3 / 3600, T_at_3tau),
            xytext=(t3 / 3600 - 3.0, T_at_3tau + 1.3), color="darkorange", fontsize=10,
            arrowprops=dict(arrowstyle="->", color="darkorange"))
ax.annotate("5τ=%.1fh (99.3%%)\n＝整定(飽和)時間" % (t5 / 3600), (t5 / 3600, T_at_5tau),
            xytext=(t5 / 3600 - 12, T_at_5tau - 4.5), color="purple", fontsize=10,
            arrowprops=dict(arrowstyle="->", color="purple"))

ax.set_xlabel("時間 [h]", fontsize=12)
ax.set_ylabel("タンク水温 [℃]", fontsize=12)
ax.set_xlim(0, 150000 / 3600)
ax.set_ylim(22, 40)
ax.grid(True, color="lightgray", linewidth=0.8)
ax.set_axisbelow(True)
ax.set_title("同一モデルで温度管理 ON / OFF（ctrl_k 切替）＋ 時定数 τ・3τ・5τ", fontsize=13)
ax.legend(fontsize=9, loc="center right")
plt.tight_layout()
out = os.path.join(HERE, "onoff_compare.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print("OFF 最終 %.2f℃ / ON 最終 %.2f℃" % (T_off[-1], T_on[-1]))
print("時定数 τ=%.0fs (%.1fh), 整定 5τ=%.0fs (%.1fh)" % (tau, tau / 3600, t5, t5 / 3600))
print("saved:", out)
