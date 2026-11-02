"""The very long run, before the national series: world population and output from 10,000 BC, and Maddison's own
(2010) regional estimates for AD 1 to 1820.

Inputs (read in place): LONGRUN_XLSX, a compilation of published long-run series by David Roodman (2020) for
"Modeling the Human Trajectory" (github.com/droodman/Modeling-Human-Trajectory, GWP.xlsx), whose sheets transcribe:
  De Long (1998), "Estimates of world GDP, one million B.C. to present": world GDP and GDP per head, "ex-Nordhaus"
      variant (comparable with Maddison's concept), 1990 international dollars;
  HYDE 3.2.1 (Klein Goldewijk et al. 2017): world population by region, central, lower and upper estimates;
  McEvedy and Jones (1978), Atlas of World Population History: world population;
  Maddison (2010), Historical Statistics of the World Economy 1 to 2008 AD: GDP (1990 GK$) and population by
      country and region for AD 1, 1000, 1500, 1600, 1700 and 1820.
Only these published figures are used (a few dozen numbers per series); the workbook itself is not redistributed.

Linking: Maddison 2010 and De Long are in 1990 dollars, the 2023 database in 2011 dollars. I rescale the older
series by one factor, the ratio of the 2023 database's world GDP per head in 1820 to Maddison 2010's, so the long line
meets the modern one in 1820. This is a presentation choice; the shapes are the authors'.

Outputs: data/world_longrun.csv, data/regions_maddison2010.csv, WORK/longrun.json.
"""
import pandas as pd
from common import *

X = pd.ExcelFile(LONGRUN_XLSX)
WD = pd.read_pickle(f"{WORK}/world.pkl")
BENCH = [1, 1000, 1500, 1600, 1700, 1820]

# ---------------- Maddison 2010 regions ----------------
def m2010(sheet, hr):
    g = X.parse(sheet, header=None); hdr = [str(h).strip() for h in g.iloc[hr]]
    Y = {int(g.iloc[i, 0]): g.iloc[i] for i in range(hr + 1, len(g)) if g.iloc[i, 0] in BENCH}
    return {nm: {y: float(Y[y][hdr.index(nm)]) for y in BENCH} for nm in hdr if nm and nm != "nan"}
G10, P10 = m2010("Maddison 2010 GDP", 2), m2010("Maddison 2010 population", 0)
REG = {}
for key, cols in M2010_REGIONS.items():
    REG[key] = {}
    for y in BENCH:
        if key == "OASIA":
            gdp = G10["Asia"][y] - sum(G10[c][y] for c in ("China", "India", "Japan", "15 W. Asia"))
            pop = P10["Asia"][y] - sum(P10[c][y] for c in ("China", "India", "Japan", "15 W. Asia"))
        else:
            gdp, pop = G10[cols][y], P10[cols][y]
        REG[key][y] = (gdp, pop)
for y in BENCH:
    tot = sum(REG[k][y][0] for k in REG)
    assert abs(tot / G10["World Total"][y] - 1) < 0.001, (y, tot, G10["World Total"][y])
    assert abs(sum(REG[k][y][1] for k in REG) / P10["World Total"][y] - 1) < 0.001
LINK = float(WD.loc[1820, "gdppc"]) / (G10["World Total"][1820] / P10["World Total"][1820] * 1000)
print("link factor 1990 -> 2011 dollars at 1820:", round(LINK, 3))
rows = []
for k, d in REG.items():
    for y in BENCH:
        gdp, pop = d[y]
        rows.append({"region": k, "name": M2010_NAMES[k], "year": y, "gdp_1990usd_millions": round(gdp, 1), "pop_thousands": round(pop, 1),
                     "gdppc_1990usd": round(gdp / pop * 1000, 1), "gdppc_linked_2011usd": round(gdp / pop * 1000 * LINK, 1),
                     "share_world_pct": round(gdp / G10["World Total"][y] * 100, 2)})
RG = pd.DataFrame(rows)
RG.to_csv(f"{DATA}/regions_maddison2010.csv", index=False)

# ---------------- world series ----------------
D = X.parse("Data", header=None).iloc[2:]
D = D[[0, 8, 12, 58]]; D.columns = ["year", "gwp_delong", "pc_delong", "pop_hyde_r"]
D = D[(D.year >= -10000) & (D.year <= 1820)].astype(float)
# HYDE world totals (sum of regions), central, lower and upper
def hyde(sheet):
    h = X.parse(sheet, header=None)
    off = 2 if sheet.endswith("central") else 1
    tot = h[h[0].astype(str).str.strip() == "Total"].iloc[0]
    out = {}
    for j in range(off, h.shape[1]):
        y, v = h.iloc[0, j], tot[j]
        if pd.notna(y) and pd.notna(v): out[float(y)] = float(v) / 1e6      # million people
    return out
HC, HL, HU = hyde("HYDE 3.2.1 central"), hyde("HYDE 3.2.1 lower"), hyde("HYDE 3.2.1 upper")
MJ = X.parse("McEvedy & Jones", header=None).iloc[2:, [0, 6]].dropna()
MJ = {float(a): float(b) for a, b in MJ.values}
out = []
for y in sorted(set(HC) | set(D.year) | set(BENCH)):
    if y < -10000 or y > 1820: continue
    r = {"year": int(y)}
    if y in HC and y <= 1820:
        r.update(pop_hyde=round(HC[y], 2))
        if HL.get(y, 0) > 0: r.update(pop_hyde_lower=round(HL[y], 2), pop_hyde_upper=round(HU[y], 2))      # HYDE gives a lower bound of 0 for 10,000 BC; no range shown there
    if y in MJ: r["pop_mcevedy_jones"] = MJ[y]
    d = D[D.year == y]
    if len(d) and pd.notna(d.gwp_delong.iloc[0]):
        r["gdp_delong_bn_linked"] = round(float(d.gwp_delong.iloc[0]) * LINK, 2)
        r["gdppc_delong_linked"] = round(float(d.pc_delong.iloc[0]) * LINK, 1)
    if y in BENCH:
        r["gdp_maddison2010_bn_linked"] = round(G10["World Total"][y] / 1000 * LINK, 1)
        r["gdppc_maddison2010_linked"] = round(G10["World Total"][y] / P10["World Total"][y] * 1000 * LINK, 1)
        r["pop_maddison2010"] = round(P10["World Total"][y] / 1000, 1)
    if len(r) > 1: out.append(r)
WL = pd.DataFrame(out)
# HYDE lower/upper sheets lack some central years: fill only where given
WL.to_csv(f"{DATA}/world_longrun.csv", index=False)
jsave({"link": LINK, "bench": BENCH, "world": out, "regions": {k: {str(y): {"gdp": v[0], "pop": v[1]} for y, v in d.items()} for k, d in REG.items()}},
      f"{WORK}/longrun.json")
print(WL.head(12).to_string()); print(RG[RG.year == 1][["name", "share_world_pct", "gdppc_1990usd"]].to_string())
