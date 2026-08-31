# -*- coding: utf-8 -*-
r"""
Windows の Python + OpenModelica(omc.exe) でパラメータスタディを一気通貫実行する。

前提:
  - Windows に OpenModelica がインストール済み
      既定: C:\Program Files\OpenModelica1.26.3-64bit\bin\omc.exe
      環境変数 OMC でパス上書き可
  - モデル OM/ana003_Tank3blocks_cyclononly_NoTemp.mo に
      parameter Real Q_cyclone = 610;  があること (追加済み)

処理:
  1) doe.csv (param_study.py gen で作成) を読む
  2) 各ケースを omc.exe で実行 (-override で5因子を上書き)
  3) タンク水温を取り出し T_final / tau / rmse を計算
  4) 実験と重ねた連番比較図 docs/img/compare_XXX.png を保存
  5) results.csv を出力 (-> param_study.py pareto で解析)

使い方 (data フォルダ内で):
  python param_study.py gen --n 30      # 先に doe.csv を作る
  python run_study.py                    # doe.csv を回す
  python param_study.py pareto --csv results.csv
"""
import os
import sys
import glob
import subprocess
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ---- 日本語フォント (あれば) ----
for cand in ["C:/Windows/Fonts/meiryo.ttc", "C:/Windows/Fonts/YuGothR.ttc",
             "C:/Windows/Fonts/msgothic.ttc", "~/.fonts/NotoSansCJKjp-Regular.otf",
             "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"]:
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

# ============================================================
# パス設定
# ============================================================
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MODEL_FILE = os.path.join(ROOT, "OM", "ana003_Tank3blocks_cyclononly_NoTemp.mo")
MODEL = "ana003_Tank3blocks_cyclononly_NoTemp"
IMG = os.path.join(ROOT, "docs", "img")
WORK = os.path.join(HERE, "_work")
os.makedirs(IMG, exist_ok=True)
os.makedirs(WORK, exist_ok=True)

OMC = os.environ.get("OMC", r"C:\Program Files\OpenModelica1.26.3-64bit\bin\omc.exe")

# ============================================================
# 実験データ (eva5.py, 2026-07-09)
# ============================================================
time_s = np.array([
    0, 5263, 10526, 15789, 21053, 26316, 31579, 36842, 42105, 47368,
    52632, 57895, 63158, 68421, 73684, 78947, 84211, 89474, 94737, 100000
], dtype=float)
_exp = {
    "4-16": [23.8, 27.8, 29.8, 31.2, 32.4, 33.4, 34.3, 35.0, 35.5, 36.0,
             36.4, 36.7, 37.0, 37.2, 37.35, 37.40, 37.50, 37.60, 37.65, 37.70],
    "4-17": [24.0, 28.0, 30.1, 31.5, 32.7, 33.7, 34.5, 35.2, 35.8, 36.2,
             36.6, 36.9, 37.15, 37.35, 37.50, 37.55, 37.60, 37.70, 37.75, 37.80],
    "4-18": [24.2, 28.4, 30.5, 31.9, 33.0, 34.0, 34.8, 35.5, 36.0, 36.4,
             36.8, 37.1, 37.35, 37.55, 37.70, 37.65, 37.75, 37.80, 37.85, 37.90],
    "4-19": [23.7, 27.6, 29.6, 31.0, 32.2, 33.2, 34.1, 34.8, 35.4, 35.8,
             36.2, 36.5, 36.8, 37.0, 37.15, 37.20, 37.30, 37.40, 37.45, 37.50],
}
exp_mean = np.mean(np.vstack([np.array(v, float) for v in _exp.values()]), axis=0)
Tair = 24.5


def run_case(case, Q, h_air, h_in, kground, level):
    """1ケースを omc.exe で実行し、時刻・OM平均水温[degC]を返す。"""
    mos_path = os.path.join(WORK, f"case_{case:03d}.mos")
    # omc.exe は Windows バイナリなので、WSL パス(/mnt/f/..)を Windows パス(F:/..)へ変換
    try:
        model_fwd = subprocess.check_output(["wslpath", "-m", MODEL_FILE]).decode().strip()
    except Exception:
        model_fwd = MODEL_FILE.replace("\\", "/")
    override = (f"Q_cyclone={Q:.4f},heatCeffToAir={h_air:.5f},"
                f"heatCefftTank2in={h_in:.5f},kground={kground:.4f},"
                f"level_start={level:.5f}")
    mos = f'''loadModel(Modelica); getErrorString();
loadFile("{model_fwd}"); getErrorString();
simulate({MODEL}, stopTime=200000, numberOfIntervals=2000,
  outputFormat="csv",
  variableFilter="time|tank1.medium.T|tank2.medium.T|tank3.medium.T",
  simflags="-override {override}");
getErrorString();
'''
    with open(mos_path, "w", encoding="utf-8") as f:
        f.write(mos)

    subprocess.run([OMC, os.path.basename(mos_path)], cwd=WORK,
                   capture_output=True, text=True)

    res = os.path.join(WORK, f"{MODEL}_res.csv")
    if not os.path.exists(res):
        raise RuntimeError(f"case {case}: 結果CSVが生成されませんでした ({res})。"
                           f"omc パス / モデルを確認してください。")
    df = pd.read_csv(res)
    t = df["time"].to_numpy(float)
    cols = [c for c in df.columns if c.endswith(".T")]
    K = df[cols].to_numpy(float)
    om_C = K.mean(axis=1) - 273.15   # 3タンク平均を代表水温[degC]へ
    # 同名結果を次ケースが上書きするので退避
    os.replace(res, os.path.join(WORK, f"{MODEL}_res_{case:03d}.csv"))
    return t, om_C


def responses(t, om_C):
    """T_final, tau, rmse(実験平均比) を計算。"""
    T_final = float(om_C[-1])   # 十分な stopTime での飽和温度
    target = Tair + 0.632 * (T_final - Tair)
    idx = np.argmax(om_C >= target) if np.any(om_C >= target) else len(om_C) - 1
    tau = float(t[idx])
    om_at_exp = np.interp(time_s, t, om_C)
    rmse = float(np.sqrt(np.mean((om_at_exp - exp_mean) ** 2)))
    return T_final, tau, rmse


def plot_case(case, t, om_C, params, rmse):
    H = 3600.0
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.plot(time_s / H, exp_mean, "ks", markersize=5, label="実験 4センサ平均")
    lbl = (f"OM #{case:03d} "
           f"(Q={params['Q']:.0f}, h_air={params['h_air']:.1f}, "
           f"level={params['level']:.3f})")
    ax.plot(t / H, om_C, "-", color="tab:red", linewidth=2.0, label=lbl)
    ax.set_xlabel("Time [h]"); ax.set_ylabel("Temperature [degC]")
    ax.set_xlim(0, t[-1] / H); ax.set_ylim(23, 40); ax.grid(True, alpha=0.4)
    ax.legend(fontsize=9, loc="lower right")
    ax.set_title(f"{case:03d}: 実験 vs OM  (RMSE={rmse:.2f} degC)")
    plt.tight_layout()
    out = os.path.join(IMG, f"compare_{case:03d}.png")
    plt.savefig(out, dpi=150, bbox_inches="tight"); plt.close()
    return out


def main():
    doe_path = os.path.join(HERE, "doe.csv")
    if not os.path.exists(doe_path):
        print("doe.csv がありません。先に:  python param_study.py gen --n 30")
        sys.exit(1)
    doe = pd.read_csv(doe_path)
    print(f"omc      : {OMC}")
    print(f"model    : {MODEL_FILE}")
    print(f"cases    : {len(doe)}\n")

    rows = []
    for _, r in doe.iterrows():
        case = int(r["case"])
        params = dict(Q=r["Q"], h_air=r["h_air"], h_in=r["h_in"],
                      kground=r["kground"], level=r["level"])
        try:
            t, om_C = run_case(case, **params)
            T_final, tau, rmse = responses(t, om_C)
            png = plot_case(case, t, om_C, params, rmse)
            print(f"#{case:03d}  T_final={T_final:5.2f}  tau={tau/3600:5.2f}h  "
                  f"rmse={rmse:5.2f}  -> {os.path.basename(png)}")
            rows.append({**{"case": case}, **params,
                         "T_final": T_final, "tau": tau, "rmse": rmse})
        except Exception as e:
            print(f"#{case:03d}  失敗: {e}")

    out = pd.DataFrame(rows)
    res_csv = os.path.join(HERE, "results.csv")
    out.to_csv(res_csv, index=False)
    print(f"\nresults.csv を出力: {res_csv}")
    if len(out):
        best = out.loc[out["rmse"].idxmin()]
        print(f"最小RMSE: #{int(best['case']):03d}  rmse={best['rmse']:.2f}  "
              f"Q={best['Q']:.0f} h_air={best['h_air']:.1f} level={best['level']:.3f}")
    print("\n次:  python param_study.py pareto --csv results.csv")


if __name__ == "__main__":
    main()
