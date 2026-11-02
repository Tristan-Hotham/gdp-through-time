"""Read the Maddison Project Database 2023 and the IMF WEO (October 2025), and write the clean panel and world series.

Outputs
  data/panel.csv     one row per country and year with an estimate of GDP per head (2011 international dollars, PPP):
                     iso, name, region, year, gdppc, pop (thousands), pop_interp (1 if population was interpolated
                     between Maddison estimates), gdp (2011 int$, gdppc x pop), growth (annual average change of GDP per
                     head since an earlier estimate), growth_from (that year), source (mpd or imf_ext), imf_est (1 if
                     the IMF's figure for that year is an estimate rather than an outturn).
  data/world.csv     world GDP, population and GDP per head, 1820 to 2024, with how each year was obtained.
  data/countries.csv one row per Maddison unit: code, display name, region, first and last estimate, number of estimates.
  WORK/panel.pkl, WORK/world.pkl for later steps.
"""
import pandas as pd
from common import *

# ---------------- Maddison ----------------
X = pd.ExcelFile(MPD_XLSX)
D = X.parse("Full data")
D = D.rename(columns={"countrycode": "iso"})
assert set(D.columns) == {"iso", "country", "region", "year", "gdppc", "pop"}, D.columns
assert D.iso.nunique() == 169 and D.year.max() == LAST_MPD and D.year.min() == 1
if os.path.exists(MPD_CHECK):      # a second, independent copy of the same release
    C = pd.read_csv(MPD_CHECK)      # Our World in Data layout: Entity, Code, Year, GDP per capita (rounded)
    C = C.rename(columns={"Code": "iso", "Year": "year", "GDP per capita": "gdppc_c"})
    m = D.dropna(subset=["gdppc"]).merge(C[["iso", "year", "gdppc_c"]], on=["iso", "year"], how="inner")
    ok = (m.gdppc - m.gdppc_c).abs() <= 1.0
    assert len(m) > 15000 and ok.mean() > 0.999, (len(m), ok.mean())
    print("second copy agrees on", int(ok.sum()), "of", len(m), "GDP per head values")

reg = X.parse("Regional data", header=None)
W = []
for _, r in reg.iloc[2:].iterrows():
    if pd.notna(r[0]) and pd.notna(r[9]) and pd.notna(r[19]):
        W.append({"year": int(r[0]), "gdppc": float(r[9]), "pop": float(r[19])})
W = pd.DataFrame(W)
W["gdp"] = W.gdppc * W["pop"] * 1000
assert W.year.min() == 1820 and W.year.max() == LAST_MPD, W.year.tolist()
print("Maddison world benchmarks:", W.year.tolist())

names = D.drop_duplicates("iso").set_index("iso")
NAME = {i: NAMES.get(i, names.loc[i, "country"]) for i in names.index}
REGION = names["region"].to_dict()

# ---------------- population: log-linear interpolation over short gaps ----------------
rows = []
for iso, g in D.groupby("iso"):
    g = g.sort_values("year")
    py = g.dropna(subset=["pop"])
    yrs, lp = py.year.values, np.log(py["pop"].values)
    for _, r in g.dropna(subset=["gdppc"]).iterrows():
        y = int(r.year)
        pop, pi = r["pop"], 0
        if pd.isna(pop) and len(yrs):
            k = np.searchsorted(yrs, y)
            if 0 < k < len(yrs) and yrs[k] - yrs[k - 1] <= POP_GAP:
                t = (y - yrs[k - 1]) / (yrs[k] - yrs[k - 1])
                pop, pi = float(np.exp(lp[k - 1] + t * (lp[k] - lp[k - 1]))), 1
        rows.append({"iso": iso, "year": y, "gdppc": float(r.gdppc), "pop": None if pd.isna(pop) else float(pop), "pop_interp": pi,
                     "source": "mpd", "imf_est": 0})
P = pd.DataFrame(rows)

# ---------------- IMF extension 2023 to 2024 ----------------
WE = pd.read_excel(WEO_XLSX, sheet_name="Countries")
WE = WE[WE["INDICATOR.ID"].isin(["NGDPRPPPPC", "NGDP_RPCH", "LP"])]
WE = WE.rename(columns={"COUNTRY.ID": "c", "INDICATOR.ID": "ind", "LATEST_ACTUAL_ANNUAL_DATA": "la"})
WEO_ALIAS = {"PSE": ["WBG"], "SDN": ["SDN", "SSD"]}


def latest_actual(s):
    s = str(s)
    m = re.findall(r"(\d{4})", s)
    return int(m[-1]) if m else 0


def weo(c, ind):
    r = WE[(WE.c == c) & (WE.ind == ind)]
    if not len(r): return None
    r = r.iloc[0]
    return {y: (float(r[y]) if pd.notna(r[y]) else None) for y in range(2015, 2031)}, latest_actual(r["la"])


ext = []
for iso in sorted(P.iso.unique()):
    last = P[(P.iso == iso) & (P.year == LAST_MPD)]
    if not len(last) or iso in FORMER:
        continue
    last = last.iloc[0]
    codes = WEO_ALIAS.get(iso, [iso])
    pcs, pops, las = [], [], []
    for c in codes:
        pc, lp = weo(c, "NGDPRPPPPC"), weo(c, "LP")
        g = weo(c, "NGDP_RPCH")
        if lp is None or (pc is None and g is None) or not all(lp[0][y] for y in [LAST_MPD] + EXT_YEARS) or \
                (not (pc and all(pc[0][y] for y in [LAST_MPD] + EXT_YEARS)) and not (g and all(g[0][y] is not None for y in EXT_YEARS))):
            pcs = None; break
        las.append(lp[1])
        popv = lp[0]
        if pc is not None and all(pc[0][y] for y in [LAST_MPD] + EXT_YEARS):
            gdp = {y: pc[0][y] * popv[y] for y in [LAST_MPD] + EXT_YEARS}
            las[-1] = min(las[-1], pc[1])
        else:      # real GDP growth when the per-head PPP series is missing
            gdp = {LAST_MPD: 1.0}
            for y in EXT_YEARS:
                gdp[y] = gdp[y - 1] * (1 + g[0][y] / 100)
            las[-1] = min(las[-1], g[1])
        pcs.append(gdp); pops.append(popv)
    if not pcs:
        continue
    for y in EXT_YEARS:
        gr = sum(p[y] for p in pcs) / sum(p[LAST_MPD] for p in pcs) if len(pcs) > 1 else pcs[0][y] / pcs[0][LAST_MPD]
        pr = sum(p[y] for p in pops) / sum(p[LAST_MPD] for p in pops)
        pop = last["pop"] * pr
        gdp = last.gdppc * last["pop"] * gr
        ext.append({"iso": iso, "year": y, "gdppc": gdp / pop, "pop": pop, "pop_interp": 0, "source": "imf_ext",
                    "imf_est": int(y > min(las))})
E = pd.DataFrame(ext)
# former states: carry forward with the sum of their successors
for a, f in FORMER.items():
    last = P[(P.iso == a) & (P.year == LAST_MPD)].iloc[0]
    s22 = P[(P.iso.isin(f["succ"])) & (P.year == LAST_MPD)]
    have = [s for s in f["succ"] if s in set(E.iso)]
    b = s22[s22.iso.isin(have)]
    for y in EXT_YEARS:
        e = E[(E.iso.isin(have)) & (E.year == y)]
        gr = (e.gdppc * e["pop"]).sum() / (b.gdppc * b["pop"]).sum()
        pr = e["pop"].sum() / b["pop"].sum()
        pop = last["pop"] * pr
        E = pd.concat([E, pd.DataFrame([{"iso": a, "year": y, "gdppc": last.gdppc * last["pop"] * gr / pop, "pop": pop, "pop_interp": 0,
                                         "source": "imf_ext", "imf_est": int(e.imf_est.max())}])])
no_ext = sorted(set(P[P.year == LAST_MPD].iso) - set(E.iso))
print("not carried to", LAST, ":", no_ext)
P = pd.concat([P, E], ignore_index=True).sort_values(["iso", "year"]).reset_index(drop=True)
P["gdp"] = P.gdppc * P["pop"] * 1000          # pop in thousands -> int$

# ---------------- growth of GDP per head ----------------
gr, gf = [], []
for iso, g in P.groupby("iso", sort=False):
    ys, vs = g.year.values, g.gdppc.values
    for y, v in zip(ys, vs):
        lo, hi = y - GROWTH_SPAN[1], y - GROWTH_SPAN[0]
        k = [(abs((y - b) - 10), b, w) for b, w in zip(ys, vs) if lo <= b <= hi]
        if k:
            _, b, w = min(k)
            gr.append(((v / w) ** (1 / (y - b)) - 1) * 100); gf.append(int(b))
        else:
            gr.append(None); gf.append(None)
P["growth"] = gr; P["growth_from"] = gf
P.loc[P.growth.isna(), "growth_from"] = None

# ---------------- world series ----------------
def no_overlap(df):
    """Rows of one year without double counting former states and their successors."""
    out = df
    for a, f in FORMER.items():
        has_a = (df.iso == a).any() and df[df.iso == a]["gdp"].notna().all()
        out = out[~out.iso.isin(f["succ"])] if has_a else out[out.iso != a]
    return out


S = []
for y, g in P.groupby("year"):
    if y < 1820: continue
    g = no_overlap(g.dropna(subset=["gdp"]))
    if y > LAST_MPD:      # countries the IMF does not cover are held at their 2022 level in the world total
        h = P[(P.iso.isin(no_ext)) & (P.year == LAST_MPD)]
        g = pd.concat([g, h])
    S.append({"year": int(y), "sum_gdp": g.gdp.sum(), "sum_pop": g["pop"].sum() * 1000, "n": len(g)})
S = pd.DataFrame(S).set_index("year")
Wb = W.set_index("year")
ratio = {y: Wb.loc[y, "gdp"] / S.loc[y, "sum_gdp"] for y in Wb.index if y >= 1950}
print("world / sum of countries:", {y: round(r, 4) for y, r in ratio.items()})
assert all(0.97 < r < 1.08 for r in ratio.values()), ratio
ry, rv = zip(*sorted(ratio.items()))
world = []
for y in range(1820, LAST + 1):
    if y in Wb.index:
        world.append({"year": y, "gdp": Wb.loc[y, "gdp"], "pop": Wb.loc[y, "pop"] * 1000, "method": "Maddison world estimate"})
    elif y > 1950:
        r = float(np.interp(y, ry, rv))
        pr = (Wb.loc[LAST_MPD, "pop"] * 1000) / S.loc[LAST_MPD, "sum_pop"]
        world.append({"year": y, "gdp": S.loc[y, "sum_gdp"] * r, "pop": S.loc[y, "sum_pop"] * (float(np.interp(y, ry, [Wb.loc[k, "pop"] * 1000 / S.loc[k, "sum_pop"] for k in ry])) if y <= LAST_MPD else pr),
                      "method": "sum of countries scaled to Maddison's world estimate" + (" (IMF growth after 2022)" if y > LAST_MPD else "")})
    else:      # 1820 to 1949: log-linear between Maddison's world benchmarks
        b = Wb.index[Wb.index <= y].max(); a = Wb.index[Wb.index > y].min()
        t = (y - b) / (a - b)
        world.append({"year": y, "gdp": float(np.exp(np.log(Wb.loc[b, "gdp"]) * (1 - t) + np.log(Wb.loc[a, "gdp"]) * t)),
                      "pop": float(np.exp(np.log(Wb.loc[b, "pop"] * 1000) * (1 - t) + np.log(Wb.loc[a, "pop"] * 1000) * t)),
                      "method": "interpolated between Maddison world estimates"})
WD = pd.DataFrame(world).set_index("year")
WD["gdppc"] = WD.gdp / WD["pop"]
WD["coverage_pop"] = [S.loc[y, "sum_pop"] / WD.loc[y, "pop"] if y in S.index else None for y in WD.index]
WD["countries"] = [int(S.loc[y, "n"]) if y in S.index else 0 for y in WD.index]

# ---------------- write ----------------
P["name"] = P.iso.map(NAME); P["region"] = P.iso.map(REGION)
cols = ["iso", "name", "region", "year", "gdppc", "pop", "pop_interp", "gdp", "growth", "growth_from", "source", "imf_est"]
out = P[cols].copy()
out["gdppc"] = out.gdppc.round(1); out["pop"] = out["pop"].round(1); out["gdp"] = (out.gdp / 1e6).round(1)   # gdp in millions
out = out.rename(columns={"gdp": "gdp_millions", "pop": "pop_thousands", "gdppc": "gdppc_2011usd", "growth": "growth_pc_pct"})
out["growth_pc_pct"] = out.growth_pc_pct.round(2)
out.to_csv(f"{DATA}/panel.csv", index=False, float_format="%.10g")
wo = WD.reset_index()[["year", "gdp", "pop", "gdppc", "method", "coverage_pop", "countries"]].copy()
wo["gdp"] = (wo.gdp / 1e6).round(0); wo["pop"] = (wo["pop"] / 1e3).round(0); wo["gdppc"] = wo.gdppc.round(1); wo["coverage_pop"] = wo.coverage_pop.round(4)
wo.rename(columns={"gdp": "gdp_millions", "pop": "pop_thousands", "gdppc": "gdppc_2011usd"}).to_csv(f"{DATA}/world.csv", index=False)
cs = P.groupby("iso").agg(first=("year", "min"), last=("year", "max"), estimates=("year", "size")).reset_index()
cs["name"] = cs.iso.map(NAME); cs["region"] = cs.iso.map(REGION); cs["maddison_name"] = cs.iso.map(names["country"])
cs["former_state"] = cs.iso.isin(list(FORMER)).astype(int)
cs[["iso", "name", "maddison_name", "region", "first", "last", "estimates", "former_state"]].to_csv(f"{DATA}/countries.csv", index=False)
P.to_pickle(f"{WORK}/panel.pkl"); WD.to_pickle(f"{WORK}/world.pkl")
jsave({"names": NAME, "region": REGION, "no_ext": no_ext, "ratio": {str(k): v for k, v in ratio.items()}, "maddison_world_years": W.year.tolist()},
      f"{WORK}/meta.json")
print("panel rows", len(P), "countries", P.iso.nunique(), "| interpolated pop", int(P.pop_interp.sum()), "| ext rows", len(E))
print(WD.loc[[1820, 1870, 1913, 1950, 2000, 2022, 2024], ["gdp", "pop", "gdppc", "coverage_pop", "countries", "method"]].to_string())
