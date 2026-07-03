# -*- coding: utf-8 -*-
"""蒲郡市・半田市の保育園空き状況を所定スキーマのJSONに変換する。"""
import json, re, os

B = "/private/tmp/claude-501/-Users-hiroka-Public-claude--claude-worktrees-infallible-newton-8bd835/34789c15-930c-47c7-a879-72875b51ebf9/scratchpad/hoiku_data"
OUT = os.path.join(B, "aki_out")
os.makedirs(OUT, exist_ok=True)

# ---------------- 蒲郡市 (PDF) ----------------
import pdfplumber

with pdfplumber.open(os.path.join(B, "aki_agents/gamagori/aki.pdf")) as pdf:
    tbl = pdf.pages[0].extract_tables()[0]

header = tbl[0]  # ['', '5歳児', ..., '0歳児', '備考']
ages_g = header[1:7]
assert ages_g == ["5歳児", "4歳児", "3歳児", "2歳児", "1歳児", "0歳児"], ages_g

items_g = {}
for row in tbl[1:]:
    name = re.sub(r"\s+", "", row[0] or "")
    if not name:
        continue
    vals = [(c or "").strip() for c in row[1:7]]
    items_g[name] = {"aki": vals}

gamagori = {
    "city": "蒲郡市",
    "asof": "2026-06-05",
    "asof_note": "空き表PDF自体に作成時点の記載なし。掲載ページ更新日（2026年6月5日）を転記。市の案内では空き状況は毎月5日頃公開",
    "target": "2026年8月入園分（令和8年度8月入所）",
    "source": "https://www.city.gamagori.lg.jp/uploaded/attachment/117074.pdf",
    "source_page": "https://www.city.gamagori.lg.jp/site/subsite-kosodate/nyuuennkizyun.html",
    "legend": "×は空きなし／△ １以上３以下の空きあり／〇 ４以上の空きあり（－は受入なし。大塚保育園は建替え工事のためR8年度の受入なし）",
    "ages": ages_g,
    "items": items_g,
}

with open(os.path.join(OUT, "gamagori.json"), "w", encoding="utf-8") as f:
    json.dump(gamagori, f, ensure_ascii=False, indent=1)
print("gamagori:", len(items_g), "facilities")

# ---------------- 半田市 (HTML) ----------------
from bs4 import BeautifulSoup

soup = BeautifulSoup(open(os.path.join(B, "aki_agents/handa/page.html"), encoding="utf-8", errors="replace").read(), "html.parser")
tables = soup.find_all("table")
t = tables[3]  # 施設別空き状況
rows = t.find_all("tr")
hdr = [c.get_text(" ", strip=True) for c in rows[0].find_all(["th", "td"])]
ages_h = hdr[1:]
assert ages_h == ["0歳児", "1歳児", "2歳児", "3歳児", "4歳児", "5歳児"], ages_h

items_h = {}
for tr in rows[1:]:
    cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
    if not cells or not cells[0]:
        continue
    name = re.sub(r"\s+", " ", cells[0]).strip()
    vals = [re.sub(r"\s+", "", v) for v in cells[1:7]]
    while len(vals) < 6:
        vals.append("")
    items_h[name] = {"aki": vals}

handa = {
    "city": "半田市",
    "asof": "2026-06-18",
    "target": "2026年8月入園分（令和8年8月入園募集時点）",
    "source": "https://www.city.handa.lg.jp/kosodate/hoikuen-youchien/1002100/1010914.html",
    "legend": "数字は受入可能数（令和8年6月18日現在）。×は定員を満たしていることを示す。空欄はその年齢の受け入れを行っていないことを示す",
    "ages": ages_h,
    "items": items_h,
}

with open(os.path.join(OUT, "handa.json"), "w", encoding="utf-8") as f:
    json.dump(handa, f, ensure_ascii=False, indent=1)
print("handa:", len(items_h), "facilities")
