"""Blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
10.5281/zenodo.23899403, https://doi.org/10.5281/zenodo.23899403 and https://blog.tristanhotham.com/2026/10/31/gdp-through-time/ stay as placeholders for the publisher."""
import json as _json, shutil, zipfile, importlib.util
from common import *

spec = importlib.util.spec_from_file_location("b", os.path.join(ROOT, "code", "05_build_site.py"))
spec.loader.exec_module(importlib.util.module_from_spec(spec))          # shared fact checks
R = jload(f"{DATA}/results.json")
REL = os.path.join(ROOT, "release"); NAME = "Hotham_WealthOfNations"
KEEP = {"DOI", "DOI_URL", "BLOG_URL"}

# words and alt text in the blog
LRr = R["longrun"]
assert 500 < LRr["pc_delong"]["-10000"] < 600 and 1150 < LRr["pc_delong"]["1800"] < 1250          # alt "between about $500 and $1,200"
assert round(LRr["regions"]["IND"]["1"]["share"]) == 32 and round(LRr["regions"]["CHN"]["1"]["share"]) == 25 and round(LRr["regions"]["WEUR"]["1"]["share"]) == 14
assert round(LRr["regions"]["CHN"]["1700"]["share"]) == 22 and round(LRr["regions"]["IND"]["1700"]["share"]) == 24 and round(LRr["regions"]["WEUR"]["1700"]["share"]) == 22
T = R["top"]
assert [round(r["share"], 1) for r in T["1820"][:3]] == [28.6, 16.6, 6.0] and round(T["1820"][7]["share"], 1) == 2.3
assert [round(r["share"], 1) for r in T[str(LAST)][:3]] == [21.4, 14.8, 8.7] and round(T[str(LAST)][9]["share"], 1) == 1.9
assert round(R["share"]["CHN"]["low"]["pct"]) == 4 and round(R["share"]["IND"]["low"]["pct"]) == 3 and round(R["share"]["USA"]["peak"]["pct"]) == 30
assert 4.5 < R["gap"]["1820"]["ratio"] < 5.5 and 25 < R["gap"]["1950"]["ratio"] < 35 and 240 < R["gap"]["2024"]["ratio"] < 260
assert 2.5 < R["gap"]["1820"]["p90_p10"] < 3.5 and 25 < max(r[3] for r in R["gap_series"]) < 31

post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = re.sub(r"\{\{(?!IMG)([^}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in KEEP else fmt(get(R, m.group(1)), m.group(3)), post)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, len(used)
assert all(re.search(r"^\{\{IMG\|" + re.escape(u), post, re.M) for u in used) and "wp:image" not in post
from PIL import Image
for img in used:
    assert Image.open(f"{REL}/blog/{img}").size[0] == 1800, img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
assert set(re.findall(r"\{\{([^|}]+)\}\}", post)) <= KEEP
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS"):
    assert bad not in vis, bad
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
ci = R["china_india"]
meta = {"title": "The Wealth of Nations, Mapped",
        "slug": "gdp-through-time",
        "excerpt": f"The world economy on one map you can play, from 10,000 BC to {LAST}. China and India made {ci['1820']:.0f}% of the world's output in 1820, {ci['1950']:.0f}% in 1950 and {ci[str(LAST)]:.0f}% in {LAST}, and the further back you go the more of the map is guesswork.",
        "seo_description": f"GDP, GDP per head and shares of world output on an interactive map, from world estimates in 10,000 BC to 169 countries in {LAST}.",
        "tags": ["maps", "economic history", "GDP", "Maddison Project", "great divergence", "China", "India", "data visualisation"],
        "header_alt": f"Title card reading 'The Wealth of Nations, Mapped' in black and red on pale paper, beside three small world maps coloured by share of world GDP for 1820, 1950 and {LAST}. Text: China and India's share of world output: {ci['1820']:.0f}% in 1820, {ci['1950']:.0f}% in 1950, {ci[str(LAST)]:.0f}% in {LAST}."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

# Zenodo
Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z): os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/gdp-through-time_data_and_code.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for d in ("code", "data", "data/hist"):
        for fn in sorted(os.listdir(os.path.join(ROOT, d))):
            p = os.path.join(ROOT, d, fn)
            if os.path.isdir(p) or fn.endswith(".pyc"): continue
            z.write(p, f"gdp-through-time/{d}/{fn}")
    for fn in ("README.md", "LICENSE", "index.html"):
        z.write(os.path.join(ROOT, fn), f"gdp-through-time/{fn}")
    z.write(os.path.join(ROOT, "reddit", "collage.py"), "gdp-through-time/reddit/collage.py")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = re.sub(r"\\cite[pt]?\{mpd2023\}", "(Bolt and van Zanden 2024)", ab)
ab = ab.replace("\\%", "%").replace("\\&", "&").replace("``", "\"").replace("''", "\"")
assert "\\" not in ab, ab[:300]
zmeta = {"title": "The Wealth of Nations, Mapped: National Output, Output per Head and Shares of the World Economy on an Interactive Map, with World Estimates from 10,000 BC",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive version: <a href=\"{PAGE}\">{PAGE}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {{https://blog.tristanhotham.com/2026/10/31/gdp-through-time/}}.</p>"
                        "<p>Sources: Maddison Project Database 2023 (Bolt and van Zanden 2024, CC BY 4.0); IMF World Economic Outlook October 2025 (2023 to 2024 only); "
                        "De Long (1998), HYDE 3.2.1, McEvedy and Jones (1978) and Maddison (2010) as compiled by Roodman (2020); historical-basemaps (GPL-3.0); Natural Earth (public domain).</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["economic history", "Maddison Project", "GDP per capita", "great divergence", "historical national accounts", "world population", "open data", "maps"],
         "license": "cc-by-4.0", "language": "eng",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "10.34894/INZBF2", "relation": "isDerivedFrom", "resource_type": "dataset"}],
         "files": sorted(os.listdir(Z))}
sj = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in sj and "\u2013" not in sj and "--" not in sj
jsave(zmeta, f"{Z}/metadata.json", indent=2)
print("blog words", words, "figures", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
