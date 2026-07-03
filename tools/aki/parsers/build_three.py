# -*- coding: utf-8 -*-
import json, os, pdfplumber

BASE = "/private/tmp/claude-501/-Users-hiroka-Public-claude--claude-worktrees-infallible-newton-8bd835/34789c15-930c-47c7-a879-72875b51ebf9/scratchpad/hoiku_data"
OUT = os.path.join(BASE, "aki_out")
os.makedirs(OUT, exist_ok=True)

def clean(v):
    if v is None:
        return ""
    return " ".join(str(v).split())

# ---------- 春日井市 ----------
kasugai_items = {}
with pdfplumber.open(os.path.join(BASE, "aki_agents/kasugai/R8.8enn.pdf")) as pdf:
    for pg in pdf.pages:
        for tbl in pg.extract_tables():
            for row in tbl:
                if row[2] in (None, "", "園名"):
                    continue
                name = clean(row[2])
                aki = [clean(c) for c in row[6:12]]
                if name.startswith("宮町字宮町"):
                    # 西部保育園の行はセル結合で注記と混ざるため目視転記（× × × × × ×）
                    name = "西部保育園"
                    aki = ["×", "×", "×", "×", "×", "×"]
                if name == "外之原保育園":
                    # ３歳児・４歳児が結合セルで「△」１つ（目視確認済み）
                    aki = ["", "", "", "△", "△", "○"]
                kasugai_items[name] = {"aki": aki}

kasugai = {
    "city": "春日井市",
    "asof": "2026-07-03",
    "asof_note": "取得日（資料に時点記載なし。受入状況は公表時点のもの）",
    "target": "2026年8月入園分",
    "source": "https://www.city.kasugai.lg.jp/kosodate/hoikuen/hoikuen/1002326/1026096.html",
    "legend": "〇=５人以上の空き △＝４名以下の空き ×＝空きなし（表中の年齢は令和８年４月１日時点。空欄=対象外（斜線）。外之原保育園の△は３・４歳児の結合セル）",
    "ages": ["0歳児", "1歳児", "2歳児", "3歳児", "4歳児", "5歳児"],
    "items": kasugai_items,
}
with open(os.path.join(OUT, "kasugai.json"), "w", encoding="utf-8") as f:
    json.dump(kasugai, f, ensure_ascii=False, indent=1)
print("kasugai:", len(kasugai_items))

# ---------- 豊川市 ----------
toyokawa_items = {}
with pdfplumber.open(os.path.join(BASE, "aki_agents/toyokawa/akizyoukyou.pdf")) as pdf:
    for tbl in pdf.pages[0].extract_tables():
        for row in tbl:
            if row[1] in (None, "", "保 育 施 設 名") or "施 設 名" in (row[1] or ""):
                continue
            name = clean(row[1]).replace(" ", "")
            aki = [clean(c) for c in row[4:10]]
            toyokawa_items[name] = {"aki": aki}

toyokawa = {
    "city": "豊川市",
    "asof": "2026-06-24",
    "target": "2026年度（令和8年度）年度途中入所分",
    "source": "https://www.city.toyokawa.lg.jp/soshiki/kodomokenkou/hoiku/2/3/5/6725.html",
    "legend": "○空きあり（-＝空きなし。空欄=対象年齢クラスなし。豊川東幼稚園・美園こども園・こざかいこども園の空き状況は２．３号認定に限る）",
    "ages": ["0歳児", "1歳児", "2歳児", "3歳児", "4歳児", "5歳児"],
    "items": toyokawa_items,
}
with open(os.path.join(OUT, "toyokawa.json"), "w", encoding="utf-8") as f:
    json.dump(toyokawa, f, ensure_ascii=False, indent=1)
print("toyokawa:", len(toyokawa_items))

# ---------- 名古屋市中村区（スキャンPDFを目視転記） ----------
F = "本園に含む"
nagoya_rows = [
    ("平池保育園", ["-", "0", "1", "0", "3", "1", "7"]),
    ("森田保育園", ["-", "0", "0", "2", "4", "5", "3"]),
    ("烏森保育園", ["-", "0", "0", "1", "2", "3", "7"]),
    ("荒輪井保育園", ["3", "3", "0", "0", "6", "2", "7"]),
    ("日吉保育園", ["-", "0", "0", "0", "1", "1", "0"]),
    ("永信保育園", ["0", "0", "0", "1", "0", "0", "0"]),
    ("千成保育園", ["0", "0", "0", "0", "0", "-", "-"]),
    ("中村保育園", ["0", "0", "0", "0", "4", "6", "6"]),
    ("並木保育園", ["-", "0", "0", "0", "1", "1", "0"]),
    ("愛厚つみき保育園", ["6", "←", "0", "0", "-", "-", "-"]),
    ("けやきの木保育園", ["0", "0", "0", "0", "0", "1", "1"]),
    ("けやきの木保育園（けやきの木分園）", [F, F, F, F, F, F, F]),
    ("びわの実保育園", ["1", "←", "0", "1", "0", "3", "5"]),
    ("ゆめの樹保育園", ["0", "0", "0", "0", "0", "0", "0"]),
    ("たかなしの森保育園", ["1", "←", "0", "1", "0", "0", "1"]),
    ("中村保育園にこにこ館", [F, F, F, F, F, F, F]),
    ("ささしまちとせ保育園", ["7", "←", "0", "0", "0", "0", "0"]),
    ("岩塚そらいろ保育園", ["-", "0", "0", "0", "0", "2", "0"]),
    ("八社あいわ保育園", ["-", "0", "0", "1", "2", "2", "0"]),
    ("ふたつばし保育園", ["2", "←", "0", "0", "0", "0", "1"]),
    ("松原ひまわり保育園", ["4", "←", "0", "1", "0", "1", "1"]),
    ("日比津保育園", ["5", "←", "0", "1", "0", "0", "0"]),
    ("さつきの森保育園", ["2", "←", "1", "0", "1", "3", "4"]),
    ("名駅南保育園", ["0", "0", "1", "0", "0", "0", "0"]),
    ("新富のぞみ保育園", ["-", "1", "0", "0", "0", "0", "0"]),
    ("柳保育園", ["-", "0", "0", "0", "0", "1", "0"]),
    ("稲葉地こども園", ["-", "1", "0", "0", "2", "0", "1"]),
    ("御田クローバーこども園", ["0", "0", "0", "0", "0", "0", "0"]),
    ("認定こども園なごや遊花幼稚園", ["-", "0", "0", "0", "0", "0", "0"]),
    ("ちいさなおうちえん中村", ["0", "0", "1", "0", "-", "-", "-"]),
    ("リーゴ岩塚", ["0", "0", "0", "0", "-", "-", "-"]),
    ("小規模保育事業所ソラーナほんじん", ["0", "1", "1", "0", "-", "-", "-"]),
    ("中村保育園わくわく館", ["5", "←", "1", "0", "-", "-", "-"]),
    ("ちいさなおうちえんアクアタウン", ["0", "0", "0", "0", "-", "-", "-"]),
    ("どりーむ館", ["1", "←", "0", "1", "-", "-", "-"]),
    ("ウィズブック保育室　中村", ["1", "←", "1", "0", "-", "-", "-"]),
    ("中島ひまわり保育室", ["4", "←", "1", "1", "-", "-", "-"]),
    ("保育室くれよん", ["0", "0", "0", "0", "-", "-", "-"]),
    ("小規模保育事業所　ひだまり", ["3", "←", "0", "0", "-", "-", "-"]),
    ("なないろ保育室名駅西", ["2", "←", "2", "←", "-", "-", "-"]),
    ("スクルドエンジェル保育室とよとみ園", ["2", "←", "1", "2", "-", "-", "-"]),
    ("すまいるなみき保育室", ["-", "0", "0", "0", "-", "-", "-"]),
    ("ラブクローバー名駅南", ["1", "←", "2", "2", "-", "-", "-"]),
    ("みなもり　なごや園", ["3", "←", "1", "1", "-", "-", "-"]),
    ("リコ保育室", ["2", "←", "0", "0", "-", "-", "-"]),
]
nagoya = {
    "city": "名古屋市中村区",
    "asof": "2026-06-11",
    "target": "2026年7月入園分（令和8年7月募集人数一覧）",
    "source": "https://www.city.nagoya.jp/nakamura/kosodate/1020728/1033291.html",
    "legend": "数値=募集人数 「-」:受入可能年齢ではないクラス年齢 「←」:左隣のクラス年齢と合わせて募集 「本園に含む」:本園の数値に含む",
    "ages": ["産明け", "6ヶ月以上", "1歳", "2歳", "3歳", "4歳", "5歳"],
    "items": {n: {"aki": a} for n, a in nagoya_rows},
}
assert all(len(a) == 7 for _, a in nagoya_rows)
with open(os.path.join(OUT, "nagoya_nakamura.json"), "w", encoding="utf-8") as f:
    json.dump(nagoya, f, ensure_ascii=False, indent=1)
print("nagoya:", len(nagoya_rows))
