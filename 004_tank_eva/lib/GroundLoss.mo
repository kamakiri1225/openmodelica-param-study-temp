within ;
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
