# openmodelica-param-study-temp

OpenModelica の水槽水温モデル（3タンク・サイクロン加熱・循環）を、実験データに
合わせ込むためのパラメータスタディ一式。集中定数モデルによる解析的な照合・フィットと、
Windows の Python + OpenModelica(omc.exe) で回す自動パラメータスタディを収録。

詳細は **[docs/parameter_study_plan.md](docs/parameter_study_plan.md)** を参照。

## 主な結果

- モデル（`OM/ana003_Tank3blocks_cyclononly_NoTemp.mo`）と実験（`data/eva5.py`）を照合。
- ベースは飽和温度が −1.6℃ 低く、立ち上がりも遅い（RMSE 2.42℃）。
- 集中定数フィットで **RMSE 0.24℃** まで一致（`Q=610` 固定、`heatCeffToAir=8.79`,
  `level_start=0.0755`）。飽和温度は放熱 UA を約12%減、立ち上がりは実効水量を
  409→241 kg（水位 128→76 mm 相当）で合う。幾何寸法はレイアウト図と一致を確認済み。

![実機フィット](docs/img/001/fit_air_level.png)

## 構成

```
OM/    OpenModelica モデル(.mo)、実行スクリプト run_sim.mos
data/  実験データ eva*.py、比較 compare_OM_vs_exp.py、
       パラメータスタディ param_study.py / run_study.py
docs/  計画書 parameter_study_plan.md、図生成 make_figures.py / fit_params.py、img/
```

## 使い方（Windows）

```bat
:: 基準ケースを OM で回して実験と比較
cd OM
"C:\Program Files\OpenModelica1.26.3-64bit\bin\omc.exe" run_sim.mos
cd ..\data
python compare_OM_vs_exp.py

:: パラメータスタディ（LHS -> omc 実行 -> パレート）
python param_study.py gen --n 30
python run_study.py
python param_study.py pareto --csv results.csv
```

必要な Python パッケージ: `numpy pandas matplotlib scipy`（pairplot 用に任意で `seaborn`）。

## ドキュメントの図を再現する（集中定数モデル・Python のみ、OM 不要）

`docs/` の図はすべて Python スクリプトで再生成できる（数秒）。リポジトリ直下で:

```bash
python docs/lumped_check.py        # 集中定数の一次確認（数値のみ）
python docs/make_figures.py        # 001: 場所差 / ベース比較 / Q・level・h_air 影響
python docs/fit_params.py          # 001: 合わせこみ図（fit_air_only / fit_air_level 等, 要 scipy）
python docs/study_pareto_demo.py   # 002: vary_size / influence / objective_map / pairplot(*)
```

`study_pareto_demo.py` が出す図（`docs/img/002/`）:
- `pairplot.png` … 設計変数＋各熱流（発熱量／上面→大気／側底→地面）＋体積＋Tmax・5τ
- `pairplot_Lx.png` … タンク別 Lx を個別に振ったスタディ
- `influence.png` … 因子ごとの影響（Tmax・5τ × 各因子）
- `vary_size.png` … タンク寸法拡大（容量増）の効果
- `objective_map.png` … 目的空間 5τ–Tmax

> 画面表示なしで走らせる場合は `MPLBACKEND=Agg` を付ける（例:
> `MPLBACKEND=Agg python docs/study_pareto_demo.py`）。

## 実機 OpenModelica で回す

集中定数は代理。実際に omc.exe を回す手順は
**[docs/003_openmodelica_paramstudy_howto.md](docs/003_openmodelica_paramstudy_howto.md)** を参照
（WSL からの実行、`-override` での因子振り、実行時間の目安など）。
