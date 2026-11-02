"""Static figures: header.png (1200 x 630), blog figures release/blog/b_*.png (1800 px wide) and paper figures
release/paper/f_*.png. All numbers come from data/results.json or the panel built in step 01."""
from matplotlib.patches import Patch, Rectangle
from figstyle import *

BLOG = os.path.join(ROOT, "release", "blog"); PAP = os.path.join(ROOT, "release", "paper")
for d in (BLOG, PAP): os.makedirs(d, exist_ok=True)


def save(fig, name, paper=True, blog=True):
    if blog: fig.savefig(f"{BLOG}/b_{name}.png", dpi=150, facecolor=fig.get_facecolor())
    if paper: fig.savefig(f"{PAP}/f_{name}.png", dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)


def title(fig, t, sub, y=0.965):
    fig.text(0.04, y, t, fontproperties=DISP, fontsize=27, color=FG, va="top")
    fig.text(0.04, y - 0.075, sub, fontsize=12.5, color=MUT, va="top")


def foot(fig, s="Source: Maddison Project Database 2023 (Bolt and van Zanden); 2023 to 2024 with IMF WEO growth. maps.tristanhotham.com/gdp-through-time"):
    fig.text(0.04, 0.02, s, fontsize=9.5, color=MUT)


def axstyle(ax):
    ax.set_facecolor(BG)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=RULE, lw=0.8); ax.set_axisbelow(True)
    ax.tick_params(labelsize=11)


def series(iso, v, lo=1820):
    s = SER[iso][v].dropna(); return s[s.index >= lo]


def plot_gapped(ax, s, col, lw=2.2, gap=45, label=None, dots_before=1950):
    xs, ys = list(s.index), list(s.values)
    seg_x, seg_y = [xs[0]], [ys[0]]
    for x, y in zip(xs[1:], ys[1:]):
        if x - seg_x[-1] > gap:
            ax.plot(seg_x, seg_y, color=col, lw=lw); seg_x, seg_y = [], []
        seg_x.append(x); seg_y.append(y)
    ax.plot(seg_x, seg_y, color=col, lw=lw, label=label)
    iso = [x for i, x in enumerate(xs) if x < dots_before and (i == 0 or x - xs[i - 1] > 1) and (i == len(xs) - 1 or xs[i + 1] - x > 1)]
    if iso: ax.scatter(iso, [s.loc[x] for x in iso], s=14, color=col, zorder=3)


L = R["meta"]["last"]

# ---------------- 1. maps: share of world GDP at four dates ----------------
fig = plt.figure(figsize=(12, 8.2), facecolor=BG)
title(fig, "Share of world GDP at four dates", "Present-day borders; hatched: no estimate; dotted: nearest estimate within 10 years (India 1821 for 1820)")
for k, y in enumerate((1820, 1913, 1950, L)):
    ax = fig.add_axes([0.02 + (k % 2) * 0.49, 0.5 - (k // 2) * 0.34, 0.47, 0.32])
    draw_map(ax, y, "share")
    ax.text(0.02, 0.06, str(y), transform=ax.transAxes, fontproperties=DISP, fontsize=22, color=FG)
it = legend_items("share")
fig.legend([Patch(fc=c, ec="none") for c, _ in it] + [Patch(fc=NODATA, hatch="////", ec="#9c9384", lw=0)], [l for _, l in it] + ["no estimate"],
           loc="lower center", ncol=5, frameon=False, fontsize=9.5, bbox_to_anchor=(0.5, 0.03), handlelength=1.2)
foot(fig, "Source: Maddison Project Database 2023 (Bolt and van Zanden). maps.tristanhotham.com/gdp-through-time")
save(fig, "maps")

# ---------------- 2. share lines ----------------
fig = plt.figure(figsize=(12, 7), facecolor=BG)
title(fig, "Half the world, then a tenth, then a third", "Share of world GDP (%), 2011 international dollars at purchasing power parity")
ax = fig.add_axes([0.07, 0.12, 0.88, 0.7]); axstyle(ax)
KS = [("CHN", "China"), ("IND", "India"), ("USA", "United States"), ("GBR", "United Kingdom"), ("JPN", "Japan"), ("DEU", "Germany")]
for iso, nm in KS:
    s = series(iso, "share"); plot_gapped(ax, s, SERIES_COL[iso], label=nm)
ci = [(y, R["china_india"][str(y)]) for y in (1820, 1870, 1913, 1950, 1973, 2000, L)]
ax.plot([c[0] for c in ci], [c[1] for c in ci], color=RED, lw=1.2, ls=(0, (4, 3)), label="China and India together (benchmark years)")
ax.set_xlim(1820, L); ax.set_ylim(0, 47); ax.yaxis.set_major_formatter(lambda v, p: f"{v:.0f}%")
ax.legend(frameon=False, fontsize=10.5, loc="upper center", ncol=3)
foot(fig); save(fig, "share")

# ---------------- 3. top 10 shares, 1820 and last ----------------
fig = plt.figure(figsize=(12, 7), facecolor=BG)
title(fig, f"The ten largest economies, 1820 and {L}", "Share of world GDP (%); India 1820 is its 1821 estimate")
for k, y in enumerate(("1820", str(L))):
    ax = fig.add_axes([0.13 + k * 0.48, 0.1, 0.33, 0.64]); ax.set_facecolor(BG)
    t = R["top"][y][:10]
    ax.barh(range(10)[::-1], [r["share"] for r in t], color=[SERIES_COL.get(r["iso"], "#83BD84") for r in t])
    for i, r in enumerate(t):
        ax.text(-0.6, 9 - i, NAMES_SHORT.get(r["name"], r["name"]), ha="right", va="center", fontsize=11)
        ax.text(r["share"] + 0.4, 9 - i, f"{r['share']:.1f}%", va="center", fontsize=10.5, color=MUT)
    ax.set_xlim(0, 32); ax.set_yticks([]); ax.set_xticks([])
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_title(y, fontproperties=DISP, fontsize=22, loc="left", x=-0.3)
foot(fig); save(fig, "top")

# ---------------- 4. GDP per head take-offs ----------------
fig = plt.figure(figsize=(12, 7), facecolor=BG)
title(fig, "Take-offs", "GDP per head, 2011 international dollars, logarithmic scale")
ax = fig.add_axes([0.08, 0.12, 0.87, 0.7]); axstyle(ax)
for iso, nm in [("USA", "United States"), ("GBR", "United Kingdom"), ("JPN", "Japan"), ("KOR", "South Korea"), ("CHN", "China"), ("IND", "India")]:
    plot_gapped(ax, series(iso, "gdppc", 1870), SERIES_COL[iso], label=nm)
ax.set_yscale("log"); ax.set_xlim(1870, L); ax.set_ylim(400, 80000)
ax.set_yticks([500, 1000, 2000, 5000, 10000, 20000, 50000]); ax.yaxis.set_major_formatter(lambda v, p: f"${v:,.0f}"); ax.minorticks_off()
ax.legend(frameon=False, fontsize=10.5, loc="upper left", ncol=2)
foot(fig); save(fig, "pc")

# ---------------- 5. the gap ----------------
fig = plt.figure(figsize=(12, 7), facecolor=BG)
title(fig, "How many times richer", "GDP per head, richest over poorest country and 90th over 10th percentile (1 million people or more)")
ax = fig.add_axes([0.08, 0.12, 0.87, 0.7]); axstyle(ax)
gs = np.array(R["gap_series"], dtype=float)
ax.plot(gs[:, 0], gs[:, 2], color=RED, lw=2, label="Richest over poorest")
ax.plot(gs[:, 0], gs[:, 3], color="#2F5FA7", lw=2, label="90th over 10th percentile")
ax.set_yscale("log"); ax.set_xlim(1820, L); ax.set_yticks([2, 5, 10, 20, 50, 100, 200]); ax.yaxis.set_major_formatter(lambda v, p: f"{v:g}x"); ax.minorticks_off()
for y in ("1820", "1913", "1950", str(L)):
    g = R["gap"][y]; ax.annotate(f"{g['richest']} / {g['poorest']}", (int(y), g["ratio"]), xytext=(0, 9), textcoords="offset points", fontsize=8.5, color=MUT,
                                 ha="left" if y == "1820" else "right" if y == str(L) else "center")
ax.legend(frameon=False, fontsize=10.5, loc="upper left", bbox_to_anchor=(0.0, 0.9))
foot(fig); save(fig, "gap")

# ---------------- 6. coverage ----------------
fig = plt.figure(figsize=(12, 6.6), facecolor=BG)
title(fig, "How much the record covers", "Countries with their own estimate of GDP per head in each year (Maddison Project Database 2023)")
ax = fig.add_axes([0.08, 0.13, 0.87, 0.68]); axstyle(ax)
mp = P[P.source == "mpd"]
shown = []
for y, g in mp.groupby("year"):
    keep = set(g.iso)
    for a, f in FORMER.items():
        keep -= set(f["succ"]) if y <= f["until"] else {a}
    shown.append((y, len(keep)))
sh = np.array(shown)
pos = np.array([year_pos(y) for y in sh[:, 0]])
ax.vlines(pos, 0, sh[:, 1], color="#7c705d", lw=1.4)
ticks = [1, 1000, 1500, 1700, 1820, 1870, 1913, 1950, 2000, LAST_MPD]
ax.set_xticks([year_pos(t) for t in ticks]); ax.set_xticklabels(["AD 1" if t == 1 else str(t) for t in ticks], fontsize=10)
ax.set_xlim(-0.01, year_pos(LAST_MPD) + 0.01); ax.set_ylabel("countries")
ax.text(year_pos(1), R["data"]["ad1_n"] + 6, f"{R['data']['ad1_n']}", ha="center", fontsize=10, color=MUT)
ax.text(0.01, 0.92, "The time axis is uneven, as on the interactive map.", transform=ax.transAxes, fontsize=10, color=MUT)
foot(fig, "Source: Maddison Project Database 2023 (Bolt and van Zanden). maps.tristanhotham.com/gdp-through-time")
save(fig, "coverage")

# ---------------- 7. per head map, last year (paper only) ----------------
fig = plt.figure(figsize=(12, 6.8), facecolor=BG)
title(fig, f"GDP per head, {L}", "2011 international dollars; Maddison 2022 carried forward with IMF growth")
ax = fig.add_axes([0.02, 0.12, 0.96, 0.72]); draw_map(ax, L, "pc")
it = legend_items("pc")
fig.legend([Patch(fc=c, ec="none") for c, _ in it] + [Patch(fc=NODATA, hatch="////", ec="#9c9384", lw=0)], [l for _, l in it] + ["no estimate"],
           loc="lower center", ncol=5, frameon=False, fontsize=9.5, bbox_to_anchor=(0.5, 0.04), handlelength=1.2)
foot(fig); save(fig, "pcmap", blog=False)

# ---------------- 8. largest economy bands (paper only) ----------------
fig = plt.figure(figsize=(12, 2.6), facecolor=BG)
ax = fig.add_axes([0.04, 0.3, 0.92, 0.45]); ax.set_facecolor(BG)
for s in R["largest_seq"]:
    ax.add_patch(Rectangle((s["from"], 0), s["to"] + 1 - s["from"], 1, color=SERIES_COL[s["iso"]]))
    if s["to"] - s["from"] > 20: ax.text((s["from"] + s["to"] + 1) / 2, 0.5, f"{s['name']} {s['from']} to {s['to']}", ha="center", va="center", color="white", fontsize=11)
ax.set_xlim(1820, L + 1); ax.set_ylim(0, 1); ax.set_yticks([]); [sp.set_visible(False) for sp in ax.spines.values()]
fig.text(0.04, 0.88, "Largest economy by year (estimates within 10 years)", fontproperties=DISPB, fontsize=15)
save(fig, "lead", blog=False)


# ---------------- 9. ten thousand years (world) ----------------
WLc = pd.read_csv(f"{DATA}/world_longrun.csv")
KN = [(-10000, 0), (1, .38), (1500, .56), (1820, .66), (L, 1)]
xp = lambda y: np.interp(y, [k[0] for k in KN], [k[1] for k in KN])
fig = plt.figure(figsize=(12, 8.4), facecolor=BG)
title(fig, "Ten thousand years of the world economy", "World GDP per head (2011 $, older series linked at 1820) and population; dashed: lines between estimates")
ax1 = fig.add_axes([0.09, 0.5, 0.86, 0.33]); ax2 = fig.add_axes([0.09, 0.1, 0.86, 0.33])
for ax in (ax1, ax2): axstyle(ax); ax.set_yscale("log"); ax.minorticks_off()
d = WLc.dropna(subset=["gdppc_delong_linked"]); d = d[d.year <= 1800]
ax1.plot(xp(d.year), d.gdppc_delong_linked, ls="--", marker="o", ms=3, color="#B07A12", lw=1.5, label="De Long (1998)")
d = WLc.dropna(subset=["gdppc_maddison2010_linked"])
ax1.plot(xp(d.year), d.gdppc_maddison2010_linked, ls="--", marker="o", ms=4, color="#2F5FA7", lw=1.5, label="Maddison (2010)")
w = WD.loc[1820:L]
ax1.plot(xp(w.index), w.gdppc, color=RED, lw=2.2, label="Maddison Project 2023")
ax1.set_yticks([500, 1000, 2000, 5000, 10000, 20000]); ax1.yaxis.set_major_formatter(lambda v, p: f"${v:,.0f}")
ax1.legend(frameon=False, fontsize=10.5, loc="upper left")
d = WLc.dropna(subset=["pop_hyde_lower"])
ax2.fill_between(xp(d.year), d.pop_hyde_lower, d.pop_hyde_upper, color="#2E8A6E", alpha=0.16, lw=0, label="HYDE 3.2.1 low to high")
d = WLc.dropna(subset=["pop_hyde"]); ax2.plot(xp(d.year), d.pop_hyde, ls="--", color="#2E8A6E", lw=1.6, marker="o", ms=2.5, label="HYDE 3.2.1 central")
d = WLc.dropna(subset=["pop_mcevedy_jones"]); ax2.plot(xp(d.year), d.pop_mcevedy_jones, ls=":", color="#6E5A7E", lw=1.6, marker="o", ms=2.5, label="McEvedy and Jones (1978)")
ax2.plot(xp(w.index), w["pop"] / 1e6, color=RED, lw=2.2, label="Maddison Project 2023")
ax2.set_yticks([1, 10, 100, 1000, 10000]); ax2.yaxis.set_major_formatter(lambda v, p: f"{v / 1000:,.0f} bn" if v >= 1000 else f"{v:,.0f} m")
ax2.legend(frameon=False, fontsize=10, loc="upper left")
ticks = [-10000, -5000, -2000, 1, 1000, 1500, 1820, 1950, 2000]
for ax in (ax1, ax2):
    ax.set_xticks([xp(t) for t in ticks]); ax.set_xticklabels([yr(t) if t < 1000 else str(t) for t in ticks], fontsize=10); ax.set_xlim(0, 1)
foot(fig, "Sources: De Long 1998; Maddison 2010; HYDE 3.2.1; McEvedy and Jones 1978 (via Roodman 2020); Maddison Project 2023")
save(fig, "longrun")

# ---------------- 10. Maddison's regions, AD 1 and 1700 ----------------
RGd = gpd.read_file(f"{DATA}/map_regions_maddison2010.geojson").to_crs(ROB)
RGN = pd.read_csv(f"{DATA}/regions_maddison2010.csv")
fig = plt.figure(figsize=(12, 5.8), facecolor=BG)
title(fig, "Before the nations: Maddison's regions", "Share of world GDP, Maddison (2010); striped: many values are assumed near subsistence", y=0.96)
for k, y in enumerate((1, 1700)):
    ax = fig.add_axes([0.02 + k * 0.49, 0.17, 0.47, 0.64]); ax.set_axis_off()
    ax.add_patch(matplotlib.patches.Rectangle((-1.42e7, -6.3e6), 3.14e7, 1.5e7, color=SEA, zorder=-10))
    sh = RGN[RGN.year == y].set_index("region").share_world_pct
    RGd.assign(c=[colour(sh[r], "share") for r in RGd.r]).plot(ax=ax, color=RGd.assign(c=[colour(sh[r], "share") for r in RGd.r]).c, edgecolor="white", lw=0.4)
    RGd.plot(ax=ax, facecolor="none", edgecolor="white", lw=0, hatch="//", alpha=0.6)
    for _, rr in RGd.iterrows():
        lx, ly = {"WEUR": (-5, 50), "WOFF": (-100, 42), "EEUR": (30, 47), "FSU": (85, 62), "LATAM": (-60, -12), "CHN": (103, 33), "IND": (78, 20),
                  "JPN": (150, 40), "OASIA": (115, 0), "WASIA": (45, 28), "AFR": (20, 3)}[rr.r]
        from pyproj import Transformer
        X_, Y_ = Transformer.from_crs("EPSG:4326", ROB, always_xy=True).transform(lx, ly)
        ax.text(X_, Y_, f"{sh[rr.r]:.0f}%" if sh[rr.r] >= 1 else f"{sh[rr.r]:.1f}%", ha="center", va="center", fontsize=10.5, fontweight="medium", bbox=dict(fc="white", ec="none", pad=1.5, alpha=0.85))
    ax.set_xlim(-1.42e7, 1.72e7); ax.set_ylim(-6.3e6, 8.7e6)
    ax.text(0.02, 0.05, yr(y), transform=ax.transAxes, fontproperties=DISP, fontsize=22, color=FG)
it = legend_items("share")
fig.legend([Patch(fc=c, ec="none") for c, _ in it], [l for _, l in it], loc="lower center", ncol=5, frameon=False, fontsize=9.5, bbox_to_anchor=(0.5, 0.045), handlelength=1.2)
foot(fig, "Source: Maddison (2010), via Roodman (2020). Greenland (in his Western Europe) not drawn. maps.tristanhotham.com/gdp-through-time")
save(fig, "regions")

# ---------------- header ----------------
fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=BG)
fig.text(0.04, 0.89, "DATA STUDY · ECONOMIC HISTORY", fontsize=13, color=RED, fontweight="medium")
fig.text(0.04, 0.80, "The Wealth", fontproperties=DISP, fontsize=54, color=FG, va="top")
fig.text(0.04, 0.665, "of Nations,", fontproperties=DISP, fontsize=54, color=FG, va="top")
fig.text(0.04, 0.53, "Mapped", fontproperties=DISP, fontsize=54, color=RED, va="top")
ci = R["china_india"]
fig.text(0.04, 0.36, f"China and India's share of\nworld output: {ci['1820']:.0f}% in 1820,\n{ci['1950']:.0f}% in 1950, {ci[str(L)]:.0f}% in {L}.", fontsize=14.5, color=FG, va="top", linespacing=1.5)
fig.text(0.04, 0.06, "Dr Tristan Hotham · maps.tristanhotham.com/gdp-through-time", fontsize=11.5, color=MUT)
for k, y in enumerate((1820, 1950, L)):
    ax = fig.add_axes([0.47, 0.67 - k * 0.315, 0.51, 0.3]); draw_map(ax, y, "share", lw=0.15)
    ax.text(0.0, 0.05, str(y), transform=ax.transAxes, fontsize=12, color="white", fontweight="medium", bbox=dict(fc=RED, ec="none", pad=3))
fig.savefig(os.path.join(ROOT, "header.png"), dpi=100, facecolor=BG); plt.close(fig)
from PIL import Image
assert Image.open(os.path.join(ROOT, "header.png")).size == (1200, 630)
print("figures done:", sorted(os.listdir(BLOG)), sorted(f for f in os.listdir(PAP) if f.endswith(".png")))
