model ana002_Tank3blocks_002_machineAreaTankMist_NoTemp
  extends Modelica.Icons.Example;
  import Modelica.Fluid.Vessels.BaseClasses.VesselPortsData;
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
  parameter Real heatCeffToAir = 10;
  parameter Real Tair_deg = 19.5;
  parameter Real Tair_K = Tair_deg + 273.15;
  //25;
  parameter Real T_ini = 18.5 + 273.15;
  //25 + 273.15;
  // 機械内
  parameter Real T_machine_in = 19.5;
  parameter Real Lx_machine = 2.0;
  parameter Real Ly_machine = 1.0;
  parameter Real machine_height = 1.5;
  // T3基準温度とプラス
  parameter Real Ttarget = 19.5;
  //
  parameter Real T3puls = 1.5;
  Modelica.Fluid.Machines.ControlledPump pump_flood(p_a_nominal = 1e5, p_b_nominal = 5e5, m_flow_nominal = 41/60, use_m_flow_set = true, redeclare package Medium = fluid1, use_HeatTransfer = true, T_start = T_ini) annotation(
    Placement(transformation(origin = {334, 52}, extent = {{10, -10}, {-10, 10}}, rotation = -90)));
  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow HF_flood annotation(
    Placement(transformation(origin = {302, 56}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Vessels.OpenTank tank1(height = tank_height, crossArea = Lx1_1*Ly1_1, level_start = level_start, T_start = T_ini, portsData= {VesselPortsData(diameter = diamDmyPipe, height = 0), VesselPortsData(diameter = diamDmyPipe, height = 0), VesselPortsData(diameter = diamDmyPipe, height = 0.12)}, redeclare package Medium = fluid1, use_T_start = true, use_HeatTransfer = true, nPorts = 3) annotation(
    Placement(transformation(origin = {12, 14}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Blocks.Sources.TimeTable tT_HF_flood(table = [0, 560; 36000, 560]) annotation(
    Placement(transformation(origin = {274, 56}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.TimeTable tT_pumpQ_flood(table = [0, 28/60; 36000, 28/60]) annotation(
    Placement(transformation(origin = {364, 48}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Fluid.Pipes.StaticPipe pipe_pump_flood(redeclare package Medium = fluid1, diameter = 0.1, length = 0.5) annotation(
    Placement(transformation(origin = {298, 130}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.TimeTable tT_HF_cover(table = [0, 610; 36000, 610]) annotation(
    Placement(transformation(origin = {120, 74}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow HF_cover annotation(
    Placement(transformation(origin = {154, 74}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Machines.ControlledPump pump_cover(redeclare package Medium = fluid1, m_flow_nominal = 41/60, p_a_nominal = 1e5, p_b_nominal = 5e5, use_HeatTransfer = true, use_m_flow_set = true, T_start = T_ini) annotation(
    Placement(transformation(origin = {186, 74}, extent = {{10, -10}, {-10, 10}}, rotation = -90)));
  Modelica.Blocks.Sources.TimeTable tT_pumpQ_flood1(table = [0, 57.05/60; 36000, 57.05/60]) annotation(
    Placement(transformation(origin = {228, 72}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Fluid.Pipes.StaticPipe pipe_pump_cover(redeclare package Medium = fluid1, diameter = 0.1, length = 0.5) annotation(
    Placement(transformation(origin = {118, 108}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.Convection CV_tank_to_air annotation(
    Placement(transformation(origin = {-8, 56}, extent = {{-10, -10}, {10, 10}}, rotation = -90)));
  Modelica.Blocks.Sources.Constant CV_tank2toAir(k = heatCeffToAir*(Lx1_1*Ly1_1)) annotation(
    Placement(transformation(origin = {30, 66}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Fluid.Vessels.OpenTank tank2(redeclare package Medium = fluid1, T_start = T_ini, crossArea = Lx2_1*Ly1_2, height = tank_height, level_start = level_start, nPorts = 3, portsData(each diameter = diamDmyPipe, each height = 0), use_HeatTransfer = true, use_T_start = true) annotation(
    Placement(transformation(origin = {140, 20}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Fluid.Vessels.OpenTank tank3(redeclare package Medium = fluid1, T_start = T_ini, crossArea = Lx3_1*Ly3_1, height = tank_height, level_start = level_start*0.9, nPorts = 6, portsData(each diameter = diamDmyPipe, each height = 0), use_HeatTransfer = true, use_T_start = true) annotation(
    Placement(transformation(origin = {246, 14}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Fluid.Fittings.SimpleGenericOrifice path_1to2(redeclare package Medium = fluid1, diameter = diamDmyPipe, zeta = zetaDmyPipe) annotation(
    Placement(transformation(origin = {74, -12}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Fittings.SimpleGenericOrifice path_1to21(redeclare package Medium = fluid1, diameter = diamDmyPipe, zeta = zetaDmyPipe) annotation(
    Placement(transformation(origin = {186, -18}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Sensors.Temperature T_flood_out(redeclare package Medium = fluid1) annotation(
    Placement(transformation(origin = {267, 156}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Blocks.Sources.TimeTable tT_HF_cyclone(table = [0, 610; 36000, 610]) annotation(
    Placement(transformation(origin = {-136, 62}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow HF_cyclone annotation(
    Placement(transformation(origin = {-100, 60}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Machines.ControlledPump pump_cyclone(redeclare package Medium = fluid1, T_start = T_ini, m_flow_nominal = 41/60, p_a_nominal = 1e5, p_b_nominal = 5e5, use_HeatTransfer = true, use_m_flow_set = true) annotation(
    Placement(transformation(origin = {-62, 62}, extent = {{10, -10}, {-10, 10}}, rotation = -90)));
  Modelica.Blocks.Sources.TimeTable tT_pumpQ_cyclone(table = [0, 110/60; 36000, 110/60]) annotation(
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
    Placement(transformation(origin = {192, -62}, extent = {{-10, -10}, {10, 10}})));
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
    Placement(transformation(origin = {148, 126}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.TimeTable tT_HF_HD1OP(table = [0, 110; 36000, 110]) annotation(
    Placement(transformation(origin = {298, -24}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow HF_HD1OP annotation(
    Placement(transformation(origin = {334, -26}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Machines.ControlledPump pump_HD1OP(redeclare package Medium = fluid1, T_start = T_ini, m_flow_nominal = 41/60, p_a_nominal = 1e5, p_b_nominal = 5e5, use_HeatTransfer = true, use_m_flow_set = true) annotation(
    Placement(transformation(origin = {368, -24}, extent = {{10, -10}, {-10, 10}}, rotation = -90)));
  Modelica.Blocks.Sources.TimeTable tT_pumpQ_HD1OP(table = [0, 13/60; 36000, 13/60]) annotation(
    Placement(transformation(origin = {408, -26}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Fluid.Pipes.StaticPipe pipe_pump_HD1OP(redeclare package Medium = fluid1, diameter = 0.1, length = 0.5) annotation(
    Placement(transformation(origin = {408, 62}, extent = {{10, -10}, {-10, 10}}, rotation = -90)));
  Modelica.Fluid.Sensors.Temperature T_machine_out(redeclare package Medium = fluid1) annotation(
    Placement(transformation(origin = {-117, 130}, extent = {{-5, -5}, {5, 5}})));
  Modelica.Thermal.HeatTransfer.Components.ThermalConductor tC_machibe(G = Lx_machine*Ly_machine*kground/tank_thickness) annotation(
    Placement(transformation(origin = {-44, 174}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.HeatCapacitor heatCapacitor(C = 4000) annotation(
    Placement(transformation(origin = {-124, 196}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.Convection CV_machine1 annotation(
    Placement(transformation(origin = {-148, 178}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant CV_const_tank1in1111(k = heatCeffToAir*Lx_machine*Ly_machine) annotation(
    Placement(transformation(origin = {-178, 196}, extent = {{-10, -10}, {10, 10}})));
  inner Modelica.Fluid.System system annotation(
    Placement(transformation(origin = {282, -162}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Vessels.OpenTank machine_liquid(redeclare package Medium = fluid1, T_start = T_ini, crossArea = Lx_machine*Ly_machine, height = machine_height, level_start = 0.01, nPorts = 5, portsData= {VesselPortsData(diameter = 0.1, height = 0), VesselPortsData(diameter = 0.1, height = 0), VesselPortsData(diameter = 0.1, height = 0), VesselPortsData(diameter = 0.1, height = 0), VesselPortsData(diameter = 0.1, height = 0)}, use_HeatTransfer = true, use_T_start = true) annotation(
    Placement(transformation(origin = {24, 194}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Fluid.Fittings.SimpleGenericOrifice path_machine_to_tank1(redeclare package Medium = fluid1, diameter = diamDmyPipe, zeta = zetaDmyPipe) annotation(
    Placement(transformation(origin = {-144, 104}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Celsius.PrescribedTemperature prescribedTemperature annotation(
    Placement(transformation(origin = {-20, -186}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.TimeTable timeTable(table = [0, Tair_deg - 0.5; 36000, Tair_deg + 2])  annotation(
    Placement(transformation(origin = {-94, -176}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Vessels.ClosedVolume machine_volume(redeclare package Medium = fluid1, nPorts = 2, V = 0.2, use_portsData = false, T_start = T_ini) annotation(
    Placement(transformation(origin = {-104, 160}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.TimeTable timeTable2(table = [0, Tair_deg - 0.5; 36000, Tair_deg + 2]) annotation(
    Placement(transformation(origin = {-78, -218}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Vessels.ClosedVolume machine_gas(redeclare package Medium = gas1, T_start = T_ini, V = Lx_machine*Ly_machine, nPorts = 2, use_portsData = false, use_HeatTransfer = true) annotation(
    Placement(transformation(origin = {14, 296}, extent = {{-10, 10}, {10, -10}}, rotation = -0)));
  Modelica.Thermal.HeatTransfer.Components.Convection conv annotation(
    Placement(transformation(origin = {4, 250}, extent = {{10, 10}, {-10, -10}}, rotation = -90)));
  Modelica.Blocks.Math.Product Gc_conv_machine_water2air annotation(
    Placement(transformation(origin = {-28, 250}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant hconv_const(k = heatCefftMachine2in*5) annotation(
    Placement(transformation(origin = {-70, 258}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant area_conv(k = Lx_machine*Ly_machine) annotation(
    Placement(transformation(origin = {-70, 226}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Fittings.SimpleGenericOrifice oriffice2(redeclare package Medium = gas1, diameter = diamDmyPipe, zeta = zetaDmyPipe) annotation(
    Placement(transformation(origin = {-34, 308}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Fittings.SimpleGenericOrifice path_mistOut(redeclare package Medium = fluid1, diameter = diamDmyPipe, zeta = zetaDmyPipe) annotation(
    Placement(transformation(origin = {92, 248}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Sources.MassFlowSource_T mistRemover_airSply(nPorts = 1, redeclare package Medium = gas1, use_m_flow_in = true, use_T_in = true, T = 291.15)  annotation(
    Placement(transformation(origin = {-76, 308}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.TimeTable tT_m_flow_mistRemoverAir(table = [0, 1; 2000, 1; 2010, 1; 10000, 1])  annotation(
    Placement(transformation(origin = {-192, 316}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Continuous.FirstOrder firstOrder_airSply(T = 0.1)  annotation(
    Placement(transformation(origin = {-152, 316}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Sources.Boundary_pT boundary_airOut(p = 1e5, nPorts = 1, redeclare package Medium = gas1)  annotation(
    Placement(transformation(origin = {94, 304}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Fluid.Sensors.MassFlowRate m_flow_gas_machiningChm_out(redeclare package Medium = gas1)  annotation(
    Placement(transformation(origin = {52, 306}, extent = {{-10, 10}, {10, -10}}, rotation = -0)));
  Modelica.Blocks.Math.Gain ratioMist(k = -0.001)  annotation(
    Placement(transformation(origin = {74, 276}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Fluid.Sources.MassFlowSource_T mistRemover_airSply1(redeclare package Medium = fluid1, nPorts = 1, use_T_in = false, use_m_flow_in = true) annotation(
    Placement(transformation(origin = {140, 248}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Thermal.HeatTransfer.Celsius.TemperatureSensor T_gas_machiningChm_in annotation(
    Placement(transformation(origin = {-22, 334}, extent = {{-10, 10}, {10, -10}}, rotation = 90)));
  Modelica.Blocks.Interaction.Show.RealValue realValue1 annotation(
    Placement(transformation(origin = {-6, 368}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Add add_K annotation(
    Placement(transformation(origin = {-126, 282}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant const_K(k = 273.15)  annotation(
    Placement(transformation(origin = {-168, 288}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.Convection CV_machine11 annotation(
    Placement(transformation(origin = {-140, 236}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant CV_const_tank1in11111(k = heatCeffToAir*Lx_machine*Ly_machine*10) annotation(
    Placement(transformation(origin = {-234, 256}, extent = {{-10, -10}, {10, 10}})));
equation
  connect(tT_HF_flood.y, HF_flood.Q_flow) annotation(
    Line(points = {{285, 56}, {292, 56}}, color = {0, 0, 127}));
  connect(tT_pumpQ_flood.y, pump_flood.m_flow_set) annotation(
    Line(points = {{353, 48}, {353, 47}, {342, 47}}, color = {0, 0, 127}));
  connect(pump_flood.port_b, pipe_pump_flood.port_a) annotation(
    Line(points = {{334, 62}, {334, 129}, {308, 129}, {308, 130}}, color = {0, 127, 255}));
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
  connect(CV_tank_to_air.fluid, tank1.heatPort) annotation(
    Line(points = {{-8, 46}, {-8, 14}}, color = {191, 0, 0}));
  connect(CV_tank2toAir.y, CV_tank_to_air.Gc) annotation(
    Line(points = {{19, 66}, {5, 66}, {5, 56}, {2, 56}}, color = {0, 0, 127}));
  connect(tank3.ports[2], pump_flood.port_a) annotation(
    Line(points = {{246, -6}, {246, 18}, {334, 18}, {334, 42}}, color = {0, 127, 255}));
  connect(tank1.ports[2], path_1to2.port_a) annotation(
    Line(points = {{12, -6}, {12, -12}, {64, -12}}, color = {0, 127, 255}));
  connect(path_1to2.port_b, tank2.ports[1]) annotation(
    Line(points = {{84, -12}, {140, -12}, {140, 0}}, color = {0, 127, 255}));
  connect(tank2.ports[2], path_1to21.port_a) annotation(
    Line(points = {{140, 0}, {138, 0}, {138, -10}, {178, -10}, {178, -18}, {176, -18}}, color = {0, 127, 255}));
  connect(path_1to21.port_b, tank3.ports[3]) annotation(
    Line(points = {{196, -18}, {244, -18}, {244, -6}, {246, -6}}, color = {0, 127, 255}));
  connect(T_flood_out.port, pipe_pump_flood.port_b) annotation(
    Line(points = {{268, 152}, {268, 130}, {288, 130}}, color = {0, 127, 255}));
  connect(tT_HF_cyclone.y, HF_cyclone.Q_flow) annotation(
    Line(points = {{-124, 62}, {-110, 62}, {-110, 60}}, color = {0, 0, 127}));
  connect(HF_cyclone.port, pump_cyclone.heatPort) annotation(
    Line(points = {{-90, 60}, {-68, 60}, {-68, 66}}, color = {191, 0, 0}));
  connect(tT_pumpQ_cyclone.y, pump_cyclone.m_flow_set) annotation(
    Line(points = {{-47, 58}, {-54, 58}}, color = {0, 0, 127}));
  connect(tank1.ports[1], pump_cyclone.port_a) annotation(
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
  connect(CV_pumpB212.y, convection_ground_tank122.Gc) annotation(
    Line(points = {{212, -114}, {220, -114}}, color = {0, 0, 127}));
  connect(CV_const_tank1in12.y, CV_tank1in112.Gc) annotation(
    Line(points = {{203, -62}, {211, -62}, {211, -48}, {216, -48}}, color = {0, 0, 127}));
  connect(tank3.heatPort, CV_tank1in112.fluid) annotation(
    Line(points = {{226, 14}, {226, -38}}, color = {191, 0, 0}));
  connect(CV_tank1in112.solid, tC_ground_tank122.port_b) annotation(
    Line(points = {{226, -58}, {230, -58}, {230, -72}}, color = {191, 0, 0}));
  connect(tC_ground_tank122.port_a, convection_ground_tank122.fluid) annotation(
    Line(points = {{230, -92}, {230, -104}}, color = {191, 0, 0}));
  connect(CV_tank_to_air1.fluid, tank2.heatPort) annotation(
    Line(points = {{88, 36}, {88, 20}, {120, 20}}, color = {191, 0, 0}));
  connect(CV_tank2toAir1.y, CV_tank_to_air1.Gc) annotation(
    Line(points = {{68, 48}, {78, 48}, {78, 46}}, color = {0, 0, 127}));
  connect(CV_tank2toAir11.y, CV_tank_to_air11.Gc) annotation(
    Line(points = {{192, 38}, {195, 38}, {195, 40}, {198, 40}}, color = {0, 0, 127}));
  connect(CV_tank_to_air11.fluid, tank3.heatPort) annotation(
    Line(points = {{208, 30}, {208, 14}, {226, 14}}, color = {191, 0, 0}));
  connect(pump_cyclone.port_b, pipe_pump_cover1.port_b) annotation(
    Line(points = {{-62, 72}, {-56, 72}, {-56, 126}, {138, 126}}, color = {0, 127, 255}));
  connect(pipe_pump_cover1.port_a, tank3.ports[5]) annotation(
    Line(points = {{158, 126}, {244, 126}, {244, -6}, {246, -6}}, color = {0, 127, 255}));
  connect(tT_HF_HD1OP.y, HF_HD1OP.Q_flow) annotation(
    Line(points = {{310, -24}, {324, -24}, {324, -26}}, color = {0, 0, 127}));
  connect(HF_HD1OP.port, pump_HD1OP.heatPort) annotation(
    Line(points = {{344, -26}, {362, -26}, {362, -20}}, color = {191, 0, 0}));
  connect(tT_pumpQ_HD1OP.y, pump_HD1OP.m_flow_set) annotation(
    Line(points = {{398, -26}, {376, -26}, {376, -28}}, color = {0, 0, 127}));
  connect(tank3.ports[6], pump_HD1OP.port_a) annotation(
    Line(points = {{246, -6}, {246, -48}, {368, -48}, {368, -34}}, color = {0, 127, 255}));
  connect(pump_HD1OP.port_b, pipe_pump_HD1OP.port_a) annotation(
    Line(points = {{368, -14}, {368, 28}, {408, 28}, {408, 52}}, color = {0, 127, 255}));
  connect(heatCapacitor.port, tC_machibe.port_b) annotation(
    Line(points = {{-124, 186}, {-122, 186}, {-122, 188}, {-34, 188}, {-34, 174}}, color = {191, 0, 0}));
  connect(CV_const_tank1in1111.y, CV_machine1.Gc) annotation(
    Line(points = {{-167, 196}, {-167, 188}, {-148, 188}}, color = {0, 0, 127}));
  connect(CV_machine1.fluid, tC_machibe.port_a) annotation(
    Line(points = {{-138, 178}, {-54, 178}, {-54, 174}}, color = {191, 0, 0}));
  connect(tC_machibe.port_b, machine_liquid.heatPort) annotation(
    Line(points = {{-34, 174}, {4, 174}, {4, 194}}, color = {191, 0, 0}));
  connect(pipe_pump_flood.port_b, machine_liquid.ports[2]) annotation(
    Line(points = {{288, 130}, {232, 130}, {232, 174}, {24, 174}}, color = {0, 127, 255}));
  connect(pipe_pump_cover.port_b, machine_liquid.ports[3]) annotation(
    Line(points = {{108, 108}, {36, 108}, {36, 174}, {24, 174}}, color = {0, 127, 255}));
  connect(pipe_pump_HD1OP.port_b, machine_liquid.ports[4]) annotation(
    Line(points = {{408, 72}, {408, 123}, {406, 123}, {406, 164}, {35.5, 164}, {35.5, 174}, {24, 174}}, color = {0, 127, 255}));
  connect(path_machine_to_tank1.port_a, tank1.ports[3]) annotation(
    Line(points = {{-154, 104}, {-178, 104}, {-178, -20}, {12, -20}, {12, -6}}, color = {0, 127, 255}));
  connect(T_machine_out.port, path_machine_to_tank1.port_b) annotation(
    Line(points = {{-116, 126}, {-114, 126}, {-114, 104}, {-134, 104}}, color = {0, 127, 255}));
  connect(prescribedTemperature.port, convection_ground_tank122.solid) annotation(
    Line(points = {{-10, -186}, {230, -186}, {230, -124}}, color = {191, 0, 0}));
  connect(timeTable.y, prescribedTemperature.T) annotation(
    Line(points = {{-82, -176}, {-32, -176}, {-32, -186}}, color = {0, 0, 127}));
  connect(convection_ground_tank12.solid, prescribedTemperature.port) annotation(
    Line(points = {{46, -120}, {46, -186}, {-10, -186}}, color = {191, 0, 0}));
  connect(convection_ground_tank121.solid, prescribedTemperature.port) annotation(
    Line(points = {{-22, -108}, {-10, -108}, {-10, -186}}, color = {191, 0, 0}));
  connect(CV_tank_to_air1.solid, prescribedTemperature.port) annotation(
    Line(points = {{88, 56}, {80, 56}, {80, 148}, {-200, 148}, {-200, -156}, {-10, -156}, {-10, -186}}, color = {191, 0, 0}));
  connect(CV_tank_to_air.solid, prescribedTemperature.port) annotation(
    Line(points = {{-8, 66}, {-8, 150}, {-212, 150}, {-212, -158}, {-10, -158}, {-10, -186}}, color = {191, 0, 0}));
  connect(CV_machine1.solid, prescribedTemperature.port) annotation(
    Line(points = {{-158, 178}, {-204, 178}, {-204, -136}, {-10, -136}, {-10, -186}}, color = {191, 0, 0}));
  connect(CV_tank_to_air11.solid, prescribedTemperature.port) annotation(
    Line(points = {{208, 50}, {204, 50}, {204, 150}, {-210, 150}, {-210, -156}, {-10, -156}, {-10, -186}}, color = {191, 0, 0}));
  connect(machine_volume.ports[2], path_machine_to_tank1.port_b) annotation(
    Line(points = {{-104, 150}, {-104, 104}, {-134, 104}}, color = {0, 127, 255}));
  connect(hconv_const.y, Gc_conv_machine_water2air.u1) annotation(
    Line(points = {{-59, 258}, {-51, 258}, {-51, 256}, {-41, 256}}, color = {0, 0, 127}));
  connect(area_conv.y, Gc_conv_machine_water2air.u2) annotation(
    Line(points = {{-59, 226}, {-41, 226}, {-41, 244}}, color = {0, 0, 127}));
  connect(Gc_conv_machine_water2air.y, conv.Gc) annotation(
    Line(points = {{-17, 250}, {-6, 250}}, color = {0, 0, 127}));
  connect(oriffice2.port_b, machine_gas.ports[1]) annotation(
    Line(points = {{-24, 308}, {14, 308}, {14, 306}}, color = {0, 127, 255}));
  connect(mistRemover_airSply.ports[1], oriffice2.port_a) annotation(
    Line(points = {{-66, 308}, {-44, 308}}, color = {0, 127, 255}));
  connect(firstOrder_airSply.y, mistRemover_airSply.m_flow_in) annotation(
    Line(points = {{-141, 316}, {-86, 316}}, color = {0, 0, 127}));
  connect(tT_m_flow_mistRemoverAir.y, firstOrder_airSply.u) annotation(
    Line(points = {{-180, 316}, {-164, 316}}, color = {0, 0, 127}));
  connect(m_flow_gas_machiningChm_out.port_b, boundary_airOut.ports[1]) annotation(
    Line(points = {{62, 306}, {84, 306}, {84, 304}}, color = {0, 127, 255}));
  connect(machine_gas.ports[2], m_flow_gas_machiningChm_out.port_a) annotation(
    Line(points = {{14, 306}, {42, 306}}, color = {0, 127, 255}));
  connect(m_flow_gas_machiningChm_out.m_flow, ratioMist.u) annotation(
    Line(points = {{52, 296}, {52, 276}, {62, 276}}, color = {0, 0, 127}));
  connect(path_mistOut.port_b, mistRemover_airSply1.ports[1]) annotation(
    Line(points = {{102, 248}, {130, 248}}, color = {0, 127, 255}));
  connect(ratioMist.y, mistRemover_airSply1.m_flow_in) annotation(
    Line(points = {{86, 276}, {150, 276}, {150, 256}}, color = {0, 0, 127}));
  connect(path_mistOut.port_a, machine_liquid.ports[5]) annotation(
    Line(points = {{82, 248}, {58, 248}, {58, 174}, {24, 174}}, color = {0, 127, 255}));
  connect(path_machine_to_tank1.port_b, machine_liquid.ports[1]) annotation(
    Line(points = {{-134, 104}, {24, 104}, {24, 174}}, color = {0, 127, 255}));
  connect(conv.solid, machine_liquid.heatPort) annotation(
    Line(points = {{4, 240}, {4, 194}}, color = {191, 0, 0}));
  connect(machine_gas.heatPort, conv.fluid) annotation(
    Line(points = {{4, 296}, {4, 260}}, color = {191, 0, 0}));
  connect(T_gas_machiningChm_in.port, machine_gas.heatPort) annotation(
    Line(points = {{-22, 324}, {4, 324}, {4, 296}}, color = {191, 0, 0}));
  connect(realValue1.numberPort, T_gas_machiningChm_in.T) annotation(
    Line(points = {{-17.5, 368}, {-22, 368}, {-22, 344}}, color = {0, 0, 127}));
  connect(const_K.y, add_K.u1) annotation(
    Line(points = {{-157, 288}, {-138, 288}}, color = {0, 0, 127}));
  connect(add_K.y, mistRemover_airSply.T_in) annotation(
    Line(points = {{-115, 282}, {-88, 282}, {-88, 312}}, color = {0, 0, 127}));
  connect(add_K.u2, timeTable.y) annotation(
    Line(points = {{-138, 276}, {-220, 276}, {-220, -162}, {-78, -162}, {-78, -176}, {-82, -176}}, color = {0, 0, 127}));
  connect(CV_const_tank1in11111.y, CV_machine11.Gc) annotation(
    Line(points = {{-222, 256}, {-140, 256}, {-140, 246}}, color = {0, 0, 127}));
  connect(CV_machine11.solid, prescribedTemperature.port) annotation(
    Line(points = {{-150, 236}, {-248, 236}, {-248, -154}, {-10, -154}, {-10, -186}}, color = {191, 0, 0}));
  connect(CV_machine11.fluid, machine_gas.heatPort) annotation(
    Line(points = {{-130, 236}, {-96, 236}, {-96, 296}, {4, 296}}, color = {191, 0, 0}));
  annotation(
    uses(Modelica(version = "4.0.0")),
    Diagram(coordinateSystem(extent = {{-260, 400}, {420, -240}}), graphics = {Text(origin = {65, 350}, extent = {{-67, 36}, {67, -36}}, textString = "mist remover排気中のmist/空気の質量比が一定であると仮定を置く。
（mist remover air供給の操作に連動して取り除くmistの流量が変化する。）"), Text(origin = {141, 216}, extent = {{-71, 10}, {71, -10}}, textString = "mist除去による水の質量と熱量の喪失する現象を、
液相の水をtankから排出する事で代表する。
(評価したいのはmist含有排気の挙動や状態ではなく、
循環する水の温度・熱量であるため。)"), Line(origin = {-71.9862, 326.58}, points = {{-20, 0}, {20, 0}}, arrow = {Arrow.None, Arrow.Filled}), Text(origin = {-74, 339}, extent = {{-18, 7}, {18, -7}}, textString = "給気"), Line(origin = {87.5402, 323.983}, points = {{-20, 0}, {20, 0}}, arrow = {Arrow.None, Arrow.Filled}), Text(origin = {92, 333}, extent = {{-18, 7}, {18, -7}}, textString = "排気")}),
    version = "");
end ana002_Tank3blocks_002_machineAreaTankMist_NoTemp;
