import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator

# ============================================================
# データ（画像から読み取った概算値、全20点）
# NC:T7は除外
# ============================================================

# 2026-02-19 11:30からの経過時間 [s]
# 2-22の瞬間的な温度低下を表現するため、13500秒を含めています。
time_s = [
    0, 1000, 2000, 3000, 4000,
    5000, 6000, 7000, 8000, 9000,
    10000, 11000, 12000, 13000, 13500,
    14000, 15500, 17000, 18500, 20000
]

# ------------------------------------------------------------
# 2-1
# ------------------------------------------------------------
temperature_2_1 = [
    18.25, 19.48, 19.70, 19.88, 20.02,
    20.12, 20.22, 20.32, 20.42, 20.52,
    20.61, 20.69, 20.76, 20.83, 20.88,
    20.92, 20.95, 21.00, 21.05, 21.10
]

# ------------------------------------------------------------
# 2-9
# ------------------------------------------------------------
temperature_2_9 = [
    18.75, 19.25, 19.28, 19.38, 19.48,
    19.58, 19.70, 19.81, 19.90, 20.00,
    20.10, 20.20, 20.28, 20.34, 20.37,
    20.40, 20.46, 20.52, 20.56, 20.62
]

# ------------------------------------------------------------
# 2-3
# ------------------------------------------------------------
temperature_2_3 = [
    18.65, 19.42, 19.57, 19.67, 19.80,
    19.91, 20.03, 20.14, 20.24, 20.34,
    20.43, 20.52, 20.61, 20.68, 20.72,
    20.76, 20.82, 20.88, 20.91, 20.96
]

# ------------------------------------------------------------
# 2-17
# ------------------------------------------------------------
temperature_2_17 = [
    18.85, 19.43, 19.53, 19.64, 19.77,
    19.89, 20.01, 20.12, 20.23, 20.33,
    20.43, 20.53, 20.62, 20.69, 20.73,
    20.77, 20.85, 20.91, 20.95, 21.00
]

# ------------------------------------------------------------
# 2-22
# 13500秒付近の瞬間的な低下を含む
# ------------------------------------------------------------
temperature_2_22 = [
    18.75, 19.30, 19.22, 19.37, 19.49,
    19.61, 19.72, 19.83, 19.94, 20.06,
    20.18, 20.29, 20.40, 20.50, 18.00,
    20.98, 21.07, 21.14, 21.21, 21.27
]

# ------------------------------------------------------------
# 2-21
# 画像に見られる変動を概略的に再現
# ------------------------------------------------------------
temperature_2_21 = [
    19.48, 19.75, 19.72, 19.88, 20.05,
    19.98, 20.08, 20.02, 20.22, 20.15,
    20.25, 20.38, 20.33, 20.45, 20.38,
    20.50, 20.58, 20.56, 20.42, 20.30
]

# ============================================================
# データ数の確認
# ============================================================

series = {
    "2-1": temperature_2_1,
    "2-9": temperature_2_9,
    "2-3": temperature_2_3,
    "2-17": temperature_2_17,
    "2-22": temperature_2_22,
    "2-21": temperature_2_21
}

for name, values in series.items():
    if len(values) != len(time_s):
        raise ValueError(
            f"{name}のデータ数がtime_sと一致しません。"
            f"time_s={len(time_s)}, {name}={len(values)}"
        )

# ============================================================
# 日時データの作成
# ============================================================

start_date = pd.Timestamp("2026-02-19 11:30:00")

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
    "2-1": temperature_2_1,
    "2-9": temperature_2_9,
    "2-3": temperature_2_3,
    "2-17": temperature_2_17,
    "2-22": temperature_2_22,
    "2-21": temperature_2_21
})

# データをターミナルへ表示
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

fig, ax = plt.subplots(figsize=(11, 7))

# ------------------------------------------------------------
# 各温度系列を描画
# ------------------------------------------------------------

ax.plot(
    df["Date"],
    df["2-1"],
    color="tab:blue",
    linestyle="-",
    marker="o",
    markersize=3.5,
    linewidth=1.5,
    label="2-1"
)

ax.plot(
    df["Date"],
    df["2-9"],
    color="tab:orange",
    linestyle="-",
    marker="o",
    markersize=3.5,
    linewidth=1.5,
    label="2-9"
)

ax.plot(
    df["Date"],
    df["2-3"],
    color="tab:green",
    linestyle="-",
    marker="o",
    markersize=3.5,
    linewidth=1.5,
    label="2-3"
)

ax.plot(
    df["Date"],
    df["2-17"],
    color="tab:red",
    linestyle="-",
    marker="o",
    markersize=3.5,
    linewidth=1.5,
    label="2-17"
)

ax.plot(
    df["Date"],
    df["2-22"],
    color="tab:purple",
    linestyle="-",
    marker="o",
    markersize=3.5,
    linewidth=1.5,
    label="2-22"
)

ax.plot(
    df["Date"],
    df["2-21"],
    color="tab:brown",
    linestyle="-",
    marker="o",
    markersize=3.5,
    linewidth=1.5,
    label="2-21"
)

# ============================================================
# 下側X軸：日時
# ============================================================

ax.set_xlabel("Date", fontsize=16)
ax.set_ylabel("Temperature [°C]", fontsize=16)

# 1時間ごとの目盛
date_ticks = pd.date_range(
    start="2026-02-19 12:00:00",
    end="2026-02-19 17:00:00",
    freq="1h"
)

ax.set_xticks(date_ticks)

ax.xaxis.set_major_formatter(
    mdates.DateFormatter("%m-%d %H:%M")
)

# 10分ごとの補助目盛
ax.xaxis.set_minor_locator(
    mdates.MinuteLocator(interval=10)
)

ax.tick_params(
    axis="x",
    which="major",
    labelrotation=25,
    labelsize=11
)

ax.tick_params(
    axis="y",
    which="major",
    labelsize=11
)

# X軸範囲
end_date = start_date + pd.Timedelta(seconds=20000)

ax.set_xlim(
    start_date,
    end_date
)

# ============================================================
# Y軸
# ============================================================

ax.set_ylim(18.0, 22.0)

# 主目盛：0.5℃
ax.yaxis.set_major_locator(
    MultipleLocator(0.5)
)

# 補助目盛：0.1℃
ax.yaxis.set_minor_locator(
    MultipleLocator(0.1)
)

# ============================================================
# グリッド
# ============================================================

ax.grid(
    True,
    which="major",
    linestyle="-",
    linewidth=0.7,
    color="gray",
    alpha=0.45
)

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

top_time_ticks = [
    0, 2500, 5000, 7500, 10000,
    12500, 15000, 17500, 20000
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

ax_top.tick_params(
    axis="x",
    which="major",
    labelsize=11
)

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