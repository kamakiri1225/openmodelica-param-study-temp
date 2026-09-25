# -*- coding: utf-8 -*-
"""draw_model.py — Modelica(.mo)の配置注釈(Placement/connect Line)を解析して
モデルの接続図(概略)をPNGに描く。OMEdit無しでモデル構成を可視化する。
使い方: python draw_model.py <model.mo> <out.png> [タイトル]
"""
import sys, re, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch

for fp in ["/home/kamakiri/.fonts/NotoSansCJKjp-Regular.otf",
           r"C:\Windows\Fonts\meiryo.ttc"]:
    if os.path.exists(fp):
        fm.fontManager.addfont(fp); plt.rcParams["font.family"]=fm.FontProperties(fname=fp).get_name(); break
plt.rcParams["axes.unicode_minus"]=False

src_raw = open(sys.argv[1], encoding="utf-8", errors="ignore").read()
out = sys.argv[2]
title = sys.argv[3] if len(sys.argv) > 3 else os.path.basename(sys.argv[1])

# 改行正規化
src_raw = src_raw.replace("\r\n", "\n").replace("\r", "\n")
# 角括弧[...]内の ';'(TimeTableのtable行)を ',' に無害化して文抽出を安定化
src = re.sub(r'\[[^\]]*\]', lambda m: m.group(0).replace(';', ','), src_raw)
# 埋め込みローカルクラス(2スペースの model .. end ..;)を除去して本体だけ解析
src = re.sub(r'\n  model \w+.*?\n  end \w+;', '', src, flags=re.S)

# --- コンポーネント抽出: (修飾)型 or 大文字始まりのローカル型 名前 ... annotation(Placement(...)) ---
comp_re = re.compile(
    r'(?:^|\n)[ \t]*(?:inner\s+|outer\s+)?((?:[A-Za-z_]\w*\.)+[A-Za-z_]\w*|[A-Z]\w*)\s+([A-Za-z_]\w*)\b'
    r'.*?annotation\(\s*Placement\(transformation\('
    r'[^;]*?origin\s*=\s*\{\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\}'
    r'[^;]*?extent\s*=\s*\{\{\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\}\s*,\s*\{\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\}\}',
    re.S)
comps = {}
for m in comp_re.finditer(src):
    typ, name, ox, oy, e1, e2, e3, e4 = m.groups()
    ox, oy = float(ox), float(oy)
    w = abs(float(e3) - float(e1)); h = abs(float(e4) - float(e2))
    if w < 10: w = 18
    if h < 10: h = 18
    comps[name] = dict(typ=typ.split(".")[-1], x=ox, y=oy, w=w, h=h)

# --- connect抽出: points は {{..},{..}} を丸ごと取得(以前は最初の}で切れて線が消えていた) ---
conn_re = re.compile(
    r'connect\(\s*([\w\.]+(?:\[\d+\])?)\s*,\s*([\w\.]+(?:\[\d+\])?)\s*\)\s*annotation\('
    r'[^;]*?Line\(\s*points\s*=\s*(\{\{.*?\}\})'
    r'(?:[^;]*?color\s*=\s*\{\s*([-\d]+)\s*,\s*([-\d]+)\s*,\s*([-\d]+)\s*\})?',
    re.S)
conns = []
for m in conn_re.finditer(src):
    a, b, pts, r, g, bl = m.groups()
    P = [(float(x), float(y)) for x, y in re.findall(r'\{\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\}', pts)]
    color = (int(r)/255, int(g)/255, int(bl)/255) if r is not None else (0.4, 0.4, 0.4)
    conns.append((a.split(".")[0], b.split(".")[0], P, color))

# --- 描画 ---
xs = [c["x"] for c in comps.values()]; ys = [c["y"] for c in comps.values()]
if not xs:
    print("no components parsed"); sys.exit(1)
pad = 40
fig, ax = plt.subplots(figsize=(15, 11), dpi=110)
# 接続線(色: 青=流体, 赤=熱, 緑=信号)
for a, b, P, color in conns:
    if len(P) >= 2:
        xsl = [p[0] for p in P]; ysl = [p[1] for p in P]
        ax.plot(xsl, ysl, "-", color=color, lw=1.3, alpha=0.8, zorder=1)

# コンポーネント箱
def boxcolor(typ):
    t = typ.lower()
    if "tank" in t or "opentank" in t or "closedvolume" in t: return "#d6eaf8", "#2471a3"
    if "pump" in t: return "#fdebd0", "#ca6f1e"
    if "heatflow" in t or "prescribedheat" in t: return "#fadbd8", "#c0392b"
    if "convection" in t or "thermalconductor" in t: return "#fef9e7", "#b7950b"
    if "pid" in t or "feedback" in t or "sensor" in t or "timetable" in t or "constant" in t: return "#e8f8f5", "#148f77"
    return "#f2f3f4", "#566573"
for name, c in comps.items():
    fc, ec = boxcolor(c["typ"])
    ax.add_patch(FancyBboxPatch((c["x"]-c["w"]/2, c["y"]-c["h"]/2), c["w"], c["h"],
                                boxstyle="round,pad=1.5", fc=fc, ec=ec, lw=1.2, zorder=2))
    # ラベルは枠の下に置く(OMEdit流)。白背景で可読性を確保し、枠と重ならないようにする
    ax.text(c["x"], c["y"]-c["h"]/2-2.5, name, ha="center", va="top", fontsize=5.6, zorder=4,
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.7))

ax.set_xlim(min(xs)-pad, max(xs)+pad)
ax.set_ylim(min(ys)-pad-14, max(ys)+pad)   # 下側にラベル用の余白
ax.set_aspect("equal"); ax.axis("off")
ax.set_title(title, fontsize=14)
# 凡例
from matplotlib.lines import Line2D
leg = [Line2D([0],[0],color=(0,127/255,1),lw=2,label="流体配管"),
       Line2D([0],[0],color=(191/255,0,0),lw=2,label="熱ポート"),
       Line2D([0],[0],color=(0,0,127/255),lw=2,label="信号")]
ax.legend(handles=leg, loc="upper right", fontsize=9)
fig.tight_layout(); fig.savefig(out)
print(f"components={len(comps)} connections={len(conns)} -> {out}")
