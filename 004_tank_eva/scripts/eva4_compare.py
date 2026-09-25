# -*- coding: utf-8 -*-
"""eva4(温度管理あり)の温度データと、温度管理の効果を示す図。
eva4(管理あり,平坦) と eva5(管理なし,昇温) を同一リグの対比として重ねる。"""
import os, csv
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
for fp in ["/home/kamakiri/.fonts/NotoSansCJKjp-Regular.otf", r"C:\Windows\Fonts\meiryo.ttc"]:
    if os.path.exists(fp):
        fm.fontManager.addfont(fp); plt.rcParams["font.family"]=fm.FontProperties(fname=fp).get_name(); break
plt.rcParams["axes.unicode_minus"]=False
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def meanT(csvpath, cols):
    rows=list(csv.DictReader(open(csvpath,encoding="utf-8-sig")))
    t=np.array([float(r["Time [s]"]) for r in rows])
    T=np.mean([[float(r[c]) for r in rows] for c in cols],axis=0)
    return t,T
t4,T4=meanT(os.path.join(ROOT,"eva4/data/temperature_20points_without_NC_T7.csv"),["4-16","4-17","4-18","4-19"])
t5,T5=meanT(os.path.join(ROOT,"eva5/data/temperature_20points.csv"),["4-16","4-17","4-18","4-19"])
fig,ax=plt.subplots(figsize=(10,6),dpi=140)
ax.plot(t5/3600,T5,"o-",color="#c0392b",ms=4,lw=1.8,label="eva5 実測: 温度管理なし(自由昇温)")
ax.plot(t4/3600,T4,"s-",color="#1f77b4",ms=5,lw=2,label="eva4 実測: 温度管理あり(保持)")
ax.axhline(25,color="#2ca02c",ls="--",lw=1.5,label="温度管理の目標 Ttarget=25℃")
ax.set_xlabel("経過時間 [h]",fontsize=15); ax.set_ylabel("水温 [℃]",fontsize=15)
ax.set_title("温度管理の効果：同じ加熱610Wでも、管理ありなら目標付近で保持",fontsize=14,pad=10)
ax.set_xlim(0,28); ax.set_ylim(22,40); ax.tick_params(labelsize=13)
ax.grid(True,alpha=0.3); ax.legend(fontsize=12,loc="center right")
ax.annotate("eva4: 23.8→24.4℃ で保持\n(PIDが余剰熱を除去)",xy=(7,24.4),xytext=(9,27.5),fontsize=11,
            color="#1f77b4",arrowprops=dict(arrowstyle="->",color="#1f77b4"))
fig.tight_layout()
out=os.path.join(ROOT,"eva4/docs/img/eva4_control_effect.png"); os.makedirs(os.path.dirname(out),exist_ok=True)
fig.savefig(out); print("saved",out)
# 参考: eva4の1次遅れ同定(保持)の再掲図もコピー
import shutil
if os.path.exists(os.path.join(ROOT,"eva4/fit_lumped.png")):
    shutil.copy(os.path.join(ROOT,"eva4/fit_lumped.png"),os.path.join(ROOT,"eva4/docs/img/eva4_fit.png"))
