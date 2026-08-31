# -*- coding: utf-8 -*-
"""
集中定数モデルによる一次確認 (OpenModelica を回さずにモデルの妥当性を評価)。
docs/parameter_study_plan.md の 1.2 節・付録の数値を再現する。

  python docs/lumped_check.py
"""
import numpy as np

# --- モデルパラメータ (ana003_Tank3blocks_cyclononly_NoTemp.mo より) ---
h_air = 10.0        # heatCeffToAir   [W/m2K]
h_in = 10.0         # heatCefftTank2in[W/m2K]
kground = 80.0      # kground         [W/mK]
th = 2.3 / 1000     # tank_thickness  [m]
level = 128 / 1000  # level_start     [m]
rho_w, cp_w = 1000.0, 4186.0
Q, Tair = 610.0, 24.5

# 幾何 [m]
Lx1_1, Ly1_1 = 0.903, 0.479
Lx2_1, Lx2_2, Ly2_1, Ly2_2 = 1.191, 0.478, 1.670, 0.337
Lx3_1, Ly3_1 = 0.573, 1.191
A1 = Lx1_1 * Ly1_1
A2 = Lx2_1 * Ly2_1 + Lx2_2 * Ly2_2
A3 = Lx3_1 * Ly3_1

UA_air = h_air * (A1 + A2 + A3)


def ground_UA(A_in, A_cond, A_g):
    R = 1 / (h_in * A_in) + 1 / (A_cond * kground / th) + 1 / (h_air * A_g)
    return 1 / R


UAg1 = ground_UA(A1 + Ly1_1 * level, A1 + Lx1_1 * level + Ly1_1 * level,
                 A1 + Ly1_1 * level)
A2in = A2 + Ly2_1 * level + Ly2_2 * level + Lx2_1 * level
UAg2 = ground_UA(A2in, Lx2_1 * Ly2_1 + Lx2_1 * level + Ly2_1 * level, A2in)
A3g = A3 + Lx3_1 * level + Ly3_1 * level
UAg3 = ground_UA(A3g, A3g, A3g)
UA_ground = UAg1 + UAg2 + UAg3
UA = UA_air + UA_ground

m = (A1 * level + A2 * level + A3 * 0.9 * level) * rho_w
C = m * cp_w
Tfin = Tair + Q / UA
tau = C / UA

print(f"上面積 [m2] : tank1={A1:.3f} tank2={A2:.3f} tank3={A3:.3f}")
print(f"UA_air     = {UA_air:.2f} W/K")
print(f"UA_ground  = {UA_ground:.2f} W/K (t1={UAg1:.2f} t2={UAg2:.2f} t3={UAg3:.2f})")
print(f"UA_total   = {UA:.2f} W/K")
print(f"水質量      = {m:.1f} kg,  C={C:.3e} J/K")
print(f"T_final    = {Tfin:.2f} degC   (実験 ~37.7)")
print(f"tau        = {tau:.0f} s = {tau/3600:.2f} h   (実験 ~23000 s)")
