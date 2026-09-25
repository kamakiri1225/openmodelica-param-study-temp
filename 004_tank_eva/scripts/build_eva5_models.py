# -*- coding: utf-8 -*-
"""eva5 モデルを原本から連番・自己完結で生成する。
  eva5_01_base            : 非パッケージ(参照)
  eva5_02_pumpHeat        : 投入熱+ポンプを PumpHeat 部品に集約
  eva5_03_pumpHeat_ground : さらに地面放熱を GroundLoss 部品に集約
lib/PumpHeat.mo, lib/GroundLoss.mo も単独再利用用に出力する。物理は3つとも等価。
"""
import re, os

ROOT = "/mnt/f/work/002_CAE/openfoam/20251017_OpenCAE2025/ana006_OM_tank_eva_001"
SRC = os.path.join(ROOT, "eva5/model/ana003_Tank3blocks_cyclononly_NoTemp.mo")

base = open(SRC, encoding="utf-8").read().replace("\r\n", "\n").replace("\r", "\n")
# ヘッダ(先頭の // ブロック)を除去して model 以降だけ取り出す
base = base[base.index("model "):]
# 元クラス名を除去(後で各連番名に置換)
ORIG = "ana003_Tank3blocks_cyclononly_NoTemp"

# ---- PumpHeat 部品(2スペースインデント; 埋め込み用) ----
PUMPHEAT = '''  //--- 再利用部品: 投入熱+循環ポンプ ---
  model PumpHeat "投入熱＋循環ポンプ をまとめた再利用部品 (サイクロン/フラッド/カバー等)"
    replaceable package Medium = Modelica.Media.Water.StandardWater
      constrainedby Modelica.Media.Interfaces.PartialMedium "作動流体";
    parameter Modelica.Units.SI.HeatFlowRate Q = 610 "投入熱 [W]";
    parameter Modelica.Units.SI.MassFlowRate m_flow = 110/60 "ポンプ質量流量 [kg/s]";
    parameter Medium.Temperature T_start = 293.15 "初期温度 [K]";
    Modelica.Fluid.Interfaces.FluidPort_a port_a(redeclare package Medium = Medium) "吸込(タンクから)" annotation(
      Placement(transformation(extent = {{-110, -10}, {-90, 10}}), iconTransformation(extent = {{-110, -10}, {-90, 10}})));
    Modelica.Fluid.Interfaces.FluidPort_b port_b(redeclare package Medium = Medium) "吐出(タンクへ)" annotation(
      Placement(transformation(extent = {{90, -10}, {110, 10}}), iconTransformation(extent = {{90, -10}, {110, 10}})));
    Modelica.Fluid.Machines.ControlledPump pump(redeclare package Medium = Medium, m_flow_nominal = m_flow, p_a_nominal = 1e5, p_b_nominal = 5e5, use_HeatTransfer = true, use_m_flow_set = true, T_start = T_start) annotation(
      Placement(transformation(origin = {0, 0}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow HF annotation(
      Placement(transformation(origin = {-30, 40}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Sources.Constant qSet(k = Q) annotation(
      Placement(transformation(origin = {-70, 40}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Sources.Constant mSet(k = m_flow) annotation(
      Placement(transformation(origin = {-40, -40}, extent = {{-10, -10}, {10, 10}})));
  equation
    connect(port_a, pump.port_a) annotation(Line(points = {{-100, 0}, {-10, 0}}, color = {0, 127, 255}));
    connect(pump.port_b, port_b) annotation(Line(points = {{10, 0}, {100, 0}}, color = {0, 127, 255}));
    connect(qSet.y, HF.Q_flow) annotation(Line(points = {{-59, 40}, {-40, 40}}, color = {0, 0, 127}));
    connect(HF.port, pump.heatPort) annotation(Line(points = {{-20, 40}, {0, 40}, {0, 8}}, color = {191, 0, 0}));
    connect(mSet.y, pump.m_flow_set) annotation(Line(points = {{-29, -40}, {7, -40}, {7, -7}}, color = {0, 0, 127}));
    annotation(
      Icon(coordinateSystem(preserveAspectRatio = false), graphics = {
        Rectangle(extent = {{-100, 60}, {100, -60}}, lineColor = {0, 0, 0}, fillColor = {245, 245, 245}, fillPattern = FillPattern.Solid),
        Ellipse(extent = {{-35, 35}, {35, -35}}, lineColor = {0, 0, 0}, fillColor = {253, 235, 208}, fillPattern = FillPattern.Solid),
        Polygon(points = {{-10, 25}, {28, 0}, {-10, -25}, {-10, 25}}, lineColor = {0, 0, 0}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid),
        Rectangle(extent = {{-70, 8}, {-45, -8}}, lineColor = {0, 0, 0}, fillColor = {250, 100, 100}, fillPattern = FillPattern.Solid),
        Line(points = {{-100, 0}, {-70, 0}}, color = {0, 127, 255}),
        Line(points = {{35, 0}, {100, 0}}, color = {0, 127, 255}),
        Text(extent = {{-100, -65}, {100, -95}}, textString = "%name"),
        Text(extent = {{-40, 55}, {60, 40}}, textString = "Q=%Q W")}),
      Documentation(info = "<html><p>投入熱+循環ポンプ1系統を1部品化。port_aを吸込, port_bを吐出へ。Qとm_flowを与える。</p></html>"));
  end PumpHeat;
'''

# ---- GroundLoss 部品(2スペースインデント; 埋め込み用) ----
GROUNDLOSS = '''  //--- 再利用部品: タンク→地面 放熱経路 ---
  model GroundLoss "タンク底面から地面への放熱(液→内壁→壁伝導→地面)をまとめた再利用部品"
    parameter Modelica.Units.SI.ThermalConductance Gc_liquid = 100 "液→内壁 熱コンダクタンス [W/K]";
    parameter Modelica.Units.SI.ThermalConductance G_wall = 100 "壁の熱伝導 [W/K]";
    parameter Modelica.Units.SI.ThermalConductance Gc_ground = 100 "壁→地面 熱コンダクタンス [W/K]";
    Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a port_water "水側(タンクheatPortへ)" annotation(
      Placement(transformation(extent = {{-110, -10}, {-90, 10}}), iconTransformation(extent = {{-110, -10}, {-90, 10}})));
    Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_b port_ground "地面側" annotation(
      Placement(transformation(extent = {{90, -10}, {110, 10}}), iconTransformation(extent = {{90, -10}, {110, 10}})));
    Modelica.Thermal.HeatTransfer.Components.Convection convLiquid annotation(
      Placement(transformation(origin = {-50, 0}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Thermal.HeatTransfer.Components.ThermalConductor wall(G = G_wall) annotation(
      Placement(transformation(origin = {0, 0}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Thermal.HeatTransfer.Components.Convection convGround annotation(
      Placement(transformation(origin = {50, 0}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Sources.Constant GcL(k = Gc_liquid) annotation(
      Placement(transformation(origin = {-50, 40}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Sources.Constant GcG(k = Gc_ground) annotation(
      Placement(transformation(origin = {50, 40}, extent = {{-10, -10}, {10, 10}})));
  equation
    connect(port_water, convLiquid.fluid) annotation(Line(points = {{-100, 0}, {-60, 0}}, color = {191, 0, 0}));
    connect(convLiquid.solid, wall.port_b) annotation(Line(points = {{-40, 0}, {-10, 0}}, color = {191, 0, 0}));
    connect(wall.port_a, convGround.fluid) annotation(Line(points = {{10, 0}, {40, 0}}, color = {191, 0, 0}));
    connect(convGround.solid, port_ground) annotation(Line(points = {{60, 0}, {100, 0}}, color = {191, 0, 0}));
    connect(GcL.y, convLiquid.Gc) annotation(Line(points = {{-39, 40}, {-50, 40}, {-50, 10}}, color = {0, 0, 127}));
    connect(GcG.y, convGround.Gc) annotation(Line(points = {{61, 40}, {50, 40}, {50, 10}}, color = {0, 0, 127}));
    annotation(
      Icon(coordinateSystem(preserveAspectRatio = false), graphics = {
        Rectangle(extent = {{-100, 60}, {100, -60}}, lineColor = {0, 0, 0}, fillColor = {245, 245, 245}, fillPattern = FillPattern.Solid),
        Rectangle(extent = {{-80, -20}, {80, -55}}, lineColor = {166, 113, 46}, fillColor = {246, 236, 224}, fillPattern = FillPattern.Solid),
        Line(points = {{-100, 0}, {100, 0}}, color = {191, 0, 0}),
        Text(extent = {{-100, -62}, {100, -92}}, textString = "%name"),
        Text(extent = {{-90, 52}, {90, 28}}, textString = "地面放熱")}),
      Documentation(info = "<html><p>水側(port_water)→液内壁(Gc_liquid)→壁伝導(G_wall)→地面(Gc_ground, port_ground)の放熱経路を1部品化。</p></html>"));
  end GroundLoss;
'''

# ---- AirLoss 部品(2スペースインデント; 埋め込み用) ----
AIRLOSS = '''  //--- 再利用部品: タンク上面→外気 放熱 ---
  model AirLoss "タンク上面から外気への放熱(自然対流)をまとめた再利用部品"
    parameter Modelica.Units.SI.ThermalConductance Gc_air = 100 "上面→外気 熱コンダクタンス [W/K]";
    Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a port_water "水側(タンクheatPortへ)" annotation(
      Placement(transformation(extent = {{-110, -10}, {-90, 10}}), iconTransformation(extent = {{-110, -10}, {-90, 10}})));
    Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_b port_air "外気側" annotation(
      Placement(transformation(extent = {{90, -10}, {110, 10}}), iconTransformation(extent = {{90, -10}, {110, 10}})));
    Modelica.Thermal.HeatTransfer.Components.Convection conv annotation(
      Placement(transformation(origin = {0, 0}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Sources.Constant Gc(k = Gc_air) annotation(
      Placement(transformation(origin = {0, 40}, extent = {{-10, -10}, {10, 10}})));
  equation
    connect(port_water, conv.fluid) annotation(Line(points = {{-100, 0}, {-10, 0}}, color = {191, 0, 0}));
    connect(conv.solid, port_air) annotation(Line(points = {{10, 0}, {100, 0}}, color = {191, 0, 0}));
    connect(Gc.y, conv.Gc) annotation(Line(points = {{11, 40}, {0, 40}, {0, 10}}, color = {0, 0, 127}));
    annotation(
      Icon(coordinateSystem(preserveAspectRatio = false), graphics = {
        Rectangle(extent = {{-100, 60}, {100, -60}}, lineColor = {0, 0, 0}, fillColor = {245, 245, 245}, fillPattern = FillPattern.Solid),
        Rectangle(extent = {{-80, 55}, {80, 20}}, lineColor = {84, 153, 199}, fillColor = {234, 242, 248}, fillPattern = FillPattern.Solid),
        Line(points = {{-100, 0}, {100, 0}}, color = {191, 0, 0}),
        Text(extent = {{-100, -62}, {100, -92}}, textString = "%name"),
        Text(extent = {{-90, -20}, {90, -48}}, textString = "外気放熱")}),
      Documentation(info = "<html><p>タンク上面(port_water)から外気(port_air)への自然対流放熱を1部品化。Gc_air=熱伝達率×上面積。</p></html>"));
  end AirLoss;
'''

def pack_air(text):
    for a,b in [("CV_tank_to_air11.fluid","airLoss3.port_water"),
                ("CV_tank_to_air1.fluid","airLoss2.port_water"),
                ("CV_tank_to_air.fluid","airLoss1.port_water"),
                ("CV_tank_to_air11.solid","airLoss3.port_air"),
                ("CV_tank_to_air1.solid","airLoss2.port_air"),
                ("CV_tank_to_air.solid","airLoss1.port_air")]:
        assert a in text, "missing "+a
        text = text.replace(a,b)
    names = ["CV_tank_to_air","CV_tank2toAir","CV_tank_to_air1","CV_tank2toAir1","CV_tank_to_air11","CV_tank2toAir11"]
    text = remove_decls(text, names)
    text = remove_connects(text, names)
    a1=("  AirLoss airLoss1(Gc_air = heatCeffToAir*(Lx1_1*Ly1_1)) annotation(\n"
        "    Placement(transformation(origin = {-8, 56}, extent = {{-20, -20}, {20, 20}})));\n")
    a2=("  AirLoss airLoss2(Gc_air = heatCeffToAir*(Lx2_1*Ly2_1 + Lx2_2*Ly2_2)) annotation(\n"
        "    Placement(transformation(origin = {88, 46}, extent = {{-20, -20}, {20, 20}})));\n")
    a3=("  AirLoss airLoss3(Gc_air = heatCeffToAir*(Lx3_1*Ly3_1)) annotation(\n"
        "    Placement(transformation(origin = {208, 40}, extent = {{-20, -20}, {20, 20}})));\n")
    text = text.replace("  inner Modelica.Fluid.System system", a1+a2+a3+"  inner Modelica.Fluid.System system", 1)
    text = insert_after_import(text, AIRLOSS)
    return text

# ---- TempControl 部品(2スペースインデント; 埋め込み用) ----
TEMPCONTROL = '''  //--- 再利用部品: 温度管理(冷却)ループ tank1→tank3 ---
  model TempControl "tank1から引いてtank3へ返す温度管理(冷却)ループ。PIDで除熱し目標温度に保持"
    replaceable package Medium = Modelica.Media.Water.StandardWater
      constrainedby Modelica.Media.Interfaces.PartialMedium "作動流体";
    parameter Boolean enabled = true "温度管理 ON(true)/OFF(false)" annotation(choices(checkBox = true));
    parameter Real Ttarget = 24.5 "目標温度 [degC]";
    parameter Real ctrl_k = 2000 "制御ゲイン [W/K]";
    parameter Modelica.Units.SI.HeatFlowRate cooling_capacity = 3500 "冷却能力[W] (Daikinオイルコン 3.5kW=3500, 5.0kW=5000)";
    parameter Real flow_Lmin = 25 "循環流量 [L/min]";
    parameter Modelica.Units.SI.MassFlowRate m_flow = flow_Lmin/60 "質量流量[kg/s] (水: 1L≈1kg換算, 25L/min=0.417kg/s)";
    parameter Medium.Temperature T_start = 297.65 "初期温度 [K]";
    Modelica.Fluid.Interfaces.FluidPort_a port_a(redeclare package Medium = Medium) "tank1から(吸込)" annotation(
      Placement(transformation(extent = {{-110, -10}, {-90, 10}}), iconTransformation(extent = {{-110, -10}, {-90, 10}})));
    Modelica.Fluid.Interfaces.FluidPort_b port_b(redeclare package Medium = Medium) "tank3へ(吐出)" annotation(
      Placement(transformation(extent = {{90, -10}, {110, 10}}), iconTransformation(extent = {{90, -10}, {110, 10}})));
    Modelica.Fluid.Machines.ControlledPump pump(redeclare package Medium = Medium, m_flow_nominal = m_flow, p_a_nominal = 1e5, p_b_nominal = 5e5, use_HeatTransfer = true, use_m_flow_set = true, T_start = T_start) annotation(
      Placement(transformation(origin = {0, 0}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Sources.Constant mSet(k = m_flow) annotation(
      Placement(transformation(origin = {-40, -40}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor Tsens annotation(
      Placement(transformation(origin = {30, 40}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Sources.Constant target(k = Ttarget + 273.15) annotation(
      Placement(transformation(origin = {-90, 60}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Continuous.LimPID pid(controllerType = Modelica.Blocks.Types.SimpleController.PI, k = ctrl_k, Ti = 200, yMax = 0, yMin = (if enabled then -cooling_capacity else 0), initType = Modelica.Blocks.Types.Init.InitialState) "オイルコン: 冷却のみ(y<=0), 除熱上限=冷却能力。enabled=falseで除熱0(管理OFF)" annotation(
      Placement(transformation(origin = {-40, 60}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow cooler annotation(
      Placement(transformation(origin = {0, 40}, extent = {{-10, -10}, {10, 10}}, rotation = -90)));
  equation
    connect(port_a, pump.port_a) annotation(Line(points = {{-100, 0}, {-10, 0}}, color = {0, 127, 255}));
    connect(pump.port_b, port_b) annotation(Line(points = {{10, 0}, {100, 0}}, color = {0, 127, 255}));
    connect(mSet.y, pump.m_flow_set) annotation(Line(points = {{-29, -40}, {7, -40}, {7, -7}}, color = {0, 0, 127}));
    connect(pump.heatPort, Tsens.port) annotation(Line(points = {{0, 8}, {30, 8}, {30, 30}}, color = {191, 0, 0}));
    connect(target.y, pid.u_s) annotation(Line(points = {{-79, 60}, {-52, 60}}, color = {0, 0, 127}));
    connect(Tsens.T, pid.u_m) annotation(Line(points = {{40, 40}, {40, 48}, {-40, 48}, {-40, 48}}, color = {0, 0, 127}));
    connect(pid.y, cooler.Q_flow) annotation(Line(points = {{-29, 60}, {0, 60}, {0, 50}}, color = {0, 0, 127}));
    connect(cooler.port, pump.heatPort) annotation(Line(points = {{0, 30}, {0, 8}}, color = {191, 0, 0}));
    annotation(
      Icon(coordinateSystem(preserveAspectRatio = false), graphics = {
        Rectangle(extent = {{-100, 60}, {100, -60}}, lineColor = {0, 0, 0}, fillColor = {245, 245, 245}, fillPattern = FillPattern.Solid),
        Ellipse(extent = {{-35, 35}, {35, -35}}, lineColor = {0, 0, 0}, fillColor = {208, 235, 253}, fillPattern = FillPattern.Solid),
        Polygon(points = {{-10, 25}, {28, 0}, {-10, -25}, {-10, 25}}, lineColor = {0, 0, 0}, fillColor = {255, 255, 255}, fillPattern = FillPattern.Solid),
        Rectangle(extent = {{-70, 8}, {-45, -8}}, lineColor = {0, 0, 0}, fillColor = {100, 150, 250}, fillPattern = FillPattern.Solid),
        Line(points = {{-100, 0}, {-70, 0}}, color = {0, 127, 255}),
        Line(points = {{35, 0}, {100, 0}}, color = {0, 127, 255}),
        Text(extent = {{-100, -65}, {100, -95}}, textString = "%name"),
        Text(extent = {{-60, 55}, {80, 38}}, textString = "Tset=%Ttarget C")}),
      Documentation(info = "<html><p>tank1(port_a)から引いて冷却しtank3(port_b)へ返す温度管理ループ。
Tsensで水温を測り、PID(ctrl_k)がcoolerで除熱してTtargetに保持する。ctrl_k=0で管理OFF。</p></html>"));
  end TempControl;
'''

# ---- TempControlIn 部品: TempControl のセンサを吸込口(タンクから引いた水)に変えたもの ----
TEMPCONTROL_IN = TEMPCONTROL.replace("model TempControl ", "model TempControlIn ", 1).replace("end TempControl;", "end TempControlIn;", 1)
_a = TEMPCONTROL_IN
TEMPCONTROL_IN = TEMPCONTROL_IN.replace(
    "    Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor Tsens annotation(",
    "    Modelica.Fluid.Sensors.Temperature Tsens(redeclare package Medium = Medium) \"吸込(タンクから引いた水)の温度\" annotation(", 1)
TEMPCONTROL_IN = TEMPCONTROL_IN.replace(
    "    connect(pump.heatPort, Tsens.port) annotation(Line(points = {{0, 8}, {30, 8}, {30, 30}}, color = {191, 0, 0}));",
    "    connect(port_a, Tsens.port) annotation(Line(points = {{-100, 0}, {-60, 0}, {-60, 20}, {30, 20}, {30, 30}}, color = {0, 127, 255}));", 1)
TEMPCONTROL_IN = TEMPCONTROL_IN.replace("  //--- 再利用部品: 温度管理", "  //--- 再利用部品: 温度管理(センサ=吸込口)", 1)
assert TEMPCONTROL_IN.count("Modelica.Fluid.Sensors.Temperature Tsens")==1 and "connect(port_a, Tsens.port)" in TEMPCONTROL_IN

LOOP_T1 = ("tank1.ports[3]", "{{12, -6}, {12, 96}, {100, 96}}")
LOOP_T2 = ("tank2.ports[3]", "{{140, 0}, {140, -12}, {90, -12}, {90, 96}, {100, 96}}")

def pack_tempctrl(text, CAP="3500", src=LOOP_T1, comp="TempControl"):
    inst = (f"  {comp} tempControl(redeclare package Medium = fluid1, Ttarget = Ttarget, ctrl_k = 2000, cooling_capacity = "+CAP+", flow_Lmin = 25, T_start = T_ini) annotation(\n"
            "    Placement(transformation(origin = {120, 96}, extent = {{-20, -20}, {20, 20}})));\n")
    text = text.replace("  inner Modelica.Fluid.System system", inst+"  inner Modelica.Fluid.System system", 1)
    conns = (f"  connect({src[0]}, tempControl.port_a) annotation(\n"
             f"    Line(points = {src[1]}, color = {{0, 127, 255}}, thickness = 0.5));\n"
             "  connect(tempControl.port_b, tank3.ports[1]) annotation(\n"
             "    Line(points = {{140, 96}, {246, 96}, {246, -6}}, color = {0, 127, 255}, thickness = 0.5));\n")
    text = text.replace("  annotation(\n    uses(Modelica", conns+"  annotation(\n    uses(Modelica", 1)
    text = insert_after_import(text, TEMPCONTROL if comp == "TempControl" else TEMPCONTROL_IN)
    return text

# ---- CoolingCoilCtrl 部品(冷却コイル型オイルコン; 2スペースインデント) ----
COOLINGCOIL = '''  //--- 再利用部品: 温度管理(冷却コイル型オイルコン) tank1→tank3 ---
  model CoolingCoilCtrl "冷却コイル型オイルコン(option c): 冷却側の基準温度Tcoolへ熱コンダクタンスUA_coolで除熱。タンク水温は平衡へ1次遅れで追従"
    replaceable package Medium = Modelica.Media.Water.StandardWater
      constrainedby Modelica.Media.Interfaces.PartialMedium "作動流体";
    parameter Boolean enabled = true "温度管理 ON(true)/OFF(false)" annotation(choices(checkBox = true));
    parameter Real Tcool = 14 "冷却側の基準温度(冷媒/蒸発器温度) [degC] ← 設定ノブ";
    parameter Modelica.Units.SI.ThermalConductance UA_cool = 57 "冷却コイル熱コンダクタンス [W/K]";
    parameter Real flow_Lmin = 25 "循環流量 [L/min]";
    parameter Modelica.Units.SI.MassFlowRate m_flow = flow_Lmin/60 "質量流量[kg/s] (水: 1L≈1kg換算, 25L/min=0.417kg/s)";
    parameter Medium.Temperature T_start = 297.65 "初期温度 [K]";
    Modelica.Fluid.Interfaces.FluidPort_a port_a(redeclare package Medium = Medium) "tank1から(吸込)" annotation(
      Placement(transformation(extent = {{-110, -10}, {-90, 10}}), iconTransformation(extent = {{-110, -10}, {-90, 10}})));
    Modelica.Fluid.Interfaces.FluidPort_b port_b(redeclare package Medium = Medium) "tank3へ(吐出)" annotation(
      Placement(transformation(extent = {{90, -10}, {110, 10}}), iconTransformation(extent = {{90, -10}, {110, 10}})));
    Modelica.Fluid.Machines.ControlledPump pump(redeclare package Medium = Medium, m_flow_nominal = m_flow, p_a_nominal = 1e5, p_b_nominal = 5e5, use_HeatTransfer = true, use_m_flow_set = true, T_start = T_start) annotation(
      Placement(transformation(origin = {0, 0}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Sources.Constant mSet(k = m_flow) annotation(
      Placement(transformation(origin = {-40, -40}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Thermal.HeatTransfer.Components.ThermalConductor coil(G = (if enabled then UA_cool else 0)) "enabled=falseでG=0→除熱なし(管理OFF)" annotation(
      Placement(transformation(origin = {0, 40}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
    Modelica.Thermal.HeatTransfer.Celsius.FixedTemperature coolant(T = Tcool) "冷却側=基準温度Tcoolに保持(実機のオイル/冷媒側の設定)" annotation(
      Placement(transformation(origin = {0, 78}, extent = {{-10, -10}, {10, 10}}, rotation = -90)));
  equation
    connect(port_a, pump.port_a) annotation(Line(points = {{-100, 0}, {-10, 0}}, color = {0, 127, 255}));
    connect(pump.port_b, port_b) annotation(Line(points = {{10, 0}, {100, 0}}, color = {0, 127, 255}));
    connect(mSet.y, pump.m_flow_set) annotation(Line(points = {{-29, -40}, {7, -40}, {7, -7}}, color = {0, 0, 127}));
    connect(pump.heatPort, coil.port_a) annotation(Line(points = {{0, 8}, {0, 30}}, color = {191, 0, 0}));
    connect(coil.port_b, coolant.port) annotation(Line(points = {{0, 50}, {0, 68}}, color = {191, 0, 0}));
    annotation(
      Icon(coordinateSystem(preserveAspectRatio = false), graphics = {
        Rectangle(extent = {{-100, 60}, {100, -60}}, lineColor = {0, 0, 0}, fillColor = {245, 245, 245}, fillPattern = FillPattern.Solid),
        Ellipse(extent = {{-35, 35}, {35, -35}}, lineColor = {0, 0, 0}, fillColor = {208, 235, 253}, fillPattern = FillPattern.Solid),
        Line(points = {{-25, 20}, {-25, -20}, {-10, -20}, {-10, 20}, {5, 20}, {5, -20}, {20, -20}, {20, 20}}, color = {0, 90, 200}),
        Line(points = {{-100, 0}, {-35, 0}}, color = {0, 127, 255}),
        Line(points = {{35, 0}, {100, 0}}, color = {0, 127, 255}),
        Text(extent = {{-100, -65}, {100, -95}}, textString = "%name"),
        Text(extent = {{-90, 55}, {90, 38}}, textString = "Tcool=%Tcool C")}),
      Documentation(info = "<html><p>冷却コイル型オイルコン(option c の実体)。冷却側を基準温度Tcoolに保持し、
コイル熱コンダクタンスUA_coolでタンク水から除熱する。除熱量=UA_cool*(水温-Tcool)で水温依存。
タンク水温は平衡 T=(Q+UA_tank*Tamb+UA_cool*Tcool)/(UA_tank+UA_cool) へ 1次遅れ τ=C/(UA_tank+UA_cool) で追従。
タンクの管理温度を下げたい→Tcoolを下げる。enabled=falseで除熱0(管理OFF=eva5相当)。</p></html>"));
  end CoolingCoilCtrl;
'''

# ---- ImmersionCooler 部品(浸漬形オイルコン AKJ相当, 目標温度Ttargetに保持; 2スペースインデント) ----
IMMERSION = '''  //--- 再利用部品: 浸漬形オイルコン(タンクに沈めた冷却コイル。目標温度Ttargetに向けて冷媒温度をゆっくり調整) ---
  model ImmersionCooler "浸漬形オイルコン: 冷却コイルが常に UA_cool*(水温-冷媒温度) で除熱し、冷媒温度を目標温度Ttargetに向けてゆっくり調整"
    parameter Boolean enabled = true "温度管理 ON(true)/OFF(false)" annotation(choices(checkBox = true));
    parameter Real Ttarget = 24.5 "目標温度 [degC]";
    parameter Modelica.Units.SI.ThermalConductance UA_cool = 57 "冷却コイルの熱コンダクタンス [W/K]";
    parameter Real Tcool_init = 14 "冷媒(蒸発)温度の初期値 [degC]";
    parameter Real Tcool_min = 5 "冷媒(蒸発)温度の下限 [degC]";
    parameter Real k_ctrl = 0.2 "冷媒温度調整のゲイン [K/K]";
    parameter Modelica.Units.SI.Time Ti_ctrl = 10800 "冷媒温度調整の積分時間 [s]";
    Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a port "タンクへ(浸漬)" annotation(
      Placement(transformation(extent = {{-10, -110}, {10, -90}}), iconTransformation(extent = {{-10, -110}, {10, -90}})));
    Modelica.Thermal.HeatTransfer.Components.ThermalConductor coil(G = (if enabled then UA_cool else 0)) "冷却コイル(enabled=falseで0)" annotation(
      Placement(transformation(origin = {0, -60}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
    Modelica.Thermal.HeatTransfer.Sources.PrescribedTemperature evap "冷媒(蒸発)温度" annotation(
      Placement(transformation(origin = {0, -20}, extent = {{-10, -10}, {10, 10}}, rotation = -90)));
    Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor Tsens "タンク水温" annotation(
      Placement(transformation(origin = {60, -60}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Sources.Constant target(k = Ttarget + 273.15) "目標温度[K]" annotation(
      Placement(transformation(origin = {-80, 40}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Continuous.LimPID pid(controllerType = Modelica.Blocks.Types.SimpleController.PI, k = k_ctrl, Ti = Ti_ctrl, yMax = 0, yMin = Tcool_min - Ttarget, initType = Modelica.Blocks.Types.Init.InitialOutput, y_start = Tcool_init - Ttarget) "冷媒温度の目標からの差[K]" annotation(
      Placement(transformation(origin = {-40, 40}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Math.Add add "冷媒温度 = 目標温度 + 調整量" annotation(
      Placement(transformation(origin = {0, 20}, extent = {{-10, -10}, {10, 10}}, rotation = -90)));
  equation
    connect(port, coil.port_a) annotation(Line(points = {{0, -100}, {0, -70}}, color = {191, 0, 0}));
    connect(coil.port_b, evap.port) annotation(Line(points = {{0, -50}, {0, -30}}, color = {191, 0, 0}));
    connect(port, Tsens.port) annotation(Line(points = {{0, -100}, {40, -100}, {40, -60}, {50, -60}}, color = {191, 0, 0}));
    connect(target.y, pid.u_s) annotation(Line(points = {{-69, 40}, {-52, 40}}, color = {0, 0, 127}));
    connect(Tsens.T, pid.u_m) annotation(Line(points = {{71, -60}, {80, -60}, {80, 0}, {-40, 0}, {-40, 28}}, color = {0, 0, 127}));
    connect(target.y, add.u1) annotation(Line(points = {{-69, 40}, {-60, 40}, {-60, 60}, {6, 60}, {6, 32}}, color = {0, 0, 127}));
    connect(pid.y, add.u2) annotation(Line(points = {{-29, 40}, {-6, 40}, {-6, 32}}, color = {0, 0, 127}));
    connect(add.y, evap.T) annotation(Line(points = {{0, 9}, {0, -8}}, color = {0, 0, 127}));
    annotation(
      Icon(coordinateSystem(preserveAspectRatio = false), graphics = {
        Rectangle(extent = {{-100, 100}, {100, -40}}, lineColor = {0, 0, 0}, fillColor = {245, 245, 245}, fillPattern = FillPattern.Solid),
        Rectangle(extent = {{-60, 90}, {60, 40}}, lineColor = {84, 153, 199}, fillColor = {208, 235, 253}, fillPattern = FillPattern.Solid),
        Line(points = {{-30, -40}, {-30, -80}, {-10, -80}, {-10, -40}, {10, -40}, {10, -80}, {30, -80}, {30, -40}}, color = {0, 90, 200}, thickness = 1.5),
        Line(points = {{0, -80}, {0, -100}}, color = {191, 0, 0}),
        Text(extent = {{-100, 105}, {100, 130}}, textString = "%name"),
        Text(extent = {{-55, 75}, {55, 55}}, textString = "Tset=%Ttarget C")}),
      Documentation(info = "<html><p>浸漬形オイルコン(Daikin AKJ9相当)。タンクに沈めた冷却コイルが、常に
除熱量 = UA_cool*(タンク水温 - 冷媒温度) で熱を奪う。冷媒温度は、水温が目標温度Ttargetになるよう
PI(ゲインk_ctrl, 積分時間Ti_ctrl)でゆっくり調整する(初期値Tcool_init, 下限Tcool_min)。
enabled=falseで除熱0(温度管理なし)。</p></html>"));
  end ImmersionCooler;
'''

def pack_immersion(text, tank="tank1"):
    # tank1 の真上に配置し、まっすぐ下ろして heatPort に直結(線を分かりやすく)
    inst = ("  ImmersionCooler immCooler(Ttarget = 24.5, UA_cool = 57, Tcool_init = 14, enabled = true) annotation(\n"
            "    Placement(transformation(origin = {12, 92}, extent = {{-16, -16}, {16, 16}})));\n")
    text = text.replace("  inner Modelica.Fluid.System system", inst+"  inner Modelica.Fluid.System system", 1)
    conn = (f"  connect(immCooler.port, {tank}.heatPort) annotation(\n"
            f"    Line(points = {{{{12, 76}}, {{12, 14}}}}, color = {{191, 0, 0}}, thickness = 0.5));\n")
    text = text.replace("  annotation(\n    uses(Modelica", conn+"  annotation(\n    uses(Modelica", 1)
    text = insert_after_import(text, IMMERSION)
    return text

def pack_coilctrl(text, src=LOOP_T1):
    inst = ("  CoolingCoilCtrl coilCtrl(redeclare package Medium = fluid1, Tcool = 14, UA_cool = 57, flow_Lmin = 25, T_start = T_ini) annotation(\n"
            "    Placement(transformation(origin = {120, 96}, extent = {{-20, -20}, {20, 20}})));\n")
    text = text.replace("  inner Modelica.Fluid.System system", inst+"  inner Modelica.Fluid.System system", 1)
    conns = (f"  connect({src[0]}, coilCtrl.port_a) annotation(\n"
             f"    Line(points = {src[1]}, color = {{0, 127, 255}}, thickness = 0.5));\n"
             "  connect(coilCtrl.port_b, tank3.ports[1]) annotation(\n"
             "    Line(points = {{140, 96}, {246, 96}, {246, -6}}, color = {0, 127, 255}, thickness = 0.5));\n")
    text = text.replace("  annotation(\n    uses(Modelica", conns+"  annotation(\n    uses(Modelica", 1)
    text = insert_after_import(text, COOLINGCOIL)
    return text

def header(name, ver, desc):
    return ("// ============================================================\n"
            f"//  {name}\n//  version {ver}  (2026-09-25)\n{desc}"
            "//  解説は eva5/docs/ を参照。\n"
            "// ============================================================\n")

def rename(text, newname):
    return text.replace(f"model {ORIG}\n", f"model {newname}\n", 1)\
               .replace(f"end {ORIG};", f"end {newname};", 1)

def insert_after_import(text, block):
    anchor = "  import Modelica.Fluid.Vessels.BaseClasses.VesselPortsData;\n"
    assert anchor in text, "import anchor not found"
    return text.replace(anchor, anchor + block, 1)

def remove_decls(text, names):
    for nm in sorted(names, key=len, reverse=True):
        text = re.sub(r'\n[ \t]*[\w\.][^\n]*\b'+re.escape(nm)+r'\b[^\n]*\n[ \t]*Placement[^\n]*;', '', text, count=1)
    return text

def remove_connects(text, keys):
    for k in sorted(keys, key=len, reverse=True):
        text = re.sub(r'\n[ \t]*connect\([^\n]*'+re.escape(k)+r'[^\n]*\n[ \t]*Line[^\n]*;', '', text)
    return text

def pack_pump(text):
    # 4部品→pumpHeat
    text = remove_decls(text, ["tT_HF_cyclone","tT_pumpQ_cyclone","HF_cyclone","pump_cyclone"])
    text = remove_connects(text, ["tT_HF_cyclone.y","HF_cyclone.port","tT_pumpQ_cyclone.y"])
    text = text.replace("pump_cyclone.port_a","pumpHeat.port_a").replace("pump_cyclone.port_b","pumpHeat.port_b")
    inst = ("  PumpHeat pumpHeat(redeclare package Medium = fluid1, Q = Q_cyclone, m_flow = 110/60, T_start = T_ini) annotation(\n"
            "    Placement(transformation(origin = {-74, 62}, extent = {{-20, -20}, {20, 20}})));\n")
    text = text.replace("  inner Modelica.Fluid.System system", inst+"  inner Modelica.Fluid.System system", 1)
    text = insert_after_import(text, PUMPHEAT)
    return text

def pack_ground(text):
    # 境界connectの端点を groundLoss へ(長い名前優先)
    for a,b in [("CV_tank1in112.fluid","groundLoss3.port_water"),
                ("CV_tank1in111.fluid","groundLoss1.port_water"),
                ("CV_tank1in11.fluid","groundLoss2.port_water"),
                ("convection_ground_tank121.solid","groundLoss1.port_ground"),
                ("convection_ground_tank122.solid","groundLoss3.port_ground"),
                ("convection_ground_tank12.solid","groundLoss2.port_ground")]:
        assert a in text, "missing "+a
        text = text.replace(a,b)
    names = ["CV_const_tank1in1","CV_tank1in11","tC_ground_tank12","CV_pumpB21","convection_ground_tank12",
             "CV_const_tank1in11","CV_tank1in111","tC_ground_tank121","CV_pumpB211","convection_ground_tank121",
             "CV_const_tank1in12","CV_tank1in112","tC_ground_tank122","CV_pumpB212","convection_ground_tank122"]
    text = remove_decls(text, names)
    text = remove_connects(text, names)
    g1=("  GroundLoss groundLoss1(Gc_liquid = heatCefftTank2in*(Lx1_1*Ly1_1 + Ly1_1*level_start), "
        "G_wall = (Lx1_1*Ly1_1 + Lx1_1*level_start + Ly1_1*level_start)*kground/tank_thickness, "
        "Gc_ground = heatCeffToAir*(Lx1_1*Ly1_1 + Ly1_1*level_start)) annotation(\n"
        "    Placement(transformation(origin = {-20, -84}, extent = {{-20, -20}, {20, 20}})));\n")
    g2=("  GroundLoss groundLoss2(Gc_liquid = heatCefftTank2in*(Lx2_1*Ly2_1 + Lx2_2*Ly2_2 + Ly2_1*level_start + Ly2_2*level_start + Lx2_1*level_start), "
        "G_wall = (Lx2_1*Ly2_1 + Lx2_1*level_start + Ly2_1*level_start)*kground/tank_thickness, "
        "Gc_ground = heatCeffToAir*(Lx2_1*Ly2_1 + Lx2_2*Ly2_2 + Ly2_1*level_start + Ly2_2*level_start + Lx2_1*level_start)) annotation(\n"
        "    Placement(transformation(origin = {48, -92}, extent = {{-20, -20}, {20, 20}})));\n")
    g3=("  GroundLoss groundLoss3(Gc_liquid = heatCefftTank2in*(Lx3_1*Ly3_1 + Lx3_1*level_start + Ly3_1*level_start), "
        "G_wall = (Lx3_1*Ly3_1 + Lx3_1*level_start + Ly3_1*level_start)*kground/tank_thickness, "
        "Gc_ground = heatCeffToAir*(Lx3_1*Ly3_1 + Lx3_1*level_start + Ly3_1*level_start)) annotation(\n"
        "    Placement(transformation(origin = {230, -92}, extent = {{-20, -20}, {20, 20}})));\n")
    text = text.replace("  inner Modelica.Fluid.System system", g1+g2+g3+"  inner Modelica.Fluid.System system", 1)
    text = insert_after_import(text, GROUNDLOSS)
    return text

MODELDIR = os.path.join(ROOT, "eva5/model")

# 01 base
m01 = header("eva5_01_base   (ベース, 温度管理なし・非パッケージ)", "1.0.0",
             "//  3槽・サイクロン投入熱610W・自由昇温。実測RMSE0.24℃。level_start=0.0755, heatCeffToAir=8.79。\n") \
      + rename(base, "eva5_01_base")
open(os.path.join(MODELDIR,"eva5_01_base.mo"),"w",encoding="utf-8").write(m01)

# 02 pumpHeat
m02 = header("eva5_02_pumpHeat   (投入熱+ポンプを pumpHeat 部品に集約・自己完結)", "1.1.0",
             "//  物理は 01 と等価。1ファイルで開けばよい(外部ライブラリ不要)。\n") \
      + pack_pump(rename(base, "eva5_02_pumpHeat"))
open(os.path.join(MODELDIR,"eva5_02_pumpHeat.mo"),"w",encoding="utf-8").write(m02)

# 03 pumpHeat + ground
m03 = header("eva5_03_pumpHeat_ground   (pumpHeat + groundLoss に集約・自己完結)", "1.2.0",
             "//  物理は 01 と等価。地面放熱も部品化(各タンク1個)。1ファイルで開けばよい。\n") \
      + pack_ground(pack_pump(rename(base, "eva5_03_pumpHeat_ground")))
open(os.path.join(MODELDIR,"eva5_03_pumpHeat_ground.mo"),"w",encoding="utf-8").write(m03)

# 04 pumpHeat + ground + air (全放熱をパッケージ化)
m04 = header("eva5_04_pumpHeat_ground_air   (pumpHeat + groundLoss + airLoss に集約・自己完結)", "1.3.0",
             "//  物理は 01 と等価。加熱も放熱(地面・外気)も全て部品化。1ファイルで開けばよい。\n") \
      + pack_air(pack_ground(pack_pump(rename(base, "eva5_04_pumpHeat_ground_air"))))
open(os.path.join(MODELDIR,"eva5_04_pumpHeat_ground_air.mo"),"w",encoding="utf-8").write(m04)

# eva4: eva5_04(全部品化) をコピーして温度管理(TempControl, tank1→tank3ループ)を追加。物理は"温度管理あり"(eva4相当)
EVA4DIR = os.path.join(ROOT, "eva4/model")
def eva4header(name, desc):
    return ("// ============================================================\n"
            f"//  {name}   (eva5_04 全部品化 + 温度管理 TempControl)\n"
            "//  version 1.0.0  (2026-09-25)\n"
            "//  タンク/加熱/放熱の設定は eva5_04 と同一。tank1→tank3 の冷却ループで目標温度に保持。\n"
            f"{desc}"
            "//  温度管理あり → eva4(温度管理あり実測)に対応。解説は eva4/docs/ 参照。\n"
            "// ============================================================\n")
# A: 能力上限なし(ana001 の regulator 方式相当。PIDで保持)
me4a = eva4header("eva4_01_regLib",
        "//  温度管理をライブラリ化(TempControl)。冷却能力の上限を実質なし(1e9)＝ana001 regulator 相当。\n") \
      + pack_tempctrl(pack_air(pack_ground(pack_pump(rename(base, "eva4_01_regLib")))), CAP="1e9")
open(os.path.join(EVA4DIR,"eva4_01_regLib.mo"),"w",encoding="utf-8").write(me4a)
# B: Daikinカタログ準拠(冷却能力3.5kW=3500 を除熱上限)
me4b = eva4header("eva4_02_catalog",
        "//  Daikinオイルコン(HK289B)準拠: 冷却能力 cooling_capacity=3500W(3.5kW, 5.0kW=5000)を除熱上限にPI制御。\n") \
      + pack_tempctrl(pack_air(pack_ground(pack_pump(rename(base, "eva4_02_catalog")))), CAP="3500")
open(os.path.join(EVA4DIR,"eva4_02_catalog.mo"),"w",encoding="utf-8").write(me4b)
# C: 冷却コイル型(能力が水温依存)。立ち上がり(τ≈2.8h)まで eva4 に一致する物理モデル
me4c = eva4header("eva4_03_coilCtrl",
        "//  冷却コイル型オイルコン(CoolingCoilCtrl): 除熱=UA_cool*(水温-Tcool)で水温依存。\n"
        "//  UA_cool=57W/K, Tcool=14℃ で 平衡24.5℃・時定数τ2.8h → eva4の緩やかな立ち上がりまで再現。\n") \
      + pack_coilctrl(pack_air(pack_ground(pack_pump(rename(base, "eva4_03_coilCtrl")))))
open(os.path.join(EVA4DIR,"eva4_03_coilCtrl.mo"),"w",encoding="utf-8").write(me4c)
# 04: 浸漬形オイルコン(冷却コイルをタンクに沈める。Daikin AKJ9相当・概念図に忠実)
me4d = eva4header("eva4_04_immersion",
        "//  浸漬形オイルコン(ImmersionCooler): 冷却コイルをtank1に沈め、冷媒温度Tcoolへ直接除熱(撹拌で均一)。\n"
        "//  Daikinオイルコンの冷凍サイクル概念図(AKJ9浸漬形)に忠実。UA_cool=57,Tcool=14で eva4 に一致。\n") \
      + pack_immersion(pack_air(pack_ground(pack_pump(rename(base, "eva4_04_immersion")))), tank="tank1")
open(os.path.join(EVA4DIR,"eva4_04_immersion.mo"),"w",encoding="utf-8").write(me4d)

# ---- SensorCooler 部品(冷却機のセンサ位置を変えられる浸漬形オイルコン; 2スペースインデント) ----
SENSORCOOLER = '''  //--- 再利用部品: センサ位置を選べるオイルコン(冷却機側の小さな水の塊を冷やし、その水かポンプ出口の温度で制御) ---
  model SensorCooler "オイルコン: 冷却機側の小さな水の塊(m_local)を除熱。制御に使う温度は 冷却機側の水 または ポンプ出口"
    parameter Boolean enabled = true "温度管理 ON(true)/OFF(false)" annotation(choices(checkBox = true));
    parameter Boolean sensorAtPumpOut = false "センサ位置: false=冷却機側の水, true=ポンプ出口" annotation(choices(checkBox = true));
    parameter Real Ttarget = 24.5 "目標温度 [degC]";
    parameter Modelica.Units.SI.HeatFlowRate capacity = 3500 "冷却能力(除熱の上限) [W]";
    parameter Real ctrl_k = 3000 "制御ゲイン [W/K]";
    parameter Modelica.Units.SI.Time Ti = 600 "積分時間 [s]";
    parameter Modelica.Units.SI.Mass m_local = 10 "冷却機側の水の量 [kg]";
    parameter Real flow_Lmin = 25 "タンクと冷却機側の水の入れ替わり流量 [L/min]";
    parameter Real T_init = 23.8 "冷却機側の水の初期温度 [degC]";
    Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a port "タンクへ" annotation(
      Placement(transformation(extent = {{-10, -110}, {10, -90}}), iconTransformation(extent = {{-10, -110}, {10, -90}})));
    Modelica.Blocks.Interfaces.RealInput T_pumpOut if sensorAtPumpOut "ポンプ出口温度 [K]" annotation(
      Placement(transformation(origin = {-120, 0}, extent = {{-20, -20}, {20, 20}}), iconTransformation(origin = {-120, 0}, extent = {{-20, -20}, {20, 20}})));
    Modelica.Thermal.HeatTransfer.Components.ThermalConductor exchange(G = flow_Lmin/60*4186) "タンクとの水の入れ替わり(流量×比熱)" annotation(
      Placement(transformation(origin = {0, -70}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
    Modelica.Thermal.HeatTransfer.Components.HeatCapacitor localWater(C = m_local*4186, T(start = T_init + 273.15, fixed = true)) "冷却機側の水" annotation(
      Placement(transformation(origin = {40, -40}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow cooler "除熱(負の熱流)" annotation(
      Placement(transformation(origin = {0, -10}, extent = {{-10, -10}, {10, 10}}, rotation = -90)));
    Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor Tlocal "冷却機側の水温" annotation(
      Placement(transformation(origin = {70, -60}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Sources.Constant target(k = Ttarget + 273.15) "目標温度[K]" annotation(
      Placement(transformation(origin = {-80, 50}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Continuous.LimPID pid(controllerType = Modelica.Blocks.Types.SimpleController.PI, k = ctrl_k, Ti = Ti, yMax = 0, yMin = (if enabled then -capacity else 0), initType = Modelica.Blocks.Types.Init.InitialState) "冷却のみ(y<=0)" annotation(
      Placement(transformation(origin = {-40, 50}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Blocks.Interfaces.RealOutput T_used "制御に使っている温度 [K]" annotation(
      Placement(transformation(origin = {-40, 0}, extent = {{-5, -5}, {5, 5}})));
  equation
    if not sensorAtPumpOut then
      T_used = Tlocal.T;
    end if;
    connect(T_pumpOut, T_used) annotation(Line(points = {{-120, 0}, {-40, 0}}, color = {0, 0, 127}));
    connect(port, exchange.port_a) annotation(Line(points = {{0, -100}, {0, -80}}, color = {191, 0, 0}));
    connect(exchange.port_b, localWater.port) annotation(Line(points = {{0, -60}, {0, -50}, {40, -50}}, color = {191, 0, 0}));
    connect(cooler.port, localWater.port) annotation(Line(points = {{0, -20}, {0, -50}, {40, -50}}, color = {191, 0, 0}));
    connect(localWater.port, Tlocal.port) annotation(Line(points = {{40, -50}, {40, -60}, {60, -60}}, color = {191, 0, 0}));
    connect(target.y, pid.u_s) annotation(Line(points = {{-69, 50}, {-52, 50}}, color = {0, 0, 127}));
    connect(T_used, pid.u_m) annotation(Line(points = {{-40, 0}, {-40, 38}}, color = {0, 0, 127}));
    connect(pid.y, cooler.Q_flow) annotation(Line(points = {{-29, 50}, {0, 50}, {0, 0}}, color = {0, 0, 127}));
    annotation(
      Icon(coordinateSystem(preserveAspectRatio = false), graphics = {
        Rectangle(extent = {{-100, 100}, {100, -40}}, lineColor = {0, 0, 0}, fillColor = {245, 245, 245}, fillPattern = FillPattern.Solid),
        Rectangle(extent = {{-60, 90}, {60, 40}}, lineColor = {84, 153, 199}, fillColor = {208, 235, 253}, fillPattern = FillPattern.Solid),
        Ellipse(extent = {{-20, 30}, {20, -10}}, lineColor = {0, 90, 200}, fillColor = {170, 213, 255}, fillPattern = FillPattern.Solid),
        Line(points = {{0, -40}, {0, -100}}, color = {191, 0, 0}),
        Text(extent = {{-100, 105}, {100, 130}}, textString = "%name"),
        Text(extent = {{-55, 75}, {55, 55}}, textString = "Tset=%Ttarget C")}),
      Documentation(info = "<html><p>冷却機側の小さな水の塊(m_local)を除熱し、その水はタンクと flow_Lmin の流量で入れ替わる。
PI制御で使う温度は sensorAtPumpOut=false なら冷却機側の水温、true ならポンプ出口温度(T_pumpOut)。
冷却のみ、除熱上限 capacity。enabled=falseで除熱0。</p></html>"));
  end SensorCooler;
'''

def pack_sensorcooler(text, pumpout):
    inst = (f"  SensorCooler sCooler(Ttarget = 24.5, capacity = 3500, m_local = 10, flow_Lmin = 25, sensorAtPumpOut = {'true' if pumpout else 'false'}, enabled = true) annotation(\n"
            "    Placement(transformation(origin = {12, 92}, extent = {{-16, -16}, {16, 16}})));\n")
    conn = ("  connect(sCooler.port, tank1.heatPort) annotation(\n"
            "    Line(points = {{12, 76}, {12, 14}}, color = {191, 0, 0}, thickness = 0.5));\n")
    if pumpout:
        inst += ("  Modelica.Fluid.Sensors.Temperature T_pumpOut(redeclare package Medium = fluid1) \"ポンプ出口温度\" annotation(\n"
                 "    Placement(transformation(origin = {-40, 92}, extent = {{-10, -10}, {10, 10}})));\n")
        conn += ("  connect(T_pumpOut.port, pumpHeat.port_b) annotation(\n"
                 "    Line(points = {{-40, 82}, {-40, 62}, {-54, 62}}, color = {0, 127, 255}));\n"
                 "  connect(T_pumpOut.T, sCooler.T_pumpOut) annotation(\n"
                 "    Line(points = {{-33, 92}, {-7, 92}}, color = {0, 0, 127}));\n")
    text = text.replace("  inner Modelica.Fluid.System system", inst+"  inner Modelica.Fluid.System system", 1)
    text = text.replace("  annotation(\n    uses(Modelica", conn+"  annotation(\n    uses(Modelica", 1)
    return insert_after_import(text, SENSORCOOLER)

# 05: センサを冷却機側の小さな水の塊に付けた目標温度制御
me4e = eva4header("eva4_05_localSensor",
        "//  オイルコン(SensorCooler): 冷却機側の水10kgを除熱(タンクと25L/minで入れ替わり)。その水温で目標24.5℃にPI制御。\n") \
      + pack_sensorcooler(pack_air(pack_ground(pack_pump(rename(base, "eva4_05_localSensor")))), pumpout=False)
open(os.path.join(EVA4DIR,"eva4_05_localSensor.mo"),"w",encoding="utf-8").write(me4e)
# 06: センサをポンプ出口に付けた目標温度制御
me4f = eva4header("eva4_06_pumpOutSensor",
        "//  オイルコン(SensorCooler): 05と同じ構成で、制御に使う温度をポンプ出口(pumpHeat.port_b)にしたもの。\n") \
      + pack_sensorcooler(pack_air(pack_ground(pack_pump(rename(base, "eva4_06_pumpOutSensor")))), pumpout=True)
open(os.path.join(EVA4DIR,"eva4_06_pumpOutSensor.mo"),"w",encoding="utf-8").write(me4f)

# ---- StagnantZone 部品(タンク内の混ざりにくい部分; 2スペースインデント) ----
STAGNANT = """  //--- 再利用部品: タンク内の混ざりにくい部分(よどみ部)。本体とは少ない混合流量でだけ熱をやり取りする ---
  model StagnantZone "タンク内の混ざりにくい部分(よどみ部): 水 m_zone を持ち、本体とは混合流量 mix_Lmin でだけ入れ替わる"
    parameter Modelica.Units.SI.Mass m_zone = 20 "よどみ部の水の量 [kg]";
    parameter Real mix_Lmin = 0.15 "本体との混合流量 [L/min]";
    parameter Real T_init = 23.8 "初期水温 [degC]";
    Modelica.Thermal.HeatTransfer.Interfaces.HeatPort_a port "タンク本体へ" annotation(
      Placement(transformation(extent = {{90, -10}, {110, 10}}), iconTransformation(extent = {{90, -10}, {110, 10}})));
    Modelica.Thermal.HeatTransfer.Components.ThermalConductor mixing(G = mix_Lmin/60*4186) "本体との混合(流量×比熱)" annotation(
      Placement(transformation(origin = {40, 0}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Thermal.HeatTransfer.Components.HeatCapacitor zone(C = m_zone*4186, T(start = T_init + 273.15, fixed = true)) "よどみ部の水" annotation(
      Placement(transformation(origin = {-20, 10}, extent = {{-10, -10}, {10, 10}})));
  equation
    connect(zone.port, mixing.port_a) annotation(Line(points = {{-20, 0}, {30, 0}}, color = {191, 0, 0}));
    connect(mixing.port_b, port) annotation(Line(points = {{50, 0}, {100, 0}}, color = {191, 0, 0}));
    annotation(
      Icon(coordinateSystem(preserveAspectRatio = false), graphics = {
        Rectangle(extent = {{-100, 60}, {100, -60}}, lineColor = {0, 0, 0}, fillColor = {245, 245, 245}, fillPattern = FillPattern.Solid),
        Rectangle(extent = {{-80, 20}, {60, -50}}, lineColor = {84, 153, 199}, fillColor = {170, 200, 230}, fillPattern = FillPattern.Solid),
        Line(points = {{60, 0}, {100, 0}}, color = {191, 0, 0}),
        Text(extent = {{-100, -65}, {100, -95}}, textString = "%name"),
        Text(extent = {{-90, 55}, {90, 30}}, textString = "mix=%mix_Lmin L/min")}),
      Documentation(info = "<html><p>タンクの中の、吹き出し口・吸い込み口から遠く混ざりにくい部分。
本体(OpenTank)とは混合流量 mix_Lmin でだけ熱をやり取りする。よどみ部の水温は本体の水温に
時定数 m_zone*4186/(mix_Lmin/60*4186) で遅れて追従する。</p></html>"));
  end StagnantZone;
"""

def set_T0(text, T0="23.8"):
    a = "  parameter Real T_ini = 24.5 + 273.15;"
    assert a in text
    return text.replace(a, f"  parameter Real T_ini = {T0} + 273.15 \"初期水温(eva4実測の開始時)\";", 1)

def pack_split(text, f_zone="0.7", mix="0.15"):
    a = "Modelica.Fluid.Vessels.OpenTank tank1(height = tank_height, crossArea = Lx1_1*Ly1_1,"
    assert a in text
    text = text.replace(a, "Modelica.Fluid.Vessels.OpenTank tank1(height = tank_height, crossArea = Lx1_1*Ly1_1*(1 - f_zone),", 1)
    inst = (f"  parameter Real f_zone = {f_zone} \"tank1 のうち、混ざりにくい部分(よどみ部)の割合\";\n"
            f"  StagnantZone zone1(m_zone = f_zone*Lx1_1*Ly1_1*level_start*995, mix_Lmin = {mix}, T_init = T_ini - 273.15) annotation(\n"
            "    Placement(transformation(origin = {-40, -30}, extent = {{-16, -16}, {16, 16}})));\n")
    text = text.replace("  inner Modelica.Fluid.System system", inst+"  inner Modelica.Fluid.System system", 1)
    conn = ("  connect(zone1.port, tank1.heatPort) annotation(\n"
            "    Line(points = {{-24, -30}, {-16, -30}, {-16, 14}, {-8, 14}}, color = {191, 0, 0}, thickness = 0.5));\n")
    text = text.replace("  annotation(\n    uses(Modelica", conn+"  annotation(\n    uses(Modelica", 1)
    return insert_after_import(text, STAGNANT)

# 07: 温度管理ループを tank2 → tank3 に変更(目標温度制御, 冷却能力3500W)
me4g = eva4header("eva4_07_loop2to3",
        "//  温度管理ループを tank2(ports[3])から引いて tank3(ports[1])に返す形に変更。引いた水の温度で目標24.5℃にPI制御(冷却能力3500W)。\n"
        "//  初期水温は eva4 実測の開始時 23.8℃。\n") \
      + set_T0(pack_tempctrl(pack_air(pack_ground(pack_pump(rename(base, "eva4_07_loop2to3")))), CAP="3500", src=LOOP_T2, comp="TempControlIn"))
open(os.path.join(EVA4DIR,"eva4_07_loop2to3.mo"),"w",encoding="utf-8").write(me4g)
# 08: 07 と同じループで冷却コイル型
me4h = eva4header("eva4_08_loop2to3_coil",
        "//  温度管理ループ tank2 → tank3。冷却コイル型(CoolingCoilCtrl: UA_cool=57W/K, Tcool=14℃)。初期水温 23.8℃。\n") \
      + set_T0(pack_coilctrl(pack_air(pack_ground(pack_pump(rename(base, "eva4_08_loop2to3_coil")))), src=LOOP_T2))
open(os.path.join(EVA4DIR,"eva4_08_loop2to3_coil.mo"),"w",encoding="utf-8").write(me4h)
# 09: 07 + tank1 を「よく混ざる本体」と「混ざりにくい部分(よどみ部)」に分割
me4i = eva4header("eva4_09_loop2to3_split",
        "//  07 に加えて tank1 を分割: 本体(30%)＋よどみ部 zone1(70%)。よどみ部は本体と混合流量 mix_Lmin でだけ入れ替わる。\n") \
      + pack_split(set_T0(pack_tempctrl(pack_air(pack_ground(pack_pump(rename(base, "eva4_09_loop2to3_split")))), CAP="3500", src=LOOP_T2, comp="TempControlIn")))
open(os.path.join(EVA4DIR,"eva4_09_loop2to3_split.mo"),"w",encoding="utf-8").write(me4i)

# lib 単独部品(dedent 2)
def dedent2(s): return re.sub(r'(?m)^  ','',s)
open(os.path.join(ROOT,"lib/PumpHeat.mo"),"w",encoding="utf-8").write("within ;\n"+dedent2(PUMPHEAT.split("\n",1)[1]))
open(os.path.join(ROOT,"lib/GroundLoss.mo"),"w",encoding="utf-8").write("within ;\n"+dedent2(GROUNDLOSS.split("\n",1)[1]))
open(os.path.join(ROOT,"lib/AirLoss.mo"),"w",encoding="utf-8").write("within ;\n"+dedent2(AIRLOSS.split("\n",1)[1]))
open(os.path.join(ROOT,"lib/TempControl.mo"),"w",encoding="utf-8").write("within ;\n"+dedent2(TEMPCONTROL.split("\n",1)[1]))
open(os.path.join(ROOT,"lib/CoolingCoilCtrl.mo"),"w",encoding="utf-8").write("within ;\n"+dedent2(COOLINGCOIL.split("\n",1)[1]))
open(os.path.join(ROOT,"lib/ImmersionCooler.mo"),"w",encoding="utf-8").write("within ;\n"+dedent2(IMMERSION.split("\n",1)[1]))
open(os.path.join(ROOT,"lib/TempControlIn.mo"),"w",encoding="utf-8").write("within ;\n"+dedent2(TEMPCONTROL_IN.split("\n",1)[1]))
open(os.path.join(ROOT,"lib/StagnantZone.mo"),"w",encoding="utf-8").write("within ;\n"+dedent2(STAGNANT.split("\n",1)[1]))
open(os.path.join(ROOT,"lib/SensorCooler.mo"),"w",encoding="utf-8").write("within ;\n"+dedent2(SENSORCOOLER.split("\n",1)[1]))

# ---- 検証 ----
def chk(name, text, must, mustnot):
    ok=True
    for s in must:
        if text.count(s)<1: print(f"  [NG] {name}: 欠落 {s!r}"); ok=False
    for s in mustnot:
        if text.count(s)>0: print(f"  [NG] {name}: 残存 {s!r} ({text.count(s)})"); ok=False
    print(f"  [{'OK' if ok else '!!'}] {name}")
    return ok

print("=== 検証 ===")
chk("01", m01, ["model eva5_01_base","pump_cyclone","end eva5_01_base;"], ["PumpHeat","GroundLoss","ana003"])
chk("02", m02, ["model eva5_02_pumpHeat","model PumpHeat","PumpHeat pumpHeat","pumpHeat.port_a","pumpHeat.port_b"],
    ["pump_cyclone","HF_cyclone","tT_HF_cyclone","tT_pumpQ_cyclone","TankLib","ana003"])
gm=["CV_const_tank1in1","CV_tank1in11","tC_ground_tank12","CV_pumpB21","convection_ground_tank12",
    "CV_const_tank1in11","CV_tank1in111","tC_ground_tank121","CV_pumpB211","convection_ground_tank121",
    "CV_const_tank1in12","CV_tank1in112","tC_ground_tank122","CV_pumpB212","convection_ground_tank122"]
chk("03", m03, ["model eva5_03_pumpHeat_ground","model PumpHeat","model GroundLoss","PumpHeat pumpHeat",
                "GroundLoss groundLoss1","GroundLoss groundLoss2","GroundLoss groundLoss3"],
    ["pump_cyclone","TankLib","ana003"]+gm)
airnames=["CV_tank_to_air","CV_tank2toAir","CV_tank_to_air1","CV_tank2toAir1","CV_tank_to_air11","CV_tank2toAir11"]
chk("04", m04, ["model eva5_04_pumpHeat_ground_air","model PumpHeat","model GroundLoss","model AirLoss",
                "PumpHeat pumpHeat","GroundLoss groundLoss1","AirLoss airLoss1","AirLoss airLoss2","AirLoss airLoss3"],
    ["pump_cyclone","TankLib","ana003"]+gm+airnames)
print("04 port_water:", m04.count(".port_water"), " port_air:", m04.count(".port_air"),
      " port_ground:", m04.count(".port_ground"), " prescribedTemperature.port:", m04.count("prescribedTemperature.port"))
print("生成:", sorted(os.listdir(MODELDIR)))
