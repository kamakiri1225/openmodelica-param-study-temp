within ;
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
