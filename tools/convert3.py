#!/usr/bin/env python3
"""施設データ v3: ここdeサーチ公式CSV（認可＋認可外）を正とし、
P29幼稚園（私学助成園の補完）＋市公式パッチをマージ。OSM依存を廃止。
座標付与は国土地理院ジオコーディングAPI（キャッシュ付き・失敗時Nominatim）。
出力: out/facilities.geojson, out/summary.json
"""
import csv, glob, json, math, os, re, time, unicodedata, urllib.request, urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, 'out')
CACHE = os.path.join(BASE, 'geocache_gsi.json')
R5 = lambda x: round(x, 5)

def norm(s):
    return re.sub(r'[\s　・･☆（）()]', '', unicodedata.normalize('NFKC', s or ''))

def dist_m(a, b):
    return math.hypot((a[0]-b[0])*91000, (a[1]-b[1])*111000)

AICHI_BBOX = (136.55, 34.50, 137.95, 35.50)
def in_aichi(lng, lat):
    return AICHI_BBOX[0] <= lng <= AICHI_BBOX[2] and AICHI_BBOX[1] <= lat <= AICHI_BBOX[3]

cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
def save_cache():
    json.dump(cache, open(CACHE, 'w'), ensure_ascii=False)

def gsi_geocode(addr):
    url = 'https://msearch.gsi.go.jp/address-search/AddressSearch?q=' + urllib.parse.quote(addr)
    req = urllib.request.Request(url, headers={'User-Agent': 'hoikuen-map-aichi/1.0'})
    with urllib.request.urlopen(req, timeout=15) as r:
        js = json.load(r)
    time.sleep(0.25)
    if js:
        lng, lat = js[0]['geometry']['coordinates']
        return [R5(lng), R5(lat)]
    return None

def geocode(addr):
    if addr in cache:
        return cache[addr]
    result = None
    # 全住所→建物名等を除いた住所→丁目/番地なし の順で試す
    tries = [addr, re.sub(r'\d[\d\-番地の丁目]*$', '', addr)]
    for q in tries:
        try:
            result = gsi_geocode(q)
        except Exception:
            time.sleep(1)
        if result and in_aichi(*result):
            break
        result = None
    cache[addr] = result
    if len(cache) % 50 == 0:
        save_cache()
    return result

feats = []
def add(n, t, coords, addr, city, src):
    feats.append({'n': n, 't': t, 'lng': coords[0], 'lat': coords[1], 'a': addr, 'c': city, 's': src})

# 市区町村名の正規化: N03の正式名リストと前方一致で照合する
# （「蒲郡市」の郡を郡名と誤認するようなregex破壊を避ける。郡付き「愛知郡東郷町」にも対応）
_n03 = json.load(open(f'{BASE}/n03/N03-20240101_23.geojson'))
CITY_NAMES = sorted(
    {(f['properties'].get('N03_004') or '') + (f['properties'].get('N03_005') or '') for f in _n03['features']},
    key=len, reverse=True)

def clean_city(c):
    c = (c or '').strip().replace('　', ' ')
    body = re.sub(r'^[^市区町村 ]{1,6}郡', '', c)  # 郡プレフィクス候補を外した形も試す
    for name in CITY_NAMES:
        if c.startswith(name) or body.startswith(name):
            return name
    return c

TYPE_MAP_NINKA = [
    (r'^保育所$', 'hoiku'),
    (r'^認定こども園', 'kodomoen'),
    (r'幼稚園$', 'youchien'),
    (r'^(小規模保育|家庭的保育|事業所内保育)', 'other'),
    (r'^居宅訪問型', None),  # 施設ではないため除外
]

skipped_geo, skipped_type = [], []

# ---------- 1. ここdeサーチ 認可 ----------
rows = list(csv.reader(open(f'{BASE}/kokode_csv/公表施設情報_認可_愛知県_20260703.csv', encoding='cp932')))
n_ninka = 0
for r in rows[1:]:
    if r[131] != '通常営業':
        continue
    t = 'MISS'
    for pat, ty in TYPE_MAP_NINKA:
        if re.search(pat, r[114]):
            t = ty
            break
    if t == 'MISS':
        skipped_type.append(r[114]); continue
    if t is None:
        continue
    name = r[116].strip() or r[2].strip()
    addr = (r[119] + r[120].strip().replace('　',' ') + r[121]).strip()
    coords = geocode(addr)
    if not coords:
        skipped_geo.append((name, addr)); continue
    add(name, t, coords, addr, clean_city(r[120]), 'kokode')
    n_ninka += 1
print('認可 追加:', n_ninka, flush=True)

# ---------- 2. ここdeサーチ 認可外 ----------
n_nk = 0
for fn in sorted(glob.glob(f'{BASE}/kokode_csv/公表施設情報_認可外_*.csv')):
    rows = list(csv.reader(open(fn, encoding='cp932')))
    for r in rows[1:]:
        if r[21] != '通常営業':
            continue
        if 'ベビーシッター' in r[17] or '居宅訪問' in r[17]:
            continue  # 通う施設ではないため除外
        name = r[1].strip()
        if not name:
            continue
        addr = (r[6] + r[7].strip().replace('　',' ') + r[8]).strip()
        coords = geocode(addr)
        if not coords:
            skipped_geo.append((name, addr)); continue
        add(name, 'other', coords, addr, clean_city(r[7]), 'kokode')
        n_nk += 1
print('認可外 追加:', n_nk, flush=True)
save_cache()

# ---------- 重複排除の準備（グリッド索引） ----------
from collections import defaultdict
GRID = 0.01
grid = defaultdict(list)
for f in feats:
    grid[(int(f['lng']/GRID), int(f['lat']/GRID))].append(f)
def is_dup(name, coords):
    gx, gy = int(coords[0]/GRID), int(coords[1]/GRID)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for g in grid[(gx+dx, gy+dy)]:
                d = dist_m(coords, (g['lng'], g['lat']))
                if d < 60:
                    return True
                nn, gn = norm(name), norm(g['n'])
                if d < 400 and (nn == gn or nn in gn or gn in nn):
                    return True
    return False
def register(f):
    grid[(int(f['lng']/GRID), int(f['lat']/GRID))].append(f)

# ---------- 3. P29幼稚園の補完（私学助成園など kokode未収載分） ----------
p29 = json.load(open(f'{BASE}/p29/P29-23_23_GML/P29-23_23.geojson'))
n_p29 = 0
for f in p29['features']:
    p = f['properties']
    if p.get('P29_003') != '16011':
        continue
    lng, lat = R5(f['geometry']['coordinates'][0]), R5(f['geometry']['coordinates'][1])
    if is_dup(p['P29_004'], (lng, lat)):
        continue
    ft = {'n': p['P29_004'], 't': 'youchien', 'lng': lng, 'lat': lat,
          'a': p.get('P29_005') or '', 'c': None, 's': 'mlit'}
    feats.append(ft); register(ft); n_p29 += 1
print('P29幼稚園 補完:', n_p29, flush=True)

# ---------- 4. 市公式パッチ ----------
n_patch = 0
patch_dir = f'{BASE}/../../..'  # placeholder, real path below
PATCH_DIR = '/Users/hiroka/Public/claude/副業/アプリ/hoikuen-map-aichi/tools/patches'
ncache = json.load(open(f'{PATCH_DIR}/_geocache.json')) if os.path.exists(f'{PATCH_DIR}/_geocache.json') else {}
for fn in sorted(glob.glob(f'{PATCH_DIR}/*.json')):
    if os.path.basename(fn).startswith('_'):
        continue
    patch = json.load(open(fn))
    for item in patch['facilities']:
        coords = ncache.get(item['a']) or geocode(item['a'])
        if not coords:
            skipped_geo.append((item['n'], item['a'])); continue
        coords = [R5(coords[0]), R5(coords[1])]
        if is_dup(item['n'], coords):
            continue
        ft = {'n': item['n'], 't': item['t'], 'lng': coords[0], 'lat': coords[1],
              'a': item['a'], 'c': patch['city'], 's': 'city'}
        feats.append(ft); register(ft); n_patch += 1
print('市公式パッチ 補完:', n_patch, flush=True)

# ---------- 5. 市区町村未設定分をN03 PIPで補完 ----------
n03 = json.load(open(f'{BASE}/n03/N03-20240101_23.geojson'))
polys = []
for f in n03['features']:
    p = f['properties']
    city = (p.get('N03_004') or '') + (p.get('N03_005') or '')
    g = f['geometry']
    for rings in ([g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']):
        xs = [c[0] for c in rings[0]]; ys = [c[1] for c in rings[0]]
        polys.append((city, (min(xs), min(ys), max(xs), max(ys)), rings))
def pip(lng, lat, ring):
    inside = False; j = len(ring)-1
    for i in range(len(ring)):
        xi, yi = ring[i][0], ring[i][1]; xj, yj = ring[j][0], ring[j][1]
        if ((yi > lat) != (yj > lat)) and (lng < (xj-xi)*(lat-yi)/(yj-yi+1e-12)+xi):
            inside = not inside
        j = i
    return inside
def city_of(lng, lat):
    for city, bb, rings in polys:
        if bb[0] <= lng <= bb[2] and bb[1] <= lat <= bb[3] and pip(lng, lat, rings[0]):
            if not any(pip(lng, lat, h) for h in rings[1:]):
                return city
    return None

VALID_CITIES = set()
for f in n03['features']:
    p = f['properties']
    VALID_CITIES.add((p.get('N03_004') or '') + (p.get('N03_005') or ''))

final = []
for f in feats:
    if not f['c'] or f['c'] not in VALID_CITIES:
        f['c'] = city_of(f['lng'], f['lat'])
    if not f['c']:
        continue
    final.append(f)

out_feats = [{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [f['lng'], f['lat']]},
              'properties': {'n': f['n'], 't': f['t'], 'c': f['c'], 'a': f['a'], 's': f['s']}} for f in final]
json.dump({'type': 'FeatureCollection', 'features': out_feats},
          open(f'{OUT}/facilities.geojson', 'w'), ensure_ascii=False, separators=(',', ':'))

summary = defaultdict(lambda: defaultdict(int))
for f in final:
    summary[f['c']][f['t']] += 1
json.dump(summary, open(f'{OUT}/summary.json', 'w'), ensure_ascii=False, separators=(',', ':'))

from collections import Counter
print('=== 完了 ===')
print('総施設数:', len(final), '市区町村:', len(summary))
print('種別:', Counter(f['t'] for f in final))
print('ジオコーディング失敗:', len(skipped_geo), skipped_geo[:8])
print('未知の施設類型:', set(skipped_type))
zero = [c for c, v in summary.items() if v.get('hoiku', 0) == 0 and not c.endswith('村')]
print('保育園0の市町(村除く):', zero)
print('長久手市:', dict(summary.get('長久手市', {})))
print('津島市:', dict(summary.get('津島市', {})))
print('刈谷市:', dict(summary.get('刈谷市', {})))
