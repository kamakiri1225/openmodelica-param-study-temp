model ana001_Tank_004
  extends Modelica.Icons.Example;
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
  parameter Real Lx1 = 500/1000;
  parameter Real Ly1 = 300/1000;
  // tank2
  parameter Real Lx2 = 500/1000;
  parameter Real Ly2 = 300/1000;
  // tank3
  parameter Real Lx3 = 250/1000;
  parameter Real Ly3 = 300/1000;
  // tank4
  parameter Real Lx4 = 250/1000;
  parameter Real Ly4 = 300/1000;
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
  Modelica.Fluid.Machines.ControlledPump pump_pumpB(p_a_nominal = 1e5, p_b_nominal = 5e5, m_flow_nominal = 41/60, use_m_flow_set = true, redeclare package Medium = fluid1, use_HeatTransfer = true) annotation(
    Placement(transformation(origin = {310, 94}, extent = {{10, -10}, {-10, 10}}, rotation = -90)));
  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow HF_pumpB annotation(
    Placement(transformation(origin = {276, 98}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Vessels.OpenTank tank1(height = tank_height, crossArea = Lx1*Ly1, level_start = level_start, T_start = T_ini, portsData(each diameter = diamDmyPipe, each height = 0), redeclare package Medium = fluid1, use_T_start = true, use_HeatTransfer = true, nPorts = 2) annotation(
    Placement(transformation(origin = {12, 14}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Blocks.Sources.TimeTable tT_HF_pumpB(table = [0, 1000; 36000, 1000]) annotation(
    Placement(transformation(origin = {274, 72}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.TimeTable tT_pumpB(table = [0, 40/60; 36000, 40/60]) annotation(
    Placement(transformation(origin = {352, 82}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Fluid.Pipes.StaticPipe pipe_pump_flood(redeclare package Medium = fluid1, diameter = 0.1, length = 0.5) annotation(
    Placement(transformation(origin = {298, 130}, extent = {{10, -10}, {-10, 10}}, rotation = -0)));
  Modelica.Thermal.HeatTransfer.Celsius.FixedTemperature Tambient(T = Tair) annotation(
    Placement(transformation(origin = {-114, -124}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.ThermalConductor tC_ground_tank1(G = Lx1*Ly1*kground/tank_thickness) annotation(
    Placement(transformation(origin = {-16, -64}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Modelica.Thermal.HeatTransfer.Components.Convection convection_ground_tank1 annotation(
    Placement(transformation(origin = {-18, -90}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Modelica.Blocks.Sources.Constant CV_pumpB2(k = heatCeffToAir*2*(Lx1*Ly1 + Lx1*level_start + Ly1*level_start)) annotation(
    Placement(transformation(origin = {-52, -90}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.Convection CV_tank1in1 annotation(
    Placement(transformation(origin = {-16, -32}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Modelica.Blocks.Sources.Constant CV_const_tank1in(k = heatCefftTank2in*(Lx1*Ly1 + 2*Lx1*level_start + 2*Ly1*level_start)) annotation(
    Placement(transformation(origin = {-54, -30}, extent = {{-10, -10}, {10, 10}}, rotation = -0)));
  Modelica.Blocks.Sources.TimeTable tT_Ttgt_Treg(table = [0, 25; 18000, 25; 36000, 25]) annotation(
    Placement(transformation(origin = {130, -217}, extent = {{6, -6}, {-6, 6}})));
  Modelica.Blocks.Math.Add add annotation(
    Placement(transformation(origin = {111, -204}, extent = {{6, -6}, {-6, 6}}, rotation = -90)));
  Modelica.Blocks.Sources.Constant const(k = 273.15) annotation(
    Placement(transformation(origin = {107, -222}, extent = {{-4, -4}, {4, 4}}, rotation = 90)));
  Modelica.Fluid.Sensors.VolumeFlowRate V_flow_pumpF_in(redeclare package Medium = fluid1) annotation(
    Placement(transformation(origin = {130, -44}, extent = {{5, 5}, {-5, -5}})));
  Modelica.Blocks.Math.Gain LPM_V_flow_pumpF_in(k = 1000*60) annotation(
    Placement(transformation(origin = {148, -42}, extent = {{4, -4}, {-4, 4}}, rotation = -90)));
  Modelica.Fluid.Machines.ControlledPump pumpF(redeclare package Medium = fluid1, control_m_flow = true, m_flow_nominal = 25/60, p_a_nominal = 1e5, p_b_nominal = 1e6, use_m_flow_set = true, T_start = T_ini) annotation(
    Placement(transformation(origin = {102, -86}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.TimeTable tT_m_flow_pumpF(table = [0, 25/60; 36000, 25/60]) annotation(
    Placement(transformation(origin = {106, -59}, extent = {{6, -6}, {-6, 6}}, rotation = -0)));
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
  Modelica.Blocks.Sources.TimeTable tT_HF_pumpA(table = [0, 1200; 36000, 1200]) annotation(
    Placement(transformation(origin = {82, 68}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow HF_pumpA annotation(
    Placement(transformation(origin = {116, 68}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Machines.ControlledPump pump_pumpA(redeclare package Medium = fluid1, m_flow_nominal = 41/60, p_a_nominal = 1e5, p_b_nominal = 5e5, use_HeatTransfer = true, use_m_flow_set = true, T_start = T_ini) annotation(
    Placement(transformation(origin = {148, 68}, extent = {{10, -10}, {-10, 10}}, rotation = -90)));
  Modelica.Blocks.Sources.TimeTable tT_pumpA(table = [0, 70/60; 36000, 70/60]) annotation(
    Placement(transformation(origin = {188, 66}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Fluid.Pipes.StaticPipe pipe_pump_cover(redeclare package Medium = fluid1, diameter = 0.1, length = 0.5) annotation(
    Placement(transformation(origin = {120, 106}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Fluid.Vessels.ClosedVolume V_pump_cover(redeclare package Medium = fluid1, V = 0.001, nPorts = 3, use_portsData = false, T_start = T_ini) annotation(
    Placement(transformation(origin = {20, 150}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Pipes.StaticPipe pipe_m_to_tank(redeclare package Medium = fluid1, diameter = 0.1, length = 0.5) annotation(
    Placement(transformation(origin = {-72, 108}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.Convection CV_tank_to_air annotation(
    Placement(transformation(origin = {-8, 66}, extent = {{10, -10}, {-10, 10}}, rotation = 90)));
  Modelica.Blocks.Sources.Constant CV_tank2toAir(k = heatCeffToAir*Lx1*Ly1) annotation(
    Placement(transformation(origin = {-40, 66}, extent = {{-10, -10}, {10, 10}}, rotation = -0)));
  Modelica.Fluid.Vessels.OpenTank tank2(redeclare package Medium = fluid1, T_start = T_ini, crossArea = Lx2*Ly2, height = tank_height, level_start = level_start, nPorts = 4, portsData(each diameter = diamDmyPipe, each height = 0), use_HeatTransfer = true, use_T_start = true) annotation(
    Placement(transformation(origin = {146, 12}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Fluid.Vessels.OpenTank tank3(redeclare package Medium = fluid1, T_start = T_ini, crossArea = Lx3*Ly3, height = tank_height, level_start = level_start, nPorts = 3, portsData(each diameter = diamDmyPipe, each height = 0), use_HeatTransfer = true, use_T_start = true) annotation(
    Placement(transformation(origin = {310, 24}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Fluid.Fittings.SimpleGenericOrifice path_1to2(redeclare package Medium = fluid1, diameter = diamDmyPipe, zeta = zetaDmyPipe) annotation(
    Placement(transformation(origin = {80, -12}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Fittings.SimpleGenericOrifice path_1to21(redeclare package Medium = fluid1, diameter = diamDmyPipe, zeta = zetaDmyPipe) annotation(
    Placement(transformation(origin = {214, 2}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Sensors.Temperature T_pumpB_out(redeclare package Medium = fluid1) annotation(
    Placement(transformation(origin = {267, 156}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Sources.Constant CV_tank2toAir1(k = heatCeffToAir*Lx1*Ly1) annotation(
    Placement(transformation(origin = {62, 34}, extent = {{-10, -10}, {10, 10}}, rotation = -0)));
  Modelica.Thermal.HeatTransfer.Components.Convection CV_tank_to_air1 annotation(
    Placement(transformation(origin = {94, 34}, extent = {{10, -10}, {-10, 10}}, rotation = 90)));
  Modelica.Blocks.Sources.Constant CV_const_tank1in1(k = heatCefftTank2in*(Lx1*Ly1 + 2*Lx1*level_start + 2*Ly1*level_start)) annotation(
    Placement(transformation(origin = {18, -42}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.Convection CV_tank1in11 annotation(
    Placement(transformation(origin = {48, -44}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Modelica.Thermal.HeatTransfer.Components.ThermalConductor tC_ground_tank11(G = Lx1*Ly1*kground/tank_thickness) annotation(
    Placement(transformation(origin = {50, -74}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Modelica.Thermal.HeatTransfer.Components.Convection convection_ground_tank11 annotation(
    Placement(transformation(origin = {50, -104}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Modelica.Blocks.Sources.Constant CV_pumpB21(k = heatCeffToAir*2*(Lx1*Ly1 + Lx1*level_start + Ly1*level_start)) annotation(
    Placement(transformation(origin = {18, -104}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant CV_const_tank1in11(k = heatCefftTank2in*(Lx1*Ly1 + 2*Lx1*level_start + 2*Ly1*level_start)) annotation(
    Placement(transformation(origin = {220, -50}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.Convection CV_tank1in111 annotation(
    Placement(transformation(origin = {248, -50}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Modelica.Thermal.HeatTransfer.Components.ThermalConductor tC_ground_tank111(G = Lx1*Ly1*kground/tank_thickness) annotation(
    Placement(transformation(origin = {248, -80}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Modelica.Thermal.HeatTransfer.Components.Convection convection_ground_tank111 annotation(
    Placement(transformation(origin = {248, -114}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Modelica.Blocks.Sources.Constant CV_pumpB211(k = heatCeffToAir*2*(Lx1*Ly1 + Lx1*level_start + Ly1*level_start)) annotation(
    Placement(transformation(origin = {212, -106}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant CV_tank2toAir11(k = heatCeffToAir*Lx1*Ly1) annotation(
    Placement(transformation(origin = {218, 34}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.Convection CV_tank_to_air11 annotation(
    Placement(transformation(origin = {250, 32}, extent = {{10, -10}, {-10, 10}}, rotation = 90)));
  inner Modelica.Fluid.System system annotation(
    Placement(transformation(origin = {-186, -188}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Vessels.OpenTank tank4(redeclare package Medium = fluid1, T_start = T_ini, crossArea = Lx4*Ly4, height = tank_height, level_start = level_start, nPorts = 3, portsData(each diameter = diamDmyPipe, each height = 0), use_HeatTransfer = true, use_T_start = true) annotation(
    Placement(transformation(origin = {310, -58}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Fluid.Fittings.SimpleGenericOrifice path_1to211(redeclare package Medium = fluid1, diameter = diamDmyPipe, zeta = zetaDmyPipe) annotation(
    Placement(transformation(origin = {308, -22}, extent = {{-10, -10}, {10, 10}}, rotation = -90)));
equation
  connect(tT_HF_pumpB.y, HF_pumpB.Q_flow) annotation(
    Line(points = {{285, 72}, {260.5, 72}, {260.5, 98}, {266, 98}}, color = {0, 0, 127}));
  connect(tT_pumpB.y, pump_pumpB.m_flow_set) annotation(
    Line(points = {{341, 82}, {341, 89}, {318, 89}}, color = {0, 0, 127}));
  connect(pump_pumpB.port_b, pipe_pump_flood.port_a) annotation(
    Line(points = {{310, 104}, {310, 117}, {308, 117}, {308, 130}}, color = {0, 127, 255}));
  connect(convection_ground_tank1.fluid, tC_ground_tank1.port_a) annotation(
    Line(points = {{-18, -80}, {-18, -78}, {-16, -78}, {-16, -74}}, color = {191, 0, 0}));
  connect(convection_ground_tank1.solid, Tambient.port) annotation(
    Line(points = {{-18, -100}, {-17, -100}, {-17, -124}, {-104, -124}}, color = {191, 0, 0}));
  connect(CV_pumpB2.y, convection_ground_tank1.Gc) annotation(
    Line(points = {{-41, -90}, {-28, -90}}, color = {0, 0, 127}));
  connect(CV_tank1in1.solid, tC_ground_tank1.port_b) annotation(
    Line(points = {{-16, -42}, {-16, -54}}, color = {191, 0, 0}));
  connect(CV_const_tank1in.y, CV_tank1in1.Gc) annotation(
    Line(points = {{-43, -30}, {-45.5, -30}, {-45.5, -32}, {-26, -32}}, color = {0, 0, 127}));
  connect(CV_tank1in1.fluid, tank1.heatPort) annotation(
    Line(points = {{-16, -22}, {-8, -22}, {-8, 14}}, color = {191, 0, 0}));
  connect(add.u1, tT_Ttgt_Treg.y) annotation(
    Line(points = {{114.6, -211.2}, {114.6, -215}, {143, -215}}, color = {0, 0, 127}));
  connect(add.u2, const.y) annotation(
    Line(points = {{107.4, -211.2}, {107.4, -218.2}}, color = {0, 0, 127}));
  connect(V_flow_pumpF_in.V_flow, LPM_V_flow_pumpF_in.u) annotation(
    Line(points = {{130, -49.5}, {130, -52.75}, {148, -52.75}, {148, -47}}, color = {0, 0, 127}));
  connect(tT_m_flow_pumpF.y, pumpF.m_flow_set) annotation(
    Line(points = {{99, -59}, {97.8, -59}, {97.8, -78}, {95.8, -78}}, color = {0, 0, 127}));
  connect(V_flow_pumpF_in.port_b, pumpF.port_a) annotation(
    Line(points = {{125, -44}, {125, -42}, {91, -42}, {91, -86}}, color = {0, 127, 255}));
  connect(pumpF.port_b, vol_pumpF_out.ports[1]) annotation(
    Line(points = {{112, -86}, {130, -86}}, color = {0, 127, 255}));
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
  connect(T_Treg_out.T, feedback2.u2) annotation(
    Line(points = {{123, -163.5}, {123, -178}}, color = {0, 0, 127}));
  connect(feedback2.u1, add.y) annotation(
    Line(points = {{118.2, -183}, {111.2, -183}, {111.2, -197}}, color = {0, 0, 127}));
  connect(Q_Treg.Q_flow, PID_Treg.y) annotation(
    Line(points = {{141, -142}, {158, -142}, {158, -183}, {151, -183}}, color = {0, 0, 127}));
  connect(vol_Treg.heatPort, Qout_Treg.port_a) annotation(
    Line(points = {{108, -142}, {113, -142}}, color = {191, 0, 0}));
  connect(Qout_Treg.port_b, Q_Treg.port) annotation(
    Line(points = {{121, -142}, {127, -142}}, color = {191, 0, 0}));
  connect(HF_pumpB.port, pump_pumpB.heatPort) annotation(
    Line(points = {{286, 98}, {304, 98}}, color = {191, 0, 0}));
  connect(tT_HF_pumpA.y, HF_pumpA.Q_flow) annotation(
    Line(points = {{93, 68}, {105, 68}}, color = {0, 0, 127}));
  connect(HF_pumpA.port, pump_pumpA.heatPort) annotation(
    Line(points = {{126, 68}, {142, 68}, {142, 72}}, color = {191, 0, 0}));
  connect(tT_pumpA.y, pump_pumpA.m_flow_set) annotation(
    Line(points = {{177, 66}, {155, 66}, {155, 64}}, color = {0, 0, 127}));
  connect(pump_pumpA.port_b, pipe_pump_cover.port_a) annotation(
    Line(points = {{148, 78}, {148, 107}, {130, 107}, {130, 106}}, color = {0, 127, 255}));
  connect(pipe_pump_cover.port_b, V_pump_cover.ports[1]) annotation(
    Line(points = {{110, 106}, {20.5, 106}, {20.5, 120}, {18.25, 120}, {18.25, 140}, {20, 140}}, color = {0, 127, 255}));
  connect(CV_tank_to_air.fluid, tank1.heatPort) annotation(
    Line(points = {{-8, 56}, {-8, 14}}, color = {191, 0, 0}));
  connect(CV_tank2toAir.y, CV_tank_to_air.Gc) annotation(
    Line(points = {{-29, 66}, {-18, 66}}, color = {0, 0, 127}));
  connect(CV_tank_to_air.solid, Tambient.port) annotation(
    Line(points = {{-8, 76}, {-8, 150}, {-216, 150}, {-216, -124}, {-104, -124}}, color = {191, 0, 0}));
  connect(tank2.ports[1], V_flow_pumpF_in.port_a) annotation(
    Line(points = {{146, -8}, {135, -8}, {135, -4}, {136, -4}, {136, -44}, {135, -44}}, color = {0, 127, 255}));
  connect(tank3.ports[1], pump_pumpB.port_a) annotation(
    Line(points = {{310, 4}, {310, 84}}, color = {0, 127, 255}));
  connect(pipe_pump_flood.port_b, V_pump_cover.ports[2]) annotation(
    Line(points = {{288, 130}, {288, 128}, {20, 128}, {20, 140}}, color = {0, 127, 255}));
  connect(pump_pumpA.port_a, tank2.ports[2]) annotation(
    Line(points = {{148, 58}, {148, 23}, {146, 23}, {146, -8}}, color = {0, 127, 255}));
  connect(V_pump_cover.ports[3], pipe_m_to_tank.port_b) annotation(
    Line(points = {{20, 140}, {10, 140}, {10, 108}, {-62, 108}}, color = {0, 127, 255}));
  connect(pipe_m_to_tank.port_a, tank1.ports[1]) annotation(
    Line(points = {{-82, 108}, {-98, 108}, {-98, -6}, {12, -6}}, color = {0, 127, 255}));
  connect(tank1.ports[2], path_1to2.port_a) annotation(
    Line(points = {{12, -6}, {12, -12}, {70, -12}}, color = {0, 127, 255}));
  connect(path_1to2.port_b, tank2.ports[3]) annotation(
    Line(points = {{90, -12}, {116, -12}, {116, -8}, {146, -8}}, color = {0, 127, 255}));
  connect(tank2.ports[4], path_1to21.port_a) annotation(
    Line(points = {{146, -8}, {167, -8}, {167, 2}, {204, 2}}, color = {0, 127, 255}));
  connect(path_1to21.port_b, tank3.ports[2]) annotation(
    Line(points = {{224, 2}, {255, 2}, {255, 4}, {310, 4}}, color = {0, 127, 255}));
  connect(T_pumpB_out.port, pipe_pump_flood.port_b) annotation(
    Line(points = {{268, 152}, {268, 130}, {288, 130}}, color = {0, 127, 255}));
  connect(CV_tank2toAir1.y, CV_tank_to_air1.Gc) annotation(
    Line(points = {{74, 34}, {119, 34}, {119, 36}, {204, 36}}, color = {0, 0, 127}));
  connect(CV_tank_to_air1.solid, Tambient.port) annotation(
    Line(points = {{214, 46}, {214, 168}, {-234, 168}, {-234, -124}, {-104, -124}}, color = {191, 0, 0}));
  connect(CV_tank_to_air1.fluid, tank2.heatPort) annotation(
    Line(points = {{214, 26}, {96, 26}, {96, 12}, {126, 12}}, color = {191, 0, 0}));
  connect(CV_const_tank1in1.y, CV_tank1in11.Gc) annotation(
    Line(points = {{29, -42}, {37.5, -42}, {37.5, -44}, {38, -44}}, color = {0, 0, 127}));
  connect(CV_tank1in11.fluid, tank2.heatPort) annotation(
    Line(points = {{48, -34}, {48, -36}, {126, -36}, {126, 12}}, color = {191, 0, 0}));
  connect(CV_tank1in11.solid, tC_ground_tank11.port_b) annotation(
    Line(points = {{48, -54}, {50, -54}, {50, -64}}, color = {191, 0, 0}));
  connect(tC_ground_tank11.port_a, convection_ground_tank11.fluid) annotation(
    Line(points = {{50, -84}, {50, -94}}, color = {191, 0, 0}));
  connect(CV_pumpB21.y, convection_ground_tank11.Gc) annotation(
    Line(points = {{30, -104}, {40, -104}}, color = {0, 0, 127}));
  connect(convection_ground_tank11.solid, Tambient.port) annotation(
    Line(points = {{50, -114}, {54, -114}, {54, -124}, {-104, -124}}, color = {191, 0, 0}));
  connect(CV_pumpB211.y, convection_ground_tank111.Gc) annotation(
    Line(points = {{223, -106}, {231, -106}, {231, -114}, {238, -114}}, color = {0, 0, 127}));
  connect(convection_ground_tank111.solid, Tambient.port) annotation(
    Line(points = {{248, -124}, {-104, -124}}, color = {191, 0, 0}));
  connect(tC_ground_tank111.port_a, convection_ground_tank111.fluid) annotation(
    Line(points = {{248, -90}, {248, -104}}, color = {191, 0, 0}));
  connect(CV_tank1in111.solid, tC_ground_tank111.port_b) annotation(
    Line(points = {{248, -60}, {248, -70}}, color = {191, 0, 0}));
  connect(CV_const_tank1in11.y, CV_tank1in111.Gc) annotation(
    Line(points = {{231, -50}, {237, -50}}, color = {0, 0, 127}));
  connect(CV_tank1in111.fluid, tank3.heatPort) annotation(
    Line(points = {{248, -40}, {248, -9}, {290, -9}, {290, 24}}, color = {191, 0, 0}));
  connect(CV_tank2toAir11.y, CV_tank_to_air11.Gc) annotation(
    Line(points = {{229, 34}, {234.5, 34}, {234.5, 32}, {240, 32}}, color = {0, 0, 127}));
  connect(CV_tank_to_air11.fluid, tank3.heatPort) annotation(
    Line(points = {{250, 22}, {250, 29}, {290, 29}, {290, 24}}, color = {191, 0, 0}));
  connect(CV_tank_to_air11.solid, Tambient.port) annotation(
    Line(points = {{250, 42}, {250, 188}, {-252, 188}, {-252, -142}, {-104, -142}, {-104, -124}}, color = {191, 0, 0}));
  connect(pipe_Treg_2_tank8_1.port_b, tank4.ports[1]) annotation(
    Line(points = {{100, -182}, {90, -182}, {90, -246}, {310, -246}, {310, -78}}, color = {0, 127, 255}));
  connect(tank3.ports[3], path_1to211.port_a) annotation(
    Line(points = {{310, 4}, {310, -4}, {308, -4}, {308, -12}}, color = {0, 127, 255}));
  connect(path_1to211.port_b, tank4.ports[2]) annotation(
    Line(points = {{308, -32}, {308, -55}, {310, -55}, {310, -78}}, color = {0, 127, 255}));
  connect(path_1to21.port_b, tank4.ports[3]) annotation(
    Line(points = {{224, 2}, {276, 2}, {276, -78}, {310, -78}}, color = {0, 127, 255}));
  annotation(
    uses(Modelica(version = "4.0.0")),
    Diagram(coordinateSystem(extent = {{-260, 200}, {380, -260}}), graphics = {Rectangle(origin = {125, -176}, fillColor = {85, 255, 255}, pattern = LinePattern.Dash, fillPattern = FillPattern.Solid, extent = {{-47, 54}, {47, -54}}), Text(origin = {126, -236}, extent = {{-44, 4}, {44, -4}}, textString = "Temperature regulator")}),
    version = "");
end ana001_Tank_004;
