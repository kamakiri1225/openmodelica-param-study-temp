within ;
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
