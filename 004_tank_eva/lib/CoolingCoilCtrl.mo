within ;
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
