# -*- coding: utf-8 -*-
import json, os, re
import pdfplumber

BASE="/private/tmp/claude-501/-Users-hiroka-Public-claude--claude-worktrees-infallible-newton-8bd835/34789c15-930c-47c7-a879-72875b51ebf9/scratchpad/hoiku_data"
OUT=os.path.join(BASE,"aki_out")
os.makedirs(OUT,exist_ok=True)

def clean(s):
    if s is None: return ""
    return re.sub(r"\s+","",s)

# ---------- 岡崎市 ----------
ok_pdf=os.path.join(BASE,"aki_agents/okazaki/aki_202608.pdf")
items={}
with pdfplumber.open(ok_pdf) as pdf:
    full_text="\n".join((p.extract_text() or "") for p in pdf.pages)
    t=pdf.pages[0].extract_tables()[0]
    for row in t:
        name=clean(row[1]) if len(row)>=9 else ""
        if not name or name=="受入園":
            continue
        aki=[clean(c) if clean(c) in ("〇","△","×","○","✕") else clean(c) for c in row[3:9]]
        # normalize nothing; keep as-is, unreadable/blank -> ""
        items[name]={"aki":[a if a else "" for a in aki]}

okazaki={
 "city":"岡崎市",
 "asof":"2026-07-03",
 "asof_note":"PDF内に時点記載なし（申込期間:6月4日～12日と記載）。市HPによれば本PDFは2026-06-04正午過ぎに訂正版へ差替え公表されたもの。asofは取得日(2026-07-03)。",
 "target":"2026年8月入園分（令和8年8月1日入園）",
 "source":"https://www.city.okazaki.lg.jp/_res/projects/default_project/_page_/001/003/640/20260801akijoukyou.pdf",
 "legend":"〇・・・空きあり（４名以上） △・・・空き若干名 ×・・・空きなし",
 "ages":["0歳クラス","1歳クラス","2歳クラス","3歳クラス","4歳クラス","5歳クラス"],
 "items":items,
}
with open(os.path.join(OUT,"okazaki.json"),"w",encoding="utf-8") as f:
    json.dump(okazaki,f,ensure_ascii=False,indent=1)
print("okazaki facilities:",len(items))

# ---------- 豊橋市 ----------
ty_items={}
tybase=os.path.join(BASE,"aki_agents/toyohashi")
for fn,kubun in [("hoikuen.pdf","保育園"),("kodomoen.pdf","認定こども園")]:
    with pdfplumber.open(os.path.join(tybase,fn)) as pdf:
        p=pdf.pages[0]
        seen=set()
        for t in p.extract_tables():
            for row in t:
                name=clean(row[0])
                if not name or "クラス" in (row[2] or "") and name.endswith(("保育園","こども園","幼稚園"))==False:
                    pass
                if not name or name in ("私立保育園","公立保育園","私立認定こども園","公立認定こども園"):
                    continue
                if name in seen:  # kodomoen page duplicate table
                    continue
                seen.add(name)
                aki=[clean(c) for c in row[3:9]]
                ty_items[name]={"aki":[a if a in ("×","△","○","◎") else "" for a in aki]}

toyohashi={
 "city":"豊橋市",
 "asof":"2026-06-17",
 "asof_note":"保育園PDFの記載時点は令和8年(2026年)6月16日、認定こども園PDFは同6月17日。asofは新しい方を記載。",
 "target":"2026年8月入所分（令和8年8月入園申込）",
 "source":"https://www.city.toyohashi.lg.jp/63210.htm （PDF: /secure/119480/【保育園】8月入園　受入可能月齢・受入可能人数0616.pdf, /secure/119480/【認定こども園】8月入園　受入可能月齢・受入可能人数0617.pdf）",
 "legend":"「×」０人、「△」１〜２人、「○」３〜５人、「◎」６人以上",
 "ages":["0歳児クラス","1歳児クラス","2歳児クラス","3歳児クラス","4歳児クラス","5歳児クラス"],
 "items":ty_items,
}
with open(os.path.join(OUT,"toyohashi.json"),"w",encoding="utf-8") as f:
    json.dump(toyohashi,f,ensure_ascii=False,indent=1)
print("toyohashi facilities:",len(ty_items))
