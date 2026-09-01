model TankHotWater_cyclone_cup_TempCtrl
  extends Modelica.Icons.Example;
  import pi = Modelica.Constants.pi;
  //ambient (= 地面温度 = 外気温)
  parameter Real Tamb = 273.15 + 24.5 "外気温/地面温度";
  //初期水温(eva4実測の初期値に合わせる。基準モデルの物理パラメータではなく実験のスタート状態)
  parameter Real T_ini_deg = 23.8 "初期水温 [degC] (eva4実測の初期)";
  parameter Real T_ini_K = T_ini_deg + 273.15;
  //---- タンク幾何 : 3槽を等価な単一矩形 Lx×Ly[m] に簡略化 ----
  parameter Real Lx = 1764/1000 "タンク等価幅";
  parameter Real Ly = 1829/1000 "タンク等価奥行";
  parameter Real A_top = Lx*Ly "液面(上面)面積 ≒ 3.23 m2";
  parameter Real A_bot = A_top "底面積";
  parameter Real peri = 2*(Lx + Ly) "周長 ≒ 7.19 m";
  parameter Real tank_height = 240/1000 "タンク高さ";
  parameter Real level_fill = 75.5/1000 "有効水位(立ち上がり時定数に合わせたフィット値)";
  parameter Real wall_t = 2.3/1000 "タンク板厚";
  parameter Real crossArea_tank = A_top "断面積";
  parameter Real A_side = peri*level_fill "濡れ側壁面積";
  parameter Real A_mid = peri*level_fill "壁伝導の代表面積";
  //---- 材料 (鋼) ----
  parameter Real rho = 7000 "タンク密度";
  parameter Real k_steel = 16 "熱伝導率(ステンレス相当)";
  parameter Real cp = 450 "比熱";
  parameter Real V_wall = (peri*tank_height + A_bot)*wall_t "タンク鋼材体積";
  //---- 熱伝達率 ----
  parameter Real h_side = 9 "側面-外気の熱伝達率(自然対流, cup と同じ物理値)";
  parameter Real h_top = 11.2 "上面-外気の実効熱伝達率(自然対流, UA≒46 W/K に調整)";
  parameter Real h_water_wall = 200 "水↔壁の固液熱伝達率(壁≒水)";
  //底面は地面に接触せず15mm程度浮いている→空気層の伝導が支配(断熱的)
  parameter Real t_airgap = 15/1000 "タンク底-地面の空気層厚";
  parameter Real k_air = 0.026 "空気の熱伝導率";
  parameter Real h_bottom = k_air/t_airgap "底面→地面の実効熱伝達率(空気層15mm伝導≒1.7)";
  //---- 発熱 (サイクロン投入熱) ----
  parameter Real Q_cyclone = 610 "サイクロン投入熱 [W]";
  //==== ここから下だけが「温度管理を付けた」追加分 ====
  parameter Real Ttarget_deg = 24.5 "温度管理の目標水温 [degC] (=外気)";
  parameter Real Ttarget_K = Ttarget_deg + 273.15;
  parameter Real ctrl_k = 3000 "温度管理ゲイン [W/K] (0=管理なし=基準モデルと同一)";
  parameter Real ctrl_Ti = 1500 "温度管理の積分時間 [s]";
  replaceable package Medium = Modelica.Media.Water.StandardWater;
  Modelica.Fluid.Vessels.OpenTank tank(redeclare package Medium = Medium, T_start = T_ini_K, crossArea = crossArea_tank, height = tank_height, level_start = level_fill, nPorts = 0, use_HeatTransfer = true, use_portsData = false) annotation(
    Placement(transformation(origin = {50, -30}, extent = {{-20, -20}, {20, 20}})));
  inner Modelica.Fluid.System system annotation(
    Placement(transformation(origin = {100, 176}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.Convection convection1 "上面→外気" annotation(
    Placement(transformation(origin = {-52, 30}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.Constant const(k = h_top*A_top) annotation(
    Placement(transformation(origin = {-54, 70}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.ThermalConductor thermalConductor1(G = 2*k_steel*A_mid/wall_t) annotation(
    Placement(transformation(origin = {-42, -82}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.Convection convection2 "側壁→外気" annotation(
    Placement(transformation(origin = {-142, -82}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.Constant const1(k = h_side*A_side) annotation(
    Placement(transformation(origin = {-142, -44}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Sources.FixedTemperature fixedTemperature2(T = Tamb) annotation(
    Placement(transformation(origin = {-186, -8}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.ThermalConductor thermalConductor2(G = 2*k_steel*A_mid/wall_t) annotation(
    Placement(transformation(origin = {-98, -82}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.HeatCapacitor heatCapacitor1(C = cp*V_wall*rho, T(fixed = true, start = T_ini_K)) annotation(
    Placement(transformation(origin = {-72, -48}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.Convection convection3 "底面→地面" annotation(
    Placement(transformation(origin = {-142, -126}, extent = {{10, 10}, {-10, -10}})));
  Modelica.Blocks.Sources.Constant const2(k = h_bottom*A_bot) annotation(
    Placement(transformation(origin = {-144, -164}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.Convection convection4 "水↔壁(固液)" annotation(
    Placement(transformation(origin = {-2, -84}, extent = {{-10, 10}, {10, -10}})));
  Modelica.Blocks.Sources.Constant const4(k = A_side*h_water_wall) annotation(
    Placement(transformation(origin = {-2, -120}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Real y_sim_T "タンク水温(シミュレーション) [degC] : 実測 4-16..4-19 に対応";
  Real y_exp_T "タンク水温(実験, eva4=温度管理あり) [degC]";
  Real y_cool "冷却(除熱)量 [W] (>0=冷却)";
  Modelica.Thermal.HeatTransfer.Sources.FixedHeatFlow fixedHeatFlow(Q_flow = Q_cyclone) annotation(
    Placement(transformation(origin = {6, 54}, extent = {{-10, -10}, {10, 10}})));
  // 実験データ(eva4, 温度管理あり) 水温 4-16 [time_s, degC]
  Modelica.Blocks.Sources.CombiTimeTable combiTimeTable1(table = [0, 23.73; 1326, 23.84; 2653, 23.86; 3979, 23.87; 5305, 24.21; 6632, 24.10; 7958, 24.13; 9284, 24.19; 10611, 24.22; 11937, 24.26; 13263, 24.28; 14589, 24.29; 15916, 24.32; 17242, 24.35; 18568, 24.38; 19895, 24.37; 21221, 24.36; 22547, 24.40; 23874, 24.41; 25200, 24.44], extrapolation = Modelica.Blocks.Types.Extrapolation.HoldLastPoint) annotation(
    Placement(transformation(origin = {40, 90}, extent = {{-10, -10}, {10, 10}})));
  //---- 温度管理レギュレータ (基準モデルに追加した分) ----
  Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor Treg_sensor annotation(
    Placement(transformation(origin = {120, 20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant Treg_target(k = Ttarget_K) annotation(
    Placement(transformation(origin = {180, 70}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Math.Feedback Treg_fb annotation(
    Placement(transformation(origin = {140, 70}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Continuous.PI Treg_pid(k = ctrl_k, T = ctrl_Ti, initType = Modelica.Blocks.Types.Init.InitialState) annotation(
    Placement(transformation(origin = {100, 70}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow Treg_Q annotation(
    Placement(transformation(origin = {66, 70}, extent = {{10, -10}, {-10, 10}})));
equation
//------ 実験との比較 (タンク水温 [degC]) ------
  y_sim_T = tank.medium.T - 273.15;
  y_exp_T = combiTimeTable1.y[1];
  y_cool = -Treg_Q.Q_flow;
//------
  connect(tank.heatPort, convection1.solid) annotation(
    Line(points = {{30, -30}, {0, -30}, {0, 30}, {-42, 30}}, color = {191, 0, 0}));
  connect(const.y, convection1.Gc) annotation(
    Line(points = {{-43, 70}, {-52, 70}, {-52, 40}}, color = {0, 0, 127}));
  connect(fixedTemperature2.port, convection1.fluid) annotation(
    Line(points = {{-176, -8}, {-119, -8}, {-119, 30}, {-62, 30}}, color = {191, 0, 0}));
  connect(heatCapacitor1.port, thermalConductor1.port_a) annotation(
    Line(points = {{-72, -58}, {-72, -82}, {-52, -82}}, color = {191, 0, 0}));
  connect(thermalConductor2.port_b, heatCapacitor1.port) annotation(
    Line(points = {{-88, -82}, {-72, -82}, {-72, -58}}, color = {191, 0, 0}));
  connect(thermalConductor2.port_a, convection2.solid) annotation(
    Line(points = {{-108, -82}, {-132, -82}}, color = {191, 0, 0}));
  connect(thermalConductor2.port_a, convection3.solid) annotation(
    Line(points = {{-108, -82}, {-122, -82}, {-122, -126}, {-132, -126}}, color = {191, 0, 0}));
  connect(convection4.solid, thermalConductor1.port_b) annotation(
    Line(points = {{-12, -84}, {-32, -84}, {-32, -82}}, color = {191, 0, 0}));
  connect(const2.y, convection3.Gc) annotation(
    Line(points = {{-133, -164}, {-142, -164}, {-142, -136}}, color = {0, 0, 127}));
  connect(convection3.fluid, fixedTemperature2.port) annotation(
    Line(points = {{-152, -126}, {-176, -126}, {-176, -8}}, color = {191, 0, 0}));
  connect(convection2.fluid, fixedTemperature2.port) annotation(
    Line(points = {{-152, -82}, {-176, -82}, {-176, -8}}, color = {191, 0, 0}));
  connect(convection4.fluid, tank.heatPort) annotation(
    Line(points = {{8, -84}, {28, -84}, {28, -30}, {30, -30}}, color = {191, 0, 0}));
  connect(const4.y, convection4.Gc) annotation(
    Line(points = {{-2, -108}, {-2, -94}}, color = {0, 0, 127}));
  connect(const1.y, convection2.Gc) annotation(
    Line(points = {{-131, -44}, {-142, -44}, {-142, -72}}, color = {0, 0, 127}));
  connect(fixedHeatFlow.port, tank.heatPort) annotation(
    Line(points = {{16, 54}, {16, 12}, {30, 12}, {30, -30}}, color = {191, 0, 0}));
//---- レギュレータ結線 : 水温を測り、目標との差をPIで冷却熱流に ----
  connect(Treg_sensor.port, tank.heatPort) annotation(
    Line(points = {{110, 20}, {30, 20}, {30, -30}}, color = {191, 0, 0}));
  connect(Treg_target.y, Treg_fb.u1) annotation(
    Line(points = {{169, 70}, {148, 70}}, color = {0, 0, 127}));
  connect(Treg_sensor.T, Treg_fb.u2) annotation(
    Line(points = {{131, 20}, {140, 20}, {140, 62}}, color = {0, 0, 127}));
  connect(Treg_fb.y, Treg_pid.u) annotation(
    Line(points = {{131, 70}, {112, 70}}, color = {0, 0, 127}));
  connect(Treg_pid.y, Treg_Q.Q_flow) annotation(
    Line(points = {{89, 70}, {76, 70}}, color = {0, 0, 127}));
  connect(Treg_Q.port, tank.heatPort) annotation(
    Line(points = {{56, 70}, {30, 70}, {30, -30}}, color = {191, 0, 0}));
  annotation(
    Documentation(info = "<html>
<p>
【001_cup_tank/tempctrl】温度管理あり版。基準モデル TankHotWater_cyclone_cup(温度管理なし)を
<b>一切変更せず</b>、水温センサ+目標(=外気24.5℃)+PI+冷却熱流(PrescribedHeatFlow)の
レギュレータ<b>だけを追加</b>したもの(フェアな比較)。
ctrl_k=0 で基準モデルと完全一致(37.7℃まで上昇), ctrl_k>0 で水温を目標に保持。
実測 eva4(温度管理あり, 水温≒24℃保持)と比較する。y_cool = 冷却(除熱)量[W]。
</p>
</html>"),
    uses(Modelica(version = "4.0.0")),
    experiment(StartTime = 0, StopTime = 25200, Tolerance = 1e-06, Interval = 50),
    Diagram(coordinateSystem(extent = {{-200, 200}, {200, -180}})),
    version = "");
end TankHotWater_cyclone_cup_TempCtrl;
