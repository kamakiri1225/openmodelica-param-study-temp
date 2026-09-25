within ;
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
