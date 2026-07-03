#!/usr/bin/env python3
"""施設データ v2: P14+P29 に OSM(Overpass) を補完マージ。
市町村判定は N03 行政区域ポリゴンの点内包(PIP)で正確に。
出力: out/facilities.geojson, out/summary.json （鉄道・バスはconvert.pyのまま）
"""
import json, os, re, math, unicodedata
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, 'out')
R5 = lambda x: round(x, 5)

# ---------- N03 境界 → PIP ----------
n03 = json.load(open(f'{BASE}/n03/N03-20240101_23.geojson'))
polys = []  # (city, bbox, rings)  rings=[ [ [lng,lat],... ] outer only + holes ]
for f in n03['features']:
    p = f['properties']
    shi = p.get('N03_004') or ''
    ku = p.get('N03_005') or ''
    city = shi + ku  # 政令市はN03_005に区名（名古屋市千種区）、他はN03_004のみ
    g = f['geometry']
    rings_list = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
    for rings in rings_list:
        xs = [c[0] for c in rings[0]]; ys = [c[1] for c in rings[0]]
        polys.append((city, (min(xs), min(ys), max(xs), max(ys)), rings))

def pip_ring(lng, lat, ring):
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if ((yi > lat) != (yj > lat)) and (lng < (xj - xi) * (lat - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside

def city_of(lng, lat):
    for city, bb, rings in polys:
        if not (bb[0] <= lng <= bb[2] and bb[1] <= lat <= bb[3]):
            continue
        if pip_ring(lng, lat, rings[0]):
            hole = any(pip_ring(lng, lat, h) for h in rings[1:])
            if not hole:
                return city
    return '不明'

def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・･]', '', s)

def dist_m(a, b):
    dx = (a[0]-b[0]) * 91000  # lng→m at 35N
    dy = (a[1]-b[1]) * 111000
    return math.hypot(dx, dy)

feats = []   # {'n','t','c','a','s',lng,lat}
def add(n, t, lng, lat, a, s):
    feats.append({'n': n, 't': t, 'lng': R5(lng), 'lat': R5(lat), 'a': a, 's': s})

# ---------- P14 保育所（公的・優先） ----------
p14 = json.load(open(f'{BASE}/p14/P14-21_23.geojson'))
for f in p14['features']:
    p = f['properties']; code = p.get('P14_006')
    if code == '0504': t = 'hoiku'
    elif code in ('0505', '0506'): t = 'other'
    else: continue
    lng, lat = f['geometry']['coordinates'][:2]
    add(p.get('P14_008') or '名称不明', t, lng, lat, (p.get('P14_002') or '') + (p.get('P14_004') or ''), 'mlit')

# ---------- P29 幼稚園・こども園（公的・優先） ----------
p29 = json.load(open(f'{BASE}/p29/P29-23_23_GML/P29-23_23.geojson'))
for f in p29['features']:
    p = f['properties']; code = p.get('P29_003')
    if code == '16011': t = 'youchien'
    elif code == '16013': t = 'kodomoen'
    else: continue
    lng, lat = f['geometry']['coordinates'][:2]
    add(p.get('P29_004') or '名称不明', t, lng, lat, p.get('P29_005') or '', 'mlit')

n_public = len(feats)

# ---------- OSM 補完 ----------
osm = json.load(open(f'{BASE}/osm_hoiku.json'))
osm_feats = []
for e in osm.get('elements', []):
    tags = e.get('tags', {})
    name = tags.get('name') or tags.get('name:ja')
    if not name: continue
    if e['type'] == 'node': lng, lat = e['lon'], e['lat']
    else:
        c = e.get('center');
        if not c: continue
        lng, lat = c['lon'], c['lat']
    nm = norm(name)
    if 'こども園' in nm or '子ども園' in nm or 'こどもえん' in nm: t = 'kodomoen'
    elif '幼稚園' in nm: t = 'youchien'
    elif re.search(r'保育|ナーサリー|nursery|キッズ|託児', nm, re.I): t = 'hoiku' if re.search(r'保育園|保育所', nm) else 'other'
    else: t = 'hoiku' if tags.get('amenity') == 'kindergarten' else 'other'
    addr = tags.get('addr:full') or ''
    osm_feats.append({'n': name, 't': t, 'lng': R5(lng), 'lat': R5(lat), 'a': addr, 's': 'osm'})

# 重複排除: 既存(公的)と 同名200m以内 or 任意60m以内 → skip。OSM内部も同様
added, skip_near, skip_name = 0, 0, 0
GRID = 0.01  # ~1km grid index
grid = defaultdict(list)
for f in feats:
    grid[(int(f['lng']/GRID), int(f['lat']/GRID))].append(f)
def neighbors(lng, lat):
    gx, gy = int(lng/GRID), int(lat/GRID)
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            yield from grid[(gx+dx, gy+dy)]
for f in osm_feats:
    dup = False
    for g in neighbors(f['lng'], f['lat']):
        d = dist_m((f['lng'],f['lat']), (g['lng'],g['lat']))
        if d < 60: dup = True; skip_near += 1; break
        if d < 250 and (norm(f['n']) == norm(g['n']) or norm(f['n']) in norm(g['n']) or norm(g['n']) in norm(f['n'])):
            dup = True; skip_name += 1; break
    if dup: continue
    feats.append(f); grid[(int(f['lng']/GRID), int(f['lat']/GRID))].append(f); added += 1

# ---------- 市町村割当（PIP）＋県外除外 ----------
final = []
for f in feats:
    c = city_of(f['lng'], f['lat'])
    if c == '不明': continue  # 県外(隣県OSM境界誤差)は除外
    f['c'] = c
    final.append(f)

out_feats = [{'type':'Feature','geometry':{'type':'Point','coordinates':[f['lng'],f['lat']]},
    'properties':{'n':f['n'],'t':f['t'],'c':f['c'],'a':f['a'],'s':f['s']}} for f in final]
json.dump({'type':'FeatureCollection','features':out_feats}, open(f'{OUT}/facilities.geojson','w'), ensure_ascii=False, separators=(',',':'))

summary = defaultdict(lambda: defaultdict(int))
for f in final:
    summary[f['c']][f['t']] += 1
json.dump(summary, open(f'{OUT}/summary.json','w'), ensure_ascii=False, separators=(',',':'))

print(f'公的データ: {n_public} / OSM候補: {len(osm_feats)} / OSM追加: {added} (近接重複skip {skip_near}・同名skip {skip_name})')
print(f'最終施設数: {len(final)} / 市区町村: {len(summary)}')
zero = [c for c,v in summary.items() if v.get('hoiku',0)==0]
print('保育園0の市区町村:', len(zero), zero[:10])
from collections import Counter
print('種別:', Counter(f['t'] for f in final))
