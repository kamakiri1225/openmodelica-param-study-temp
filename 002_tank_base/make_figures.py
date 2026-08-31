# -*- coding: utf-8 -*-
"""
ドキュメント用の図を生成する。

OpenModelica は Windows で実行するため、ここでは同じ支配方程式の
「集中定数解析解」を OM 相当のベースラインとして用い、
  - fig001: 実験 vs OM相当(ベース)
  - fig002: Q を変えたときの変化 (実験・ベース重畳)
  - fig003: 初期水位 level を変えたとき (実験・ベース重畳)
  - fig004: 外気側熱伝達率 h_air を変えたとき (実験・ベース重畳)
を docs/img/ に出力する。

  python docs/make_figures.py

実測CSV(OM結果)が用意できたら data/compare_OM_vs_exp.py で
実データ版の連番比較図(compare_001.png ...)を作成する。
"""
import os
import glob
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 日本語フォント登録 (見つからなければ既定のまま)
for cand in ["~/.fonts/NotoSansCJKjp-Regular.otf",
             "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
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
IMG = os.path.join(HERE, "docs", "img")
IMG1 = IMG
IMG2 = IMG
os.makedirs(IMG1, exist_ok=True)
os.makedirs(IMG2, exist_ok=True)

# ============================================================
# 実験データ (eva5.py, 2026-07-09)
# ============================================================
time_s = np.array([
    0, 5263, 10526, 15789, 21053, 26316, 31579, 36842, 42105, 47368,
    52632, 57895, 63158, 68421, 73684, 78947, 84211, 89474, 94737, 100000
], dtype=float)
exp = {
    "4-16": [23.8, 27.8, 29.8, 31.2, 32.4, 33.4, 34.3, 35.0, 35.5, 36.0,
             36.4, 36.7, 37.0, 37.2, 37.35, 37.40, 37.50, 37.60, 37.65, 37.70],
    "4-17": [24.0, 28.0, 30.1, 31.5, 32.7, 33.7, 34.5, 35.2, 35.8, 36.2,
             36.6, 36.9, 37.15, 37.35, 37.50, 37.55, 37.60, 37.70, 37.75, 37.80],
    "4-18": [24.2, 28.4, 30.5, 31.9, 33.0, 34.0, 34.8, 35.5, 36.0, 36.4,
             36.8, 37.1, 37.35, 37.55, 37.70, 37.65, 37.75, 37.80, 37.85, 37.90],
    "4-19": [23.7, 27.6, 29.6, 31.0, 32.2, 33.2, 34.1, 34.8, 35.4, 35.8,
             36.2, 36.5, 36.8, 37.0, 37.15, 37.20, 37.30, 37.40, 37.45, 37.50],
}
exp = {k: np.array(v, float) for k, v in exp.items()}
exp_mean = np.mean(np.vstack(list(exp.values())), axis=0)

# ============================================================
# 集中定数モデル (ana003_Tank3blocks_cyclononly_NoTemp.mo と同じ式)
# ============================================================
Tair = 24.5
rho_w, cp_w = 1000.0, 4186.0
th = 2.3 / 1000
Lx1_1, Ly1_1 = 0.903, 0.479
Lx2_1, Lx2_2, Ly2_1, Ly2_2 = 1.191, 0.478, 1.670, 0.337
Lx3_1, Ly3_1 = 0.573, 1.191
A1 = Lx1_1 * Ly1_1
A2 = Lx2_1 * Ly2_1 + Lx2_2 * Ly2_2
A3 = Lx3_1 * Ly3_1

# 基準パラメータ
BASE = dict(Q=610.0, h_air=10.0, h_in=10.0, kground=80.0, level=0.128)


def UA_of(h_air, h_in, kground, level):
    UA_air = h_air * (A1 + A2 + A3)

    def g(A_in, A_cond, A_g):
        R = 1 / (h_in * A_in) + 1 / (A_cond * kground / th) + 1 / (h_air * A_g)
        return 1 / R
    UAg1 = g(A1 + Ly1_1 * level, A1 + Lx1_1 * level + Ly1_1 * level, A1 + Ly1_1 * level)
    A2in = A2 + Ly2_1 * level + Ly2_2 * level + Lx2_1 * level
    UAg2 = g(A2in, Lx2_1 * Ly2_1 + Lx2_1 * level + Ly2_1 * level, A2in)
    A3g = A3 + Lx3_1 * level + Ly3_1 * level
    UAg3 = g(A3g, A3g, A3g)
    return UA_air + UAg1 + UAg2 + UAg3


def C_of(level):
    m = (A1 * level + A2 * level + A3 * 0.9 * level) * rho_w
    return m * cp_w


def temp(t, Q=None, h_air=None, h_in=None, kground=None, level=None):
    p = dict(BASE)
    for k, v in dict(Q=Q, h_air=h_air, h_in=h_in, kground=kground, level=level).items():
        if v is not None:
            p[k] = v
    UA = UA_of(p["h_air"], p["h_in"], p["kground"], p["level"])
    C = C_of(p["level"])
    tau = C / UA
    return Tair + (p["Q"] / UA) * (1 - np.exp(-t / tau))


H = 3600.0          # s -> h
TMAX_S = 200000.0   # OM は飽和まで見えるよう ~56h まで描画（実験は 100000s まで）
TMAX_H = TMAX_S / H
tt = np.linspace(0, TMAX_S, 600)


def plot_exp(ax, mean_only=False):
    if not mean_only:
        for k, v in exp.items():
            ax.plot(time_s / H, v, "o", markersize=3, alpha=0.35, color="gray")
    ax.plot(time_s / H, exp_mean, "ks", markersize=5, label="実験 4センサ平均")


def finish(ax, title, fname):
    ax.set_xlabel("Time [h]", fontsize=12)
    ax.set_ylabel("Temperature [degC]", fontsize=12)
    ax.set_xlim(0, TMAX_H)
    ax.set_ylim(23, 40)
    ax.grid(True, alpha=0.4)
    ax.legend(fontsize=9, loc="lower right")
    ax.set_title(title, fontsize=12)
    plt.tight_layout()
    out = os.path.join(IMG, fname)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print("saved:", out)
    plt.close()


# ---- fig000: 実験センサの場所ごとの違い (絶対値 + 平均からの偏差) ----
colors = {"4-16": "tab:blue", "4-17": "tab:orange",
          "4-18": "tab:green", "4-19": "tab:red"}
fig, (axL, axR) = plt.subplots(1, 2, figsize=(13, 5.5))
for k, v in exp.items():
    axL.plot(time_s / H, v, "-o", color=colors[k], markersize=4, linewidth=1.5, label=k)
axL.plot(time_s / H, exp_mean, "k--", linewidth=1.5, label="4点平均")
axL.set_xlabel("Time [h]"); axL.set_ylabel("Temperature [degC]")
axL.set_xlim(0, time_s[-1] / H); axL.grid(True, alpha=0.4)
axL.legend(fontsize=9, loc="lower right")
axL.set_title("実験センサ 場所ごとの温度")
for k, v in exp.items():
    axR.plot(time_s / H, v - exp_mean, "-o", color=colors[k], markersize=4,
             linewidth=1.5, label=k)
axR.axhline(0, color="k", linewidth=1.0, linestyle="--")
axR.set_xlabel("Time [h]"); axR.set_ylabel("平均からの偏差 [degC]")
axR.set_xlim(0, time_s[-1] / H); axR.grid(True, alpha=0.4)
axR.legend(fontsize=9, loc="upper right")
axR.set_title("平均からの偏差 (場所差を拡大)")
plt.tight_layout()
_out = os.path.join(IMG1, "exp_by_location.png")
plt.savefig(_out, dpi=150, bbox_inches="tight"); plt.close()
print("saved:", _out)

# ---- fig001: 実験 vs OM相当(ベース) ----
fig, ax = plt.subplots(figsize=(9, 5.5))
plot_exp(ax)
ax.plot(tt / H, temp(tt), "-", color="tab:red", linewidth=2.2,
        label="OM相当ベース (Q=610, h_air=10, level=0.128)")
finish(ax, "001: 実験 vs OM相当ベースライン", "001/exp_vs_OM_base.png")

# ---- fig002: Q を変える ----
fig, ax = plt.subplots(figsize=(9, 5.5))
plot_exp(ax, mean_only=True)
ax.plot(tt / H, temp(tt), "--", color="black", linewidth=1.8, label="ベース Q=610")
for Q, c in zip([550, 650, 690, 750], ["tab:blue", "tab:green", "tab:orange", "tab:red"]):
    ax.plot(tt / H, temp(tt, Q=Q), "-", color=c, linewidth=1.8, label=f"Q={Q} W")
finish(ax, "Q(投入熱)の影響 — 飽和温度が上下", "002/vary_Q.png")

# ---- fig003: level を変える ----
fig, ax = plt.subplots(figsize=(9, 5.5))
plot_exp(ax, mean_only=True)
ax.plot(tt / H, temp(tt), "--", color="black", linewidth=1.8, label="ベース level=0.128")
for lv, c in zip([0.09, 0.11, 0.14, 0.16], ["tab:blue", "tab:green", "tab:orange", "tab:red"]):
    ax.plot(tt / H, temp(tt, level=lv), "-", color=c, linewidth=1.8, label=f"level={lv:.2f} m")
finish(ax, "level(水量)の影響 — 応答の速さ(時定数)が変化", "002/vary_level.png")

# ---- fig004: h_air を変える ----
fig, ax = plt.subplots(figsize=(9, 5.5))
plot_exp(ax, mean_only=True)
ax.plot(tt / H, temp(tt), "--", color="black", linewidth=1.8, label="ベース h_air=10")
for h, c in zip([6, 8, 14, 18], ["tab:blue", "tab:green", "tab:orange", "tab:red"]):
    ax.plot(tt / H, temp(tt, h_air=h), "-", color=c, linewidth=1.8, label=f"h_air={h}")
finish(ax, "h_air(外気放熱)の影響 — 飽和温度と速さの両方", "002/vary_h_air.png")

print("\n完了: docs/img/ に4枚出力しました。")
