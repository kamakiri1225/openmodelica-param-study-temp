import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ============================================================
# データ（画像から読み取った概算値、全20点）
# ============================================================

# 2026-07-08 10:00からの経過時間 [s]
time_s = [
    0, 1326, 2653, 3979, 5305,
    6632, 7958, 9284, 10611, 11937,
    13263, 14589, 15916, 17242, 18568,
    19895, 21221, 22547, 23874, 25200
]

# 温度 4-16 [°C]
temperature_4_16 = [
    23.73, 23.84, 23.86, 23.87, 24.21,
    24.10, 24.13, 24.19, 24.22, 24.26,
    24.28, 24.29, 24.32, 24.35, 24.38,
    24.37, 24.36, 24.40, 24.41, 24.44
]

# 温度 4-17 [°C]
temperature_4_17 = [
    24.02, 24.13, 24.06, 24.11, 24.18,
    24.15, 24.15, 24.20, 24.23, 24.26,
    24.29, 24.30, 24.33, 24.36, 24.39,
    24.38, 24.36, 24.40, 24.42, 24.45
]

# 温度 4-18 [°C]
temperature_4_18 = [
    24.00, 24.14, 24.05, 24.10, 24.15,
    24.16, 24.16, 24.21, 24.23, 24.26,
    24.29, 24.30, 24.34, 24.37, 24.40,
    24.38, 24.36, 24.41, 24.42, 24.44
]

# 温度 4-19 [°C]
temperature_4_19 = [
    23.42, 23.59, 23.69, 23.78, 24.05,
    24.15, 24.15, 24.19, 24.21, 24.25,
    24.27, 24.29, 24.31, 24.34, 24.37,
    24.36, 24.30, 24.34, 24.35, 24.36
]

# ============================================================
# 日時データの作成
# ============================================================

start_date = pd.Timestamp("2026-07-08 10:00:00")

dates = [
    start_date + pd.Timedelta(seconds=t)
    for t in time_s
]

# ============================================================
# DataFrameの作成
# ============================================================

df = pd.DataFrame({
    "Date": dates,
    "Time [s]": time_s,
    "4-16": temperature_4_16,
    "4-17": temperature_4_17,
    "4-18": temperature_4_18,
    "4-19": temperature_4_19
})

# ターミナルへデータを表示
print(df.to_string(index=False))

# CSVファイルへ保存
df.to_csv(
    "temperature_20points_without_NC_T7.csv",
    index=False,
    encoding="utf-8-sig"
)

# ============================================================
# グラフ作成
# ============================================================

fig, ax = plt.subplots(figsize=(11, 6))

ax.plot(
    df["Date"],
    df["4-16"],
    color="tab:blue",
    linestyle="-",
    marker="o",
    markersize=4,
    linewidth=1.5,
    label="4-16"
)

ax.plot(
    df["Date"],
    df["4-17"],
    color="tab:orange",
    linestyle="-",
    marker="o",
    markersize=4,
    linewidth=1.5,
    label="4-17"
)

ax.plot(
    df["Date"],
    df["4-18"],
    color="tab:green",
    linestyle="-",
    marker="o",
    markersize=4,
    linewidth=1.5,
    label="4-18"
)

ax.plot(
    df["Date"],
    df["4-19"],
    color="tab:red",
    linestyle="-",
    marker="o",
    markersize=4,
    linewidth=1.5,
    label="4-19"
)

# ============================================================
# 下側X軸：日時
# ============================================================

ax.set_xlabel("Date", fontsize=16)
ax.set_ylabel("Temperature [°C]", fontsize=16)

# 1時間ごとの日時目盛
date_ticks = pd.date_range(
    start=start_date,
    end=start_date + pd.Timedelta(seconds=25200),
    freq="1h"
)

ax.set_xticks(date_ticks)

ax.xaxis.set_major_formatter(
    mdates.DateFormatter("%m-%d %H:%M")
)

ax.tick_params(
    axis="x",
    labelrotation=45,
    labelsize=11
)

ax.tick_params(
    axis="y",
    labelsize=11
)

# X軸範囲
ax.set_xlim(
    start_date,
    start_date + pd.Timedelta(seconds=25200)
)

# Y軸範囲
ax.set_ylim(23.0, 25.0)

# Y軸の目盛間隔を0.25°Cに設定
ax.set_yticks([
    23.00, 23.25, 23.50, 23.75,
    24.00, 24.25, 24.50, 24.75, 25.00
])

# 主グリッド
ax.grid(
    True,
    which="major",
    linestyle="-",
    linewidth=0.7,
    color="gray",
    alpha=0.45
)

# 補助目盛と補助グリッド
ax.minorticks_on()

ax.grid(
    True,
    which="minor",
    linestyle="--",
    linewidth=0.5,
    color="gray",
    alpha=0.25
)

# ============================================================
# 上側X軸：経過時間 [s]
# ============================================================

ax_top = ax.twiny()
ax_top.set_xlim(ax.get_xlim())

# 5000秒ごとの目盛
top_time_ticks = [
    0, 5000, 10000, 15000, 20000, 25000
]

top_date_ticks = [
    start_date + pd.Timedelta(seconds=t)
    for t in top_time_ticks
]

ax_top.set_xticks(top_date_ticks)
ax_top.set_xticklabels([
    str(t) for t in top_time_ticks
])

ax_top.set_xlabel("Time [s]", fontsize=16)
ax_top.tick_params(axis="x", labelsize=11)

# ============================================================
# 凡例
# ============================================================

ax.legend(
    loc="center left",
    bbox_to_anchor=(1.02, 0.5),
    fontsize=11,
    frameon=True
)

# ============================================================
# 保存・表示
# ============================================================

plt.tight_layout()

plt.savefig(
    "temperature_20points_without_NC_T7.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()