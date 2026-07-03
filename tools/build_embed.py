#!/usr/bin/env python3
"""data/*.geojson から data/embedded.js を生成。
施設・集計・駅の3つを window.__FAC/__SUMMARY/__STATIONS に同梱し、
index.html を file:// でダブルクリックしても（fetch不要で）動くようにする。
バス・鉄道路線は容量が大きいためHTTP時のみ遅延fetch。
使い方: python3 tools/build_embed.py  （data/変換後に実行）
"""
import json, os
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
fac = json.load(open(f'{D}/facilities.geojson'))
summ = json.load(open(f'{D}/summary.json'))
sta = json.load(open(f'{D}/rail_stations.geojson'))
import glob
aki = {}
for fn in sorted(glob.glob(f'{D}/aki/*.json')):
    a = json.load(open(fn))
    aki[a['city']] = a
with open(f'{D}/embedded.js', 'w') as f:
    f.write('// 自動生成（tools/build_embed.py）: file://でも動くようcore dataを同梱\n')
    f.write('window.__FAC=' + json.dumps(fac, ensure_ascii=False, separators=(',', ':')) + ';\n')
    f.write('window.__SUMMARY=' + json.dumps(summ, ensure_ascii=False, separators=(',', ':')) + ';\n')
    f.write('window.__STATIONS=' + json.dumps(sta, ensure_ascii=False, separators=(',', ':')) + ';\n')
    f.write('window.__AKI=' + json.dumps(aki, ensure_ascii=False, separators=(',', ':')) + ';\n')
print('embedded.js', round(os.path.getsize(f'{D}/embedded.js') / 1e6, 2), 'MB')

# index.html の <script src="data/embedded.js?v=..."> をファイル内容ハッシュに更新（ブラウザキャッシュ対策）
import hashlib, re
h = hashlib.md5(open(f'{D}/embedded.js', 'rb').read()).hexdigest()[:8]
ip = os.path.join(os.path.dirname(D), 'index.html')
html = open(ip).read()
new_html = re.sub(r'data/embedded\.js\?v=[0-9a-z]+', f'data/embedded.js?v={h}', html)
if new_html != html:
    open(ip, 'w').write(new_html)
    print('index.html: embedded.js version →', h)
