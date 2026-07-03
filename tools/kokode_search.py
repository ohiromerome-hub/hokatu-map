#!/usr/bin/env python3
"""ここdeサーチの検索POSTを試す（津島市=23208）"""
import re, urllib.request, urllib.parse, http.cookiejar, sys

BASE = 'https://www.wam.go.jp/kokodesearch'
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
op.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')]

# 1. 検索ページ取得（セッション＋トークン）
html = op.open(f'{BASE}/ANN010105E00.do', timeout=30).read().decode('utf-8', 'ignore')
hidden = dict(re.findall(r'<input[^>]*type="hidden"[^>]*name="([^"]+)"[^>]*value="([^"]*)"', html))
# name が先に来るパターンも拾う
for m in re.finditer(r'<input[^>]*name="([^"]+)"[^>]*type="hidden"[^>]*value="([^"]*)"', html):
    hidden.setdefault(m.group(1), m.group(2))
print('hidden keys:', {k: (v[:12] + '..' if len(v) > 12 else v) for k, v in hidden.items() if k.startswith('_')})

city = sys.argv[1] if len(sys.argv) > 1 else '23208'
params = {
    '_FORMID': 'ANN010105',
    '_TARGETID': '/ANN010105E13',
    '_FRAMEID': hidden.get('_FRAMEID', ''),
    '_LUID': hidden.get('_LUID', ''),
    '_SUBINDEX': hidden.get('_SUBINDEX', '-1'),
    '_TOKEN': hidden.get('_TOKEN', ''),
    'vo_headVO_keyword': '',
    'vo_headVO_lat': '', 'vo_headVO_lng': '',
    'vo_headVO_searchMethod': '2',
    'vo_headVO_searchRange': '',
    'vo_headVO_selectCity': city,
    'vo_headVO_filterBySelectedCity': '1',
    # 施設種別: 全部ON
    'vo_headVO_facility': '1',
    'vo_headVO_kindergarten': '1',
    'vo_headVO_authorizedNurserySchool': '1',
    'vo_headVO_authorizedChildcare': '1',
    'vo_headVO_smallChildcare': '1',
    'vo_headVO_homeChildcare': '1',
    'vo_headVO_inHouseChildcare': '1',
    'vo_headVO_homeVisitTypeChildcare': '1',
    'vo_headVO_babyHotel': '1',
    'vo_headVO_babysitterProvider': '1',
    'vo_headVO_privateChildcare': '1',
    'vo_headVO_privateInHouseChildcare': '1',
    'vo_headVO_familyBasedChildcare': '1',
    'vo_headVO_other': '1',
    'vo_headVO_openHolidays': '0',
    'vo_headVO_temporaryCustody': '0',
    'vo_headVO_childcareSick': '0',
    'vo_headVO_childcareCustody': '0',
    'vo_headVO_companyLedChildcareCommunitySlot': '0',
}
data = urllib.parse.urlencode(params).encode()
res = op.open(urllib.request.Request(f'{BASE}/ANN010105E13.do', data=data), timeout=30)
out = res.read().decode('utf-8', 'ignore')
open('kokode_result.html', 'w').write(out)
title = re.search(r'<title>([^<]*)', out)
print('POST →', res.status, 'size', len(out), 'title:', title.group(1) if title else '?')
# 施設リンクらしきもの
links = re.findall(r'(ANN\d+E\d+[^"\']*)["\']', out)
print('page ids in result:', sorted(set(l[:12] for l in links))[:10])
hits = re.findall(r'施設[^<]{0,10}件|該当[^<]{0,15}件|検索結果[^<]{0,15}', out)
print('hits:', hits[:5])
