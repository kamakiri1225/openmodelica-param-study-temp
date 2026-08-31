# cup — 桶の水加熱 1DCAE（15W）

桶（内寸 底面 **160×90mm**, 高さ30mm）に水を **20mm** 入れ、底面を **15W** で加熱する
OpenModelica モデルと、実験データとの比較。

## ファイル
- `CupHotWater_15W_001.mo` … モデル（SUS304桶＋水、上面蒸発＋側/底放熱）
- `water_heating_temperature_measurement.csv` … 実験データ（time_s, 桶水温[℃]）
- `run_cup.mos` … OM 実行スクリプト
- `plot_cup_compare.py` … OM 結果と実験の比較図を作る
- `CupHotWater_15W_compare.png` … 比較図（RMSE 0.55℃）

## 使い方
```bash
# 1) OM で実行（このフォルダで）
"C:\Program Files\OpenModelica1.26.3-64bit\bin\omc.exe" run_cup.mos   # Windows
#  WSL:  "/mnt/c/Program Files/OpenModelica1.26.3-64bit/bin/omc.exe" run_cup.mos
# 2) 比較図
python plot_cup_compare.py
```

## 修正した点（元モデルのバグ）
1. `combiTimeTable1` が式で参照されているのに未宣言 → 実験データ表を追加
2. 桶 `level_start = 0`（水なし）→ `level_fill`（20mm）に修正
3. 寸法 190×100mm → 実機の **160×90mm** に修正
4. `nPorts=0` と `portsData` の不整合 → `use_portsData=false`

修正後、OM と実験は **RMSE 0.55℃** でよく一致する。
