# 空き状況データの更新手順

市町村ごとに公開形式が違うため、**1市=1取込スクリプト**の構成。
出力は `data/aki/<市>.json`（形式は下記共通スキーマ）→ `build_embed.py` で同梱。

## 共通スキーマ（data/aki/*.json）

```json
{
  "city": "豊田市",
  "asof": "2026-06-12",          ← 市の公表時点（必ず市資料の記載を転記）
  "target": "2026年8月入園分",
  "source": "市の掲載ページURL",
  "legend": "記号の凡例",
  "ages": ["0〜2歳","3歳","4歳","5歳"],
  "items": { "園名": {"cap":"定員", "aki":["×","〇","△","〇"], "app":["26人","0人","0人","0人"]} }
}
```

- 施設との名寄せはアプリ側（`akiNorm()`）: 【公】等・末尾の園種を除去、淨→浄・ヶ→ケ正規化
- **取込が止まった市は data/aki から外す**（古い空き情報を出し続けるのが最悪。ファイルが無ければUIは自動で非表示）

## 豊田市（毎月更新・PDF）

1. 掲載ページ: https://www.city.toyota.aichi.jp/kurashi/kosodateshien/azukari/hoiku/1016125/1016130.html
   PDFのURLパターン: `.../_page_/001/016/130/rYYMM.pdf`（YY=令和年、MM=入園希望月）
2. `bash tools/aki/fetch_toyota_aki.sh`（スクリプト内のURLを最新月に書き換え）
3. `<venv>/bin/python tools/aki/parse_toyota_aki.py <PDF>` → `aki_toyota.json`（要 pdfplumber）
4. 出力の `asof`・園数・サンプル数園をPDFと目視照合
5. `data/aki/toyota.json` に配置 → `python3 tools/build_embed.py`

Claude Codeへの依頼は「豊田市の空き状況を最新に更新して」でOK（この手順を実行する）。

## 次に追加する市の候補と形式メモ（2026-07-03調査）

| 市 | 形式 | 備考 |
|----|------|------|
| 名古屋市 | **Excelオープンデータ**・月2回更新 | 二次利用OK明記。パーサー作成が最も楽なはず |
| 一宮市 | HTML表 | 「保育施設空き状況（通年入所）」ページ |
| 岡崎・豊橋ほか | PDF/HTML混在 | 市ごとに個別調査 |
