#!/usr/bin/env python3
"""tools/patches/*.json の手動補完データを facilities.geojson にマージする。
- 住所をNominatimでジオコーディング（1req/s・キャッシュ tools/patches/_geocache.json）
- 既存施設と同名または60m以内なら追加しない（重複防止）
- summary.json を再集計し、build_embed.py を呼んで embedded.js も更新
使い方: python3 tools/apply_patches.py
"""
import json, os, re, time, math, unicodedata, urllib.request, urllib.parse, subprocess

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
DATA = os.path.join(ROOT, 'data')
PATCH_DIR = os.path.join(TOOLS, 'patches')
CACHE_PATH = os.path.join(PATCH_DIR, '_geocache.json')

def norm(s):
    return re.sub(r'[\s　・･☆（）()]', '', unicodedata.normalize('NFKC', s or ''))

def dist_m(a, b):
    return math.hypot((a[0]-b[0])*91000, (a[1]-b[1])*111000)

cache = json.load(open(CACHE_PATH)) if os.path.exists(CACHE_PATH) else {}

def geocode(addr):
    """番地→町名→市名の順に段階的にNominatimへ問い合わせ"""
    if addr in cache:
        return cache[addr]
    # 試行クエリ: フル住所 → 番地を落とす → 丁目まで
    candidates = [addr,
                  re.sub(r'\d[\d\-番地の]*$', '', addr),
                  re.sub(r'[一二三四五六七八九十\d]+丁目.*$', '', addr)]
    result = None
    for q in candidates:
        q = q.strip()
        if not q:
            continue
        url = ('https://nominatim.openstreetmap.org/search?format=json&countrycodes=jp&limit=1&q='
               + urllib.parse.quote(q))
        req = urllib.request.Request(url, headers={'User-Agent': 'hoikuen-map-aichi/1.0 (data patch geocoder)'})
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                js = json.load(r)
            time.sleep(1.1)  # rate limit
            if js:
                result = [round(float(js[0]['lon']), 5), round(float(js[0]['lat']), 5)]
                break
        except Exception as e:
            print('  geocode error:', q, e)
            time.sleep(1.1)
    cache[addr] = result
    json.dump(cache, open(CACHE_PATH, 'w'), ensure_ascii=False, indent=1)
    return result

fac = json.load(open(f'{DATA}/facilities.geojson'))
existing = [(f['properties'], f['geometry']['coordinates']) for f in fac['features']]

added, skipped, failed = [], [], []
for fn in sorted(os.listdir(PATCH_DIR)):
    if not fn.endswith('.json') or fn.startswith('_'):
        continue
    patch = json.load(open(os.path.join(PATCH_DIR, fn)))
    city = patch['city']
    print(f'== {fn} ({city}) ==')
    for item in patch['facilities']:
        dup = next((p for p, c in existing if norm(p['n']) == norm(item['n'])), None)
        if dup:
            skipped.append(item['n']); continue
        coords = geocode(item['a'])
        if not coords:
            failed.append(item['n']); print('  ✗ geocode失敗:', item['n'], item['a']); continue
        near = next((p for p, c in existing if dist_m(coords, c) < 60), None)
        if near:
            skipped.append(item['n'] + f"（{near['n']}と近接）"); continue
        feat = {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': coords},
                'properties': {'n': item['n'], 't': item['t'], 'c': city, 'a': item['a'], 's': 'city'}}
        fac['features'].append(feat)
        existing.append((feat['properties'], coords))
        added.append(item['n']); print('  ✓', item['n'], coords)

json.dump(fac, open(f'{DATA}/facilities.geojson', 'w'), ensure_ascii=False, separators=(',', ':'))

# summary再集計
from collections import defaultdict
summary = defaultdict(lambda: defaultdict(int))
for f in fac['features']:
    p = f['properties']
    summary[p['c']][p['t']] += 1
json.dump(summary, open(f'{DATA}/summary.json', 'w'), ensure_ascii=False, separators=(',', ':'))

subprocess.run(['python3', os.path.join(TOOLS, 'build_embed.py')], check=True)
print(f'\n追加 {len(added)} / 重複skip {len(skipped)} / 失敗 {len(failed)}')
print('総施設数:', len(fac['features']))
