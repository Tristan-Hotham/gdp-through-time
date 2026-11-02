"""House style for static figures: fonts (static Fraunces instances cut from the variable font into WORK), palette,
the map geometry and value helpers shared by the figures and the collage."""
import matplotlib
import matplotlib.patches
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.colors import to_rgb
import pandas as pd
import geopandas as gpd
from common import *

FD = os.path.join(WORK, "fonts"); os.makedirs(FD, exist_ok=True)
if not os.path.exists(f"{FD}/Fraunces-Black.ttf"):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    for w, nm in ((900, "Black"), (700, "Bold")):
        instancer.instantiateVariableFont(TTFont(f"{FONTS}/FrauncesVar.ttf"), {"wght": w, "opsz": 144, "SOFT": 0, "WONK": 0}).save(f"{FD}/Fraunces-{nm}.ttf")
DISP = fm.FontProperties(fname=f"{FD}/Fraunces-Black.ttf"); DISPB = fm.FontProperties(fname=f"{FD}/Fraunces-Bold.ttf")
SERP = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Regular.ttf")
for f in ("IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf"):
    fm.fontManager.addfont(f"{FONTS}/{f}")
MONO = "IBM Plex Mono"
plt.rcParams.update({"font.family": MONO, "font.size": 12, "axes.edgecolor": "#68625A", "axes.labelcolor": "#22201C",
                     "xtick.color": "#68625A", "ytick.color": "#68625A", "hatch.color": "#9c9384", "hatch.linewidth": 0.8})
BG, FG, MUT, RULE, RED = "#F7F2E7", "#22201C", "#68625A", "#E0D6C1", "#B23A2A"
SEA, NODATA = "#E9EEF0", "#D9D2C3"

R = jload(f"{DATA}/results.json")
P = pd.read_pickle(f"{WORK}/panel.pkl"); WD = pd.read_pickle(f"{WORK}/world.pkl")
P = P.merge(WD[["gdp"]].rename(columns={"gdp": "wgdp"}), left_on="year", right_index=True, how="left")
P["share"] = P.gdp / P.wgdp * 100
SER = {i: g.set_index("year") for i, g in P.groupby("iso")}
G = gpd.read_file(f"{DATA}/map_countries.geojson")
ROB = "+proj=robin"
GR = G.to_crs(ROB)

BREAKS = {"gdp": [3e9, 1e10, 3e10, 1e11, 3e11, 1e12, 3e12, 1e13], "pc": [750, 1000, 1500, 2500, 4000, 7000, 12000, 25000],
          "share": [.1, .25, .5, 1, 2, 4, 8, 16], "growth": [-3, -1, 0, 1, 2, 3, 4, 6]}


def val(iso, y, v, carry=CARRY):
    if iso not in SER: return None, None
    s = SER[iso][v].dropna()
    if y in s.index: return float(s.loc[y]), int(y)
    if not len(s): return None, None
    d = np.abs(s.index.values - y); k = d.min()
    if k > carry: return None, None
    yy = s.index.values[d == k].min()
    return float(s.loc[yy]), int(yy)


def colour(v, ind):
    b = BREAKS[ind]; k = 0
    while k < len(b) and v >= b[k]: k += 1
    return (DIV if ind == "growth" else RAMP)[k]


def visible(row, y):
    if row["former"]: return y <= FORMER[row["id"]]["until"]
    for a, f in FORMER.items():
        if (row["m"] in f["succ"] or row["id"] in f.get("extra_poly", [])) and y <= f["until"]: return False
    return True


def draw_map(ax, y, ind="share", edge="#FFFCF4", lw=0.25):
    """Choropleth for year y on a Robinson projection: colour, dotted if the nearest estimate, hatched if none."""
    ax.set_facecolor(SEA)
    rows = GR[[visible(r, y) for _, r in GR.iterrows()]]
    cols, hatch, near = [], [], []
    for _, r in rows.iterrows():
        v, yy = val(r["m"], y, {"pc": "gdppc"}.get(ind, ind)) if r["m"] else (None, None)
        if v is None: cols.append(NODATA); hatch.append(True); near.append(False)
        else: cols.append(colour(v, ind)); hatch.append(False); near.append(yy != y)
    rows = rows.assign(c=cols, h=hatch, n=near)
    rows[~rows.h].plot(ax=ax, color=rows[~rows.h].c, edgecolor=edge, linewidth=lw)
    if rows.h.any():
        rows[rows.h].plot(ax=ax, facecolor=NODATA, edgecolor=edge, linewidth=lw, hatch="////")
    if rows.n.any():
        rows[rows.n].plot(ax=ax, facecolor="none", edgecolor="#ffffff", linewidth=0, hatch="...")
    ax.set_xlim(-1.42e7, 1.72e7); ax.set_ylim(-6.3e6, 8.7e6); ax.set_axis_off()
    ax.add_patch(matplotlib.patches.Rectangle((-1.42e7, -6.3e6), 3.14e7, 1.5e7, color=SEA, zorder=-10))
    return rows


def legend_items(ind):
    b = BREAKS[ind]; cols = DIV if ind == "growth" else RAMP
    f = {"share": lambda v: f"{v:g}%", "pc": lambda v: f"${v:,.0f}", "gdp": lambda v: f"${v / 1e9:,.0f} bn" if v < 1e12 else f"${v / 1e12:,.0f} tn",
         "growth": lambda v: f"{v:+g}%"}[ind]
    labs = [f"under {f(b[0])}"] + [f"{f(b[k])} to {f(b[k + 1])}" for k in range(len(b) - 1)] + [f"{f(b[-1])} or more"]
    return list(zip(cols, labs))
