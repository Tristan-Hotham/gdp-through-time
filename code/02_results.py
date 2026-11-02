"""Headline findings: data/results.json holds every number quoted on the page, in the paper, blog, collage and post.
Overtakes are judged on years in which both countries have their own estimate; rankings at a benchmark year use each
country's estimate in that year or, failing that, its nearest estimate up to CARRY years away (as the map does)."""
import pandas as pd
from common import *

P = pd.read_pickle(f"{WORK}/panel.pkl"); WD = pd.read_pickle(f"{WORK}/world.pkl")
META = jload(f"{WORK}/meta.json"); NAME = META["names"]
P = P.merge(WD[["gdp"]].rename(columns={"gdp": "wgdp"}), left_on="year", right_index=True, how="left")
P["share"] = P.gdp / P.wgdp * 100
SER = {iso: g.set_index("year") for iso, g in P.groupby("iso")}
r1 = lambda v, k=1: None if v is None or (isinstance(v, float) and np.isnan(v)) else round(float(v), k)


def val(iso, y, v, carry=CARRY):
    """Estimate in year y, or the nearest within carry years (earlier first on a tie), as on the map."""
    s = SER[iso][v].dropna()
    if y in s.index: return float(s.loc[y]), int(y)
    if not len(s): return None, None
    d = np.abs(s.index.values - y); k = d.min()
    if k > carry: return None, None
    yy = s.index.values[d == k].min()
    return float(s.loc[yy]), int(yy)


def shown(y):
    """Map units shown in year y: former states up to their break-up, their successors after."""
    units = set(SER)
    for a, f in FORMER.items():
        units -= set(f["succ"]) if y <= f["until"] else {a}
    return units


def ranking(y, v, n=15, big=False):
    out = []
    for iso in shown(y):
        x, yy = val(iso, y, v)
        if x is None: continue
        if big:
            p, _ = val(iso, y, "pop")
            if p is None or p < BIG_POP: continue
        out.append({"iso": iso, "name": NAME[iso], "value": x, "year": yy})
    return sorted(out, key=lambda r: -r["value"])[:n]


def overtake(a, b, v, since=None):
    x = pd.concat([SER[a][v], SER[b][v]], axis=1, keys=["a", "b"]).dropna()
    if since: x = x.loc[since:]
    ab = x.a > x.b
    first = int(x.index[ab].min()) if ab.any() else None
    below = x.index[~ab]
    for_good = int(x.index[x.index > below.max()].min()) if len(below) and (x.index > below.max()).any() else (int(x.index.min()) if not len(below) else None)
    return {"first": first, "for_good": for_good, "years_compared": int(len(x))}


R = {"meta": {"title": TITLE, "slug": SLUG, "page": PAGE, "repo": REPO, "last": LAST, "last_mpd": LAST_MPD, "carry": CARRY,
              "pop_gap": POP_GAP, "growth_span": list(GROWTH_SPAN), "big_pop_m": BIG_POP / 1000}}

# ---------------- data ----------------
mpd = P[P.source == "mpd"]
R["data"] = {
    "estimates": int(len(mpd)), "countries": int(P.iso.nunique()), "former_states": len(FORMER),
    "pre1820": int((mpd.year < 1820).sum()), "pre1820_countries": int(mpd[mpd.year < 1820].iso.nunique()),
    "ad1_n": int((mpd.year == 1).sum()), "ad1": sorted(NAME[i] for i in mpd[mpd.year == 1].iso),
    "y1000_n": int((mpd.year == 1000).sum()), "y1500_n": int((mpd.year == 1500).sum()), "y1700_n": int((mpd.year == 1700).sum()),
    "y1820_n": int((mpd.year == 1820).sum()), "y1870_n": int((mpd.year == 1870).sum()), "y1913_n": int((mpd.year == 1913).sum()),
    "y1950_n": int((mpd.year == 1950).sum()), "y2022_n": int((mpd.year == LAST_MPD).sum()),
    "pop_interp": int(P.pop_interp.sum()), "ext_countries": int(P[P.source == "imf_ext"].iso.nunique()),
    "no_ext": [NAME[i] for i in META["no_ext"]], "ext_estimate_rows": int(P[(P.source == "imf_ext") & (P.imf_est == 1)].shape[0]),
    "first_year": int(mpd.year.min()), "with_gdp": int(P.gdp.notna().sum()),
    "world_years": META["maddison_world_years"], "world_ratio_min": r1(min(META["ratio"].values()), 4), "world_ratio_max": r1(max(META["ratio"].values()), 4),
    "coverage": {str(y): r1(WD.loc[y, "coverage_pop"] * 100, 1) for y in (1820, 1870, 1913, 1950)},
}
assert R["data"]["countries"] == 169 and R["data"]["ad1_n"] == 14

# ---------------- world ----------------
w = lambda y, k: float(WD.loc[y, k])
R["world"] = {str(y): {"gdp": w(y, "gdp"), "pop": w(y, "pop"), "gdppc": r1(w(y, "gdppc"), 0)} for y in (1820, 1870, 1913, 1950, 1973, 2000, LAST_MPD, LAST)}
R["world"]["gdp_x"] = r1(w(LAST, "gdp") / w(1820, "gdp"), 0)
R["world"]["gdppc_x"] = r1(w(LAST, "gdppc") / w(1820, "gdppc"), 1)
R["world"]["pop_x"] = r1(w(LAST, "pop") / w(1820, "pop"), 1)

# ---------------- shares of world GDP ----------------
SH = {}
for iso in ("CHN", "IND", "USA", "GBR", "JPN", "SUN", "DEU", "KOR", "FRA", "RUS"):
    s = SER[iso]["share"].dropna()
    s = s[s.index >= 1820]
    d = {"first": {"year": int(s.index[0]), "pct": r1(s.iloc[0])}, "peak": {"year": int(s.idxmax()), "pct": r1(s.max())},
         "low": {"year": int(s.idxmin()), "pct": r1(s.min())}, "last": {"year": int(s.index[-1]), "pct": r1(s.iloc[-1])}}
    for y in (1820, 1870, 1913, 1950, 1973, 2000, LAST):
        x, yy = val(iso, y, "share")
        d[str(y)] = r1(x)
    SH[iso] = d
R["share"] = SH
assert SH["CHN"]["peak"]["year"] == 1820 and SH["CHN"]["low"]["year"] == 1961
assert SH["IND"]["peak"]["year"] == 1821 and SH["IND"]["low"]["year"] == 1979
assert SH["USA"]["peak"]["year"] == 1944 and SH["GBR"]["peak"]["year"] == 1870

# China and India together
ci = {}
for y in (1820, 1870, 1913, 1950, 1973, 2000, LAST):
    ci[str(y)] = r1(sum(val(i, y, "share")[0] for i in ("CHN", "IND")))
R["china_india"] = ci

# ---------------- overtakes ----------------
R["overtake"] = {
    "usa_gbr_gdp": overtake("USA", "GBR", "gdp"),
    "usa_gbr_pc": overtake("USA", "GBR", "gdppc"),
    "usa_chn_gdp": overtake("USA", "CHN", "gdp"),
    "chn_usa_gdp": overtake("CHN", "USA", "gdp", since=1950),
    "jpn_gbr_pc": overtake("JPN", "GBR", "gdppc"),
    "kor_jpn_pc": overtake("KOR", "JPN", "gdppc"),
    "kor_gbr_pc": overtake("KOR", "GBR", "gdppc"),
    "ind_gbr_gdp": overtake("IND", "GBR", "gdp", since=1900),
    "ind_jpn_gdp": overtake("IND", "JPN", "gdp", since=1950),
}
O = R["overtake"]
# China's estimates either side of the US overtaking it
cy = SER["CHN"]["gdp"].dropna().index
R["overtake"]["usa_chn_gdp"]["china_prev_estimate"] = int(cy[cy < O["usa_chn_gdp"]["first"]].max())
R["overtake"]["usa_gbr_gdp"]["usa_bn"] = r1(SER["USA"].loc[O["usa_gbr_gdp"]["first"], "gdp"] / 1e9, 0)
R["overtake"]["usa_gbr_gdp"]["gbr_bn"] = r1(SER["GBR"].loc[O["usa_gbr_gdp"]["first"], "gdp"] / 1e9, 0)
assert O["usa_gbr_gdp"]["first"] == O["usa_gbr_gdp"]["for_good"]          # the US never fell back below Britain
assert O["chn_usa_gdp"]["for_good"] == O["chn_usa_gdp"]["first"]           # and China has stayed ahead since
assert O["kor_jpn_pc"]["first"] == O["kor_jpn_pc"]["for_good"] and O["kor_gbr_pc"]["first"] == O["kor_gbr_pc"]["for_good"]

# ---------------- take-offs ----------------
def pc(iso, y): return float(SER[iso].loc[y, "gdppc"])
def cagr(iso, a, b): return r1(((pc(iso, b) / pc(iso, a)) ** (1 / (b - a)) - 1) * 100)
R["takeoff"] = {
    "jpn": {"1870": r1(pc("JPN", 1870), 0), "1950": r1(pc("JPN", 1950), 0), "1973": r1(pc("JPN", 1973), 0), "x_50_73": r1(pc("JPN", 1973) / pc("JPN", 1950)),
            "g_50_73": cagr("JPN", 1950, 1973), "gbr_1950": r1(pc("GBR", 1950), 0), "pct_gbr_1950": r1(pc("JPN", 1950) / pc("GBR", 1950) * 100, 0),
            "pct_gbr_1973": r1(pc("JPN", 1973) / pc("GBR", 1973) * 100, 0)},
    "kor": {"1950": r1(pc("KOR", 1950), 0), "1960": r1(pc("KOR", 1960), 0), "last": r1(pc("KOR", LAST), 0), "x_60_last": r1(pc("KOR", LAST) / pc("KOR", 1960), 0),
            "g_60_00": cagr("KOR", 1960, 2000), "pct_jpn_1960": r1(pc("KOR", 1960) / pc("JPN", 1960) * 100, 0)},
    "chn": {"1978": r1(pc("CHN", 1978), 0), "last": r1(pc("CHN", LAST), 0), "x_78_last": r1(pc("CHN", LAST) / pc("CHN", 1978), 1), "g_78_last": cagr("CHN", 1978, LAST)},
}
# poorer than: countries richer per head than South Korea in 1960 (1 million people or more, own 1960 estimate)
g60 = P[(P.year == 1960) & (P["pop"] >= BIG_POP)]
R["takeoff"]["kor"]["richer_1960"] = int((g60.gdppc > pc("KOR", 1960)).sum())
R["takeoff"]["kor"]["n_1960"] = int(len(g60))
R["takeoff"]["kor"]["ghana_1960"] = r1(pc("GHA", 1960), 0)
assert pc("GHA", 1960) > pc("KOR", 1960)

# fastest sustained growth of GDP per head: best 25-year spell per country since 1950 (10 million people or more)
fd = []
for iso, s in SER.items():
    if iso in FORMER: continue
    g = s.dropna(subset=["gdppc"])
    for y in g.index:
        if y - 25 in g.index and y - 25 >= 1950 and y <= LAST_MPD and g.loc[y, "pop"] >= 10000:
            fd.append((((g.loc[y, "gdppc"] / g.loc[y - 25, "gdppc"]) ** (1 / 25) - 1) * 100, iso, y - 25, y))
fd.sort(reverse=True)
best, seen = [], set()
for gr, iso, a, b in fd:
    if iso in seen: continue
    seen.add(iso); best.append({"iso": iso, "name": NAME[iso], "from": int(a), "to": int(b), "growth": r1(gr),
                                "x": r1(float(SER[iso].loc[b, "gdppc"] / SER[iso].loc[a, "gdppc"]))})
    if len(best) == 10: break
assert [r["iso"] for r in best[:5]] == ["IRQ", "AGO", "KOR", "JPN", "TWN"] and best[7]["iso"] == "CHN"
R["fastest"] = best

# ---------------- the gap between richest and poorest ----------------
GAP = []
B = P[P["pop"] >= BIG_POP]
for y in (1500, 1600, 1700, 1820, 1870, 1913, 1950, 1973, 2000, LAST_MPD, LAST):
    g = B[(B.year == y) & (B.iso.isin(shown(y)))]
    mx, mn = g.loc[g.gdppc.idxmax()], g.loc[g.gdppc.idxmin()]
    q = g.gdppc.quantile([0.1, 0.9]).values
    d = {"year": y, "n": int(len(g)), "richest": NAME[mx.iso], "richest_iso": mx.iso, "richest_pc": r1(mx.gdppc, 0), "poorest": NAME[mn.iso],
         "poorest_iso": mn.iso, "poorest_pc": r1(mn.gdppc, 0), "ratio": r1(mx.gdppc / mn.gdppc), "p90_p10": r1(q[1] / q[0])}
    GAP.append(d)
R["gap"] = {str(d["year"]): d for d in GAP}
G = R["gap"]
assert G["1820"]["richest"] == "United Kingdom" and G[str(LAST)]["richest"] == "Qatar"
assert G["1950"]["ratio"] < G["2000"]["ratio"] < G[str(LAST)]["ratio"] and G["1820"]["ratio"] < G["1913"]["ratio"]
assert G["1600"]["richest"] == "Netherlands" and G["1700"]["richest"] == "Netherlands"

# all years: ratio for the chart (countries with their own estimate that year, 20 or more of them)
gs = []
for y, g in B.groupby("year"):
    g = g[g.iso.isin(shown(y))]
    if len(g) < 20: continue
    q = g.gdppc.quantile([0.1, 0.9]).values
    gs.append([int(y), int(len(g)), r1(g.gdppc.max() / g.gdppc.min()), r1(q[1] / q[0])])
R["gap_series"] = gs

# ---------------- leaders ----------------
def segments(seq):
    out = []
    for y, c in seq:
        if out and out[-1]["iso"] == c: out[-1]["to"] = y
        else: out.append({"iso": c, "name": NAME[c], "from": y, "to": y})
    return out


rich = []
for y in range(1820, LAST + 1):
    g = B[(B.year == y) & (B.iso.isin(shown(y)))]
    if len(g) >= 20: rich.append((y, g.loc[g.gdppc.idxmax()].iso))
R["richest_seq"] = segments(rich)
big = []
for y in range(1820, LAST + 1):
    rk = ranking(y, "gdp", n=1)
    if rk: big.append((y, rk[0]["iso"]))
R["largest_seq"] = segments(big)
assert [x["iso"] for x in R["largest_seq"]] == ["CHN", "USA", "CHN"] and R["largest_seq"][2]["from"] == O["chn_usa_gdp"]["first"]

# ---------------- top 15 and share at benchmark years ----------------
R["top"] = {}
for y in (1820, 1870, 1913, 1950, 1973, 2000, LAST):
    R["top"][str(y)] = [{"name": r["name"], "iso": r["iso"], "gdp": r["value"], "share": r1(val(r["iso"], y, "share")[0]), "year": r["year"]} for r in ranking(y, "gdp", 15)]
R["top_pc"] = {str(y): [{"name": r["name"], "iso": r["iso"], "gdppc": r1(r["value"], 0), "year": r["year"]} for r in ranking(y, "gdppc", 10, big=True)]
               for y in (1700, 1820, 1913, 1950, LAST)}
t20 = R["top"][str(LAST)]
R["top15_share_last"] = r1(sum(r["share"] for r in t20))
R["top15_share_1820"] = r1(sum(r["share"] for r in R["top"]["1820"]))
assert R["top"]["1820"][0]["iso"] == "CHN" and R["top"]["1820"][1]["iso"] == "IND"
assert R["top"][str(LAST)][0]["iso"] == "CHN" and R["top"][str(LAST)][1]["iso"] == "USA" and R["top"][str(LAST)][2]["iso"] == "IND"

# ---------------- regions: the West ----------------
WEST = P[P.region.isin(["Western Europe", "Western Offshoots"])]
wsh = {}
for y in (1820, 1870, 1913, 1950, 1973, 2000, LAST):
    tot = 0
    for iso in WEST.iso.unique():
        x, _ = val(iso, y, "share")
        tot += x or 0
    wsh[str(y)] = r1(tot)
R["west_share"] = wsh
R["west_peak"] = max(wsh, key=wsh.get)


# ---------------- the very long run (01b_longrun.py) ----------------
LR = jload(f"{WORK}/longrun.json")
WL = pd.read_csv(f"{DATA}/world_longrun.csv").set_index("year")
RGN = pd.read_csv(f"{DATA}/regions_maddison2010.csv")
g = lambda y, c: (None if y not in WL.index or pd.isna(WL.loc[y, c]) else r1(WL.loc[y, c], 1))
lr = {"link": r1(LR["link"], 3), "pop": {}, "pc_delong": {}, "m2010": {}}
for y in (-10000, -5000, -3000, -2000, -1000, 1, 1000, 1500, 1820):
    lr["pop"][str(y)] = {"hyde": g(y, "pop_hyde"), "lo": g(y, "pop_hyde_lower"), "hi": g(y, "pop_hyde_upper"), "mj": g(y, "pop_mcevedy_jones"), "m2010": g(y, "pop_maddison2010")}
for y in (-10000, -5000, -1000, 1, 1000, 1500, 1800):
    lr["pc_delong"][str(y)] = r1(WL.loc[y, "gdppc_delong_linked"], 0)
for y in LR["bench"]:
    lr["m2010"][str(y)] = {"pc": r1(WL.loc[y, "gdppc_maddison2010_linked"], 0), "gdp_bn": r1(WL.loc[y, "gdp_maddison2010_bn_linked"], 0), "pop": r1(WL.loc[y, "pop_maddison2010"], 0)}
lr["pc_x_delong"] = r1(WL.loc[1800, "gdppc_delong_linked"] / WL.loc[-10000, "gdppc_delong_linked"], 1)
lr["pc_x_since_1820"] = R["world"]["gdppc_x"]
lr["pop_x"] = r1(WD.loc[LAST, "pop"] / 1e6 / WL.loc[-10000, "pop_hyde"], 0)
lr["hyde_mj_2000bc"] = r1(WL.loc[-2000, "pop_hyde"] / WL.loc[-2000, "pop_mcevedy_jones"], 1)
reg = {}
for k in M2010_REGIONS:
    d = RGN[RGN.region == k].set_index("year")
    reg[k] = {"name": M2010_NAMES[k], **{str(y): {"share": r1(d.loc[y, "share_world_pct"]), "pc": r1(d.loc[y, "gdppc_linked_2011usd"], 0), "pc90": r1(d.loc[y, "gdppc_1990usd"], 0)} for y in LR["bench"]}}
lr["regions"] = reg
y1 = RGN[RGN.year == 1]
lr["assumed_ad1"] = int(y1.gdppc_1990usd.round(1).isin([400.0, 425.0, 450.0]).sum())
lr["n_regions"] = len(M2010_REGIONS)
lr["india_peak"] = max(LR["bench"], key=lambda y: reg["IND"][str(y)]["share"])
lr["china_peak"] = max(LR["bench"], key=lambda y: reg["CHN"][str(y)]["share"])
lr["weur_low"] = min(LR["bench"], key=lambda y: reg["WEUR"][str(y)]["share"])
lr["ci_ad1"] = r1(reg["CHN"]["1"]["share"] + reg["IND"]["1"]["share"])
R["longrun"] = lr
assert lr["india_peak"] in (1, 1700) and lr["weur_low"] == 1000

R["pc1820"] = {i: r1(val(i, 1820, "gdppc")[0], 0) for i in ("CHN", "IND")}
import glob
R["hist_n"] = len(glob.glob(f"{HB}/world_*.geojson"))
R["hist_bc"] = len(glob.glob(f"{HB}/world_bc*.geojson"))
jsave(R, f"{DATA}/results.json", indent=1)
print(json.dumps({k: R[k] for k in ("share", "china_india", "overtake", "takeoff", "west_share")}, indent=None)[:3000])
print("gap", [(d["year"], d["n"], d["richest"], d["poorest"], d["ratio"], d.get("same41_ratio"), d["p90_p10"]) for d in GAP])
print("richest", [(s["name"], s["from"], s["to"]) for s in R["richest_seq"]])
print("largest", [(s["name"], s["from"], s["to"]) for s in R["largest_seq"]])
print("fastest", [(f["name"], f["from"], f["growth"], f["x"]) for f in best])
print("top last", [(r["name"], r["share"]) for r in t20])
print("top 1820", [(r["name"], r["share"], r["year"]) for r in R["top"]["1820"]])
