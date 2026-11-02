"""Compact page data: data/site.json (fetched by the page).
units: Maddison code -> {n: name, r: region, y: years, pc: GDP per head, p: population (thousands, null if unknown),
       g: growth of GDP per head (% a year, null if no earlier estimate 5 to 15 years back), gf: from year, f: flags
       (1 population interpolated, 2 carried forward with IMF growth, 4 IMF estimate rather than outturn)}.
world: GDP in billions of 2011 int$ for 1820 to LAST (index 0 = 1820) and how each year was obtained (0 Maddison world
       estimate, 1 interpolated, 2 scaled sum of countries, 3 with IMF growth).
"""
import pandas as pd
from common import *

P = pd.read_pickle(f"{WORK}/panel.pkl"); WD = pd.read_pickle(f"{WORK}/world.pkl")
META = jload(f"{WORK}/meta.json")
units = {}
for iso, g in P.groupby("iso"):
    g = g.sort_values("year")
    rp = lambda v, k: [None if pd.isna(x) else (round(float(x), k) if k else int(round(float(x)))) for x in v]
    units[iso] = {"n": META["names"][iso], "r": META["region"][iso], "y": g.year.astype(int).tolist(), "pc": rp(g.gdppc, 0),
                  "p": rp(g["pop"], 0), "g": rp(g.growth, 2), "gf": rp(g.growth_from, 0),
                  "f": (g.pop_interp.astype(int) + 2 * (g.source == "imf_ext").astype(int) + 4 * g.imf_est.astype(int)).tolist()}
code = lambda m: 0 if m.startswith("Maddison world") else 1 if m.startswith("interpolated") else 3 if "IMF" in m else 2
site = {"units": units, "world": {"y0": 1820, "gdp": [round(float(v) / 1e9, 1) for v in WD.gdp], "pop": [round(float(v) / 1e6, 2) for v in WD["pop"]], "m": [code(m) for m in WD.method]},
        "former": {a: {"until": f["until"], "succ": f["succ"]} for a, f in FORMER.items()},
        "knots": TIME_KNOTS, "carry": CARRY, "last": LAST, "last_mpd": LAST_MPD, "big_pop": BIG_POP,
        "hist": jload(f"{DATA}/hist/index.json")["years"], "first": FIRST}
# the very long run: world series (linked to 2011 dollars at 1820) and Maddison (2010) regions
WL = pd.read_csv(f"{DATA}/world_longrun.csv")
col = lambda c: [[int(y), round(float(v), 2)] for y, v in zip(WL.year, WL[c]) if pd.notna(v)]
site["longrun"] = {"pop_hyde": col("pop_hyde"), "pop_lo": col("pop_hyde_lower"), "pop_hi": col("pop_hyde_upper"), "pop_mj": col("pop_mcevedy_jones"),
                   "pc_delong": col("gdppc_delong_linked"), "gdp_delong": col("gdp_delong_bn_linked"), "pc_m2010": col("gdppc_maddison2010_linked"),
                   "gdp_m2010": col("gdp_maddison2010_bn_linked"), "pop_m2010": col("pop_maddison2010")}
RG = pd.read_csv(f"{DATA}/regions_maddison2010.csv")
site["regions"] = {k: {"n": M2010_NAMES[k], "y": g.year.tolist(), "gdp": [round(v * jload(f"{WORK}/longrun.json")["link"] / 1000, 2) for v in g.gdp_1990usd_millions],
                       "pc": g.gdppc_linked_2011usd.round(0).tolist(), "sh": g.share_world_pct.tolist(), "p": g.pop_thousands.round(0).tolist()} for k, g in RG.groupby("region")}
jsave(site, f"{DATA}/site.json")
print("site.json", os.path.getsize(f"{DATA}/site.json") // 1024, "KB;", len(units), "units")
