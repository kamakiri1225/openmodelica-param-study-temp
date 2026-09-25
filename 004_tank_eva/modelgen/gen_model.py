# -*- coding: utf-8 -*-
"""
gen_model.py  —  YAML設定から OpenModelica のタンク水温モデル(.mo)を自動生成する。

使い方:
    python gen_model.py config/example_3tank.yaml
    → generated/<model_name>.mo と generated/run_<model_name>.mos を出力

生成モデルは自己完結（再利用部品 PumpHeat/GroundLoss/AirLoss/TempControl を
モデル内に同梱）。部品の定義は ../lib/*.mo を読み込んで埋め込む。
"""
import sys, os, yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LIBDIR = os.path.join(os.path.dirname(HERE), "lib")   # ana006/lib


def load_lib(name):
    """../lib/<name>.mo を読み、within除去＋2スペース字下げして埋め込み用に返す"""
    txt = open(os.path.join(LIBDIR, name + ".mo"), encoding="utf-8").read()
    txt = txt.replace("\r\n", "\n")
    # 先頭の within ; を除去
    i = txt.index("model ")
    body = txt[i:]
    # 2スペース字下げ
    return "\n".join(("  " + ln if ln.strip() else ln) for ln in body.split("\n"))


def gen(cfg):
    name = cfg["model_name"]
    Tamb = cfg.get("ambient_degC", 24.5)
    thick = cfg.get("tank_thickness_mm", 2.3) / 1000.0
    tanks = cfg["tanks"]
    # 熱伝達率などの既定値(一般値)。YAMLの defaults: で上書き、各タンクで個別上書きも可
    DEF = {"h_air": 10.0,          # 上面・外面→外気 自然対流 [W/m2K] (一般値。eva5合わせこみは8.79)
           "h_liquid_wall": 10.0,  # 液→内壁 [W/m2K] (eva5タンク準拠=10。※コップは58で別物。飽和温度に効くので要調整)
           "k_ground": 1.5,        # 底→地面 熱伝導率 [W/mK] (非律速なので値は結果にほぼ効かない=任意でOK)
           "height_mm": 240,       # タンク高さ [mm]
           "level_mm": 150}        # 水位 [mm]
    DEF.update(cfg.get("defaults", {}))
    def tv(t, key):               # タンク値: 個別 > defaults の順
        return t.get(key, DEF[key])
    # 接続: 各タンクの connect_to から構築(相互なので重複除去)。旧式 connections も併用可
    conns = []
    seen = set()
    def add_conn(a, b):
        key = tuple(sorted([a, b]))
        if a != b and key not in seen:
            seen.add(key); conns.append([a, b])
    for t in tanks:
        for other in (t.get("connect_to") or []):
            add_conn(t["id"], other)
    for a, b in cfg.get("connections", []):
        add_conn(a, b)
    pumps = cfg.get("pumps", [])
    tc = cfg.get("temperature_control", {"enabled": False})
    sim = cfg.get("sim", {})

    tid = [t["id"] for t in tanks]
    tmap = {t["id"]: t for t in tanks}

    # ---- ポート割り当て ----
    pc = {t: 0 for t in tid}
    def nextport(t):
        pc[t] += 1
        return pc[t]

    fluid_connects = []   # (portRef_a, portRef_b) を結ぶ(orifice経由 or 部品経由)
    comps = []            # コンポーネント宣言(テキスト, 位置)
    eqs = []              # connect文

    # タンク間接続(orifice)
    for k, (a, b) in enumerate(conns):
        ia, ib = nextport(a), nextport(b)
        oid = f"orifice_{a}_{b}"
        comps.append((f'  Modelica.Fluid.Fittings.SimpleGenericOrifice {oid}(redeclare package Medium = fluid1, diameter = 0.1, zeta = 0.1) annotation(\n'
                      f'    Placement(transformation(origin = {{{60+120*k}, -40}}, extent = {{{{-10, -10}}, {{10, 10}}}})));', None))
        eqs.append(f'  connect({a}.ports[{ia}], {oid}.port_a);')
        eqs.append(f'  connect({oid}.port_b, {b}.ports[{ib}]);')

    # ポンプ(PumpHeat)
    for j, p in enumerate(pumps):
        pid = p["id"]
        frm, to = p["from"], p["to"]
        iF, iT = nextport(frm), nextport(to)
        Q = p["heat_W"]; fL = p["flow_Lmin"]
        comps.append((f'  PumpHeat {pid}(redeclare package Medium = fluid1, Q = {Q}, m_flow = {fL}/60, T_start = T_ini) annotation(\n'
                      f'    Placement(transformation(origin = {{{-40}, {120+40*j}}}, extent = {{{{-15, -15}}, {{15, 15}}}})));', None))
        eqs.append(f'  connect({frm}.ports[{iF}], {pid}.port_a);')
        eqs.append(f'  connect({pid}.port_b, {to}.ports[{iT}]);')

    # 温度管理(TempControl)
    if tc.get("enabled", False):
        frm, to = tc["from"], tc["to"]
        iF, iT = nextport(frm), nextport(to)
        cap = float(tc.get("spec_kW", 3.5)) * 1000.0
        Ttg = tc.get("Ttarget_degC", 25)
        fL = tc.get("flow_Lmin", 25)
        comps.append((f'  TempControl tempCtrl(redeclare package Medium = fluid1, enabled = true, Ttarget = {Ttg}, '
                      f'cooling_capacity = {cap:.0f}, flow_Lmin = {fL}, T_start = T_ini) annotation(\n'
                      f'    Placement(transformation(origin = {{{120}, {200}}}, extent = {{{{-15, -15}}, {{15, 15}}}})));', None))
        eqs.append(f'  connect({frm}.ports[{iF}], tempCtrl.port_a);')
        eqs.append(f'  connect(tempCtrl.port_b, {to}.ports[{iT}]);')

    # ---- タンク本体＋放熱(GroundLoss/AirLoss) ----
    for i, t in enumerate(tanks):
        T = t["id"]; x = 120 * i
        Lx = t["Lx_mm"] / 1000.0; Ly = t["Ly_mm"] / 1000.0     # 幾何は必須
        H = tv(t, "height_mm") / 1000.0; lev = tv(t, "level_mm") / 1000.0   # level=level_start(初期水位)
        A_bot = Lx * Ly; A_side = 2 * (Lx + Ly) * lev; A_top = Lx * Ly
        ha = tv(t, "h_air"); hlw = tv(t, "h_liquid_wall"); kg = tv(t, "k_ground")
        n = pc[T]
        comps.append((f'  Modelica.Fluid.Vessels.OpenTank {T}(redeclare package Medium = fluid1, T_start = T_ini, '
                      f'crossArea = {A_bot:.5f}, height = {H:.4f}, level_start = {lev:.4f}, nPorts = {n}, '
                      f'portsData(each diameter = 0.1, each height = 0), use_HeatTransfer = true, use_T_start = true) annotation(\n'
                      f'    Placement(transformation(origin = {{{x}, 0}}, extent = {{{{-20, -20}}, {{20, 20}}}})));', None))
        # GroundLoss
        Gc_liq = hlw * (A_bot + A_side)
        G_wall = A_bot * kg / thick
        Gc_grd = ha * A_bot
        comps.append((f'  GroundLoss ground_{T}(Gc_liquid = {Gc_liq:.3f}, G_wall = {G_wall:.3f}, Gc_ground = {Gc_grd:.3f}) annotation(\n'
                      f'    Placement(transformation(origin = {{{x}, -120}}, extent = {{{{-15, -15}}, {{15, 15}}}})));', None))
        eqs.append(f'  connect({T}.heatPort, ground_{T}.port_water);')
        eqs.append(f'  connect(ground_{T}.port_ground, amb.port);')
        # AirLoss
        Gc_air = ha * A_top
        comps.append((f'  AirLoss air_{T}(Gc_air = {Gc_air:.3f}) annotation(\n'
                      f'    Placement(transformation(origin = {{{x}, 90}}, extent = {{{{-15, -15}}, {{15, 15}}}})));', None))
        eqs.append(f'  connect({T}.heatPort, air_{T}.port_water);')
        eqs.append(f'  connect(air_{T}.port_air, amb.port);')

    # 外気/地面境界 + system
    comps.append((f'  Modelica.Thermal.HeatTransfer.Celsius.FixedTemperature amb(T = {Tamb}) annotation(\n'
                  f'    Placement(transformation(origin = {{{-160}, -120}}, extent = {{{{-10, -10}}, {{10, 10}}}})));', None))
    comps.append(('  inner Modelica.Fluid.System system annotation(\n'
                  '    Placement(transformation(origin = {-160, 200}, extent = {{-10, -10}, {10, 10}})));', None))

    # ---- connect に線注釈を付与(OMEditで線を表示させる) ----
    import re as _re
    org = {}
    for c, _ in comps:
        m = _re.search(r'\s([A-Za-z_]\w*)\(.*?origin = \{\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\}', c, _re.S)
        if m:
            org[m.group(1)] = (m.group(2), m.group(3))
    def _cn(ref):
        return ref.split(".")[0].split("[")[0]
    def _is_heat(eq):
        return any(k in eq for k in ["heatPort", "port_water", "port_ground", "port_air"])
    ann_eqs = []
    for eq in eqs:
        m = _re.match(r'\s*connect\((.+?),\s*(.+?)\)\s*;', eq)
        if m:
            a, b = m.group(1), m.group(2)
            xa, ya = org.get(_cn(a), ("0", "0")); xb, yb = org.get(_cn(b), ("0", "0"))
            color = "{191, 0, 0}" if _is_heat(eq) else "{0, 127, 255}"
            ann_eqs.append(f'  connect({a}, {b}) annotation(Line(points = {{{{{xa}, {ya}}}, {{{xb}, {yb}}}}}, color = {color}));')
        else:
            ann_eqs.append(eq)
    eqs = ann_eqs

    # ---- 埋め込む部品クラス ----
    used = ["PumpHeat", "GroundLoss", "AirLoss"]
    if tc.get("enabled", False):
        used.append("TempControl")
    lib_txt = "\n".join(load_lib(nm) for nm in used)

    # ---- 組み立て ----
    header = (f"// ============================================================\n"
              f"//  {name}   (gen_model.py が YAML から自動生成)\n"
              f"//  タンク{len(tanks)}槽, ポンプ{len(pumps)}, 温度管理={'あり' if tc.get('enabled') else 'なし'}\n"
              f"//  部品(PumpHeat/GroundLoss/AirLoss/TempControl)はモデル内に同梱(自己完結)\n"
              f"// ============================================================\n")
    out = header
    out += f"model {name}\n"
    out += "  extends Modelica.Icons.Example;\n"
    out += f"  replaceable package fluid1 = Modelica.Media.Water.StandardWater;\n"
    out += f"  parameter Real T_ini = {Tamb} + 273.15 \"初期水温[K]\";\n"
    out += "  //--- 同梱部品 ---\n"
    out += lib_txt + "\n"
    out += "  //--- タンク・ポンプ・放熱・温度管理 ---\n"
    out += "\n".join(c for c, _ in comps) + "\n"
    out += "equation\n"
    out += "\n".join(eqs) + "\n"
    out += ("  annotation(\n"
            "    uses(Modelica(version = \"4.0.0\")),\n"
            "    Diagram(coordinateSystem(extent = {{-260, 300}, {380, -220}})),\n"
            f"    experiment(StartTime = 0, StopTime = {sim.get('stopTime',100000)}, "
            f"Interval = {sim.get('stopTime',100000)/sim.get('intervals',2000):.1f}));\n")
    out += f"end {name};\n"
    return out


def gen_mos(cfg):
    name = cfg["model_name"]; sim = cfg.get("sim", {})
    tvars = "|".join(f"{t['id']}.medium.T" for t in cfg["tanks"])
    return (f'// {name} 実行スクリプト (自己完結)\n'
            f'loadModel(Modelica); getErrorString();\n'
            f'loadFile("{name}.mo"); getErrorString();\n'
            f'simulate({name}, stopTime={sim.get("stopTime",100000)}, '
            f'numberOfIntervals={sim.get("intervals",2000)}, outputFormat="csv", '
            f'variableFilter="time|{tvars}"); getErrorString();\n')


def main():
    if len(sys.argv) < 2:
        print("usage: python gen_model.py <config.yaml>"); sys.exit(1)
    cfg = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
    outdir = os.path.join(HERE, "generated")
    os.makedirs(outdir, exist_ok=True)
    mo = gen(cfg); mos = gen_mos(cfg)
    name = cfg["model_name"]
    open(os.path.join(outdir, name + ".mo"), "w", encoding="utf-8", newline="\n").write(mo)
    open(os.path.join(outdir, f"run_{name}.mos"), "w", encoding="utf-8", newline="\n").write(mos)
    print(f"生成: generated/{name}.mo  ({len(mo.splitlines())} 行)")
    print(f"生成: generated/run_{name}.mos")


if __name__ == "__main__":
    main()
