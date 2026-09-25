within ;
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
