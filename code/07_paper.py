"""Build the paper: fill code/paper_template.tex from data/results.json, add tables, compile with xelatex.
Output: release/paper/Hotham_WealthOfNations.pdf and .tex (figures f_*.png beside them). The DOI stays a placeholder."""
import subprocess
import pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
P = pd.read_pickle(f"{WORK}/panel.pkl"); WD = pd.read_pickle(f"{WORK}/world.pkl")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_WealthOfNations"
tex = lambda s: str(s).replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")

# statements made in words in the paper only
gs = R["gap_series"]
peak = max(gs, key=lambda r: r[3])
assert 1995 <= peak[0] <= 2010, peak                                          # p90/p10 "high ... around 2000"
assert R["gap"]["1950"]["n"] > 1.6 * max(r[1] for r in gs if r[0] < 1950)    # the 1950 jump in coverage
assert R["fastest"][7]["iso"] == "CHN"
assert R["share"]["DEU"]["1820"] < R["share"]["FRA"]["1820"] < R["share"]["GBR"]["1820"]


def tfmt(v, f):
    if v is None: return "none"
    if f == "int": return f"{int(round(float(v))):,}"
    if f == "pc": return f"{round(float(v))}\\%"
    if f == "pc1": return f"{float(v):.1f}\\%"
    if f in ("f1", "x1"): return f"{float(v):.1f}"
    if f == "f0": return f"{float(v):.0f}"
    if f == "x": return f"{round(float(v)):,}"
    if f == "usd": return f"\\${round(float(v)):,}"
    return tex(str(v))


D = R["data"]
mp = P[P.source == "mpd"]
rows = ""
for y in (1, 1000, 1500, 1600, 1700, 1820, 1870, 1913, 1950, 1973, 2000, LAST_MPD, LAST):
    a = P[P.year == y]
    w = f"{WD.loc[y, 'gdp'] / 1e12:.1f} & {WD.loc[y, 'gdppc']:,.0f}" if y in WD.index else "& "
    cov = f"{R['data']['coverage'][str(y)]:.1f}" if str(y) in R["data"]["coverage"] else ""
    rows += f"{yr(y)} & {len(a)} & {int(a.gdp.notna().sum())} & {cov} & {w}\\\\\n"
TCOV = ("\\begin{table}[tbp]\\centering\\small\\caption{Coverage at selected years: units with an estimate of GDP per head, with GDP (population known or interpolated), "
        "share of world population in units with GDP (\\%), and world GDP (trillion 2011 int.\\ \\$) and GDP per head. Units include former states and their successors.}\\label{tab:cov}"
        "\\begin{tabular}{lrrrrr}\\toprule Year & GDP per head & GDP & Population covered & World GDP & World per head\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")

T = R["top"]
rows = ""
for i in range(10):
    rows += " & ".join(f"{tex(NAMES_SHORT.get(T[y][i]['name'], T[y][i]['name']))} & {T[y][i]['share']:.1f}" for y in ("1820", "1913", "1950", str(LAST))) + "\\\\\n"
TTOP = ("\\begin{table}[tbp]\\centering\\small\\caption{The ten largest economies by share of world GDP (\\%) at four dates (nearest estimate within ten years).}\\label{tab:top}"
        "\\begin{tabular}{lrlrlrlr}\\toprule \\multicolumn{2}{c}{1820} & \\multicolumn{2}{c}{1913} & \\multicolumn{2}{c}{1950} & \\multicolumn{2}{c}{" + str(LAST) + "}\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")

O = R["overtake"]
ON = [("usa_gbr_gdp", "United States passes United Kingdom", "GDP"), ("usa_gbr_pc", "United States passes United Kingdom", "GDP per head"),
      ("usa_chn_gdp", "United States passes China", "GDP"), ("chn_usa_gdp", "China passes United States (since 1950)", "GDP"),
      ("ind_gbr_gdp", "India passes United Kingdom (since 1900)", "GDP"), ("ind_jpn_gdp", "India passes Japan (since 1950)", "GDP"),
      ("jpn_gbr_pc", "Japan passes United Kingdom", "GDP per head"), ("kor_jpn_pc", "South Korea passes Japan", "GDP per head"),
      ("kor_gbr_pc", "South Korea passes United Kingdom", "GDP per head")]
TOVER = ("\\begin{table}[tbp]\\centering\\small\\caption{Crossings: the first year in which one country's value exceeded another's, and the first year from which it stayed ahead to " + str(LAST) +
         " (none: fell behind again), judged on years in which both have their own estimate.}\\label{tab:over}"
         "\\begin{tabular}{llrrr}\\toprule Crossing & Measure & First & Ahead since & Years compared\\\\\\midrule\n" +
         "".join(f"{a} & {m} & {O[k]['first']} & {O[k]['for_good'] if O[k]['for_good'] else 'none'} & {O[k]['years_compared']}\\\\\n" for k, a, m in ON) + "\\bottomrule\\end{tabular}\\end{table}")
TFAST = ("\\begin{table}[tbp]\\centering\\small\\caption{Best 25-year growth of GDP per head since 1950, countries of ten million people or more (one spell per country).}\\label{tab:fast}"
         "\\begin{tabular}{lrrr}\\toprule Country & Years & Growth (\\% a year) & Multiple\\\\\\midrule\n" +
         "".join(f"{tex(f['name'])} & {f['from']} to {f['to']} & {f['growth']:.1f} & {f['x']:.1f}\\\\\n" for f in R["fastest"]) + "\\bottomrule\\end{tabular}\\end{table}")
TGAP = ("\\begin{table}[tbp]\\centering\\small\\caption{Richest and poorest countries by GDP per head (2011 int.\\ \\$), countries of a million people or more with their own estimate.}\\label{tab:gap}"
        "\\begin{tabular}{rrlrlrrr}\\toprule Year & Countries & Richest & & Poorest & & Ratio & p90/p10\\\\\\midrule\n" +
        "".join(f"{g['year']} & {g['n']} & {tex(NAMES_SHORT.get(g['richest'], g['richest']))} & {g['richest_pc']:,.0f} & {tex(NAMES_SHORT.get(g['poorest'], g['poorest']))} & {g['poorest_pc']:,.0f} & {g['ratio']:.1f} & {g['p90_p10']:.1f}\\\\\n"
                for g in R["gap"].values()) + "\\bottomrule\\end{tabular}\\end{table}")
TP = R["top_pc"]
rows = "".join(" & ".join(f"{tex(TP[y][i]['name']) if i < len(TP[y]) else ''} & {TP[y][i]['gdppc']:,.0f}" if i < len(TP[y]) else " & " for y in ("1700", "1820", "1913")) + "\\\\\n" for i in range(10))
TPRE = ("\\begin{table}[tbp]\\centering\\small\\caption{Highest GDP per head (2011 int.\\ \\$) among countries of a million people or more with an estimate within ten years, 1700, 1820 and 1913.}\\label{tab:pre}"
        "\\begin{tabular}{lrlrlr}\\toprule \\multicolumn{2}{c}{1700} & \\multicolumn{2}{c}{1820} & \\multicolumn{2}{c}{1913}\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")

# sources sheet of the database, for the countries drawn individually
src = pd.read_excel(MPD_XLSX, sheet_name="Sources", header=None)
SRC, cur = {}, None
for _, r in src.iterrows():
    if isinstance(r[0], str) and re.fullmatch(r"[A-Z]{3}", r[0].strip()):
        cur = r[0].strip(); SRC[cur] = []
    elif cur and pd.notna(r[2]):
        SRC[cur].append((str(r[1]) if pd.notna(r[1]) else "", str(r[2])))
clean = lambda s: tex(dash(re.sub(r"\s+", " ", s.replace("“", "''").replace("”", "''").replace('"', "''").replace("‘", "'").replace("’", "'")).strip()))
rows = ""
for iso in ("CHN", "IND", "USA", "GBR", "JPN", "KOR", "DEU", "NLD"):
    seen = set()
    for per, s in SRC.get(iso, []):
        if s in seen: continue
        seen.add(s)
        rows += f"{iso} & {clean(per)} & {clean(s)}\\\\\n"
TSRC = ("\\begin{longtable}{lp{2.2cm}p{11cm}}\\caption{Sources of the long series for the countries shown, as listed in the Maddison Project Database 2023 sources sheet "
        "(recent years: national accounts and the Conference Board Total Economy Database).}\\label{tab:src}\\\\\\toprule Code & Years & Source\\\\\\midrule\\endhead\n" + rows + "\\bottomrule\\end{longtable}")

LRr = R["longrun"]
rows = ""
for y in ("-10000", "-5000", "-3000", "-2000", "-1000", "1", "1000", "1500", "1820"):
    q = LRr["pop"][y]
    rng = f"{q['lo']:,.1f} to {q['hi']:,.0f}" if q["lo"] else ""
    pcd = LRr["pc_delong"].get(y if y != "1820" else "1800")
    pcm = LRr["m2010"].get(y, {}).get("pc")
    rows += f"{yr(int(y))} & {q['hyde']:,.1f} & {rng} & {f'{q["mj"]:,.0f}' if q['mj'] is not None else ''} & {f'{pcd:,.0f}' if pcd is not None else ''}{'*' if y == '1820' else ''} & {f'{pcm:,.0f}' if pcm is not None else ''}\\\\\n"
TLR = ("\\begin{table}[tbp]\\centering\\small\\caption{The very long run: world population (million) from HYDE 3.2.1 (central, low to high) and McEvedy and Jones, and world GDP per head (2011 int.\\ \\$, linked at 1820) from De Long (1998) and Maddison (2010). *De Long 1800.}\\label{tab:lr}"
       "\\begin{tabular}{lrrrrr}\\toprule Year & HYDE & HYDE range & McEvedy, Jones & De Long & Maddison 2010\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
for k in ("page", "repo"):
    t = t.replace("\\url{{{meta.%s}}}" % k, "\\url{%s}" % R["meta"][k])
t = re.sub(r"\{\{(?!TABLE_|DOI_LINK)([^}|]+)(\|(\w+))?\}\}", lambda m: tfmt(get(R, m.group(1)), m.group(3) or "raw"), t)
for k, v in (("LR", TLR), ("COV", TCOV), ("TOP", TTOP), ("OVER", TOVER), ("FAST", TFAST), ("GAP", TGAP), ("PRE", TPRE), ("SRC", TSRC)):
    t = t.replace("{{TABLE_%s}}" % k, v)
t = t.replace("{{DOI_LINK}}", "https://doi.org/\\{\\{DOI\\}\\}")
assert "{{" not in t and "--" not in t and "—" not in t and "–" not in t, (re.findall(r"\{\{[^}]*\}\}", t)[:4], [l for l in t.splitlines() if "–" in l or "--" in l][:3])
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l][:12])
for ext in (".aux", ".log", ".out", ".bbl", ".blg"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("—") + txt.count("–") + txt.count("--"))
