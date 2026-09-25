# -*- coding: utf-8 -*-
"""温度管理モデル(A:能力上限なし / B:3.5kW上限)の集中定数応答を eva4 実測と比較。
温度管理=目標温度へ除熱するPI制御(冷却のみ,除熱上限=冷却能力)。参考にeva5(管理なし)も表示。
出力: eva4/docs/img/eva4_model_vs_exp.png"""
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
def meanT(p, cols):
    r=list(csv.DictReader(open(p,encoding="utf-8-sig")))
    return (np.array([float(x["Time [s]"]) for x in r]),
            np.mean([[float(x[c]) for x in r] for c in cols],axis=0))
t4,T4=meanT(os.path.join(ROOT,"eva4/data/temperature_20points_without_NC_T7.csv"),["4-16","4-17","4-18","4-19"])
t5,T5=meanT(os.path.join(ROOT,"eva5/data/temperature_20points.csv"),["4-16","4-17","4-18","4-19"])

# 集中定数(eva5合わせこみ由来): 熱容量C, 放熱UA
C=3.265*0.0755*992*4186.0   # 3槽の水
UA=46.0                     # 外気・地面への放熱(eva5同定)
Q=610.0; Tamb=24.5; T0=23.8; Ttarget=24.5
def sim(cap, Kp=3000.0, Ti=300.0):
    dt=2.0; t=np.arange(0,25200+dt,dt); T=np.empty_like(t); T[0]=T0; I=0.0
    for i in range(1,len(t)):
        e=T[i-1]-Ttarget                       # 正=高すぎ→冷却
        u=Kp*e+Kp/Ti*I
        Qc=min(max(u,0.0),cap)                 # 冷却のみ0..能力
        if u==Qc: I+=e*dt                      # アンチワインドアップ
        T[i]=T[i-1]+dt*(Q-UA*(T[i-1]-Tamb)-Qc)/C
    return t,T
def sim_coil(UA_cool=57.0, Tcool=14.0):
    dt=2.0; t=np.arange(0,25200+dt,dt); T=np.empty_like(t); T[0]=T0
    for i in range(1,len(t)):
        T[i]=T[i-1]+dt*(Q-UA*(T[i-1]-Tamb)-UA_cool*(T[i-1]-Tcool))/C
    return t,T
tA,TA=sim(1e9); tC,TC=sim_coil()
def rmse(tm,Tm): return float(np.sqrt(np.mean((np.interp(t4,tm,Tm)-T4)**2)))

fig,axes=plt.subplots(1,2,figsize=(14,5.6),dpi=140,sharey=True)
# 左: PI設定保持型(A/B; 入熱610W≪能力なので同一) — 速く平坦化
ax=axes[0]
ax.plot(t4/3600,T4,"s",color="#1f77b4",ms=6,label="eva4実測(管理あり)")
ax.plot(tA/3600,TA,"-",color="k",lw=2,label="PI設定保持型 (A/B)")
ax.axhline(Ttarget,color="#2ca02c",ls="--",lw=1.2,label=f"目標 {Ttarget}℃")
ax.set_title(f"PI設定保持型 (eva4_01/02)\n速く平坦化 → 立ち上がりが合わない (RMSE={rmse(tA,TA):.2f}℃)",fontsize=12)
ax.set_ylabel("水温 [℃]"); ax.set_ylim(23,26)
# 右: 冷却コイル型(C) — 緩やかに平衡へ
ax=axes[1]
ax.plot(t4/3600,T4,"s",color="#1f77b4",ms=6,label="eva4実測(管理あり)")
ax.plot(tC/3600,TC,"-",color="#c0392b",lw=2.5,label="冷却コイル型 (eva4_03_coilCtrl)")
ax.set_title(f"冷却コイル型 (eva4_03; UA_cool=57, Tcool=14℃)\n緩やかな立ち上がりまで一致 (RMSE={rmse(tC,TC):.2f}℃)",fontsize=12)
for ax in axes:
    ax.set_xlabel("経過時間 [h]"); ax.set_xlim(0,8); ax.grid(True,alpha=0.3); ax.legend(fontsize=10,loc="lower right")
fig.suptitle("温度管理モデルと eva4 実測の比較：設定保持型 vs 冷却コイル型",fontsize=13)
fig.tight_layout(rect=[0,0,1,0.95])
out=os.path.join(ROOT,"eva4/docs/img/eva4_model_vs_exp.png")
fig.savefig(out); print("saved",out,"  RMSE PI=%.3f coil=%.3f"%(rmse(tA,TA),rmse(tC,TC)))
