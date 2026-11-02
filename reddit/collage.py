"""Reddit collage (r/dataisbeautiful style, light background): reddit/wealth_of_nations.png, 2400 x 3200 px.
Run after code/01 to 06. Every number comes from data/results.json."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code"))
from figstyle import *
from matplotlib.patches import Patch
import matplotlib.patheffects as pe
from pyproj import Transformer

TR = Transformer.from_crs("EPSG:4326", ROB, always_xy=True)
L = R["meta"]["last"]
HALO = [pe.withStroke(linewidth=4, foreground="white")]
OUT = os.path.join(ROOT, "reddit", "wealth_of_nations.png")

fig = plt.figure(figsize=(12, 16), dpi=200, facecolor=BG)
fig.text(0.04, 0.975, "Half the world, then a tenth, then a third", fontproperties=DISP, fontsize=37, color=FG, va="top")
ci = R["china_india"]
fig.text(0.04, 0.935, f"China and India's share of world output: {ci['1820']:.0f}% in 1820, {ci['1950']:.0f}% in 1950, {ci[str(L)]:.0f}% in {L}.\n"
         "Each country's share of world GDP (purchasing power parity), on today's borders.", fontsize=13.5, color=FG, va="top", linespacing=1.55)

# labels: (iso, lon, lat of the label on open sea)
LAB = {1820: [("CHN", 158, 12), ("IND", 72, -14), ("GBR", -38, 60), ("FRA", -40, 36), ("USA", -142, 26), ("JPN", 168, 34)],
       L: [("CHN", 158, 12), ("USA", -142, 26), ("IND", 72, -14), ("JPN", 168, 34), ("RUS", 128, 79), ("DEU", -40, 55), ("BRA", -12, -18)]}
for k, y in enumerate((1820, L)):
    ax = fig.add_axes([0.02, 0.583 - k * 0.307, 0.96, 0.295])
    draw_map(ax, y, "share", lw=0.3)
    ax.text(0.015, 0.06, str(y), transform=ax.transAxes, fontproperties=DISP, fontsize=40, color=FG)
    for iso, lo, la in LAB[y]:
        v, yy = val(iso, y, "share")
        row = G[G.m == iso].iloc[0]
        x0, y0 = TR.transform(row["lx"], row["ly"]); x1, y1 = TR.transform(lo, la)
        nm = NAMES_SHORT.get(jload(f"{WORK}/meta.json")["names"][iso], jload(f"{WORK}/meta.json")["names"][iso])
        ax.plot([x0, x1], [y0, y1], color=FG, lw=0.9, zorder=5)
        ax.scatter([x0], [y0], s=12, color=FG, zorder=6)
        ax.text(x1, y1, f"{nm} {v:.1f}%" + (f" ({yy})" if yy != y else ""), fontsize=13, fontweight="medium", color=FG, ha="center", va="center",
                zorder=7, bbox=dict(fc="white", ec="none", pad=2.5, alpha=0.95))
it = legend_items("share")
fig.legend([Patch(fc=c, ec="none") for c, _ in it] + [Patch(fc=NODATA, hatch="////", ec="#9c9384", lw=0)],
           [l for _, l in it] + ["no estimate"], loc="center", ncol=5, frameon=False, fontsize=11, bbox_to_anchor=(0.5, 0.262), handlelength=1.3,
           title="Share of world GDP", title_fontsize=11.5)

# line chart
ax = fig.add_axes([0.08, 0.128, 0.6, 0.095]); ax.set_facecolor(BG)
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.grid(axis="y", color=RULE); ax.set_axisbelow(True)
west = [(int(y), v) for y, v in R["west_share"].items()]
for iso, nm in [("CHN", "China"), ("IND", "India"), ("USA", "United States"), ("GBR", "United Kingdom"), ("JPN", "Japan")]:
    s = SER[iso]["share"].dropna(); s = s[s.index >= 1820]
    ax.plot(s.index, s.values, color=SERIES_COL[iso], lw=2, label=nm)
ax.plot([w[0] for w in west], [w[1] for w in west], color=FG, lw=1.3, ls=(0, (4, 3)), label="Western Europe and offshoots")
ax.plot([int(y) for y in ci], list(ci.values()), color=RED, lw=1.3, ls=(0, (1, 2)), label="China and India together")
ax.set_xlim(1820, L); ax.set_ylim(0, 62); ax.yaxis.set_major_formatter(lambda v, p: f"{v:.0f}%"); ax.tick_params(labelsize=10.5)
ax.set_title("Share of world GDP, 1820 to " + str(L), loc="left", fontproperties=DISPB, fontsize=16)
ax.legend(frameon=False, fontsize=9.2, loc="upper left", ncol=4, bbox_to_anchor=(-0.02, -0.2), columnspacing=1.2, handlelength=1.6)

# stats
O, T, Gp = R["overtake"], R["takeoff"], R["gap"]
LRr = R["longrun"]
stats = [(f"{LRr['ci_ad1']:.0f}%", "India and China, AD 1\n(Maddison's guesses)", "#6E5A7E"),
         (str(O["usa_gbr_gdp"]["first"]), "the US economy passes\nBritain's for good", "#2F5FA7"),
         (str(O["chn_usa_gdp"]["first"]), "China passes the US\nagain (at PPP)", RED),
         (f"{T['kor']['x_60_last']:.0f}x", f"South Korea's GDP per\nhead, 1960 to {L}", "#2E8A6E"),
         (f"{Gp[str(L)]['ratio']:.0f}x", f"richest over poorest\nper head, {L}\n({Gp['1820']['ratio']:.0f}x in 1820)", "#B07A12")]
for k, (b, t, c) in enumerate(stats):
    yy = 0.232 - k * 0.0365
    fig.text(0.72, yy, b, fontproperties=DISP, fontsize=24, color=c, va="top")
    fig.text(0.835, yy - 0.002, t, fontsize=9.2, color=FG, va="top", linespacing=1.35)

fig.text(0.04, 0.012, "Source: Maddison Project Database 2023 (Bolt and van Zanden 2024, CC BY 4.0), GDP in 2011 international dollars;\n"
         "2023 to 2024 carried forward with IMF World Economic Outlook (October 2025) growth. Hatched: no estimate.\n"
         "India 1820 uses its 1821 estimate. Borders: Natural Earth. Analysis and chart: Tristan Hotham, with Python and matplotlib",
         fontsize=8.8, color=MUT, linespacing=1.5)
fig.text(0.96, 0.014, "maps.tristanhotham.com/\ngdp-through-time", fontsize=11, linespacing=1.4, color=RED, ha="right", fontweight="medium")
fig.savefig(OUT, dpi=200, facecolor=BG); plt.close(fig)
from PIL import Image
print(OUT, Image.open(OUT).size)
