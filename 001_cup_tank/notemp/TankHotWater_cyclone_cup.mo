model TankHotWater_cyclone_cup
  extends Modelica.Icons.Example;
  import pi = Modelica.Constants.pi;
  //ambient (= 地面温度 = 外気温 : eva5 センサ4-9)
  parameter Real Tamb = 273.15 + 24.5 "外気温/地面温度";
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
  //---- 温度管理(ON/OFF切替可能。既定 ctrl_k=0 = OFF = 温度管理なし) ----
  parameter Real Ttarget_deg = 24.5 "温度管理の目標水温 [degC] (=外気)";
  parameter Real Ttarget_K = Ttarget_deg + 273.15;
  parameter Real ctrl_k = 0 "温度管理ゲイン [W/K] : 0=OFF(管理なし), >0=ON(例3000で保持)";
  parameter Real ctrl_Ti = 1500 "積分時間 [s] : k=3000 で減衰比ζ≒1(行き過ぎ無)になる値。根拠 docs/control_tuning.md";
  replaceable package Medium = Modelica.Media.Water.StandardWater;
  Modelica.Fluid.Vessels.OpenTank tank(redeclare package Medium = Medium, T_start = Tamb, crossArea = crossArea_tank, height = tank_height, level_start = level_fill, nPorts = 0, use_HeatTransfer = true, use_portsData = false) annotation(
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
  Modelica.Thermal.HeatTransfer.Components.HeatCapacitor heatCapacitor1(C = cp*V_wall*rho, T(fixed = true, start = Tamb)) annotation(
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
  Real y_exp_T "タンク水温(実験) [degC]";
  Real y_cool "冷却(除熱)量 [W] (>0=冷却, ctrl_k=0なら常に0)";
  Modelica.Thermal.HeatTransfer.Sources.FixedHeatFlow fixedHeatFlow(Q_flow = Q_cyclone) annotation(
    Placement(transformation(origin = {6, 54}, extent = {{-10, -10}, {10, 10}})));
  // 実験データ(eva5, 温度管理なし) 水温 4-16 [time_s, degC]
  Modelica.Blocks.Sources.CombiTimeTable combiTimeTable1(table = [0, 23.8; 5263, 27.8; 10526, 29.8; 15789, 31.2; 21053, 32.4; 26316, 33.4; 31579, 34.3; 36842, 35.0; 42105, 35.5; 47368, 36.0; 52632, 36.4; 57895, 36.7; 63158, 37.0; 68421, 37.2; 73684, 37.35; 78947, 37.40; 84211, 37.50; 89474, 37.60; 94737, 37.65; 100000, 37.70], extrapolation = Modelica.Blocks.Types.Extrapolation.HoldLastPoint) annotation(
    Placement(transformation(origin = {40, 90}, extent = {{-10, -10}, {10, 10}})));
  //---- 温度管理レギュレータ (ctrl_k=0 で無効=温度管理なし) ----
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
//---- レギュレータ結線 (ctrl_k>0 で冷却が働く) ----
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
【001_cup_tank】cup(桶)モデルの集中定数トポロジ(水＋鋼壁＋外気, 上面/側/底の放熱)を
タンク3槽(合計上面3.265m2, 高さ240mm, 板厚2.3mm, 鋼 rho7000/cp450)に1槽集中化して適用。
サイクロン投入熱 Q=610W。外気/地面 24.5℃(eva5 センサ4-9)。
放熱経路: 上面(h_top=10 自然対流) と 側壁(h=9) と 底面。
底面は地面に接触せず15mm程度浮いており、空気層の伝導が支配(h_bot=k_air/t≒1.7)で断熱的。
このため放熱は上面が最大・底面が最小になる。h_top を UA≒46 W/K に調整し、
有効水位 level_fill=75.5mm で立ち上がり時定数(5τ≒100000s)を eva5 水温(4-16..4-19)に合わせる。
温度管理は ctrl_k で ON/OFF: ctrl_k=0=OFF(管理なし), ctrl_k>0(例3000)=ON(目標=外気に保持)。
y_sim_T = tank.medium.T を eva5 と比較。
</p>
</html>"),
    uses(Modelica(version = "4.0.0")),
    experiment(StartTime = 0, StopTime = 100000, Tolerance = 1e-06, Interval = 200),
  Diagram(coordinateSystem(extent = {{-200, 200}, {120, -180}})),
  version = "");
end TankHotWater_cyclone_cup;
