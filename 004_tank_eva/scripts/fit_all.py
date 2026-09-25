# -*- coding: utf-8 -*-
"""
fit_all.py  —  ana006 各評価(eva)の実測を集中定数(1次遅れ)モデルで同定し、
比較図と同定パラメータ表を出力する。

集中定数モデル:  C dT/dt = Q - UA (T - Tamb)
解:  T(t) = Tss + (T0 - Tss) exp(-t/tau),  Tss = Tamb + Q/UA,  tau = C/UA

各evaごとに水温センサ平均 Tw(t) に対して (Tss, tau, T0) をフィットし、
飽和温度 Tss・時定数 tau・当てはまり RMSE を求める。
実行: python fit_all.py   (docs/ で実行)
出力: 各 eva フォルダに fit_lumped.png、docs/img に一覧、docs に summary CSV
"""
import os
import csv
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from scipy.optimize import curve_fit

matplotlib.use("Agg")
# 日本語フォント
for fp in ["/home/kamakiri/.fonts/NotoSansCJKjp-Regular.otf",
           "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]:
    if os.path.exists(fp):
        fm.fontManager.addfont(fp)
        plt.rcParams["font.family"] = fm.FontProperties(fname=fp).get_name()
        break
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, "docs")
os.makedirs(os.path.join(DOCS, "img"), exist_ok=True)

# eva定義: (フォルダ, CSV, 水温センサ列, 外気列 or None, 既定外気温, モデル名, 既知Q[W])
EVA = {
    "eva1": dict(csv="temperature_20points_without_NC_T7.csv",
                 water=["2-1", "2-9", "2-3", "2-17", "2-22", "2-21"],
                 amb=None, Tamb=19.5, model="ana002 (機内+ミスト)", Q=None),
    "eva2": dict(csv="temperature_20points_without_NC_T7.csv",
                 water=["2-1", "2-9", "2-3", "2-17", "2-22", "2-21"],
                 amb=None, Tamb=19.5, model="ana002 (機内+ミスト)", Q=None),
    "eva4": dict(csv="temperature_20points_without_NC_T7.csv",
                 water=["4-16", "4-17", "4-18", "4-19"],
                 amb=None, Tamb=24.5, model="ana003 TempCtrl (温度管理あり)", Q=None),
    "eva5": dict(csv="temperature_20points.csv",
                 water=["4-16", "4-17", "4-18", "4-19"],
                 amb="4-9", Tamb=24.5, model="ana003 NoTemp (温度管理なし)", Q=610.0),
}

# 集中定数の熱容量推定用（3槽の水; ana003ベース幾何, 有効水位はeva5合わせこみ値）
CROSS_AREA = 0.903*0.479 + (1.191*1.670 + 0.478*0.337) + 0.573*1.191  # m^2
LEVEL_EFF = 0.0755   # eva5合わせこみの有効水位 [m]
CP_W = 4186.0
RHO_W = 992.0


def read_csv(path, cols):
    with open(path, encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        rows = list(r)
    t = np.array([float(x["Time [s]"]) for x in rows])
    data = {c: np.array([float(x[c]) for x in rows]) for c in cols}
    return t, data, rows


def model_T(t, Tss, tau, T0):
    return Tss + (T0 - Tss) * np.exp(-t / tau)


summary = []
COL = {"eva1": "tab:blue", "eva2": "tab:orange", "eva4": "tab:green", "eva5": "tab:red"}
fig_all, axes = plt.subplots(2, 2, figsize=(14, 9), dpi=130)
axes = axes.ravel()

for i, (e, m) in enumerate(EVA.items()):
    csv_path = os.path.join(ROOT, e, "data", m["csv"])
    allcols = list(m["water"]) + ([m["amb"]] if m["amb"] else [])
    t, data, _ = read_csv(csv_path, allcols)
    Tw = np.mean([data[c] for c in m["water"]], axis=0)
    Tamb = float(np.mean(data[m["amb"]])) if m["amb"] else m["Tamb"]

    # フィット
    T0_guess = Tw[0]
    Tss_guess = Tw[-1] + (Tw[-1] - Tw[0]) * 0.2
    tau_guess = max(t[-1] / 3.0, 1.0)
    try:
        popt, _ = curve_fit(model_T, t, Tw,
                            p0=[Tss_guess, tau_guess, T0_guess],
                            bounds=([Tw[0]-5, 1.0, Tw[0]-5],
                                    [Tw[-1]+60, 5e6, Tw[0]+5]),
                            maxfev=20000)
        Tss, tau, T0 = popt
    except Exception as ex:
        Tss, tau, T0 = Tss_guess, tau_guess, T0_guess
        print(e, "fit fallback:", ex)

    tf = np.linspace(0, t[-1], 400)
    Tfit = model_T(tf, Tss, tau, T0)
    rmse = float(np.sqrt(np.mean((model_T(t, Tss, tau, T0) - Tw)**2)))

    # 有効UA, C, Q の逆算（C=有効水質量*cp を仮定）
    C = CROSS_AREA * LEVEL_EFF * RHO_W * CP_W
    UA = C / tau
    Q_ident = UA * (Tss - Tamb)
    summary.append(dict(eva=e, model=m["model"], N=len(t), t_end=t[-1],
                        T0=T0, Tamb=Tamb, Tss=Tss, dT=Tss-Tamb,
                        tau_s=tau, tau_h=tau/3600.0, rmse=rmse,
                        C=C, UA=UA, Q_ident=Q_ident, Q_known=m["Q"]))

    ax = axes[i]
    for c in m["water"]:
        ax.plot(t/3600, data[c], "-", lw=0.8, alpha=0.5)
    ax.plot(t/3600, Tw, "o", color=COL[e], ms=5, label="実測 水温平均")
    if m["amb"]:
        ax.plot(t/3600, data[m["amb"]], "--", color="gray", lw=1.2, label=f"外気 {m['amb']}")
    ax.plot(tf/3600, Tfit, "-", color="k", lw=2,
            label=f"1次遅れフィット\nTss={Tss:.1f}°C, τ={tau/3600:.1f}h\nRMSE={rmse:.2f}°C")
    ax.set_title(f"{e}  ({m['model']})", fontsize=13)
    ax.set_xlabel("経過時間 [h]"); ax.set_ylabel("温度 [°C]")
    ax.grid(True, alpha=0.3); ax.legend(fontsize=9, loc="best")

    # 各evaフォルダにも個別図
    figi, axi = plt.subplots(figsize=(8, 5), dpi=130)
    for c in m["water"]:
        axi.plot(t/3600, data[c], "-", lw=0.9, alpha=0.5, label=c)
    axi.plot(t/3600, Tw, "o", color=COL[e], ms=5, label="水温平均")
    if m["amb"]:
        axi.plot(t/3600, data[m["amb"]], "--", color="gray", lw=1.2, label=f"外気{m['amb']}")
    axi.plot(tf/3600, Tfit, "k-", lw=2, label=f"fit Tss={Tss:.1f} τ={tau/3600:.1f}h RMSE={rmse:.2f}")
    axi.set_title(f"{e} 実測と1次遅れ同定"); axi.set_xlabel("経過時間 [h]"); axi.set_ylabel("温度 [°C]")
    axi.grid(True, alpha=0.3); axi.legend(fontsize=8)
    figi.tight_layout()
    figi.savefig(os.path.join(ROOT, e, "fit_lumped.png"))
    plt.close(figi)

fig_all.suptitle("ana006 各評価 実測水温と集中定数(1次遅れ)同定", fontsize=15)
fig_all.tight_layout(rect=[0, 0, 1, 0.98])
fig_all.savefig(os.path.join(DOCS, "img", "eva_all_fits.png"))

# summary CSV
with open(os.path.join(DOCS, "eva_summary.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["eva", "model", "N", "t_end_s", "T0_C", "Tamb_C", "Tss_C", "dT_C",
                "tau_s", "tau_h", "rmse_C", "C_J/K", "UA_W/K", "Q_ident_W", "Q_known_W"])
    for s in summary:
        w.writerow([s["eva"], s["model"], s["N"], f'{s["t_end"]:.0f}', f'{s["T0"]:.2f}',
                    f'{s["Tamb"]:.2f}', f'{s["Tss"]:.2f}', f'{s["dT"]:.2f}',
                    f'{s["tau_s"]:.0f}', f'{s["tau_h"]:.2f}', f'{s["rmse"]:.3f}',
                    f'{s["C"]:.3e}', f'{s["UA"]:.2f}', f'{s["Q_ident"]:.1f}',
                    "" if s["Q_known"] is None else f'{s["Q_known"]:.0f}'])

print("=== eva 同定結果 ===")
print(f'{"eva":5} {"Tamb":>6} {"Tss":>6} {"dT":>6} {"tau[h]":>7} {"RMSE":>6} {"UA[W/K]":>8} {"Q_ident[W]":>10}')
for s in summary:
    print(f'{s["eva"]:5} {s["Tamb"]:6.1f} {s["Tss"]:6.1f} {s["dT"]:6.1f} {s["tau_h"]:7.2f} '
          f'{s["rmse"]:6.2f} {s["UA"]:8.1f} {s["Q_ident"]:10.1f}')
