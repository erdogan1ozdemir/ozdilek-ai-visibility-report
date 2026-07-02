# -*- coding: utf-8 -*-
"""Aggregate stats from AI-visibility tool CSV exports -> report-data.json"""
import csv, json, re
from collections import Counter, defaultdict

BASE = "/Users/Erdo/Desktop/Claude Projects/Özdilek/ai özdilek/ozdilek-ai-visibility-report/data/"

def read(fn):
    rows = []
    with open(BASE + fn, encoding="utf-8-sig") as f:
        lines = [l for l in f if not l.startswith("#") or l.startswith("#,")]
        r = csv.DictReader(lines)
        for row in r:
            rows.append(row)
    return rows

def num(x):
    try: return float(x)
    except: return 0.0

out = {}

for key, fn in [("marka", "marka-gorunurluk-analizi.csv"), ("pazaryeri", "pazaryeri-gorunurluk-analizi.csv")]:
    rows = read(fn)
    total_cit = sum(int(num(r["Citations"])) for r in rows)
    bytype = Counter()
    for r in rows: bytype[r["Domain Type"]] += int(num(r["Citations"]))
    top = [{"domain": r["Domain"], "type": r["Domain Type"], "citations": int(num(r["Citations"])),
            "appearance": num(r["Appearance Rate %"]), "gap": int(num(r["Gap Score"]))} for r in rows[:15]]
    you = [r for r in rows if r["Domain Type"] == "you"]
    ozd_eco = [r for r in rows if "ozdilek" in r["Domain"]]
    out[key] = {
        "file": fn, "domains": len(rows), "total_citations": total_cit,
        "citations_by_type": dict(bytype),
        "top15": top,
        "you": [{"domain": r["Domain"], "rank": r["#"], "citations": int(num(r["Citations"])),
                 "appearance": num(r["Appearance Rate %"]), "top_prompts": r["Top Prompts"]} for r in you],
        "ozdilek_ecosystem": [{"domain": r["Domain"], "rank": r["#"], "type": r["Domain Type"],
                               "citations": int(num(r["Citations"]))} for r in ozd_eco],
    }

# URL-level: URL type distribution + listicle economy
for key, fn in [("marka_urls", "marka-gorunurluk-analizi-url-citation.csv"), ("pazaryeri_urls", "pazaryeri-gorunurluk-analizi-url-citations.csv")]:
    rows = read(fn)
    ut = Counter(); ut_c = Counter()
    for r in rows:
        ut[r["URL Type"]] += 1
        ut_c[r["URL Type"]] += int(num(r["Citations"]))
    listicles = [r for r in rows if r["URL Type"] == "listicle"]
    top_listicles = sorted(listicles, key=lambda r: -int(num(r["Citations"])))[:12]
    you_urls = [r for r in rows if r["Domain Type"] == "you"]
    out[key] = {
        "file": fn, "urls": len(rows),
        "url_type_counts": dict(ut), "url_type_citations": dict(ut_c),
        "top_listicles": [{"url": r["URL"], "title": r.get("Title",""), "citations": int(num(r["Citations"]))} for r in top_listicles],
        "you_urls": [{"url": r["URL"], "citations": int(num(r["Citations"])), "prompts": r["Top Prompts"]} for r in you_urls],
    }

# Prompt-level winners: parse "Top Prompts" columns to see which domains win each prompt (approx from domain files)
def prompt_map(fn):
    rows = read(fn)
    pm = defaultdict(list)
    for r in rows:
        tp = r["Top Prompts"] or ""
        for part in tp.split(" | "):
            m = re.match(r"^(.*?)\s*\((\d+)\)\s*$", part.strip())
            if m:
                pm[m.group(1).strip()].append((r["Domain"], int(m.group(2)), r["Domain Type"]))
    return {p: sorted(v, key=lambda x: -x[1])[:8] for p, v in pm.items()}

out["prompt_winners_marka"] = prompt_map("marka-gorunurluk-analizi.csv")
out["prompt_winners_pazaryeri"] = prompt_map("pazaryeri-gorunurluk-analizi.csv")

# Market (grocery) prompts: does ozdilekteyim appear at all?
market_prompts = [p for p in out["prompt_winners_pazaryeri"] if any(w in p.lower() for w in ["market", "gel-al", "teslimat", "yaş pasta", "aylık"])]
out["market_prompt_analysis"] = {p: out["prompt_winners_pazaryeri"][p] for p in market_prompts}

with open(BASE + "report-data.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

# Console summary
print("=== MARKA ===")
m = out["marka"]
print("domains:", m["domains"], "| total citations:", m["total_citations"])
print("by type:", m["citations_by_type"])
print("you:", m["you"])
print("ozdilek ecosystem:", [(d['domain'], d['citations']) for d in m["ozdilek_ecosystem"]])
print("top10:", [(d['domain'], d['citations']) for d in m["top15"][:10]])
print()
print("=== PAZARYERI ===")
p = out["pazaryeri"]
print("domains:", p["domains"], "| total citations:", p["total_citations"])
print("by type:", p["citations_by_type"])
print("you:", p["you"])
print("ozdilek ecosystem:", [(d['domain'], d['citations']) for d in p["ozdilek_ecosystem"]])
print("top10:", [(d['domain'], d['citations']) for d in p["top15"][:10]])
print()
print("=== URL TYPES ===")
print("marka:", out["marka_urls"]["url_type_citations"])
print("pazaryeri:", out["pazaryeri_urls"]["url_type_citations"])
print()
print("=== MARKET PROMPTS (ozdilekteyim var mı?) ===")
for pr, winners in out["market_prompt_analysis"].items():
    has_ozd = any("ozdilek" in d for d, _, _ in winners)
    print(("[OZD YOK] " if not has_ozd else "[OZD VAR] ") + pr[:70], "->", [(d, c) for d, c, _ in winners[:4]])
