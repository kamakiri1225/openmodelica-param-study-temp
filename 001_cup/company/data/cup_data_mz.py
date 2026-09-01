%matplotlib inline

import matplotlib.pyplot as plt

# 日本語フォント（Windows）
plt.rcParams&#91;"font.family"] = "Yu Gothic"
plt.rcParams&#91;"axes.unicode_minus"] = False

# 画像から読み取ったおおよその値
time = &#91;
    0, 500, 1000, 2000, 3000, 4000,
    5000, 6000, 7000, 8000, 9000
]

data = {
    "U4-1": &#91;
        27.5, 25.0, 29.5, 37.0, 41.5, 43.2,
        43.5, 43.6, 44.1, 44.5, 44.5
    ],
    "U4-2": &#91;
        27.0, 24.5, 28.0, 34.5, 38.0, 39.2,
        39.7, 39.6, 39.7, 39.8, 40.0
    ],
    "U4-3": &#91;
        26.5, 25.0, 25.2, 25.1, 25.0, 24.9,
        25.0, 24.9, 25.0, 25.0, 24.9
    ],
    "U4-4": &#91;
        28.5, 25.2, 25.3, 25.5, 26.2, 26.3,
        26.5, 25.7, 26.1, 26.3, 26.4
    ],
    "U1-2": &#91;
        27.0, 24.5, 28.5, 35.5, 38.5, 39.5,
        40.0, 39.9, 40.0, 40.1, 40.2
    ],
    "U1-4": &#91;
        27.0, 24.8, 29.0, 36.0, 39.0, 40.2,
        40.8, 40.7, 40.8, 40.8, 40.9
    ],
}

colors = {
    "U4-1": "#f36f21",
    "U4-2": "#00652e",
    "U4-3": "#00a6d6",
    "U4-4": "#a02b93",
    "U1-2": "#18566b",
    "U1-4": "#55a630",
}

# グラフ作成
fig, ax = plt.subplots(figsize=(8, 4.5))

for name, temperature in data.items():
    ax.plot(
        time,
        temperature,
        color=colors&#91;name],
        linewidth=1.5,
        marker="o",                 # ドット
        markersize=5,
        markerfacecolor=colors&#91;name],
        markeredgecolor=colors&#91;name],
        label=name
    )

# 軸の設定
ax.set_xlim(0, 10000)
ax.set_ylim(20, 50)
ax.set_xticks(&#91;0, 2000, 4000, 6000, 8000, 10000])
ax.set_yticks(&#91;20, 25, 30, 35, 40, 45, 50])

ax.set_xlabel("時間 &#91;sec]")
ax.set_ylabel("温度 &#91;℃]")

# グリッド
ax.grid(True, color="lightgray", linewidth=0.8)
ax.set_axisbelow(True)

# 凡例
ax.legend(
    loc="lower center",
    bbox_to_anchor=(0.5, 1.03),
    ncol=6,
    frameon=False
)

plt.tight_layout()
plt.show()