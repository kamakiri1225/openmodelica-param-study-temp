# -*- coding: utf-8 -*-
"""eva4: 温度管理モデル(ana001_Tank_004)のOM結果と実測(4-x)を比較。
先に run_sim.mos を実行して ana001_Tank_004_res.csv を生成しておく。"""
import os, csv
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
for fp in [r"C:\Windows\Fonts\meiryo.ttc","/home/kamakiri/.fonts/NotoSansCJKjp-Regular.otf"]:
    if os.path.exists(fp):
        fm.fontManager.addfont(fp); plt.rcParams["font.family"]=fm.FontProperties(fname=fp).get_name(); break
plt.rcParams["axes.unicode_minus"]=False
HERE=os.path.dirname(os.path.abspath(__file__))
rows=list(csv.DictReader(open(os.path.join(HERE,"data","temperature_20points_without_NC_T7.csv"),encoding="utf-8-sig")))
te=np.array([float(r["Time [s]"]) for r in rows]); Te=np.mean([[float(r[c]) for r in rows] for c in ["4-16","4-17","4-18","4-19"]],axis=0)
fig,ax=plt.subplots(figsize=(10,6),dpi=130)
for c in ["4-16","4-17","4-18","4-19"]:
    ax.plot(te/3600,[float(r[c]) for r in rows],"-",lw=0.8,alpha=0.4)
ax.plot(te/3600,Te,"s",color="#1f77b4",ms=5,label="実測 水温平均(eva4)")
res=os.path.join(HERE,"ana001_Tank_004_res.csv")
if os.path.exists(res):
    orows=list(csv.DictReader(open(res,encoding="utf-8-sig")))
    to=np.array([float(r["time"]) for r in orows])
    Ts=np.mean([[float(r[k])-273.15 for r in orows] for k in ["tank1.medium.T","tank2.medium.T","tank3.medium.T"]],axis=0)
    ax.plot(to/3600,Ts,"-",color="k",lw=2,label="OM計算(tank平均)")
    print("OM@end=%.2f  exp@end=%.2f"%(Ts[-1],Te[-1]))
else:
    print("OM結果CSV無し。先に run_sim.mos を実行:",res)
ax.axhline(25,color="#2ca02c",ls="--",lw=1.3,label="目標 Ttarget=25℃")
ax.set_xlabel("経過時間 [h]"); ax.set_ylabel("水温 [℃]"); ax.set_title("eva4 温度管理: OM計算 vs 実測")
ax.grid(True,alpha=0.3); ax.legend(fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(HERE,"compare_OM_vs_exp.png")); print("saved compare_OM_vs_exp.png")
