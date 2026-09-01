# -*- coding: utf-8 -*-
"""cup_data_mz.py の実験データ（画像読み取り値）を CSV へ書き出す。
  python write_cup_csv.py   -> cup_data_mz.csv
列: time_s, U4-1, U4-2, U4-3, U4-4, U1-2, U1-4  （温度[℃]）
"""
import os
import csv

time_s = [0, 500, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000]

data = {
    "U4-1": [27.5, 25.0, 29.5, 37.0, 41.5, 43.2, 43.5, 43.6, 44.1, 44.5, 44.5],
    "U4-2": [27.0, 24.5, 28.0, 34.5, 38.0, 39.2, 39.7, 39.6, 39.7, 39.8, 40.0],
    "U4-3": [26.5, 25.0, 25.2, 25.1, 25.0, 24.9, 25.0, 24.9, 25.0, 25.0, 24.9],
    "U4-4": [28.5, 25.2, 25.3, 25.5, 26.2, 26.3, 26.5, 25.7, 26.1, 26.3, 26.4],
    "U1-2": [27.0, 24.5, 28.5, 35.5, 38.5, 39.5, 40.0, 39.9, 40.0, 40.1, 40.2],
    "U1-4": [27.0, 24.8, 29.0, 36.0, 39.0, 40.2, 40.8, 40.7, 40.8, 40.8, 40.9],
}

cols = list(data.keys())
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cup_data_mz.csv")
with open(out, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["time_s"] + cols)
    for i, t in enumerate(time_s):
        w.writerow([t] + [data[c][i] for c in cols])
print("wrote:", out, "(%d rows x %d sensors)" % (len(time_s), len(cols)))
