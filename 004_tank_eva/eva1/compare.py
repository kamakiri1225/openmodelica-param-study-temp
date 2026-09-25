# -*- coding: utf-8 -*-
"""eva1: OpenModelica 結果と実測の比較。
先に run_sim.mos を実行して ana002_Tank3blocks_002_machineAreaTankMist_NoTemp_res.csv を生成しておく。
OM結果が無ければ実測のみ描画する。"""
import os, csv
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

for fp in [r"C:\Windows\Fonts\meiryo.ttc", r"C:\Windows\Fonts\YuGothM.ttc",
           "/home/kamakiri/.fonts/NotoSansCJKjp-Regular.otf"]:
    if os.path.exists(fp):
        fm.fontManager.addfont(fp); plt.rcParams["font.family"]=fm.FontProperties(fname=fp).get_name(); break
plt.rcParams["axes.unicode_minus"]=False

HERE=os.path.dirname(os.path.abspath(__file__))
WATER=['2-1', '2-9', '2-3', '2-17', '2-22', '2-21']
AMB=None
EXP=os.path.join(HERE,"data","temperature_20points_without_NC_T7.csv")
OMRES=os.path.join(HERE,"ana002_Tank3blocks_002_machineAreaTankMist_NoTemp_res.csv")

def read_csv(path):
    with open(path,encoding="utf-8-sig") as f:
        rows=list(csv.DictReader(f))
    return rows

# 実測
rows=read_csv(EXP)
te=np.array([float(r["Time [s]"]) for r in rows])
Tw_exp=np.mean([[float(r[c]) for r in rows] for c in WATER],axis=0)

fig,ax=plt.subplots(figsize=(10,6),dpi=130)
for c in WATER:
    ax.plot(te/3600,[float(r[c]) for r in rows],"-",lw=0.8,alpha=0.4)
ax.plot(te/3600,Tw_exp,"o",color="tab:red",ms=5,label="実測 水温平均")
if AMB:
    ax.plot(te/3600,[float(r[AMB]) for r in rows],"--",color="gray",lw=1.2,label=f"外気 {AMB}")

rmse_txt=""
if os.path.exists(OMRES):
    orows=read_csv(OMRES)
    to=np.array([float(r["time"]) for r in orows])
    Tsim=np.mean([[float(r[k])-273.15 for r in orows]
                  for k in ["tank1.medium.T","tank2.medium.T","tank3.medium.T"]],axis=0)
    ax.plot(to/3600,Tsim,"-",color="k",lw=2,label="OM計算 (tank平均)")
    sim_at_exp=np.interp(te,to,Tsim)
    rmse=float(np.sqrt(np.mean((sim_at_exp-Tw_exp)**2)))
    rmse_txt=f"  RMSE={rmse:.2f}°C"
    print(f"eva1 RMSE={rmse:.3f} degC")
else:
    print("OM結果CSVが見つかりません。先に run_sim.mos を実行してください:",OMRES)

ax.set_title("eva1 OM計算 vs 実測"+rmse_txt)
ax.set_xlabel("経過時間 [h]"); ax.set_ylabel("温度 [°C]")
ax.grid(True,alpha=0.3); ax.legend(fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(HERE,"compare_OM_vs_exp.png"))
print("saved:", os.path.join(HERE,"compare_OM_vs_exp.png"))
