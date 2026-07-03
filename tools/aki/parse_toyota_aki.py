#!/usr/bin/env python3
"""豊田市 空き状況PDFをパースして aki_toyota.json を生成"""
import json, re, sys
import pdfplumber

PDF = sys.argv[1] if len(sys.argv) > 1 else 'toyota_aki_r0808.pdf'
items = {}
asof = target = None

def cell(s):
    s = (s or '').replace('\n', '').strip()
    return s

with pdfplumber.open(PDF) as pdf:
    for page in pdf.pages:
        text = page.extract_text() or ''
        m = re.search(r'令和(\d+)年(\d+)月(\d+)日時点', text)
        if m and not asof:
            asof = f'{2018+int(m.group(1))}-{int(m.group(2)):02d}-{int(m.group(3)):02d}'
        m = re.search(r'令和(\d+)年(\d+)月入園希望者用', text)
        if m and not target:
            target = f'{2018+int(m.group(1))}年{int(m.group(2))}月入園分'
        for table in page.extract_tables():
            for row in table:
                cells = [cell(c) for c in row]
                # 園名行の判定: どこかに定員（数字のみ）とかな名がある
                # レイアウト: [地区]? かな名 園名 ローマ字 定員 空き×4 申込×4
                # 地区列がある場合とない場合があるためローマ字列を探して基準にする
                roma_idx = None
                for i, c in enumerate(cells):
                    if re.fullmatch(r'[A-Z]{3,}', c.replace(' ', '')):
                        roma_idx = i
                        break
                if roma_idx is None or roma_idx < 2:
                    continue
                name = cells[roma_idx-1]
                if not name or name in ('園名',):
                    continue
                rest = cells[roma_idx+1:]
                # 定員
                cap = rest[0] if rest and re.fullmatch(r'\d+', rest[0]) else ''
                vals = rest[1:] if cap else rest
                # 空き4列＋申込4列を取り出す（結合セルで欠ける場合は残す）
                aki = vals[:4] + [''] * (4 - len(vals[:4]))
                app = vals[4:8] + [''] * (4 - len(vals[4:8]))
                items[name] = {'cap': cap, 'aki': aki, 'app': app}

print('asof:', asof, '| target:', target, '| 園数:', len(items))
out = {'city': '豊田市', 'asof': asof, 'target': target,
       'source': 'https://www.city.toyota.aichi.jp/kurashi/kosodateshien/azukari/hoiku/1016125/1016130.html',
       'legend': '×=空きなし / △=1〜4席 / ▲=1・2歳児に空き / 〇=5席以上 / 未実施=当該年齢の受入なし',
       'ages': ['0〜2歳', '3歳', '4歳', '5歳'],
       'items': items}
json.dump(out, open('aki_toyota.json', 'w'), ensure_ascii=False, indent=1)
# 検証サンプル
for k in ['朝日', '梅坪', '五ケ丘大和', '今', '中山', '杉本']:
    print(k, items.get(k))
