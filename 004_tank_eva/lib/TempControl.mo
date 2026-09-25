within ;
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
