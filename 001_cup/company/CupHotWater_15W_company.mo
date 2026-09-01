model CupHotWater_15W_company
  extends Modelica.Icons.Example;
  import pi = Modelica.Constants.pi;
  //ambient
  parameter Real Tamb = 273.15 + 25.0 "外気温(会社実験: 参照センサU4-3≈25.0℃・初期水温)";
  //tub (桶) parameter : 底面 160×90 mm, 高さ 30 mm
  parameter Real W = 135/1000 "桶の幅(内寸)";
  parameter Real Dp = 96/1000 "桶の奥行き(内寸)";
  parameter Real L = 30/1000 "桶の高さ";
  parameter Real level_fill = 20/1000 "目標注湯水位";
  parameter Real cup_t = 0.2/1000 "桶側壁厚";
  parameter Real cup_t_bottom = 0.2/1000 "桶底厚";
  parameter Real crossArea_tub = W*Dp "桶断面積";
  parameter Real peri_in = 2*(W + Dp) "内周長";
  parameter Real peri_mid = 2*((W + cup_t) + (Dp + cup_t)) "壁中央周長";
  parameter Real peri_out = 2*((W + 2*cup_t) + (Dp + 2*cup_t)) "外周長";
  parameter Real V = ((W + 2*cup_t)*(Dp + 2*cup_t) - W*Dp)*L "桶側壁の材料体積";
  parameter Real Sin = peri_in*L "内側側壁面積";
  parameter Real Sout = peri_out*L "外側側壁面積";
  parameter Real A_top = W*Dp "液面(上面)面積";
  parameter Real A_bot_out = (W + 2*cup_t)*(Dp + 2*cup_t) "外底面積";
  parameter Real A_mid = peri_mid*L "壁中央での伝導面積";
  //cup materials (ステンレス SUS304)
  parameter Real rho = 7900 "SUS304 密度";
  parameter Real k = 16 "SUS304 熱伝導率";
  parameter Real cp = 500 "SUS304 比熱";
  parameter Real h = 9 "桶側面・底-外気(SUS壁↔外気)の熱伝達率";
  parameter Real h_top = 45 "液面(上面)の実効熱伝達率(蒸発含む, 理論~45と一致)";
  //liquid parameter
  parameter Real h_l = 58 "桶内固液熱伝達率(実効: 水↔壁の温度差4℃を再現; U4-1 vs U4-2)";
  //yakan (注湯源) parameter
  parameter Real R_y = 50/1000 "やかん半径";
  parameter Real L_y = 120/1000 "やかん高さ";
  parameter Real level_start = 100/1000 "やかん初期水位";
  replaceable package Medium = Modelica.Media.Water.StandardWater;
  Modelica.Fluid.Vessels.OpenTank cup(redeclare package Medium = Medium, T_start = Tamb, crossArea = crossArea_tub, height = L, level_start = level_fill, nPorts = 0, use_HeatTransfer = true, use_portsData = false) annotation(
    Placement(visible = true, transformation(origin = {50, -30}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
  inner Modelica.Fluid.System system annotation(
    Placement(visible = true, transformation(origin = {100, 176}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Thermal.HeatTransfer.Components.Convection convection1 annotation(
    Placement(visible = true, transformation(origin = {-52, 30}, extent = {{10, -10}, {-10, 10}}, rotation = 0)));
  Modelica.Blocks.Sources.Constant const(k = h_top*A_top) annotation(
    Placement(visible = true, transformation(origin = {-54, 70}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Thermal.HeatTransfer.Components.ThermalConductor thermalConductor1(G = 2*k*A_mid/cup_t) annotation(
    Placement(visible = true, transformation(origin = {-42, -82}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Thermal.HeatTransfer.Components.Convection convection2 annotation(
    Placement(visible = true, transformation(origin = {-142, -82}, extent = {{10, -10}, {-10, 10}}, rotation = 0)));
  Modelica.Blocks.Sources.Constant const1(k = h*Sout) annotation(
    Placement(transformation(origin = {-142, -44}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Sources.FixedTemperature fixedTemperature2(T = Tamb) annotation(
    Placement(visible = true, transformation(origin = {-186, -8}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Thermal.HeatTransfer.Components.ThermalConductor thermalConductor2(G = 2*k*A_mid/cup_t) annotation(
    Placement(visible = true, transformation(origin = {-98, -82}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Thermal.HeatTransfer.Components.HeatCapacitor heatCapacitor1(C = cp*V*rho, T(fixed = true, start = Tamb)) annotation(
    Placement(visible = true, transformation(origin = {-72, -48}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Thermal.HeatTransfer.Components.Convection convection3 annotation(
    Placement(visible = true, transformation(origin = {-142, -126}, extent = {{10, 10}, {-10, -10}}, rotation = 0)));
  Modelica.Blocks.Sources.Constant const2(k = h*A_bot_out) annotation(
    Placement(visible = true, transformation(origin = {-144, -164}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Thermal.HeatTransfer.Components.Convection convection4 annotation(
    Placement(visible = true, transformation(origin = {-2, -84}, extent = {{-10, 10}, {10, -10}}, rotation = 0)));
  Modelica.Blocks.Sources.Constant const4(k = Sin*h_l) annotation(
    Placement(visible = true, transformation(origin = {-2, -120}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Modelica.Blocks.Interfaces.RealOutput y_cup_fracLevel annotation(
    Placement(transformation(origin = {79, -18}, extent = {{-6, -6}, {6, 6}}), iconTransformation(origin = {118, -36}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealOutput y_cup_level annotation(
    Placement(transformation(origin = {71, -4}, extent = {{-6, -6}, {6, 6}}), iconTransformation(origin = {128, -26}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interaction.Show.RealValue disp_cup_level(significantDigits = 3) annotation(
    Placement(transformation(origin = {103, -4}, extent = {{-13, -10}, {13, 10}})));
  Modelica.Blocks.Interaction.Show.RealValue disp_cup_fracLevel(significantDigits = 3) annotation(
    Placement(transformation(origin = {109, -18}, extent = {{-13, -9}, {13, 9}})));
  Real y_sim_T "桶水温(シミュレーション) [degC] : 実測 U4-1 に対応";
  Real y_wall_T "桶壁温度(シミュレーション) [degC] : 実測 U4-2 に対応";
  Real y_exp_T "桶水温(実験) [degC]";
  Modelica.Thermal.HeatTransfer.Sources.FixedHeatFlow fixedHeatFlow(Q_flow = 15)  annotation(
    Placement(transformation(origin = {6, 54}, extent = {{-10, -10}, {10, 10}})));
  // 実験データ (time_s, 桶水温[degC]) : 会社実測 cup_data_mz.csv の U4-1(生時刻, 未シフト)
  Modelica.Blocks.Sources.CombiTimeTable combiTimeTable1(table = [0, 27.5; 500, 25.0; 1000, 29.5; 2000, 37.0; 3000, 41.5; 4000, 43.2; 5000, 43.5; 6000, 43.6; 7000, 44.1; 8000, 44.5; 9000, 44.5], extrapolation = Modelica.Blocks.Types.Extrapolation.HoldLastPoint) annotation(
    Placement(transformation(origin = {40, 90}, extent = {{-10, -10}, {10, 10}})));
equation
  y_cup_level = cup.level;
  y_cup_fracLevel = cup.level/cup.height;
//------ 実験との比較 (桶の水温 [degC]) ------
  y_sim_T = cup.medium.T - 273.15;
  y_wall_T = thermalConductor2.port_b.T - 273.15;
  y_exp_T = combiTimeTable1.y[1];
//------
  connect(cup.heatPort, convection1.solid) annotation(
    Line(points = {{30, -30}, {0, -30}, {0, 30}, {-42, 30}, {-42, 30}}, color = {191, 0, 0}));
  connect(const.y, convection1.Gc) annotation(
    Line(points = {{-43, 70}, {-51, 70}, {-51, 40}, {-53, 40}}, color = {0, 0, 127}));
  connect(fixedTemperature2.port, convection1.fluid) annotation(
    Line(points = {{-176, -8}, {-119, -8}, {-119, 30}, {-62, 30}}, color = {191, 0, 0}));
  connect(heatCapacitor1.port, thermalConductor1.port_a) annotation(
    Line(points = {{-72, -58}, {-72, -82}, {-52, -82}}, color = {191, 0, 0}));
  connect(thermalConductor2.port_b, heatCapacitor1.port) annotation(
    Line(points = {{-88, -82}, {-72, -82}, {-72, -58}, {-72, -58}}, color = {191, 0, 0}));
  connect(thermalConductor2.port_a, convection2.solid) annotation(
    Line(points = {{-108, -82}, {-132, -82}}, color = {191, 0, 0}));
  connect(thermalConductor2.port_a, convection3.solid) annotation(
    Line(points = {{-108, -82}, {-122, -82}, {-122, -126}, {-132, -126}}, color = {191, 0, 0}));
  connect(convection4.solid, thermalConductor1.port_b) annotation(
    Line(points = {{-12, -84}, {-32, -84}, {-32, -82}}, color = {191, 0, 0}));
  connect(const2.y, convection3.Gc) annotation(
    Line(points = {{-133, -164}, {-143, -164}, {-143, -136}, {-143, -136}}, color = {0, 0, 127}));
  connect(convection3.fluid, fixedTemperature2.port) annotation(
    Line(points = {{-152, -126}, {-176, -126}, {-176, -8}}, color = {191, 0, 0}));
  connect(convection2.fluid, fixedTemperature2.port) annotation(
    Line(points = {{-152, -82}, {-176, -82}, {-176, -8}}, color = {191, 0, 0}));
  connect(convection4.fluid, cup.heatPort) annotation(
    Line(points = {{8, -84}, {28, -84}, {28, -30}, {30, -30}}, color = {191, 0, 0}));
  connect(const4.y, convection4.Gc) annotation(
    Line(points = {{-2, -108}, {-2, -94}}, color = {0, 0, 127}));
  connect(const1.y, convection2.Gc) annotation(
    Line(points = {{-131, -44}, {-136, -44}, {-136, -42}, {-145, -42}, {-145, -70}, {-143, -70}, {-143, -72}}, color = {0, 0, 127}));
  connect(y_cup_level, disp_cup_level.numberPort) annotation(
    Line(points = {{71, -4}, {88, -4}}, color = {0, 0, 127}));
  connect(y_cup_fracLevel, disp_cup_fracLevel.numberPort) annotation(
    Line(points = {{79, -18}, {94, -18}}, color = {0, 0, 127}));
  connect(fixedHeatFlow.port, cup.heatPort) annotation(
    Line(points = {{16, 54}, {16, 12}, {30, 12}, {30, -30}}, color = {191, 0, 0}));
  annotation(
    Documentation(info = "<html>
<p>
【会社(本日)版】桶(内寸 底面135×96mm, 壁0.2mm, 高さ30mm)に水を20mm入れ、
底面を15Wで加熱する1DCAEモデル。外気温 25.0℃(参照センサU4-3)、初期水温=外気温。
放熱は 上面(蒸発込み h_top=45) と 側壁・底面(h=9=SUS壁↔外気, 桶壁SUS304経由) の2経路。
水↔壁は h_l=58 とし、実測の水(U4-1)が壁(U4-2)より約4℃高い温度差を再現する
(y_sim_T=cup.medium.T≈U4-1, y_wall_T=thermalConductor2.port_b.T≈U4-2)。
combiTimeTable1 に会社実測(cup_data_mz.csv の U4-1, 生時刻)を保持し、y_sim_T(シミュレーション)
と y_exp_T(実験) を比較する。外部比較 compare_company.py は U4-1 を -420s シフトして合わせ込む。
熱伝導率参考: http://japan-miyabi.com/thermal_light/data/03/conductivity.htm
</p>
</html>"),
    uses(Modelica(version = "4.0.0")),
    Diagram(coordinateSystem(extent = {{-300, -300}, {300, 300}}), graphics = {Text(origin = {125, -3}, extent = {{-5, 5}, {5, -5}}, textString = "[m]"), Text(origin = {135, -19}, extent = {{-9, 7}, {9, -7}}, textString = "[nond]")}),
    Icon(coordinateSystem(extent = {{-200, -200}, {200, 200}})),
    version = "",
    __OpenModelica_commandLineOptions = "",
    experiment(StartTime = 0, StopTime = 9000, Tolerance = 1e-06, Interval = 10));
end CupHotWater_15W_company;
