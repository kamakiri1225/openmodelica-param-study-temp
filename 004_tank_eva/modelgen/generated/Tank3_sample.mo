// ============================================================
//  Tank3_sample   (gen_model.py が YAML から自動生成)
//  タンク3槽, ポンプ1, 温度管理=あり
//  部品(PumpHeat/GroundLoss/AirLoss/TempControl)はモデル内に同梱(自己完結)
// ============================================================
model Tank3_sample
  extends Modelica.Icons.Example;
  replaceable package fluid1 = Modelica.Media.Water.StandardWater;
  parameter Real T_ini = 24.5 + 273.15 "初期水温[K]";
  //--- 同梱部品 ---
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

  //--- タンク・ポンプ・放熱・温度管理 ---
  Modelica.Fluid.Fittings.SimpleGenericOrifice orifice_tank1_tank2(redeclare package Medium = fluid1, diameter = 0.1, zeta = 0.1) annotation(
    Placement(transformation(origin = {60, -40}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Fittings.SimpleGenericOrifice orifice_tank2_tank3(redeclare package Medium = fluid1, diameter = 0.1, zeta = 0.1) annotation(
    Placement(transformation(origin = {180, -40}, extent = {{-10, -10}, {10, 10}})));
  PumpHeat pump1(redeclare package Medium = fluid1, Q = 610, m_flow = 110/60, T_start = T_ini) annotation(
    Placement(transformation(origin = {-40, 120}, extent = {{-15, -15}, {15, 15}})));
  TempControl tempCtrl(redeclare package Medium = fluid1, enabled = true, Ttarget = 25, cooling_capacity = 3500, flow_Lmin = 25, T_start = T_ini) annotation(
    Placement(transformation(origin = {120, 200}, extent = {{-15, -15}, {15, 15}})));
  Modelica.Fluid.Vessels.OpenTank tank1(redeclare package Medium = fluid1, T_start = T_ini, crossArea = 0.43254, height = 0.2400, level_start = 0.1500, nPorts = 3, portsData(each diameter = 0.1, each height = 0), use_HeatTransfer = true, use_T_start = true) annotation(
    Placement(transformation(origin = {0, 0}, extent = {{-20, -20}, {20, 20}})));
  GroundLoss ground_tank1(Gc_liquid = 8.471, G_wall = 282.089, Gc_ground = 4.325) annotation(
    Placement(transformation(origin = {0, -120}, extent = {{-15, -15}, {15, 15}})));
  AirLoss air_tank1(Gc_air = 4.325) annotation(
    Placement(transformation(origin = {0, 90}, extent = {{-15, -15}, {15, 15}})));
  Modelica.Fluid.Vessels.OpenTank tank2(redeclare package Medium = fluid1, T_start = T_ini, crossArea = 1.98897, height = 0.2400, level_start = 0.1500, nPorts = 2, portsData(each diameter = 0.1, each height = 0), use_HeatTransfer = true, use_T_start = true) annotation(
    Placement(transformation(origin = {120, 0}, extent = {{-20, -20}, {20, 20}})));
  GroundLoss ground_tank2(Gc_liquid = 28.473, G_wall = 1297.154, Gc_ground = 19.890) annotation(
    Placement(transformation(origin = {120, -120}, extent = {{-15, -15}, {15, 15}})));
  AirLoss air_tank2(Gc_air = 19.890) annotation(
    Placement(transformation(origin = {120, 90}, extent = {{-15, -15}, {15, 15}})));
  Modelica.Fluid.Vessels.OpenTank tank3(redeclare package Medium = fluid1, T_start = T_ini, crossArea = 0.68244, height = 0.2400, level_start = 0.1500, nPorts = 3, portsData(each diameter = 0.1, each height = 0), use_HeatTransfer = true, use_T_start = true) annotation(
    Placement(transformation(origin = {240, 0}, extent = {{-20, -20}, {20, 20}})));
  GroundLoss ground_tank3(Gc_liquid = 12.116, G_wall = 445.072, Gc_ground = 6.824) annotation(
    Placement(transformation(origin = {240, -120}, extent = {{-15, -15}, {15, 15}})));
  AirLoss air_tank3(Gc_air = 6.824) annotation(
    Placement(transformation(origin = {240, 90}, extent = {{-15, -15}, {15, 15}})));
  Modelica.Thermal.HeatTransfer.Celsius.FixedTemperature amb(T = 24.5) annotation(
    Placement(transformation(origin = {-160, -120}, extent = {{-10, -10}, {10, 10}})));
  inner Modelica.Fluid.System system annotation(
    Placement(transformation(origin = {-160, 200}, extent = {{-10, -10}, {10, 10}})));
equation
  connect(tank1.ports[1], orifice_tank1_tank2.port_a) annotation(Line(points = {{0, 0}, {60, -40}}, color = {0, 127, 255}));
  connect(orifice_tank1_tank2.port_b, tank2.ports[1]) annotation(Line(points = {{60, -40}, {120, 0}}, color = {0, 127, 255}));
  connect(tank2.ports[2], orifice_tank2_tank3.port_a) annotation(Line(points = {{120, 0}, {180, -40}}, color = {0, 127, 255}));
  connect(orifice_tank2_tank3.port_b, tank3.ports[1]) annotation(Line(points = {{180, -40}, {240, 0}}, color = {0, 127, 255}));
  connect(tank1.ports[2], pump1.port_a) annotation(Line(points = {{0, 0}, {-40, 120}}, color = {0, 127, 255}));
  connect(pump1.port_b, tank3.ports[2]) annotation(Line(points = {{-40, 120}, {240, 0}}, color = {0, 127, 255}));
  connect(tank1.ports[3], tempCtrl.port_a) annotation(Line(points = {{0, 0}, {120, 200}}, color = {0, 127, 255}));
  connect(tempCtrl.port_b, tank3.ports[3]) annotation(Line(points = {{120, 200}, {240, 0}}, color = {0, 127, 255}));
  connect(tank1.heatPort, ground_tank1.port_water) annotation(Line(points = {{0, 0}, {0, -120}}, color = {191, 0, 0}));
  connect(ground_tank1.port_ground, amb.port) annotation(Line(points = {{0, -120}, {-160, -120}}, color = {191, 0, 0}));
  connect(tank1.heatPort, air_tank1.port_water) annotation(Line(points = {{0, 0}, {0, 90}}, color = {191, 0, 0}));
  connect(air_tank1.port_air, amb.port) annotation(Line(points = {{0, 90}, {-160, -120}}, color = {191, 0, 0}));
  connect(tank2.heatPort, ground_tank2.port_water) annotation(Line(points = {{120, 0}, {120, -120}}, color = {191, 0, 0}));
  connect(ground_tank2.port_ground, amb.port) annotation(Line(points = {{120, -120}, {-160, -120}}, color = {191, 0, 0}));
  connect(tank2.heatPort, air_tank2.port_water) annotation(Line(points = {{120, 0}, {120, 90}}, color = {191, 0, 0}));
  connect(air_tank2.port_air, amb.port) annotation(Line(points = {{120, 90}, {-160, -120}}, color = {191, 0, 0}));
  connect(tank3.heatPort, ground_tank3.port_water) annotation(Line(points = {{240, 0}, {240, -120}}, color = {191, 0, 0}));
  connect(ground_tank3.port_ground, amb.port) annotation(Line(points = {{240, -120}, {-160, -120}}, color = {191, 0, 0}));
  connect(tank3.heatPort, air_tank3.port_water) annotation(Line(points = {{240, 0}, {240, 90}}, color = {191, 0, 0}));
  connect(air_tank3.port_air, amb.port) annotation(Line(points = {{240, 90}, {-160, -120}}, color = {191, 0, 0}));
  annotation(
    uses(Modelica(version = "4.0.0")),
    Diagram(coordinateSystem(extent = {{-260, 300}, {380, -220}})),
    experiment(StartTime = 0, StopTime = 100000, Interval = 50.0));
end Tank3_sample;
