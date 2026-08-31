# OM — OpenModelica モデル一覧

タンク3槽（サイクロン加熱・循環）モデル。**温度管理の有無**でフォルダを分けた。

| フォルダ / ファイル | 温度管理 | モデルクラス名 | 説明 |
|---|---|---|---|
| `temp_off/ana003_Tank3blocks_cyclononly_NoTemp.mo` | **なし** | `ana003_Tank3blocks_cyclononly_NoTemp` | サイクロン加熱のみ。水温は自由に上昇し飽和（~36℃）。**本リポジトリの主対象**（合わせこみ・パラスタ） |
| `temp_on/ana003_Tank3blocks_cyclononly.mo` | **あり** | `ana001_Tank3blocks_004_test` | PID温度レギュレータ（目標25℃）で水温を保持。flood/cover/cyclone の複数熱源あり |
| `_archive/ana002_..._machineAreaTankMist_NoTemp.mo` | なし | `ana002_..._NoTemp` | 旧版（未使用・保管） |

`temp_off/run_sim.mos` … `temp_off` 内で `omc.exe run_sim.mos` すると NoTemp モデルの
結果CSVを出力する。

## あり／なし比較（実機OM ＋ 実測）
`docs/img/002/compare_models.png`（`docs/compare_models.py`）:
- 温度管理**なし**: OM(フィット後) 37.8℃ ≈ 実測 **eva5** 37.7℃
- 温度管理**あり**: OM(PID) 24.8℃ ≈ 実測 **eva4** 〜24℃

再現手順は `docs/003_openmodelica_paramstudy_howto.md` を参照。

> 注: `OM/*.csv` や各フォルダのビルド副産物（.exe/.o/.c/.bin …）は再実行で作り直せるため
> `.gitignore` で除外している。
