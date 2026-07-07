#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
市区別ランディングページ生成スクリプト（SEO用）
  python3 tools/build_city_pages.py
data/facilities.geojson・data/summary.json・data/aki/*.json から
city/<slug>/index.html を生成する。まずは名古屋市16区。
デザインは index.html と同トーン（配色・フォント・ヘッダー）。
"""
import json, os, re, html

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://ohiromerome-hub.github.io/hokatu-map"

# 名古屋市16区 → slug / 空きJSONファイル
WARDS = [
    ("名古屋市千種区", "nagoya-chikusa", "nagoya_chikusa.json"),
    ("名古屋市東区",   "nagoya-higashi", "nagoya_higashi.json"),
    ("名古屋市北区",   "nagoya-kita",    "nagoya_kita.json"),
    ("名古屋市西区",   "nagoya-nishi",   "nagoya_nishi.json"),
    ("名古屋市中村区", "nagoya-nakamura","nagoya_nakamura.json"),
    ("名古屋市中区",   "nagoya-naka",    "nagoya_naka.json"),
    ("名古屋市昭和区", "nagoya-showa",   "nagoya_showa.json"),
    ("名古屋市瑞穂区", "nagoya-mizuho",  "nagoya_mizuho.json"),
    ("名古屋市熱田区", "nagoya-atsuta",  "nagoya_atsuta.json"),
    ("名古屋市中川区", "nagoya-nakagawa","nagoya_nakagawa.json"),
    ("名古屋市港区",   "nagoya-minato",  "nagoya_minato.json"),
    ("名古屋市南区",   "nagoya-minami",  "nagoya_minami.json"),
    ("名古屋市守山区", "nagoya-moriyama","nagoya_moriyama.json"),
    ("名古屋市緑区",   "nagoya-midori",  "nagoya_midori.json"),
    ("名古屋市名東区", "nagoya-meito",   "nagoya_meito.json"),
    ("名古屋市天白区", "nagoya-tempaku", "nagoya_tempaku.json"),
]

COLORS = {"hoiku":"#2e7d32","other":"#f9a825","kodomoen":"#7b1fa2","youchien":"#1565c0"}
LABELS = {"hoiku":"保育園・保育所","other":"小規模・認可外等","kodomoen":"認定こども園","youchien":"幼稚園"}
TYPE_ORDER = ["hoiku","kodomoen","other","youchien"]

def aki_norm(s):
    """index.html の akiNorm と同等の正規化"""
    import unicodedata
    s = unicodedata.normalize("NFKC", s or "")
    s = re.sub(r"[（(][^）)]*[）)]", "", s)
    s = re.sub(r"[【】\[\]\s　・]", "", s)
    s = re.sub(r"^(公|私)", "", s)
    s = re.sub(r"^[^市町村]{0,4}[市町村]立", "", s)
    s = s.replace("淨", "浄").replace("ヶ", "ケ")
    s = re.sub(r"(認定こども園|こども園|保育園|保育所|幼稚園|幼児園|乳児園|保育室)$", "", s)
    return s

def has_aki_values(vals):
    for v in vals:
        v = v or ""
        if re.search(r"[〇○◎△▲]", v):
            return True
        m = re.match(r"^(\d+)人?$", v)
        if m and int(m.group(1)) > 0:
            return True
    return False

def load():
    fac = json.load(open(os.path.join(BASE, "data/facilities.geojson"), encoding="utf-8"))
    summary = json.load(open(os.path.join(BASE, "data/summary.json"), encoding="utf-8"))
    return fac, summary

def page_html(city, slug, facs, summary_row, aki, ward_links):
    ward_short = city.replace("名古屋市", "")
    total = len(facs)
    counts = {t: sum(1 for f in facs if f["t"] == t) for t in TYPE_ORDER}
    url = f"{SITE}/city/{slug}/"
    map_url = "../../?city=" + city  # 相対リンク（アプリ側で市区フィルタ）

    # 空き状況インデックス
    aki_idx = {}
    aki_note = ""
    n_aki = 0
    if aki:
        for name, item in aki.get("items", {}).items():
            aki_idx[aki_norm(name)] = item
        n_aki = sum(1 for it in aki.get("items", {}).values() if has_aki_values(it.get("aki", [])))
        aki_note = f"{aki.get('asof','')}時点の公表データでは、空きあり（募集あり）の施設が <b>{n_aki}園</b> あります（{html.escape(aki.get('target',''))}）。"

    desc = (f"{city}の保育園・認定こども園・幼稚園 全{total}施設の一覧と地図。"
            + (f"最新の空き状況（{aki.get('asof','')}時点）つき。" if aki else "")
            + "住所・種別・空き状況を一覧で比較し、地図で最寄駅や通いやすさもチェック。保活・入園・転園の検討に。無料・公的オープンデータ準拠。")

    # 施設リスト（種別ごと）
    sections = []
    for t in TYPE_ORDER:
        rows = sorted([f for f in facs if f["t"] == t], key=lambda f: f["n"])
        if not rows:
            continue
        trs = []
        for f in rows:
            badge = ""
            if aki:
                item = aki_idx.get(aki_norm(f["n"]))
                if item is None:
                    badge = '<span class="bd bd-na">－</span>'
                elif has_aki_values(item.get("aki", [])):
                    badge = '<span class="bd bd-ok">空きあり</span>'
                else:
                    badge = '<span class="bd bd-no">空きなし</span>'
            trs.append(f'<tr><td class="nm">{html.escape(f["n"])}</td>'
                       f'<td class="ad">{html.escape(f["a"])}</td>'
                       f'<td class="ak">{badge}</td></tr>')
        sections.append(
            f'<h3><span class="dot" style="background:{COLORS[t]}"></span>{LABELS[t]}（{len(rows)}施設）</h3>'
            f'<div class="tblwrap"><table><thead><tr><th>施設名</th><th>住所</th><th>空き</th></tr></thead>'
            f'<tbody>{"".join(trs)}</tbody></table></div>')

    ward_nav = " ".join(
        f'<a href="../{s}/">{c.replace("名古屋市","")}</a>'
        for c, s, _ in ward_links if s != slug
    )

    aki_src = ""
    if aki and aki.get("source"):
        aki_src = f'空き状況の出典：<a href="{html.escape(aki["source"])}" target="_blank" rel="noopener">{city}公表データ</a>（{aki.get("asof","")}時点）。'

    ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": f"{city}の保育園・こども園・幼稚園一覧と空き状況",
        "url": url,
        "description": desc,
        "isPartOf": {"@type": "WebSite", "name": "あいち保活マップ", "url": SITE + "/"},
        "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "あいち保活マップ", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": city, "item": url},
        ]},
    }, ensure_ascii=False)

    aki_block = ""
    if aki:
        aki_block = f'''
  <div class="callout">
    <b>🈳 {ward_short}の空き状況</b><br>{aki_note}<br>
    <span class="mut">最新の空き状況・入園可否は必ず<a href="https://www.city.nagoya.jp/kurashi/category/8-14-4-1-3-0-0-0-0-0.html" target="_blank" rel="noopener">名古屋市公式ページ</a>でご確認ください。</span>
  </div>'''

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{city}の保育園・こども園・幼稚園 一覧【空き状況つき】｜あいち保活マップ</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index,follow">
<meta name="theme-color" content="#14213d">
<meta property="og:type" content="article">
<meta property="og:site_name" content="あいち保活マップ">
<meta property="og:title" content="{city}の保育園・こども園・幼稚園 一覧【空き状況つき】">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/ogp.png">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E%F0%9F%97%BA%EF%B8%8F%3C/text%3E%3C/svg%3E">
<script type="application/ld+json">{ld}</script>
<style>
:root{{--ink:#1a2233;--muted:#6b7688;--line:#e3e7ef;--bg:#f6f8fb;--panel:#fff;--accent:#0f62fe;--shadow:0 2px 10px rgba(20,30,60,.08)}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Noto Sans JP",sans-serif;color:var(--ink);background:var(--bg);line-height:1.65}}
header{{background:#14213d;color:#fff;padding:10px 16px;display:flex;align-items:center;gap:12px;flex-wrap:wrap}}
header .h{{font-size:16px;font-weight:800}}
header .h a{{color:#fff;text-decoration:none}}
header .h .sub{{font-size:10.5px;font-weight:600;color:#9fb3d9;display:block}}
main{{max-width:860px;margin:0 auto;padding:20px 16px 40px}}
.crumb{{font-size:11.5px;color:var(--muted);margin-bottom:12px}}
.crumb a{{color:var(--accent);text-decoration:none}}
h1{{font-size:21px;font-weight:800;line-height:1.4;margin-bottom:10px}}
.lead{{font-size:13.5px;color:#33415e;margin-bottom:14px}}
.stats{{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}}
.stat{{background:var(--panel);border:1.5px solid var(--line);border-radius:12px;padding:9px 14px;font-size:12px;font-weight:700;color:var(--muted);box-shadow:var(--shadow)}}
.stat b{{display:block;font-size:17px;color:var(--ink)}}
.btn{{display:inline-block;padding:11px 18px;border-radius:10px;background:var(--accent);color:#fff;font-size:13.5px;font-weight:800;text-decoration:none;margin:4px 8px 14px 0}}
.btn.ghost{{background:#fff;color:var(--accent);border:1.5px solid var(--accent)}}
.callout{{background:#eef3ff;border:1.5px solid #c9d8ff;border-radius:12px;padding:12px 14px;font-size:12.5px;color:#33415e;margin-bottom:16px}}
.callout .mut{{color:#6b7688;font-size:11px}}
h2{{font-size:15px;font-weight:800;margin:22px 0 10px;padding-left:9px;border-left:4px solid var(--accent)}}
h3{{font-size:13px;font-weight:800;margin:16px 0 8px;display:flex;align-items:center;gap:7px}}
h3 .dot{{width:11px;height:11px;border-radius:50%;display:inline-block}}
.tblwrap{{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--panel);box-shadow:var(--shadow)}}
table{{width:100%;border-collapse:collapse;font-size:12px}}
th{{background:#f2f6fc;color:var(--muted);font-size:10.5px;text-align:left;padding:7px 10px;white-space:nowrap}}
td{{padding:7px 10px;border-top:1px solid var(--line);vertical-align:top}}
td.nm{{font-weight:700;min-width:130px}}
td.ad{{color:var(--muted);font-size:11.5px}}
td.ak{{white-space:nowrap}}
.bd{{font-size:10px;font-weight:800;padding:2px 8px;border-radius:9px}}
.bd-ok{{background:#e5f3e6;color:#2e7d32}}
.bd-no{{background:#fdeaea;color:#c62828}}
.bd-na{{color:#98a3b8}}
.wards{{font-size:12px;line-height:2.1}}
.wards a{{color:var(--accent);text-decoration:none;margin-right:10px;white-space:nowrap}}
.src{{font-size:10.5px;color:var(--muted);margin-top:26px;line-height:1.7}}
.src a{{color:var(--muted)}}
footer{{background:#14213d;color:#8fa3c7;font-size:9.5px;padding:8px 14px;line-height:1.5}}
</style>
</head>
<body>
<header><div class="h"><a href="../../">🗺 あいち保活マップ</a><span class="sub">愛知県の保育園・こども園・幼稚園を空き状況つき地図で比較</span></div></header>
<main>
  <nav class="crumb"><a href="../../">あいち保活マップ</a> › 名古屋市 › {ward_short}</nav>
  <h1>{city}の保育園・こども園・幼稚園 一覧（全{total}施設）</h1>
  <p class="lead">{city}にある保育施設 全{total}施設（保育園・保育所 {counts["hoiku"]}、認定こども園 {counts["kodomoen"]}、小規模・認可外等 {counts["other"]}、幼稚園 {counts["youchien"]}）を一覧と地図で比較できます。{ward_short}での保活・入園・転園の検討にお役立てください。</p>
  <div class="stats">
    <div class="stat">保育園・保育所<b>{counts["hoiku"]}</b></div>
    <div class="stat">認定こども園<b>{counts["kodomoen"]}</b></div>
    <div class="stat">小規模・認可外等<b>{counts["other"]}</b></div>
    <div class="stat">幼稚園<b>{counts["youchien"]}</b></div>
  </div>
  <a class="btn" href="{html.escape(map_url)}">🗺 {ward_short}の施設を地図で見る（空き状況つき）</a>
  <a class="btn ghost" href="../../hoikuryo/">💰 保育料かんたん計算（名古屋市 概算）</a>
  {aki_block}
  <h2>{ward_short}の施設一覧</h2>
  {"".join(sections)}
  <h2>名古屋市の他の区を見る</h2>
  <div class="wards">{ward_nav}</div>
  <div class="src">
    施設情報の出典：ここdeサーチ「全国施設CSV」（こども家庭庁）・国土数値情報（国土交通省）を加工。{aki_src}<br>
    本ページの情報は公的オープンデータに基づく参考情報です。入園可否・最新の空き状況・保育料は必ず名古屋市・各施設の公式情報をご確認ください。
  </div>
</main>
<footer>あいち保活マップ — 愛知県の保育園・こども園・幼稚園を空き状況つき地図で比較（無料・公的オープンデータ準拠）</footer>
</body>
</html>
'''

def main():
    fac_geo, summary = load()
    facs_all = [{"n": f["properties"]["n"], "t": f["properties"]["t"],
                 "c": f["properties"]["c"], "a": f["properties"]["a"]}
                for f in fac_geo["features"]]
    for city, slug, akifile in WARDS:
        facs = [f for f in facs_all if f["c"] == city]
        aki = None
        p = os.path.join(BASE, "data/aki", akifile)
        if os.path.exists(p):
            aki = json.load(open(p, encoding="utf-8"))
        outdir = os.path.join(BASE, "city", slug)
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as fp:
            fp.write(page_html(city, slug, facs, summary.get(city, {}), aki, WARDS))
        print(f"OK {city} → city/{slug}/index.html ({len(facs)}施設)")

if __name__ == "__main__":
    main()
