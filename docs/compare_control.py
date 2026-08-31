# -*- coding: utf-8 -*-
"""
温度管理あり／なし の比較（実機 OpenModelica 結果）。

同一モデル ana003_Tank3blocks_cyclononly.mo を、PID ゲインだけ変えて 2 通り実行:
  - 管理あり: -override PID_Treg.k=100   -> OM/_ctrl/res_on.csv
  - 管理なし: -override PID_Treg.k=0     -> OM/_ctrl/res_off.csv
本スクリプトは両者の水温（tank1/2/3 平均）を「あり=青／なし=赤」で重ね描きする。

  python docs/compare_control.py
"""
import os
import glob
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

for cand in ["~/.fonts/NotoSansCJKjp-Regular.otf",
             "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
             "C:/Windows/Fonts/meiryo.ttc", "C:/Windows/Fonts/YuGothR.ttc"]:
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
ROOT = os.path.dirname(HERE)
CTRL = os.path.join(ROOT, "OM")
IMG2 = os.path.join(HERE, "img", "002")
os.makedirs(IMG2, exist_ok=True)
H = 3600.0


def tank_mean_C(csv):
    df = pd.read_csv(csv)
    t = df["time"].to_numpy(float)
    cols = [c for c in df.columns if c.endswith("medium.T")]
    K = df[cols].to_numpy(float)
    return t, K.mean(axis=1) - 273.15


def main():
    on = os.path.join(CTRL, "_ctrl_on.csv")
    off = os.path.join(CTRL, "_ctrl_off.csv")
    fig, ax = plt.subplots(figsize=(10, 6))
    if os.path.exists(off):
        t, T = tank_mean_C(off)
        ax.plot(t / H, T, "-", color="tab:red", linewidth=2.4, label="温度管理なし (PID k=0)")
        print("なし 飽和: %.2f degC" % T[-1])
    if os.path.exists(on):
        t, T = tank_mean_C(on)
        ax.plot(t / H, T, "-", color="tab:blue", linewidth=2.4, label="温度管理あり (PID k=100, 目標25℃)")
        print("あり 終値: %.2f degC" % T[-1])
    ax.axhline(25.0, color="0.5", ls=":", lw=1.2, label="目標 25℃")
    ax.set_xlabel("Time [h]", fontsize=13); ax.set_ylabel("水温 (tank1/2/3 平均) [degC]", fontsize=13)
    ax.grid(True, alpha=0.4); ax.legend(fontsize=12)
    ax.set_title("温度管理あり／なし の比較（同一モデル・PIDゲインのみ変更, 実機OM）", fontsize=13)
    plt.tight_layout()
    out = os.path.join(IMG2, "compare_control.png")
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print("saved:", out)


if __name__ == "__main__":
    main()
