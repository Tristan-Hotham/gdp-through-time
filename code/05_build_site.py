"""Build index.html from code/page_template.html. Every number in the text is a {{path|format}} token filled from
data/results.json (embedded); map data (data/site.json, data/map_countries.geojson, data/hist/) is fetched by the page.
Facts stated in words on the page, in the blog, paper and collage are checked here. https://doi.org/10.5281/zenodo.23899403 and https://blog.tristanhotham.com/2026/10/31/gdp-through-time/ stay as
placeholders for the publisher."""
import pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
P = pd.read_pickle(f"{WORK}/panel.pkl")
KEEP = {"DOI", "BLOG_URL", "DOI_URL"}
SER = {i: g.set_index("year") for i, g in P.groupby("iso")}

# ---------------- facts stated in words ----------------
S, O, T, G = R["share"], R["overtake"], R["takeoff"], R["gap"]
assert R["china_india"]["1820"] > 40 and R["china_india"]["1950"] < 10 and R["china_india"]["2024"] > 25          # "almost half", "a tenth", "a third"
assert abs(R["china_india"]["2024"] - R["west_share"]["2024"]) < 1.5                                                  # "almost exactly the West's"
assert R["west_peak"] == "1913"
assert S["CHN"]["1820"] > S["IND"]["1820"] > max(S[k]["1820"] or 0 for k in ("USA", "GBR", "JPN", "DEU", "FRA"))    # the two largest
assert R["pc1820"]["CHN"] < G["1820"]["richest_pc"] / 2 and R["pc1820"]["IND"] < G["1820"]["richest_pc"] / 2
assert G["1820"]["richest"] == "United Kingdom"
# US passes UK per head: swaps up to 1898 and in 1933 to 1934
u = pd.concat([SER["USA"].gdppc, SER["GBR"].gdppc], axis=1, keys=["us", "uk"]).dropna()
below = [y for y in u.index if y > O["usa_gbr_pc"]["first"] and u.loc[y, "uk"] > u.loc[y, "us"]]
assert below == [1888, 1889, 1890, 1894, 1896, 1898, 1933, 1934], below
assert O["usa_gbr_pc"]["for_good"] == 1935
# China the largest in every comparable year before the US passed it
for y in SER["CHN"].dropna(subset=["gdp"]).index:
    if y >= O["usa_chn_gdp"]["first"]: break
    others = P[(P.year == y) & (P.iso != "CHN")].gdp.max()
    assert SER["CHN"].loc[y, "gdp"] > others, y
assert O["usa_chn_gdp"]["china_prev_estimate"] == 1870 and O["usa_chn_gdp"]["first"] == 1887
assert 1860 < O["usa_gbr_gdp"]["first"] < 1866                                                                         # "in the middle of the Civil War"
assert S["USA"]["peak"]["year"] in range(1939, 1946)                                                                   # "with the rest of the industrial world at war"
assert S["CHN"]["low"]["year"] in (1960, 1961, 1962)                                                                   # end of the Great Leap famine
assert 23 <= T["kor"]["pct_jpn_1960"] <= 27                                                                            # "a quarter of Japan's"
assert R["fastest"][0]["iso"] == "IRQ" and R["fastest"][0]["from"] == 1991 and R["fastest"][1]["iso"] == "AGO" and 1975 < R["fastest"][1]["from"] < 2002
assert [f["iso"] for f in R["fastest"][2:5]] == ["KOR", "JPN", "TWN"]
assert G["1820"]["p90_p10"] < G["1950"]["p90_p10"] < G["2000"]["p90_p10"] and G["2024"]["p90_p10"] < G["2000"]["p90_p10"]   # rose, then eased a little
assert G["2024"]["richest"] == "Qatar"
assert R["top_pc"]["1700"][0]["name"] == "Netherlands" and R["top_pc"]["1700"][1]["name"] == "South Africa"
first = P[P.year < 1820].groupby("iso").year.min()
assert first["GBR"] == 1000 and P[(P.iso == "GBR") & (P.year > 1000)].year.min() == 1252 and first["NLD"] == 1348 and first["SWE"] == 1300
assert P[(P.iso == "FRA") & (P.year > 1)].year.min() // 10 == 127 and P[(P.iso == "ESP") & (P.year > 1)].year.min() // 10 == 127
assert set(R["data"]["ad1"]) <= {"Belgium", "Egypt", "France", "Greece", "Iran", "Iraq", "Israel", "Italy", "Jordan", "Portugal", "Spain", "Switzerland", "Tunisia", "Turkey"}
assert R["data"]["world_ratio_max"] < 1.005 and R["data"]["world_ratio_min"] > 0.995                                  # "never more than half a per cent"
assert R["data"]["no_ext"] == ["Cuba", "North Korea", "Syria"]
assert R["takeoff"]["jpn"]["pct_gbr_1950"] < 30
LRr = R["longrun"]
assert 2.5 <= LRr["hyde_mj_2000bc"] <= 3.3                          # McEvedy and Jones "a third of HYDE's figure" for 2000 BC
assert LRr["pc_x_delong"] < 2.5                                       # "barely doubles"
assert LRr["regions"]["WEUR"]["1000"]["share"] < LRr["regions"]["WEUR"]["1"]["share"]
assert LRr["regions"]["CHN"]["1820"]["share"] > R["share"]["CHN"]["1820"] + 2       # the two releases disagree
assert LRr["pop"]["-3000"]["hi"] / LRr["pop"]["-3000"]["lo"] > 2                   # "differ by a factor of two or more"


def build():
    tpl = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
    html = re.sub(r"\{\{(?!DOI\}\}|BLOG_URL\}\}|DOI_URL\}\})([^}|]+)(\|(\w+))?\}\}", lambda m: fmt(get(R, m.group(1)), m.group(3)), tpl)
    left = set(re.findall(r"\{\{([^}]*)\}\}", html))
    assert left <= KEEP, left
    J = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    html = html.replace("/*RESULTS*/", J(R)).replace("/*RAMP*/", J(RAMP)).replace("/*DIV*/", J(DIV)).replace("/*SCOL*/", J(SERIES_COL)).replace("/*NAMES_SHORT*/", J(NAMES_SHORT))
    html = html.replace("/*FULLSCREEN*/", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html, flags=re.S)
    vis = re.sub(r"<[^>]+>", " ", vis)
    for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv"):
        assert bad not in vis, bad
    for scr in re.findall(r"<script>(.*?)</script>", html, flags=re.S):
        for bad in ("—", "–"):
            assert bad not in scr, bad
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print("index.html", len(html.encode()) // 1024, "KB")


if __name__ == "__main__":
    build()
