within ;
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
