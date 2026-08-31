# 002_tank_base — タンク水温 ベースモデルと合わせこみ

3槽（サイクロン加熱・循環）タンクの水温モデル `OM/ana003_Tank3blocks_cyclononly_NoTemp.mo`
（温度管理なし）と実験 `eva5.py` の照合・合わせこみ。

## 結果の要点
- ベースは飽和温度が実測より約1.6℃低い（RMSE 2.42℃）。
- 集中定数フィット（Q=610固定, `heatCeffToAir`10→8.79, `level_start`0.128→0.0755）で
  **RMSE 0.24℃** に一致。飽和温度は放熱 UA、立ち上がりは水位（熱容量）で合わせる。
- 詳細: [001_fit_and_distribution.md](001_fit_and_distribution.md)、
  数式・感度・全体計画: [parameter_study_plan.md](parameter_study_plan.md)。

## 実行手順

### A. 集中定数モデル（Python のみ・数秒）
```bash
cd 002_tank_base
python lumped_check.py     # 集中定数の一次確認（数値）
python make_figures.py     # 実測の場所差・ベース比較 → docs/img/
python fit_params.py       # 合わせこみ図（fit_air_level 等, 要 scipy） → docs/img/
```

### B. 実機 OpenModelica（1ケース）
```bash
cd 002_tank_base/OM
"C:\Program Files\OpenModelica1.26.3-64bit\bin\omc.exe" run_sim.mos   # -> *_res.csv
cd ..
python compare_OM_vs_exp.py    # 実測と重ねて RMSE 判定
```
（WSL は omc パスを `/mnt/c/...`、モデルは相対パスで `run_sim.mos` を OM 内で実行）

## ファイル
| ファイル | 役割 |
|---|---|
| `OM/ana003_Tank3blocks_cyclononly_NoTemp.mo` | 温度管理なしモデル |
| `OM/run_sim.mos` | OM 実行スクリプト |
| `eva1〜5.py` | 実験データ（eva5=本モデルの温度管理なし実測） |
| `fit_params.py` | 集中定数フィット・合わせこみ図 |
| `make_figures.py` | 実測分布・ベース比較図 |
| `lumped_check.py` | 集中定数の一次確認 |
| `compare_OM_vs_exp.py` | OM結果CSVと実測の比較 |
