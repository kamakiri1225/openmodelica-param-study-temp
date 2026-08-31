model ana001_Tank3blocks_004_test
  extends Modelica.Icons.Example;
  parameter Integer portIndex = 3;
  //-----
  replaceable package fluid1 = Modelica.Media.Water.StandardWater;
  //replaceable package fluid1 = Modelica.Media.Water.StandardWaterOnePhase;
  //-----
  parameter Modelica.Units.SI.Length diamDmyPipe = 0.1;
  parameter Real zetaDmyPipe = 0.1;
  //-----
  parameter Real tank_height = 240/1000;
  parameter Real tank_thickness = 2.3/1000;
  parameter Real level_start = 160/1000;
  // tank1
  parameter Real Lx1_1 = 903/1000;
  parameter Real Lx1_2 = 1230/1000;
  parameter Real Ly1_1 = 479/1000;
  parameter Real Ly1_2 = 159/1000;
  // tank2
  parameter Real Lx2_1 = 1191/1000;
  parameter Real Lx2_2 = 478/1000;
  parameter Real Lx2_3 = 337/1000;
  parameter Real Ly2_1 = 1670/1000;
  // tank3
  parameter Real Lx3_1 = 573/1000;
  parameter Real Ly3_1 = 1191/1000;
  // タンク内熱伝達率
  parameter Real heatCefftTank2in = 100;
  // タンクの密度
  parameter Real rho_tank = 7000;
  //kg/m3
  // タンクの比熱
  parameter Real Cp_tank = 450;
  //J/kg K
  //地面との接触熱抵抗
  parameter Real kground = 80;
  //air
  parameter Real heatCeffToAir = 10;
  parameter Real Tair = 25;
  parameter Real T_ini = 25 + 273.15;
  // 機械内
  parameter Real Tmachine = 30.0;
  // T3基準温度プラス
  parameter Real T3puls = 1.5;
  Modelica.Fluid.Machines.ControlledPump pump_flood(p_a_nominal = 1e5, p_b_nominal = 5e5, m_flow_nominal = 41/60, use_m_flow_set = true, redeclare package Medium = fluid1, use_HeatTransfer = true, T_start = T_ini) annotation(
    Placement(transformation(origin = {334, 52}, extent = {{10, -10}, {-10, 10}}, rotation = -90)));
  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow HF_flood annotation(
    Placement(transformation(origin = {302, 56}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Vessels.OpenTank tank1(height = tank_height, crossArea = Lx1_1*Ly1_1, level_start = level_start, T_start = T_ini, portsData(each diameter = diamDmyPipe, each height = 0), redeclare package Medium = fluid1, use_T_start = true, use_HeatTransfer = true, nPorts = 3) annotation(
    Placement(transformation(origin = {12, 14}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Blocks.Sources.TimeTable tT_HF_flood(table = [0, 825; 36000, 825]) annotation(
    Placement(transformation(origin = {274, 56}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.TimeTable tT_pumpQ_flood(table = [0, 37.5/60; 36000, 37.5/60]) annotation(
    Placement(transformation(origin = {364, 48}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Fluid.Pipes.StaticPipe pipe_pump_flood(redeclare package Medium = fluid1, diameter = 0.1, length = 0.5) annotation(
    Placement(transformation(origin = {298, 130}, extent = {{10, -10}, {-10, 10}}, rotation = -0)));
  Modelica.Thermal.HeatTransfer.Celsius.FixedTemperature Tambient(T = Tair) annotation(
    Placement(transformation(origin = {-114, -124}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.TimeTable tT_Ttgt_Treg(table = [0, 25; 18000, 25; 36000, 25]) annotation(
    Placement(transformation(origin = {130, -217}, extent = {{6, -6}, {-6, 6}})));
  Modelica.Blocks.Math.Add add annotation(
    Placement(transformation(origin = {111, -204}, extent = {{6, -6}, {-6, 6}}, rotation = -90)));
  Modelica.Blocks.Sources.Constant const(k = 273.15) annotation(
    Placement(transformation(origin = {107, -222}, extent = {{-4, -4}, {4, 4}}, rotation = 90)));
  Modelica.Fluid.Sensors.VolumeFlowRate V_flow_pumpF_in(redeclare package Medium = fluid1) annotation(
    Placement(transformation(origin = {130, -44}, extent = {{5, 5}, {-5, -5}})));
  Modelica.Blocks.Math.Gain LPM_V_flow_pumpF_in(k = 1000*60) annotation(
    Placement(transformation(origin = {168, -92}, extent = {{4, -4}, {-4, 4}}, rotation = -90)));
  Modelica.Fluid.Machines.ControlledPump pumpF(redeclare package Medium = fluid1, control_m_flow = true, m_flow_nominal = 25/60, p_a_nominal = 1e5, p_b_nominal = 1e6, use_m_flow_set = true, T_start = T_ini) annotation(
    Placement(transformation(origin = {102, -76}, extent = {{10, -10}, {-10, 10}}, rotation = 90)));
  Modelica.Blocks.Sources.TimeTable tT_m_flow_pumpF(table = [0, 25/60; 36000, 25/60]) annotation(
    Placement(transformation(origin = {78, -81}, extent = {{-6, -6}, {6, 6}})));
  Modelica.Fluid.Vessels.ClosedVolume vol_Treg(redeclare package Medium = fluid1, T_start = T_ini, V = 0.001, nPorts = 3, use_HeatTransfer = true, use_portsData = false) annotation(
    Placement(transformation(origin = {100, -142}, extent = {{-8, 8}, {8, -8}}, rotation = -180)));
  Modelica.Fluid.Vessels.ClosedVolume vol_pumpF_out(redeclare package Medium = fluid1, V = 0.001, nPorts = 3, use_HeatTransfer = false, use_portsData = false, T_start = T_ini) annotation(
    Placement(transformation(origin = {130, -80}, extent = {{6, 6}, {-6, -6}}, rotation = 180)));
  Modelica.Fluid.Pipes.StaticPipe pipe_pumpF_2_Treg(redeclare package Medium = fluid1, diameter = 0.1, length = 0.5) annotation(
    Placement(transformation(origin = {130.321, -103.029}, extent = {{-8.25714, -7.84375}, {8.25714, 7.84375}}, rotation = -90)));
  Modelica.Fluid.Pipes.StaticPipe pipe_Treg_2_tank8_1(redeclare package Medium = fluid1, diameter = 0.1, length = 0.5) annotation(
    Placement(transformation(origin = {100.321, -173.029}, extent = {{-8.25714, -7.84375}, {8.25714, 7.84375}}, rotation = -90)));
  Modelica.Fluid.Sensors.Temperature T_pumpF_out(redeclare package Medium = fluid1) annotation(
    Placement(transformation(origin = {145, -86}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Fluid.Sensors.Temperature T_Treg_out(redeclare package Medium = fluid1) annotation(
    Placement(transformation(origin = {123, -160}, extent = {{-5, -5}, {5, 5}}, rotation = -90)));
  Modelica.Blocks.Continuous.PID PID_Treg(Td = 0, Ti = 0.1, initType = Modelica.Blocks.Types.Init.InitialOutput, k = 100, y_start = 0) annotation(
    Placement(transformation(origin = {144, -183}, extent = {{-6, -6}, {6, 6}})));
  Modelica.Blocks.Math.Feedback feedback2 annotation(
    Placement(transformation(origin = {123, -183}, extent = {{-6, 6}, {6, -6}})));
  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow Q_Treg annotation(
    Placement(transformation(origin = {134, -142}, extent = {{7, -7}, {-7, 7}})));
  Modelica.Thermal.HeatTransfer.Sensors.HeatFlowSensor Qout_Treg annotation(
    Placement(transformation(origin = {117, -142}, extent = {{-4, -4}, {4, 4}})));
  Modelica.Blocks.Sources.TimeTable tT_HF_cover(table = [0, 560; 36000, 560]) annotation(
    Placement(transformation(origin = {120, 74}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow HF_cover annotation(
    Placement(transformation(origin = {154, 74}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Machines.ControlledPump pump_cover(redeclare package Medium = fluid1, m_flow_nominal = 41/60, p_a_nominal = 1e5, p_b_nominal = 5e5, use_HeatTransfer = true, use_m_flow_set = true, T_start = T_ini) annotation(
    Placement(transformation(origin = {186, 74}, extent = {{10, -10}, {-10, 10}}, rotation = -90)));
  Modelica.Blocks.Sources.TimeTable tT_pumpQ_flood1(table = [0, 57.05/60; 36000, 57.05/60]) annotation(
    Placement(transformation(origin = {228, 72}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Fluid.Pipes.StaticPipe pipe_pump_cover(redeclare package Medium = fluid1, diameter = 0.1, length = 0.5) annotation(
    Placement(transformation(origin = {118, 108}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Fluid.Vessels.ClosedVolume V_pump_cover(redeclare package Medium = fluid1, V = 0.001, nPorts = 3, use_portsData = false, T_start = T_ini) annotation(
    Placement(transformation(origin = {14, 168}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Pipes.StaticPipe pipe_m_to_tank(redeclare package Medium = fluid1, diameter = 0.1, length = 0.5) annotation(
    Placement(transformation(origin = {-154, 108}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.Convection CV_tank_to_air annotation(
    Placement(transformation(origin = {-6, 64}, extent = {{-10, -10}, {10, 10}}, rotation = -90)));
  Modelica.Blocks.Sources.Constant CV_tank2toAir(k = heatCeffToAir*(Lx1_1*Ly1_1)) annotation(
    Placement(transformation(origin = {30, 66}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Fluid.Vessels.OpenTank tank2(redeclare package Medium = fluid1, T_start = T_ini, crossArea = Lx2_1*Ly1_2, height = tank_height, level_start = level_start, nPorts = 4, portsData(each diameter = diamDmyPipe, each height = 0), use_HeatTransfer = true, use_T_start = true) annotation(
    Placement(transformation(origin = {140, 20}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Fluid.Vessels.OpenTank tank3(redeclare package Medium = fluid1, T_start = T_ini, crossArea = Lx3_1*Ly3_1, height = tank_height, level_start = level_start*0.2, nPorts = 5, portsData(each diameter = diamDmyPipe, each height = 0), use_HeatTransfer = true, use_T_start = true) annotation(
    Placement(transformation(origin = {246, 14}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Fluid.Fittings.SimpleGenericOrifice path_1to2(redeclare package Medium = fluid1, diameter = diamDmyPipe, zeta = zetaDmyPipe) annotation(
    Placement(transformation(origin = {74, -12}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Fittings.SimpleGenericOrifice path_1to21(redeclare package Medium = fluid1, diameter = diamDmyPipe, zeta = zetaDmyPipe) annotation(
    Placement(transformation(origin = {188, -12}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Sensors.Temperature T_flood_out(redeclare package Medium = fluid1) annotation(
    Placement(transformation(origin = {267, 156}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Sources.TimeTable tT_HF_cyclone(table = [0, 568; 36000, 568]) annotation(
    Placement(transformation(origin = {-136, 62}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow HF_cyclone annotation(
    Placement(transformation(origin = {-100, 60}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Machines.ControlledPump pump_cyclone(redeclare package Medium = fluid1, T_start = T_ini, m_flow_nominal = 41/60, p_a_nominal = 1e5, p_b_nominal = 5e5, use_HeatTransfer = true, use_m_flow_set = true) annotation(
    Placement(transformation(origin = {-62, 62}, extent = {{10, -10}, {-10, 10}}, rotation = -90)));
  Modelica.Blocks.Sources.TimeTable tT_pumpQ_cyclone(table = [0, 95/60; 36000, 95/60]) annotation(
    Placement(transformation(origin = {-36, 58}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Fluid.Sensors.Temperature T_cover_out(redeclare package Medium = fluid1) annotation(
    Placement(transformation(origin = {85, 114}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Sources.Constant CV_const_tank1in1(k = heatCefftTank2in*(Lx2_1*Ly2_1 + Lx2_1*level_start + Ly2_1*level_start)) annotation(
    Placement(transformation(origin = {20, -46}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.Convection CV_tank1in11 annotation(
    Placement(transformation(origin = {48, -46}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Modelica.Thermal.HeatTransfer.Components.ThermalConductor tC_ground_tank12(G = (Lx2_1*Ly2_1 + Lx2_1*level_start + Ly2_1*level_start)*kground/tank_thickness) annotation(
    Placement(transformation(origin = {48, -82}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Modelica.Thermal.HeatTransfer.Components.Convection convection_ground_tank12 annotation(
    Placement(transformation(origin = {46, -110}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Modelica.Blocks.Sources.Constant CV_pumpB21(k = heatCeffToAir*(Lx2_1*Ly2_1 + Lx2_1*level_start + Ly2_1*level_start)) annotation(
    Placement(transformation(origin = {14, -110}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant CV_const_tank1in11(k = heatCefftTank2in*(Lx1_1*Ly1_1 + Lx1_1*level_start + Ly1_1*level_start)) annotation(
    Placement(transformation(origin = {-58, -44}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.Convection CV_tank1in111 annotation(
    Placement(transformation(origin = {-20, -42}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Modelica.Thermal.HeatTransfer.Components.ThermalConductor tC_ground_tank121(G = (Lx1_1*Ly1_1 + Lx1_1*level_start + Ly1_1*level_start)*kground/tank_thickness) annotation(
    Placement(transformation(origin = {-20, -74}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Modelica.Blocks.Sources.Constant CV_pumpB211(k = heatCeffToAir*(Lx1_1*Ly1_1 + Lx1_1*level_start + Ly1_1*level_start)) annotation(
    Placement(transformation(origin = {-58, -98}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.Convection convection_ground_tank121 annotation(
    Placement(transformation(origin = {-22, -98}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Modelica.Blocks.Sources.Constant CV_const_tank1in12(k = heatCefftTank2in*(Lx3_1*Ly3_1 + Lx3_1*level_start + Ly3_1*level_start)) annotation(
    Placement(transformation(origin = {194, -48}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.Convection CV_tank1in112 annotation(
    Placement(transformation(origin = {226, -48}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Modelica.Thermal.HeatTransfer.Components.ThermalConductor tC_ground_tank122(G = (Lx3_1*Ly3_1 + Lx3_1*level_start + Ly3_1*level_start)*kground/tank_thickness) annotation(
    Placement(transformation(origin = {230, -82}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Modelica.Thermal.HeatTransfer.Components.Convection convection_ground_tank122 annotation(
    Placement(transformation(origin = {230, -114}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Modelica.Blocks.Sources.Constant CV_pumpB212(k = heatCeffToAir*(Lx3_1*Ly3_1 + Lx3_1*level_start + Ly3_1*level_start)) annotation(
    Placement(transformation(origin = {200, -114}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.Convection CV_tank_to_air1 annotation(
    Placement(transformation(origin = {88, 46}, extent = {{10, -10}, {-10, 10}}, rotation = 90)));
  Modelica.Blocks.Sources.Constant CV_tank2toAir1(k = heatCeffToAir*(Lx2_1*Ly2_1)) annotation(
    Placement(transformation(origin = {56, 48}, extent = {{10, -10}, {-10, 10}}, rotation = 180)));
  Modelica.Thermal.HeatTransfer.Components.Convection CV_tank_to_air11 annotation(
    Placement(transformation(origin = {208, 40}, extent = {{10, -10}, {-10, 10}}, rotation = 90)));
  Modelica.Blocks.Sources.Constant CV_tank2toAir11(k = heatCeffToAir*(Lx3_1*Ly3_1)) annotation(
    Placement(transformation(origin = {180, 38}, extent = {{10, -10}, {-10, 10}}, rotation = 180)));
  Modelica.Fluid.Pipes.StaticPipe pipe_pump_cover1(redeclare package Medium = fluid1, diameter = 0.1, length = 0.5) annotation(
    Placement(transformation(origin = {150, 120}, extent = {{10, -10}, {-10, 10}})));
equation
  connect(tT_HF_flood.y, HF_flood.Q_flow) annotation(
    Line(points = {{285, 56}, {292, 56}}, color = {0, 0, 127}));
  connect(tT_pumpQ_flood.y, pump_flood.m_flow_set) annotation(
    Line(points = {{353, 48}, {353, 47}, {342, 47}}, color = {0, 0, 127}));
  connect(pump_flood.port_b, pipe_pump_flood.port_a) annotation(
    Line(points = {{334, 62}, {334, 129}, {308, 129}, {308, 130}}, color = {0, 127, 255}));
  connect(add.u1, tT_Ttgt_Treg.y) annotation(
    Line(points = {{114.6, -211.2}, {114.6, -215}, {143, -215}}, color = {0, 0, 127}));
  connect(add.u2, const.y) annotation(
    Line(points = {{107.4, -211.2}, {107.4, -218.2}}, color = {0, 0, 127}));
  connect(V_flow_pumpF_in.V_flow, LPM_V_flow_pumpF_in.u) annotation(
    Line(points = {{130, -49.5}, {130, -92.75}, {168, -92.75}, {168, -97}}, color = {0, 0, 127}));
  connect(tT_m_flow_pumpF.y, pumpF.m_flow_set) annotation(
    Line(points = {{84.6, -81}, {90.1, -81}, {90.1, -71}, {93.6, -71}}, color = {0, 0, 127}));
  connect(V_flow_pumpF_in.port_b, pumpF.port_a) annotation(
    Line(points = {{125, -44}, {125, -42}, {102, -42}, {102, -66}}, color = {0, 127, 255}));
  connect(pumpF.port_b, vol_pumpF_out.ports[1]) annotation(
    Line(points = {{102, -86}, {130, -86}}, color = {0, 127, 255}));
  connect(vol_pumpF_out.ports[2], pipe_pumpF_2_Treg.port_a) annotation(
    Line(points = {{130, -86}, {130, -95}}, color = {0, 127, 255}));
  connect(pipe_pumpF_2_Treg.port_b, vol_Treg.ports[1]) annotation(
    Line(points = {{130.321, -111.286}, {130.321, -125.286}, {100.321, -125.286}, {100.321, -150.286}}, color = {0, 127, 255}));
  connect(vol_Treg.ports[2], pipe_Treg_2_tank8_1.port_a) annotation(
    Line(points = {{100, -150}, {100, -165}}, color = {0, 127, 255}));
  connect(T_pumpF_out.port, vol_pumpF_out.ports[3]) annotation(
    Line(points = {{145, -91}, {130, -91}, {130, -86}}, color = {0, 127, 255}));
  connect(T_Treg_out.port, vol_Treg.ports[3]) annotation(
    Line(points = {{118, -160}, {100, -160}, {100, -150}}, color = {0, 127, 255}));
  connect(feedback2.y, PID_Treg.u) annotation(
    Line(points = {{128.4, -183}, {137.4, -183}}, color = {0, 0, 127}));
  connect(feedback2.u1, add.y) annotation(
    Line(points = {{118.2, -183}, {111.2, -183}, {111.2, -197}}, color = {0, 0, 127}));
  connect(Q_Treg.Q_flow, PID_Treg.y) annotation(
    Line(points = {{141, -142}, {158, -142}, {158, -183}, {151, -183}}, color = {0, 0, 127}));
  connect(vol_Treg.heatPort, Qout_Treg.port_a) annotation(
    Line(points = {{108, -142}, {113, -142}}, color = {191, 0, 0}));
  connect(Qout_Treg.port_b, Q_Treg.port) annotation(
    Line(points = {{121, -142}, {127, -142}}, color = {191, 0, 0}));
  connect(HF_flood.port, pump_flood.heatPort) annotation(
    Line(points = {{312, 56}, {328, 56}}, color = {191, 0, 0}));
  connect(tT_HF_cover.y, HF_cover.Q_flow) annotation(
    Line(points = {{131, 74}, {143, 74}}, color = {0, 0, 127}));
  connect(HF_cover.port, pump_cover.heatPort) annotation(
    Line(points = {{164, 74}, {180, 74}, {180, 78}}, color = {191, 0, 0}));
  connect(tT_pumpQ_flood1.y, pump_cover.m_flow_set) annotation(
    Line(points = {{217, 72}, {195, 72}, {195, 70}, {193, 70}}, color = {0, 0, 127}));
  connect(pump_cover.port_b, pipe_pump_cover.port_a) annotation(
    Line(points = {{186, 84}, {186, 107}, {130, 107}, {130, 108.5}, {128, 108.5}, {128, 108}}, color = {0, 127, 255}));
  connect(pipe_pump_cover.port_b, V_pump_cover.ports[1]) annotation(
    Line(points = {{108, 108}, {20.5, 108}, {20.5, 120}, {18.25, 120}, {18.25, 146}, {21.125, 146}, {21.125, 158}, {14, 158}}, color = {0, 127, 255}));
  connect(CV_tank_to_air.fluid, tank1.heatPort) annotation(
    Line(points = {{-6, 54}, {-8, 54}, {-8, 14}}, color = {191, 0, 0}));
  connect(CV_tank2toAir.y, CV_tank_to_air.Gc) annotation(
    Line(points = {{19, 66}, {5, 66}, {5, 64}, {4, 64}}, color = {0, 0, 127}));
  connect(CV_tank_to_air.solid, Tambient.port) annotation(
    Line(points = {{-6, 74}, {-8, 74}, {-8, 150}, {-216, 150}, {-216, -124}, {-104, -124}}, color = {191, 0, 0}));
  connect(tank2.ports[1], V_flow_pumpF_in.port_a) annotation(
    Line(points = {{140, 0}, {135, 0}, {135, -4}, {136, -4}, {136, -44}, {135, -44}}, color = {0, 127, 255}));
  connect(pipe_Treg_2_tank8_1.port_b, tank3.ports[1]) annotation(
    Line(points = {{100, -182}, {98, -182}, {98, -246}, {246, -246}, {246, -6}}, color = {0, 127, 255}));
  connect(tank3.ports[2], pump_flood.port_a) annotation(
    Line(points = {{246, -6}, {246, 18}, {334, 18}, {334, 42}}, color = {0, 127, 255}));
  connect(pipe_pump_flood.port_b, V_pump_cover.ports[2]) annotation(
    Line(points = {{288, 130}, {14, 130}, {14, 158}}, color = {0, 127, 255}));
  connect(V_pump_cover.ports[3], pipe_m_to_tank.port_b) annotation(
    Line(points = {{14, 158}, {10, 158}, {10, 108}, {-144, 108}}, color = {0, 127, 255}));
  connect(pipe_m_to_tank.port_a, tank1.ports[1]) annotation(
    Line(points = {{-164, 108}, {-164, -6}, {12, -6}}, color = {0, 127, 255}));
  connect(tank1.ports[3], path_1to2.port_a) annotation(
    Line(points = {{12, -6}, {12, -12}, {64, -12}}, color = {0, 127, 255}));
  connect(path_1to2.port_b, tank2.ports[3]) annotation(
    Line(points = {{84, -12}, {140, -12}, {140, 0}}, color = {0, 127, 255}));
  connect(tank2.ports[4], path_1to21.port_a) annotation(
    Line(points = {{140, 0}, {138, 0}, {138, -10}, {178, -10}, {178, -12}}, color = {0, 127, 255}));
  connect(path_1to21.port_b, tank3.ports[3]) annotation(
    Line(points = {{198, -12}, {246, -12}, {246, -6}}, color = {0, 127, 255}));
  connect(T_flood_out.port, pipe_pump_flood.port_b) annotation(
    Line(points = {{268, 152}, {268, 130}, {288, 130}}, color = {0, 127, 255}));
  connect(tT_HF_cyclone.y, HF_cyclone.Q_flow) annotation(
    Line(points = {{-124, 62}, {-110, 62}, {-110, 60}}, color = {0, 0, 127}));
  connect(HF_cyclone.port, pump_cyclone.heatPort) annotation(
    Line(points = {{-90, 60}, {-68, 60}, {-68, 66}}, color = {191, 0, 0}));
  connect(tT_pumpQ_cyclone.y, pump_cyclone.m_flow_set) annotation(
    Line(points = {{-47, 58}, {-54, 58}}, color = {0, 0, 127}));
  
  //modify
  connect(tank1.ports[portIndex-1], pump_cyclone.port_a) annotation(
    Line(points = {{12, -6}, {-62, -6}, {-62, 52}}, color = {0, 127, 255}));
  connect(pump_cover.port_a, tank3.ports[4]) annotation(
    Line(points = {{186, 64}, {194, 64}, {194, -4}, {224, -4}, {224, -6}, {246, -6}}, color = {0, 127, 255}));
  connect(T_cover_out.port, pipe_pump_cover.port_b) annotation(
    Line(points = {{85, 109}, {108, 109}, {108, 108}}, color = {0, 127, 255}));
  connect(CV_const_tank1in1.y, CV_tank1in11.Gc) annotation(
    Line(points = {{32, -46}, {38, -46}}, color = {0, 0, 127}));
  connect(CV_tank1in11.solid, tC_ground_tank12.port_b) annotation(
    Line(points = {{48, -56}, {48, -72}}, color = {191, 0, 0}));
  connect(tC_ground_tank12.port_a, convection_ground_tank12.fluid) annotation(
    Line(points = {{48, -92}, {46, -92}, {46, -100}}, color = {191, 0, 0}));
  connect(CV_pumpB21.y, convection_ground_tank12.Gc) annotation(
    Line(points = {{25, -110}, {36, -110}}, color = {0, 0, 127}));
  connect(convection_ground_tank12.solid, Tambient.port) annotation(
    Line(points = {{46, -120}, {48, -120}, {48, -144}, {-104, -144}, {-104, -124}}, color = {191, 0, 0}));
  connect(CV_tank1in11.fluid, tank2.heatPort) annotation(
    Line(points = {{48, -36}, {120, -36}, {120, 20}}, color = {191, 0, 0}));
  connect(tC_ground_tank121.port_a, convection_ground_tank121.fluid) annotation(
    Line(points = {{-20, -84}, {-20, -88}, {-22, -88}}, color = {191, 0, 0}));
  connect(CV_tank1in111.solid, tC_ground_tank121.port_b) annotation(
    Line(points = {{-20, -52}, {-20, -64}}, color = {191, 0, 0}));
  connect(CV_tank1in111.fluid, tank1.heatPort) annotation(
    Line(points = {{-20, -32}, {-6, -32}, {-6, 14}, {-8, 14}}, color = {191, 0, 0}));
  connect(CV_const_tank1in11.y, CV_tank1in111.Gc) annotation(
    Line(points = {{-47, -44}, {-30, -44}, {-30, -42}}, color = {0, 0, 127}));
  connect(CV_pumpB211.y, convection_ground_tank121.Gc) annotation(
    Line(points = {{-46, -98}, {-32, -98}}, color = {0, 0, 127}));
  connect(convection_ground_tank121.solid, Tambient.port) annotation(
    Line(points = {{-22, -108}, {-22, -124}, {-104, -124}}, color = {191, 0, 0}));
  connect(CV_pumpB212.y, convection_ground_tank122.Gc) annotation(
    Line(points = {{212, -114}, {220, -114}}, color = {0, 0, 127}));
  connect(CV_const_tank1in12.y, CV_tank1in112.Gc) annotation(
    Line(points = {{206, -48}, {216, -48}}, color = {0, 0, 127}));
  connect(tank3.heatPort, CV_tank1in112.fluid) annotation(
    Line(points = {{226, 14}, {226, -38}}, color = {191, 0, 0}));
  connect(CV_tank1in112.solid, tC_ground_tank122.port_b) annotation(
    Line(points = {{226, -58}, {230, -58}, {230, -72}}, color = {191, 0, 0}));
  connect(tC_ground_tank122.port_a, convection_ground_tank122.fluid) annotation(
    Line(points = {{230, -92}, {230, -104}}, color = {191, 0, 0}));
  connect(convection_ground_tank122.solid, Tambient.port) annotation(
    Line(points = {{230, -124}, {232, -124}, {232, -256}, {-104, -256}, {-104, -124}}, color = {191, 0, 0}));
  connect(CV_tank_to_air1.fluid, tank2.heatPort) annotation(
    Line(points = {{88, 36}, {88, 20}, {120, 20}}, color = {191, 0, 0}));
  connect(CV_tank2toAir1.y, CV_tank_to_air1.Gc) annotation(
    Line(points = {{68, 48}, {78, 48}, {78, 46}}, color = {0, 0, 127}));
  connect(CV_tank_to_air1.solid, Tambient.port) annotation(
    Line(points = {{88, 56}, {88, 154}, {-212, 154}, {-212, -130}, {-104, -130}, {-104, -124}}, color = {191, 0, 0}));
  connect(CV_tank2toAir11.y, CV_tank_to_air11.Gc) annotation(
    Line(points = {{192, 38}, {195, 38}, {195, 40}, {198, 40}}, color = {0, 0, 127}));
  connect(CV_tank_to_air11.fluid, tank3.heatPort) annotation(
    Line(points = {{208, 30}, {208, 14}, {226, 14}}, color = {191, 0, 0}));
  connect(CV_tank_to_air11.solid, Tambient.port) annotation(
    Line(points = {{208, 50}, {210, 50}, {210, 144}, {-208, 144}, {-208, -124}, {-104, -124}}, color = {191, 0, 0}));
  connect(T_flood_out.T, feedback2.u2) annotation(
    Line(points = {{270, 156}, {402, 156}, {402, -170}, {124, -170}, {124, -178}}, color = {0, 0, 127}));
  connect(pump_cyclone.port_b, pipe_pump_cover1.port_b) annotation(
    Line(points = {{-62, 72}, {-56, 72}, {-56, 122}, {140, 122}, {140, 120}}, color = {0, 127, 255}));
  connect(pipe_pump_cover1.port_a, tank3.ports[5]) annotation(
    Line(points = {{160, 120}, {246, 120}, {246, -6}}, color = {0, 127, 255}));
  annotation(
    uses(Modelica(version = "4.0.0")),
    Diagram(coordinateSystem(extent = {{-220, 180}, {380, -260}}), graphics = {Rectangle(origin = {125, -176}, fillColor = {85, 255, 255}, pattern = LinePattern.Dash, fillPattern = FillPattern.Solid, extent = {{-47, 54}, {47, -54}}), Text(origin = {126, -236}, extent = {{-44, 4}, {44, -4}}, textString = "Temperature regulator")}),
    version = "");
end ana001_Tank3blocks_004_test;
