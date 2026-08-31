# -*- coding: utf-8 -*-
"""
集中定数モデルを実験平均カーブに最小二乗フィットし、実機に最も合う
パラメータを推定する。投入熱 Q=610 W は計測入力として固定。

  python docs/fit_params.py        (要 scipy)

出力:
  - 端末にフィット結果 (h_air, level, および面積係数 fA)
  - docs/img/001/fit_air_only.png  (実験・ベース・フィットの重ね描き)
"""
import os
import glob
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from scipy.optimize import least_squares

for cand in ["~/.fonts/NotoSansCJKjp-Regular.otf",
             "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
             "C:/Windows/Fonts/meiryo.ttc", "C:/Windows/Fonts/YuGothR.ttc",
             "C:/Windows/Fonts/msgothic.ttc"]:
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

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img", "001")   # 合わせこみ(001)の図
os.makedirs(IMG, exist_ok=True)

# ---- 実験データ (eva5) ----
time_s = np.array([0, 5263, 10526, 15789, 21053, 26316, 31579, 36842, 42105, 47368,
                   52632, 57895, 63158, 68421, 73684, 78947, 84211, 89474, 94737, 100000], float)
sensors = np.array([
    [23.8, 27.8, 29.8, 31.2, 32.4, 33.4, 34.3, 35.0, 35.5, 36.0, 36.4, 36.7, 37.0, 37.2, 37.35, 37.40, 37.50, 37.60, 37.65, 37.70],
    [24.0, 28.0, 30.1, 31.5, 32.7, 33.7, 34.5, 35.2, 35.8, 36.2, 36.6, 36.9, 37.15, 37.35, 37.50, 37.55, 37.60, 37.70, 37.75, 37.80],
    [24.2, 28.4, 30.5, 31.9, 33.0, 34.0, 34.8, 35.5, 36.0, 36.4, 36.8, 37.1, 37.35, 37.55, 37.70, 37.65, 37.75, 37.80, 37.85, 37.90],
    [23.7, 27.6, 29.6, 31.0, 32.2, 33.2, 34.1, 34.8, 35.4, 35.8, 36.2, 36.5, 36.8, 37.0, 37.15, 37.20, 37.30, 37.40, 37.45, 37.50]])
exp_mean = sensors.mean(0)

# ---- 集中定数モデル (ana003_..._NoTemp.mo と同じ式) ----
Tair = 24.5
rho_w, cp_w = 1000.0, 4186.0
th = 2.3 / 1000
Q = 610.0
Lx1_1, Ly1_1 = 0.903, 0.479
Lx2_1, Lx2_2, Ly2_1, Ly2_2 = 1.191, 0.478, 1.670, 0.337
Lx3_1, Ly3_1 = 0.573, 1.191
A1 = Lx1_1 * Ly1_1
A2 = Lx2_1 * Ly2_1 + Lx2_2 * Ly2_2
A3 = Lx3_1 * Ly3_1


def UA_of(h_air, h_in, kground, level, fA=1.0):
    UA_air = h_air * (A1 + A2 + A3) * fA

    def g(Ain, Ac, Ag):
        return 1 / (1 / (h_in * Ain * fA) + 1 / (Ac * fA * kground / th) + 1 / (h_air * Ag * fA))
    u1 = g(A1 + Ly1_1 * level, A1 + Lx1_1 * level + Ly1_1 * level, A1 + Ly1_1 * level)
    A2in = A2 + Ly2_1 * level + Ly2_2 * level + Lx2_1 * level
    u2 = g(A2in, Lx2_1 * Ly2_1 + Lx2_1 * level + Ly2_1 * level, A2in)
    A3g = A3 + Lx3_1 * level + Ly3_1 * level
    u3 = g(A3g, A3g, A3g)
    return UA_air + u1 + u2 + u3


def C_of(level):
    return (A1 * level + A2 * level + A3 * 0.9 * level) * rho_w * cp_w


def curve(t, h_air=10.0, level=0.128, h_in=10.0, kground=80.0, fA=1.0):
    UA = UA_of(h_air, h_in, kground, level, fA)
    C = C_of(level)
    return Tair + (Q / UA) * (1 - np.exp(-t / (C / UA)))


def rmse(y):
    return float(np.sqrt(np.mean((y - exp_mean) ** 2)))


# ---- ベース ----
base = curve(time_s)
print("BASE      : h_air=10 level=0.128  -> Tfin=%.2f tau=%.2fh RMSE=%.2f"
      % (Tair + Q / UA_of(10, 10, 80, 0.128), C_of(0.128) / UA_of(10, 10, 80, 0.128) / 3600, rmse(base)))

# ---- フィットA: h_air & level (Q=610固定) ----
rA = least_squares(lambda x: curve(time_s, h_air=x[0], level=x[1]) - exp_mean,
                   [8, 0.09], bounds=([2, 0.03], [20, 0.20]))
ha, lv = rA.x
UAa = UA_of(ha, 10, 80, lv)
print("FIT (熱伝達): h_air=%.2f level=%.4f  -> UA=%.2f 水量=%.0fkg Tfin=%.2f tau=%.2fh RMSE=%.3f"
      % (ha, lv, UAa, C_of(lv) / cp_w, Tair + Q / UAa, C_of(lv) / UAa / 3600, rmse(curve(time_s, h_air=ha, level=lv))))

# ---- フィットB: 面積係数fA & level (h_air=10固定) = 「面積が大きすぎ」仮説 ----
rB = least_squares(lambda x: curve(time_s, fA=x[0], level=x[1]) - exp_mean,
                   [0.8, 0.09], bounds=([0.3, 0.03], [1.2, 0.20]))
fA, lvB = rB.x
print("FIT (面積) : fA=%.3f(面積%.0f%%) level=%.4f  -> 同じUA/RMSE=%.3f"
      % (fA, fA * 100, lvB, rmse(curve(time_s, fA=fA, level=lvB))))

# ---- フィット(airのみ): heatCeffToAir のみ (level=0.128 固定, Q=610固定) ----
rAir = least_squares(lambda x: curve(time_s, h_air=x[0], level=0.128) - exp_mean,
                     [8], bounds=([2], [20]))
hair = rAir.x[0]
UAair = UA_of(hair, 10, 80, 0.128)
print("FIT (airのみ): h_air=%.2f level=0.128固定  -> UA=%.2f Tfin=%.2f tau=%.2fh RMSE=%.3f"
      % (hair, UAair, Tair + Q / UAair, C_of(0.128) / UAair / 3600,
         rmse(curve(time_s, h_air=hair, level=0.128))))

# ============================================================
# 図: 実験 vs ベース vs airのみフィット
# ============================================================
H = 3600.0
tt = np.linspace(0, 200000, 600)
fig, ax = plt.subplots(figsize=(9.5, 5.8))
for s in sensors:
    ax.plot(time_s / H, s, "o", markersize=3, alpha=0.3, color="gray")
ax.plot(time_s / H, exp_mean, "ks", markersize=5, label="実験 4センサ平均")
ax.plot(tt / H, curve(tt), "-", color="tab:blue", linewidth=2.0,
        label="ベース (h_air=10)  RMSE=%.2f" % rmse(base))
ax.plot(tt / H, curve(tt, h_air=hair, level=0.128), "-", color="tab:red", linewidth=2.4,
        label="airのみフィット (heatCeffToAir=%.2f)  RMSE=%.2f"
              % (hair, rmse(curve(time_s, h_air=hair, level=0.128))))
ax.set_xlabel("Time [h]", fontsize=12)
ax.set_ylabel("Temperature [degC]", fontsize=12)
ax.set_xlim(0, 200000 / H)
ax.set_ylim(23, 42)
ax.grid(True, alpha=0.4)
ax.legend(fontsize=9, loc="lower right")
ax.set_title("airのみで合わせ込み（heatCeffToAir だけ調整, level=0.128・Q=610固定）")
plt.tight_layout()
out = os.path.join(IMG, "fit_air_only.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print("\nsaved:", out)

# ============================================================
# 図: air + 水位 の良好フィット (RMSE 0.24) — 平均 | 非平均(tank1/2/3) の2枚並び
# ============================================================
from scipy.integrate import odeint


def per_tank(h_air, level):
    """各タンクの UA_i [W/K] と C_i [J/K] を返す。"""
    def g(Ain, Ac, Ag):
        return 1 / (1 / (10 * Ain) + 1 / (Ac * 80 / th) + 1 / (h_air * Ag))
    UA1 = h_air * A1 + g(A1 + Ly1_1 * level, A1 + Lx1_1 * level + Ly1_1 * level, A1 + Ly1_1 * level)
    A2in = A2 + Ly2_1 * level + Ly2_2 * level + Lx2_1 * level
    UA2 = h_air * A2 + g(A2in, Lx2_1 * Ly2_1 + Lx2_1 * level + Ly2_1 * level, A2in)
    A3g = A3 + Lx3_1 * level + Ly3_1 * level
    UA3 = h_air * A3 + g(A3g, A3g, A3g)
    C1 = A1 * level * rho_w * cp_w
    C2 = A2 * level * rho_w * cp_w
    C3 = A3 * 0.9 * level * rho_w * cp_w
    return (UA1, UA2, UA3), (C1, C2, C3)


def tanks_transient(h_air, level, mdot=1.83):
    """3タンク+循環(ループ 1->2->3->1, Qは循環水へ)の連成ODEを解き T1,T2,T3[degC]。"""
    (UA1, UA2, UA3), (C1, C2, C3) = per_tank(h_air, level)
    w = mdot * cp_w  # 循環の熱コンダクタンス [W/K]

    def f(T, t):
        T1, T2, T3 = T
        d1 = (w * (T3 - T1) - UA1 * (T1 - Tair) + Q) / C1
        d2 = (w * (T1 - T2) - UA2 * (T2 - Tair)) / C2
        d3 = (w * (T2 - T3) - UA3 * (T3 - Tair)) / C3
        return [d1, d2, d3]
    sol = odeint(f, [Tair, Tair, Tair], tt)
    return sol[:, 0], sol[:, 1], sol[:, 2]


T1, T2, T3 = tanks_transient(ha, lv)
Tmean_tanks = (T1 + T2 + T3) / 3.0
print("tank間温度差(飽和): max-min = %.3f degC (tank1=%.2f tank2=%.2f tank3=%.2f)"
      % (max(T1[-1], T2[-1], T3[-1]) - min(T1[-1], T2[-1], T3[-1]), T1[-1], T2[-1], T3[-1]))

fig, (axA, axB) = plt.subplots(1, 2, figsize=(14, 5.8))

# 左: 平均どうし
axA.plot(time_s / H, exp_mean, "ks", markersize=5, label="実験 4センサ平均")
axA.plot(tt / H, curve(tt), "-", color="tab:blue", linewidth=1.8,
         label="ベース  RMSE=%.2f" % rmse(base))
axA.plot(tt / H, Tmean_tanks, "-", color="tab:red", linewidth=2.4,
         label="OM 平均(tank1-3)  RMSE=%.2f"
               % np.sqrt(np.mean((np.interp(time_s, tt, Tmean_tanks) - exp_mean) ** 2)))
axA.set_title("平均どうし（実験4点平均 vs OM 3タンク平均）")
axA.set_xlabel("Time [h]"); axA.set_ylabel("Temperature [degC]")
axA.set_xlim(0, 200000 / H); axA.set_ylim(23, 40); axA.grid(True, alpha=0.4)
axA.legend(fontsize=9, loc="lower right")

# 右: 非平均（実測4センサ + OM tank1/2/3）
scol = {"4-16": "tab:blue", "4-17": "tab:orange", "4-18": "tab:green", "4-19": "tab:red"}
for name, s, c in zip(["4-16", "4-17", "4-18", "4-19"], sensors, scol.values()):
    axB.plot(time_s / H, s, "o", markersize=3.5, color=c, alpha=0.8, label="実験 " + name)
axB.plot(tt / H, T1, "-", color="k", linewidth=1.6, label="OM tank1")
axB.plot(tt / H, T2, "--", color="k", linewidth=1.6, label="OM tank2")
axB.plot(tt / H, T3, ":", color="k", linewidth=1.8, label="OM tank3")
axB.set_title("非平均（実測4点分布 vs OM tank1/2/3。OMは循環でほぼ均一）")
axB.set_xlabel("Time [h]"); axB.set_ylabel("Temperature [degC]")
axB.set_xlim(0, 200000 / H); axB.set_ylim(23, 40); axB.grid(True, alpha=0.4)
axB.legend(fontsize=8, loc="lower right", ncol=2)

plt.tight_layout()
out6 = os.path.join(IMG, "fit_air_level.png")
plt.savefig(out6, dpi=150, bbox_inches="tight")
print("saved:", out6)

# ============================================================
# 図: 実測 と OM の「平均からの偏差」を同一縦軸で比較
#     (OM絶対値は tank が重なり冗長なので省略。縦軸を揃えて公平に比較)
# ============================================================
Tmean3 = (T1 + T2 + T3) / 3.0
scol2 = {"4-16": "tab:blue", "4-17": "tab:orange", "4-18": "tab:green", "4-19": "tab:red"}
tcol = {"tank1": "tab:blue", "tank2": "tab:orange", "tank3": "tab:green"}
tank_spread = max(T1[-1], T2[-1], T3[-1]) - min(T1[-1], T2[-1], T3[-1])
DEV = 0.6   # 偏差の縦軸レンジ [degC] (実測・OM 共通)
TS = 16

figD, (aE, aO) = plt.subplots(1, 2, figsize=(17, 7), sharey=True)

# 実測: 平均からの偏差
for name, s, c in zip(scol2, sensors, scol2.values()):
    aE.plot(time_s / H, s - exp_mean, "-o", color=c, markersize=6, linewidth=2.0, label=name)
aE.axhline(0, color="k", lw=1.2, ls="--")
aE.set_ylabel("平均からの偏差 [degC]", fontsize=TS)
aE.set_title("実測 4センサ 場所ごとの偏差（振れ幅 ±0.5℃）", fontsize=TS)
aE.legend(fontsize=13, loc="upper right")

# OM: 平均からの偏差 (同一縦軸)
for name, T, c in zip(tcol, [T1, T2, T3], tcol.values()):
    aO.plot(tt / H, T - Tmean3, "-", color=c, linewidth=2.6, label=name)
aO.axhline(0, color="k", lw=1.2, ls="--")
aO.set_title("OM tank1/2/3 の偏差（同一縦軸だとほぼ平坦＝均一, 実差 %.3f℃）" % tank_spread,
             fontsize=TS)
aO.legend(fontsize=13, loc="upper right")

for a in (aE, aO):
    a.set_xlabel("Time [h]", fontsize=TS)
    a.set_xlim(0, 200000 / H); a.set_ylim(-DEV, DEV)
    a.grid(True, alpha=0.4); a.tick_params(labelsize=13)
figD.suptitle("平均からの偏差 比較（縦軸を統一）: 実測は場所で ±0.5℃, OM タンク間はほぼ 0",
              fontsize=TS + 3, y=1.02)
plt.tight_layout()
outD = os.path.join(IMG, "by_location_exp_vs_OM.png")
plt.savefig(outD, dpi=150, bbox_inches="tight")
print("saved:", outD)
