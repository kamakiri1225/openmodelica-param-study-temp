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
# 図: air + 水位 の良好フィット (RMSE 0.24)
# ============================================================
fig, ax = plt.subplots(figsize=(9.5, 5.8))
for s in sensors:
    ax.plot(time_s / H, s, "o", markersize=3, alpha=0.3, color="gray")
ax.plot(time_s / H, exp_mean, "ks", markersize=5, label="実験 4センサ平均")
ax.plot(tt / H, curve(tt), "-", color="tab:blue", linewidth=2.0,
        label="ベース (h_air=10, level=0.128)  RMSE=%.2f" % rmse(base))
ax.plot(tt / H, curve(tt, h_air=ha, level=lv), "-", color="tab:red", linewidth=2.4,
        label="フィット (h_air=%.2f, level=%.3f)  RMSE=%.2f"
              % (ha, lv, rmse(curve(time_s, h_air=ha, level=lv))))
ax.set_xlabel("Time [h]", fontsize=12)
ax.set_ylabel("Temperature [degC]", fontsize=12)
ax.set_xlim(0, 200000 / H)
ax.set_ylim(23, 40)
ax.grid(True, alpha=0.4)
ax.legend(fontsize=9, loc="lower right")
ax.set_title("air＋水位で合わせ込み（heatCeffToAir・level_start 調整, Q=610固定）")
plt.tight_layout()
out6 = os.path.join(IMG, "fit_air_level.png")
plt.savefig(out6, dpi=150, bbox_inches="tight")
print("saved:", out6)
