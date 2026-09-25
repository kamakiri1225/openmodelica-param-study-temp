import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ============================================================
# データ（全20点）
# ============================================================

time_s = [
    0, 5263, 10526, 15789, 21053,
    26316, 31579, 36842, 42105, 47368,
    52632, 57895, 63158, 68421, 73684,
    78947, 84211, 89474, 94737, 100000
]

temperature_4_16 = [
    23.8, 27.8, 29.8, 31.2, 32.4,
    33.4, 34.3, 35.0, 35.5, 36.0,
    36.4, 36.7, 37.0, 37.2, 37.35,
    37.40, 37.50, 37.60, 37.65, 37.70
]

temperature_4_17 = [
    24.0, 28.0, 30.1, 31.5, 32.7,
    33.7, 34.5, 35.2, 35.8, 36.2,
    36.6, 36.9, 37.15, 37.35, 37.50,
    37.55, 37.60, 37.70, 37.75, 37.80
]

temperature_4_18 = [
    24.2, 28.4, 30.5, 31.9, 33.0,
    34.0, 34.8, 35.5, 36.0, 36.4,
    36.8, 37.1, 37.35, 37.55, 37.70,
    37.65, 37.75, 37.80, 37.85, 37.90
]

temperature_4_19 = [
    23.7, 27.6, 29.6, 31.0, 32.2,
    33.2, 34.1, 34.8, 35.4, 35.8,
    36.2, 36.5, 36.8, 37.0, 37.15,
    37.20, 37.30, 37.40, 37.45, 37.50
]

# 外気温度4-9
# 提示されたグラフから読み取った概算値
temperature_4_9 = [
    24.0, 24.3, 24.4, 24.5, 24.6,
    24.5, 24.4, 24.5, 24.6, 24.5,
    24.3, 24.2, 24.2, 24.2, 24.2,
    24.5, 24.5, 24.5, 24.6, 24.6
]

# ============================================================
# 日時データの作成
# ============================================================

start_date = pd.Timestamp("2026-07-09 10:00:00")

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
    "4-19": temperature_4_19,
    "4-9": temperature_4_9
})

# データをターミナルに表示
print(df.to_string(index=False))

# CSVへ保存
df.to_csv(
    "temperature_20points.csv",
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

# 外気温度4-9
ax.plot(
    df["Date"],
    df["4-9"],
    color="gray",
    linestyle="--",
    marker="o",
    markersize=3,
    linewidth=1.5,
    label="4-9 (Ambient)"
)

# ============================================================
# 下側X軸：日時
# ============================================================

ax.set_xlabel("Date", fontsize=13)
ax.set_ylabel("Temperature [°C]", fontsize=13)

# 日時目盛を2点おきに表示
tick_indices = list(range(0, len(df), 2))

# 最終点が含まれていなければ追加
if tick_indices[-1] != len(df) - 1:
    tick_indices.append(len(df) - 1)

ax.set_xticks(df.loc[tick_indices, "Date"])

ax.xaxis.set_major_formatter(
    mdates.DateFormatter("%m-%d\n%H:%M")
)

ax.tick_params(
    axis="x",
    labelrotation=45,
    labelsize=9
)

# Y軸の表示範囲
ax.set_ylim(20, 40)

# 主グリッド
ax.grid(
    True,
    which="major",
    linestyle="-",
    linewidth=0.6,
    alpha=0.5
)

# 補助目盛と補助グリッド
ax.minorticks_on()

ax.grid(
    True,
    which="minor",
    linestyle=":",
    linewidth=0.4,
    alpha=0.3
)

# ============================================================
# 上側X軸：経過時間 [s]
# ============================================================

ax_top = ax.twiny()
ax_top.set_xlim(ax.get_xlim())

ax_top.set_xticks(df.loc[tick_indices, "Date"])

ax_top.set_xticklabels([
    f"{df.loc[i, 'Time [s]']:.0f}"
    for i in tick_indices
])

ax_top.set_xlabel("Time [s]", fontsize=13)

# ============================================================
# 凡例
# ============================================================

ax.legend(
    loc="center left",
    bbox_to_anchor=(1.02, 0.5)
)

# レイアウト調整
plt.tight_layout()

# 画像保存
plt.savefig(
    "temperature_20points.png",
    dpi=300,
    bbox_inches="tight"
)

# グラフ表示
plt.show()