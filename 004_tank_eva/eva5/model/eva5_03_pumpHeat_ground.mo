// ============================================================
//  eva5_03_pumpHeat_ground   (pumpHeat + groundLoss に集約・自己完結)
//  version 1.2.0  (2026-09-25)
//  物理は 01 と等価。地面放熱も部品化(各タンク1個)。1ファイルで開けばよい。
//  解説は eva5/docs/ を参照。
// ============================================================
model eva5_03_pumpHeat_ground
  extends Modelica.Icons.Example;
  import Modelica.Fluid.Vessels.BaseClasses.VesselPortsData;
  //--- 再利用部品: タンク→地面 放熱経路 ---
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
  //--- 再利用部品: 投入熱+循環ポンプ ---
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
  //-----
  replaceable package fluid1 = Modelica.Media.Water.StandardWater;
  replaceable package gas1 = Modelica.Media.Air.DryAirNasa;
  //replaceable package fluid1 = Modelica.Media.Water.StandardWaterOnePhase;
  //-----
  parameter Modelica.Units.SI.Length diamDmyPipe = 0.1;
  parameter Real zetaDmyPipe = 0.1;
  //-----
  parameter Real tank_height = 240/1000;
  parameter Real tank_thickness = 2.3/1000;
  parameter Real level_start = 75.5/1000;  // eva5合わせこみ(有効水位)
  // tank1
  parameter Real Lx1_1 = 903/1000;
  parameter Real Lx1_2 = 1230/1000;
  parameter Real Ly1_1 = 479/1000;
  parameter Real Ly1_2 = 159/1000;
  // tank2
  parameter Real Lx2_1 = 1191/1000;
  parameter Real Lx2_2 = 478/1000;
  parameter Real Ly2_1 = 1670/1000;
  parameter Real Ly2_2 = 337/1000;
  // tank3
  parameter Real Lx3_1 = 573/1000;
  parameter Real Ly3_1 = 1191/1000;
  // タンク内熱伝達率
  parameter Real heatCefftTank2in = 10;
  // タンク内熱伝達率
  parameter Real heatCefftMachine2in = 120;
  // タンクの密度
  parameter Real rho_tank = 7000;
  //kg/m3
  // タンクの比熱
  parameter Real Cp_tank = 450;
  //J/kg K
  //地面との接触熱抵抗
  parameter Real kground = 80;
  //air
  parameter Real heatCeffToAir = 8.79;  // eva5合わせこみ
  parameter Real Tair_deg = 24.5;
  parameter Real Tair_K = Tair_deg + 273.15;
  //25;
  parameter Real T_ini = 24.5 + 273.15;
  //25 + 273.15;
  // 機械内
  parameter Real T_machine_in = 24.5;
  parameter Real Lx_machine = 2.0;
  parameter Real Ly_machine = 1.0;
  parameter Real machine_height = 1.5;
  // T3基準温度とプラス
  parameter Real Ttarget = 24.5;
  //
  parameter Real T3puls = 1.5;
  // サイクロン投入熱 [W]（パラメータスタディで -override 可能にするため変数化）
  parameter Real Q_cyclone = 610;
  Modelica.Fluid.Vessels.OpenTank tank1(height = tank_height, crossArea = Lx1_1*Ly1_1, level_start = level_start, T_start = T_ini, portsData = {VesselPortsData(diameter = diamDmyPipe, height = 0), VesselPortsData(diameter = diamDmyPipe, height = 0), VesselPortsData(diameter = diamDmyPipe, height = 0.12)}, redeclare package Medium = fluid1, use_T_start = true, use_HeatTransfer = true, nPorts = 3) annotation(
    Placement(transformation(origin = {12, 14}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Thermal.HeatTransfer.Components.Convection CV_tank_to_air annotation(
    Placement(transformation(origin = {-8, 56}, extent = {{-10, -10}, {10, 10}}, rotation = -90)));
  Modelica.Blocks.Sources.Constant CV_tank2toAir(k = heatCeffToAir*(Lx1_1*Ly1_1)) annotation(
    Placement(transformation(origin = {30, 66}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Fluid.Vessels.OpenTank tank2(redeclare package Medium = fluid1, T_start = T_ini, crossArea = Lx2_1*Ly2_1 + Lx2_2*Ly2_2, height = tank_height, level_start = level_start, nPorts = 3, portsData(each diameter = diamDmyPipe, each height = 0), use_HeatTransfer = true, use_T_start = true) annotation(
    Placement(transformation(origin = {140, 20}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Fluid.Vessels.OpenTank tank3(redeclare package Medium = fluid1, T_start = T_ini, crossArea = Lx3_1*Ly3_1, height = tank_height, level_start = level_start*0.9, nPorts = 6, portsData(each diameter = diamDmyPipe, each height = 0), use_HeatTransfer = true, use_T_start = true) annotation(
    Placement(transformation(origin = {246, 14}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Fluid.Fittings.SimpleGenericOrifice path_1to2(redeclare package Medium = fluid1, diameter = diamDmyPipe, zeta = zetaDmyPipe) annotation(
    Placement(transformation(origin = {74, -12}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Fittings.SimpleGenericOrifice path_1to21(redeclare package Medium = fluid1, diameter = diamDmyPipe, zeta = zetaDmyPipe) annotation(
    Placement(transformation(origin = {186, -18}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.Convection CV_tank_to_air1 annotation(
    Placement(transformation(origin = {88, 46}, extent = {{10, -10}, {-10, 10}}, rotation = 90)));
  Modelica.Blocks.Sources.Constant CV_tank2toAir1(k = heatCeffToAir*(Lx2_1*Ly2_1 + Lx2_2*Ly2_2)) annotation(
    Placement(transformation(origin = {58, 48}, extent = {{10, -10}, {-10, 10}}, rotation = 180)));
  Modelica.Thermal.HeatTransfer.Components.Convection CV_tank_to_air11 annotation(
    Placement(transformation(origin = {208, 40}, extent = {{10, -10}, {-10, 10}}, rotation = 90)));
  Modelica.Blocks.Sources.Constant CV_tank2toAir11(k = heatCeffToAir*(Lx3_1*Ly3_1)) annotation(
    Placement(transformation(origin = {180, 38}, extent = {{10, -10}, {-10, 10}}, rotation = 180)));
  Modelica.Fluid.Pipes.StaticPipe pipe_pump_cover1(redeclare package Medium = fluid1, diameter = 0.1, length = 0.5) annotation(
    Placement(transformation(origin = {148, 126}, extent = {{10, -10}, {-10, 10}})));
  PumpHeat pumpHeat(redeclare package Medium = fluid1, Q = Q_cyclone, m_flow = 110/60, T_start = T_ini) annotation(
    Placement(transformation(origin = {-74, 62}, extent = {{-20, -20}, {20, 20}})));
  GroundLoss groundLoss1(Gc_liquid = heatCefftTank2in*(Lx1_1*Ly1_1 + Ly1_1*level_start), G_wall = (Lx1_1*Ly1_1 + Lx1_1*level_start + Ly1_1*level_start)*kground/tank_thickness, Gc_ground = heatCeffToAir*(Lx1_1*Ly1_1 + Ly1_1*level_start)) annotation(
    Placement(transformation(origin = {-20, -84}, extent = {{-20, -20}, {20, 20}})));
  GroundLoss groundLoss2(Gc_liquid = heatCefftTank2in*(Lx2_1*Ly2_1 + Lx2_2*Ly2_2 + Ly2_1*level_start + Ly2_2*level_start + Lx2_1*level_start), G_wall = (Lx2_1*Ly2_1 + Lx2_1*level_start + Ly2_1*level_start)*kground/tank_thickness, Gc_ground = heatCeffToAir*(Lx2_1*Ly2_1 + Lx2_2*Ly2_2 + Ly2_1*level_start + Ly2_2*level_start + Lx2_1*level_start)) annotation(
    Placement(transformation(origin = {48, -92}, extent = {{-20, -20}, {20, 20}})));
  GroundLoss groundLoss3(Gc_liquid = heatCefftTank2in*(Lx3_1*Ly3_1 + Lx3_1*level_start + Ly3_1*level_start), G_wall = (Lx3_1*Ly3_1 + Lx3_1*level_start + Ly3_1*level_start)*kground/tank_thickness, Gc_ground = heatCeffToAir*(Lx3_1*Ly3_1 + Lx3_1*level_start + Ly3_1*level_start)) annotation(
    Placement(transformation(origin = {230, -92}, extent = {{-20, -20}, {20, 20}})));
  inner Modelica.Fluid.System system annotation(
    Placement(transformation(origin = {282, -162}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Celsius.PrescribedTemperature prescribedTemperature annotation(
    Placement(transformation(origin = {-20, -186}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.TimeTable timeTable(table = [0, Tair_deg; 36000, Tair_deg]) annotation(
    Placement(transformation(origin = {-94, -176}, extent = {{-10, -10}, {10, 10}})));
equation
  connect(CV_tank_to_air.fluid, tank1.heatPort) annotation(
    Line(points = {{-8, 46}, {-8, 14}}, color = {191, 0, 0}));
  connect(CV_tank2toAir.y, CV_tank_to_air.Gc) annotation(
    Line(points = {{19, 66}, {5, 66}, {5, 56}, {2, 56}}, color = {0, 0, 127}));
  connect(tank1.ports[2], path_1to2.port_a) annotation(
    Line(points = {{12, -6}, {12, -12}, {64, -12}}, color = {0, 127, 255}));
  connect(path_1to2.port_b, tank2.ports[1]) annotation(
    Line(points = {{84, -12}, {140, -12}, {140, 0}}, color = {0, 127, 255}));
  connect(tank2.ports[2], path_1to21.port_a) annotation(
    Line(points = {{140, 0}, {138, 0}, {138, -10}, {178, -10}, {178, -18}, {176, -18}}, color = {0, 127, 255}));
  connect(path_1to21.port_b, tank3.ports[3]) annotation(
    Line(points = {{196, -18}, {244, -18}, {244, -6}, {246, -6}}, color = {0, 127, 255}));
  connect(tank1.ports[1], pumpHeat.port_a) annotation(
    Line(points = {{12, -6}, {-62, -6}, {-62, 52}, {-74, 52}}, color = {0, 127, 255}));
  connect(groundLoss2.port_water, tank2.heatPort) annotation(
    Line(points = {{48, -36}, {120, -36}, {120, 20}}, color = {191, 0, 0}));
  connect(groundLoss1.port_water, tank1.heatPort) annotation(
    Line(points = {{-20, -32}, {-6, -32}, {-6, 14}, {-8, 14}}, color = {191, 0, 0}));
  connect(tank3.heatPort, groundLoss3.port_water) annotation(
    Line(points = {{226, 14}, {226, -38}}, color = {191, 0, 0}));
  connect(CV_tank_to_air1.fluid, tank2.heatPort) annotation(
    Line(points = {{88, 36}, {88, 20}, {120, 20}}, color = {191, 0, 0}));
  connect(CV_tank2toAir1.y, CV_tank_to_air1.Gc) annotation(
    Line(points = {{69, 48}, {79, 48}, {79, 46}, {78, 46}}, color = {0, 0, 127}));
  connect(CV_tank2toAir11.y, CV_tank_to_air11.Gc) annotation(
    Line(points = {{192, 38}, {195, 38}, {195, 40}, {198, 40}}, color = {0, 0, 127}));
  connect(CV_tank_to_air11.fluid, tank3.heatPort) annotation(
    Line(points = {{208, 30}, {208, 14}, {226, 14}}, color = {191, 0, 0}));
  connect(pumpHeat.port_b, pipe_pump_cover1.port_b) annotation(
    Line(points = {{-74, 72}, {-56, 72}, {-56, 126}, {138, 126}}, color = {0, 127, 255}));
  connect(pipe_pump_cover1.port_a, tank3.ports[5]) annotation(
    Line(points = {{158, 126}, {244, 126}, {244, -6}, {246, -6}}, color = {0, 127, 255}));
  connect(prescribedTemperature.port, groundLoss3.port_ground) annotation(
    Line(points = {{-10, -186}, {230, -186}, {230, -124}}, color = {191, 0, 0}));
  connect(timeTable.y, prescribedTemperature.T) annotation(
    Line(points = {{-82, -176}, {-32, -176}, {-32, -186}}, color = {0, 0, 127}));
  connect(groundLoss2.port_ground, prescribedTemperature.port) annotation(
    Line(points = {{46, -120}, {46, -186}, {-10, -186}}, color = {191, 0, 0}));
  connect(groundLoss1.port_ground, prescribedTemperature.port) annotation(
    Line(points = {{-22, -108}, {-10, -108}, {-10, -186}}, color = {191, 0, 0}));
  connect(CV_tank_to_air1.solid, prescribedTemperature.port) annotation(
    Line(points = {{88, 56}, {80, 56}, {80, 148}, {-200, 148}, {-200, -156}, {-10, -156}, {-10, -186}}, color = {191, 0, 0}));
  connect(CV_tank_to_air.solid, prescribedTemperature.port) annotation(
    Line(points = {{-8, 66}, {-8, 150}, {-212, 150}, {-212, -158}, {-10, -158}, {-10, -186}}, color = {191, 0, 0}));
  connect(CV_tank_to_air11.solid, prescribedTemperature.port) annotation(
    Line(points = {{208, 50}, {204, 50}, {204, 150}, {-210, 150}, {-210, -156}, {-10, -156}, {-10, -186}}, color = {191, 0, 0}));
  annotation(
    uses(Modelica(version = "4.0.0")),
    Diagram(coordinateSystem(extent = {{-260, 400}, {420, -240}})),
    version = "1.0.0");
end eva5_03_pumpHeat_ground;
