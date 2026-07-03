#!/usr/bin/env python3
"""国土数値情報 → アプリ用GeoJSON変換パイプライン（愛知県）
出力: out/ に facilities.geojson, rail_lines.geojson, rail_stations.geojson,
      bus_stops.geojson, bus_routes.geojson, summary.json
"""
import json, re, os, xml.etree.ElementTree as ET
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, 'out')
os.makedirs(OUT, exist_ok=True)

R5 = lambda x: round(x, 5)

# 愛知県の市町村（名古屋市は区単位）住所プレフィックス抽出用
NAGOYA_KU = ['千種区','東区','北区','西区','中村区','中区','昭和区','瑞穂区','熱田区','中川区','港区','南区','守山区','緑区','名東区','天白区']
CITIES = ['名古屋市','豊橋市','岡崎市','一宮市','瀬戸市','半田市','春日井市','豊川市','津島市','碧南市','刈谷市','豊田市','安城市','西尾市','蒲郡市','犬山市','常滑市','江南市','小牧市','稲沢市','新城市','東海市','大府市','知多市','知立市','尾張旭市','高浜市','岩倉市','豊明市','日進市','田原市','愛西市','清須市','北名古屋市','弥富市','みよし市','あま市','長久手市','東郷町','豊山町','大口町','扶桑町','大治町','蟹江町','飛島村','阿久比町','東浦町','南知多町','美浜町','武豊町','幸田町','設楽町','東栄町','豊根村']

def city_of(addr):
    if not addr: return '不明'
    a = addr.replace('愛知県','')
    if a.startswith('名古屋市'):
        rest = a[4:]
        for ku in NAGOYA_KU:
            if rest.startswith(ku): return '名古屋市' + ku
        return '名古屋市'
    for c in CITIES:
        if a.startswith(c): return c
    return '不明'

# ---------- 1. 施設 ----------
feats = []
p14 = json.load(open(f'{BASE}/p14/P14-21_23.geojson'))
for f in p14['features']:
    p = f['properties']; code = p.get('P14_006')
    if code == '0504': t = 'ninka'
    elif code in ('0505','0506'): t = 'other'
    else: continue
    lng, lat = f['geometry']['coordinates'][:2]
    addr = (p.get('P14_002') or '') + (p.get('P14_004') or '')
    feats.append({'type':'Feature','geometry':{'type':'Point','coordinates':[R5(lng),R5(lat)]},
        'properties':{'n':p.get('P14_008') or '名称不明','t':t,'c':city_of(addr),'a':addr}})

p29 = json.load(open(f'{BASE}/p29/P29-23_23_GML/P29-23_23.geojson'))
for f in p29['features']:
    p = f['properties']; code = p.get('P29_003')
    if code == '16011': t = 'youchien'
    elif code == '16013': t = 'kodomoen'
    else: continue
    lng, lat = f['geometry']['coordinates'][:2]
    addr = p.get('P29_005') or ''
    feats.append({'type':'Feature','geometry':{'type':'Point','coordinates':[R5(lng),R5(lat)]},
        'properties':{'n':p.get('P29_004') or '名称不明','t':t,'c':city_of(addr),'a':addr}})

json.dump({'type':'FeatureCollection','features':feats}, open(f'{OUT}/facilities.geojson','w'), ensure_ascii=False, separators=(',',':'))
print('facilities:', len(feats))

# 市町村×種別 集計
summary = defaultdict(lambda: defaultdict(int))
for f in feats:
    summary[f['properties']['c']][f['properties']['t']] += 1
json.dump(summary, open(f'{OUT}/summary.json','w'), ensure_ascii=False, separators=(',',':'))
print('cities:', len(summary))

# ---------- 2. 鉄道（愛知bboxフィルタ） ----------
BBOX = (136.55, 34.50, 137.95, 35.50)  # lng_min, lat_min, lng_max, lat_max
def inbox(lng, lat): return BBOX[0]<=lng<=BBOX[2] and BBOX[1]<=lat<=BBOX[3]

rail = json.load(open(f'{BASE}/n02/UTF-8/N02-23_RailroadSection.geojson'))
rl = []
for f in rail['features']:
    coords = f['geometry']['coordinates']
    if any(inbox(c[0],c[1]) for c in coords[::max(1,len(coords)//4)] ) or inbox(*coords[0][:2]) or inbox(*coords[-1][:2]):
        p = f['properties']
        rl.append({'type':'Feature','geometry':{'type':'LineString','coordinates':[[R5(c[0]),R5(c[1])] for c in coords]},
            'properties':{'l':p.get('N02_003'),'o':p.get('N02_004')}})
json.dump({'type':'FeatureCollection','features':rl}, open(f'{OUT}/rail_lines.geojson','w'), ensure_ascii=False, separators=(',',':'))
print('rail lines:', len(rl))

sta = json.load(open(f'{BASE}/n02/UTF-8/N02-23_Station.geojson'))
sl = []
for f in sta['features']:
    coords = f['geometry']['coordinates']
    mid = coords[len(coords)//2]
    if inbox(mid[0], mid[1]):
        p = f['properties']
        sl.append({'type':'Feature','geometry':{'type':'Point','coordinates':[R5(mid[0]),R5(mid[1])]},
            'properties':{'n':p.get('N02_005'),'l':p.get('N02_003'),'o':p.get('N02_004')}})
json.dump({'type':'FeatureCollection','features':sl}, open(f'{OUT}/rail_stations.geojson','w'), ensure_ascii=False, separators=(',',':'))
print('stations:', len(sl))

# ---------- 3. バス停（P11 GML） ----------
NS = {'gml':'http://schemas.opengis.net/gml/3.2.1','ksj':'http://nlftp.mlit.go.jp/ksj/schemas/ksj-app','xlink':'http://www.w3.org/1999/xlink'}
tree = ET.parse(f'{BASE}/p11/P11-22_23_GML/P11-22_23.xml')
root = tree.getroot()
pts = {}
for pt in root.findall('gml:Point', NS):
    pid = pt.get('{http://www.opengis.net/gml/3.2}id') or pt.get('gml:id')
    if pid is None:
        for k,v in pt.attrib.items():
            if k.endswith('id'): pid = v
    pos = pt.find('gml:pos', NS)
    lat, lng = map(float, pos.text.split())
    pts[pid] = (R5(lng), R5(lat))
bs = []
for stop in root.findall('ksj:BusStop', NS):
    loc = stop.find('ksj:loc', NS)
    ref = None
    for k,v in loc.attrib.items():
        if k.endswith('href'): ref = v.lstrip('#')
    if ref not in pts: continue
    name_el = stop.find('ksj:bsn', NS); op_el = stop.find('ksj:boc', NS)
    bs.append({'type':'Feature','geometry':{'type':'Point','coordinates':list(pts[ref])},
        'properties':{'n':name_el.text if name_el is not None else '','o':op_el.text if op_el is not None else ''}})
json.dump({'type':'FeatureCollection','features':bs}, open(f'{OUT}/bus_stops.geojson','w'), ensure_ascii=False, separators=(',',':'))
print('bus stops:', len(bs))

# ---------- 4. バスルート（N07 GML・座標間引き） ----------
tree = ET.parse(f'{BASE}/n07/N07-22_23_GML/N07-22_23.xml')
root = tree.getroot()
curves = {}
for cv in root.findall('gml:Curve', NS):
    cid = None
    for k,v in cv.attrib.items():
        if k.endswith('id'): cid = v
    pl = cv.find('.//gml:posList', NS)
    nums = pl.text.split()
    coords = [[R5(float(nums[i+1])), R5(float(nums[i]))] for i in range(0, len(nums), 2)]
    if len(coords) > 3:  # 中間点を1つおきに間引き（表示用）
        coords = [coords[0]] + coords[1:-1:2] + [coords[-1]]
    curves[cid] = coords
br = []
for rt in root.findall('ksj:BusRoute', NS):
    loc = rt.find('ksj:loc', NS)
    ref = None
    for k,v in loc.attrib.items():
        if k.endswith('href'): ref = v.lstrip('#')
    if ref not in curves: continue
    op = rt.find('ksj:boc', NS)
    br.append({'type':'Feature','geometry':{'type':'LineString','coordinates':curves[ref]},
        'properties':{'o':op.text if op is not None else ''}})
json.dump({'type':'FeatureCollection','features':br}, open(f'{OUT}/bus_routes.geojson','w'), ensure_ascii=False, separators=(',',':'))
print('bus routes:', len(br))

print('=== sizes ===')
for f in sorted(os.listdir(OUT)):
    print(f, round(os.path.getsize(os.path.join(OUT,f))/1e6, 2), 'MB')
