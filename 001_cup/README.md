# 001_cup — 桶の水加熱 1DCAE（15W）

桶に水を **20mm** 入れ、底面を **15W** で加熱する OpenModelica モデルと実験の比較。
**測定を2回**（自宅・会社）行い、桶寸法と実測データが異なるため **`home/`（自宅）** と
**`company/`（会社）** に分けて整理している。共通点：水深20mm・15W加熱・Tamb=初期水温・
放熱2経路（上面 蒸発込み h_top=55／側壁・底面 h=10, SUS304桶壁経由）。

## フォルダ構成

| | `home/`（自宅・先に実施） | `company/`（会社・後に実施） |
|---|---|---|
| モデル | `CupHotWater_15W_home.mo` | `CupHotWater_15W_company.mo` |
| 桶内寸 | 160 × 90 mm, 壁 0.5 mm | 135 × 96 mm, 壁 0.2 mm |
| 外気温 Tamb | 27.6 ℃ | 25.0 ℃（参照センサ U4-3） |
| 実測データ | `data/water_heating_temperature_measurement.csv`（単一, 〜2100s） | `data/cup_data_mz.csv`（6センサ, 〜9000s） |
| 実行 | `run_home.mos` → `compare_home.py` | `run_company.mos` → `compare_company.py` |
| 比較図 | `CupHotWater_15W_home_compare.png` | `CupHotWater_15W_company_compare.png` |

## 自宅版（home）

単一センサの実測と OM 水温を比較。**RMSE 0.55℃** で一致。h_top（上面蒸発）の影響も検討
（`htop_compare.py` → `CupHotWater_15W_home_htop_compare.png`, 55=蒸発込み vs 10=対流のみ）。

![自宅版 OM vs 実験](home/CupHotWater_15W_home_compare.png)

## 会社版（company）

6センサ実測。**実測↔モデルの対応**を明示して比較：

- **U4-1 = 水温** ↔ OM `y_sim_T`（`cup.medium.T`）… **RMSE 0.87℃**
- **U4-2 = 桶壁** ↔ OM `y_wall_T`（`thermalConductor2.port_b.T`）… **RMSE 0.80℃**
- **U4-3 = 外気温**（≈25℃ = Tamb）

実測は OM の加熱開始に合わせ **−420s（7分）シフト**、初期水温は加熱開始時の 25℃ に合わせている。

![会社版 OM vs 実測](company/CupHotWater_15W_company_compare.png)

> 実測では **水 U4-1(44.5℃) が 壁 U4-2(40.0℃) より約4℃高い**。当初 `h_l=1000` では水↔壁が
> 密結合し両方≈40℃になったため、**水↔壁の熱抵抗**を実効値 `h_l=58` とし、上面放熱 `h_top=45`
> （蒸発の理論値~45と一致）、SUS壁↔外気 `h=9` と併せて調整。これで **水（U4-1）と壁（U4-2）を
> 同時に再現**する（水深20mm・発熱15W・外気25℃は固定条件）。

## 使い方

### WSL / Linux（bash）
```bash
# 自宅版（home/ 内で）
"/mnt/c/Program Files/OpenModelica1.26.3-64bit/bin/omc.exe" run_home.mos    # -> *_home_res.csv
python3 compare_home.py                                                     # -> *_home_compare.png

# 会社版（company/ 内で）
"/mnt/c/Program Files/OpenModelica1.26.3-64bit/bin/omc.exe" run_company.mos # -> *_company_res.csv
python3 compare_company.py                                                  # -> *_company_compare.png
```

### Windows（コマンドプロンプト / PowerShell）
`omc` に PATH が通っていない場合はフルパスで実行する。フォルダへ `cd` してから：
```bat
:: 自宅版（home フォルダで）
cd home
"C:\Program Files\OpenModelica1.26.3-64bit\bin\omc.exe" run_home.mos
python compare_home.py

:: 会社版（company フォルダで）
cd ..\company
"C:\Program Files\OpenModelica1.26.3-64bit\bin\omc.exe" run_company.mos
python compare_company.py
```
PowerShell では先頭に `&` を付ける：`& "C:\Program Files\OpenModelica1.26.3-64bit\bin\omc.exe" run_home.mos`
（`omc` に PATH が通っていれば単に `omc run_home.mos` でも可）。

実験データの取得元スクリプトは `company/data/cup_data_mz.py`（画像読み取り値）、
CSV 書き出しは `company/data/write_cup_csv.py`。詳細な経緯・熱伝達率の理論は `docs/README.md`。
