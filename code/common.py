"""Shared paths, constants and helpers for the gdp-through-time project ("The Wealth of Nations, Mapped").

Raw inputs (read in place, never modified):
  /home/claude/newdata/raw14/maddison/mpd2023_web.xlsx
      Maddison Project Database 2023 (Bolt and van Zanden 2024), DataverseNL doi:10.34894/INZBF2, CC BY 4.0.
      Sheets used: "Full data" (countrycode, country, region, year, gdppc in 2011 international dollars, pop in thousands)
      and "Regional data" (Maddison's world GDP per head and world population at benchmark years).
      Retrieved from a GitHub copy of the official file:
      https://raw.githubusercontent.com/nbreznau/gwip_long/main/data/mpd2023_web.xlsx
      (sha256 ecc5916ca12789b983fc4be437f8a354bbf4291323605324ac3e0aea4c57cbb6; checked against a second copy,
      Artometrics/imperial data/mpd2023.csv, in 01_data.py when present).
  /home/claude/newdata/raw14/weo/WEOOct2025all.xlsx
      IMF World Economic Outlook database, October 2025 (sheet "Countries"): real GDP per head at PPP (NGDPRPPPPC),
      real GDP growth (NGDP_RPCH) and population (LP), used only to carry the Maddison series from 2022 to 2024.
      Retrieved from https://raw.githubusercontent.com/ayushmish605/largest-economies-information-visualization/main/data/input/WEOOct2025all.xlsx
  /home/claude/newdata/raw14/hb/world_*.geojson
      historical-basemaps by Andre Ourednik (github.com/aourednik/historical-basemaps), GPL-3.0: approximate borders of
      states at snapshot years, drawn only as a faint backdrop ("borders of the time"); the colours are always Maddison's
      present-day territories.
  /home/claude/newdata/raw/geo/ne_50m_admin_0_countries.geojson
      Natural Earth 1:50m countries (public domain): the modern borders the values belong to, and label points.
"""
import json, gzip, os, re, unicodedata
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.environ.get("GDP_RAW", "/home/claude/newdata/raw14")
MPD_XLSX = os.path.join(RAW, "maddison", "mpd2023_web.xlsx")
MPD_CHECK = os.path.join(RAW, "maddison", "mpd2023_artometrics.csv")
WEO_XLSX = os.path.join(RAW, "weo", "WEOOct2025all.xlsx")
HB = os.path.join(RAW, "hb")
LONGRUN_XLSX = os.path.join(RAW, "longrun", "roodman_GWP.xlsx")   # github.com/droodman/Modeling-Human-Trajectory GWP.xlsx (sha256 450210771d99...)
GEO = os.environ.get("GDP_GEO", "/home/claude/newdata/raw/geo")
FONTS = os.environ.get("GDP_FONTS", "/home/claude/ref/fonts")
DATA = os.path.join(ROOT, "data")
WORK = os.path.join(os.environ.get("GDPTMP", "/dev/shm/gdp-through-time"), "work")
for d in (DATA, WORK):
    os.makedirs(d, exist_ok=True)

SLUG = "gdp-through-time"
TITLE = "The Wealth of Nations, Mapped"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")

# ---------------- choices (all in one place) ----------------
LAST_MPD = 2022                 # last year of the Maddison Project Database 2023
EXT_YEARS = [2023, 2024]        # years carried forward with IMF WEO (October 2025) growth rates
LAST = EXT_YEARS[-1]
POP_GAP = 30                    # population is interpolated (log-linear) between Maddison estimates at most this many years apart
CARRY = 10                      # on the map, a country without an estimate in the chosen year shows its nearest estimate up to this many years away (marked)
GROWTH_SPAN = (5, 15)           # growth: annual average change in GDP per head since the estimate closest to ten years before, 5 to 15 years back
BIG_POP = 1000                  # thousands: "countries of a million people or more" for the rich/poor gap and the richest-country list
FIRST = -10000                  # the timeline starts at 10,000 BC (world series only before AD 1)
TIME_KNOTS = [(FIRST, 0.0), (1, 0.13), (1500, 0.25), (1820, 0.37), (1950, 0.67), (LAST, 1.0)]   # non-linear slider: (year, position 0..1)

# Former states in Maddison: the aggregate is shown up to the year it broke up; its present-day successors after.
FORMER = {
    "SUN": {"name": "USSR", "until": 1991, "succ": ["ARM", "AZE", "BLR", "EST", "GEO", "KAZ", "KGZ", "LTU", "LVA", "MDA", "RUS", "TJK", "TKM", "UKR", "UZB"]},
    "YUG": {"name": "Yugoslavia", "until": 1991, "succ": ["BIH", "HRV", "MKD", "MNE", "SRB", "SVN"], "extra_poly": ["KOS"]},
    "CSK": {"name": "Czechoslovakia", "until": 1992, "succ": ["CZE", "SVK"]},
}
# Maddison (2010) regions for AD 1 to 1820: key -> column in Maddison's tables (OASIA is Asia less the other Asian rows)
M2010_REGIONS = {"WEUR": "30 W. Europe", "WOFF": "W. Offshoots", "EEUR": "7 E. Europe", "FSU": "F. USSR", "LATAM": "L. America",
                 "CHN": "China", "IND": "India", "JPN": "Japan", "OASIA": None, "WASIA": "15 W. Asia", "AFR": "Total Africa"}
M2010_NAMES = {"WEUR": "Western Europe", "WOFF": "US, Canada, Australia, NZ", "EEUR": "Eastern Europe", "FSU": "Russia and neighbours (former USSR)",
               "LATAM": "Latin America", "CHN": "China", "IND": "Indian subcontinent", "JPN": "Japan", "OASIA": "Rest of Asia",
               "WASIA": "West Asia", "AFR": "Africa"}
# Natural Earth polygons drawn with a Maddison unit of another code
NE_TO_MPD = {"PSX": "PSE", "SDS": "SDN"}

NAMES = {   # short display names for Maddison's country labels
    "BOL": "Bolivia", "CHN": "China", "COD": "DR Congo", "COG": "Congo", "CIV": "Côte d'Ivoire", "CSK": "Czechoslovakia",
    "HKG": "Hong Kong", "IRN": "Iran", "KOR": "South Korea", "PRK": "North Korea", "LAO": "Laos", "MDA": "Moldova",
    "MKD": "North Macedonia", "RUS": "Russia", "SDN": "Sudan (incl. South Sudan)", "SUN": "USSR", "SWZ": "Eswatini",
    "SYR": "Syria", "TWN": "Taiwan", "TZA": "Tanzania (mainland)", "VEN": "Venezuela", "VNM": "Vietnam",
    "YUG": "Yugoslavia", "PSE": "Palestine", "USA": "United States", "GBR": "United Kingdom", "CZE": "Czech Republic",
    "ARE": "United Arab Emirates", "DOM": "Dominican Republic", "CAF": "Central African Republic", "TTO": "Trinidad and Tobago",
    "STP": "São Tomé and Príncipe", "LCA": "Saint Lucia", "BIH": "Bosnia and Herzegovina", "TUR": "Turkey",
}
NAMES_SHORT = {"United States": "US", "United Kingdom": "UK", "Sudan (incl. South Sudan)": "Sudan", "Tanzania (mainland)": "Tanzania",
               "United Arab Emirates": "UAE", "Central African Republic": "Central African Rep.", "Bosnia and Herzegovina": "Bosnia",
               "Trinidad and Tobago": "Trinidad", "Dominican Republic": "Dominican Rep.", "São Tomé and Príncipe": "São Tomé"}

COL = {"ink": "#22201C", "muted": "#68625A", "paper": "#F7F2E7", "rule": "#E0D6C1", "red": "#B23A2A", "nodata": "#D9D2C3"}
# sequential ramp for the choropleth (pale straw to deep green-blue), used on the page and in figures
RAMP = ["#F3EBC9", "#DDE3A6", "#B5D38E", "#83BD84", "#55A381", "#33857B", "#1F6672", "#1A4866", "#1B2C55"]
# diverging ramp for growth (decline red, growth green)
DIV = ["#8E2A20", "#C2543C", "#E59A72", "#F2D7B6", "#E3E6C3", "#A9D19A", "#67AE7E", "#2E8670", "#155E5A"]
SERIES_COL = {"CHN": "#B23A2A", "IND": "#D08A1E", "USA": "#2F5FA7", "GBR": "#6E5A7E", "JPN": "#C2457A", "KOR": "#2E8A6E",
              "DEU": "#4A4A4A", "FRA": "#5C8FE0", "SUN": "#8A6A2E", "RUS": "#8A6A2E", "NLD": "#E07B39", "ITA": "#3D7F3A", "ESP": "#9C6B30"}


def year_pos(y):
    ys, ps = zip(*TIME_KNOTS)
    return float(np.interp(y, ys, ps))


def yr(y):
    y = int(round(y))
    if y <= 0: return f"{1 - y if y == 0 else -y:,} BC".replace(",", ",")
    return f"AD {y}" if y < 1000 else str(y)


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def dash(v):
    """Remove em and en dashes and double hyphens from text (house style)."""
    if isinstance(v, str):
        v = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", v)
        v = v.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")
        while "--" in v:
            v = v.replace("--", "-")
        return v
    if isinstance(v, list):
        return [dash(x) for x in v]
    if isinstance(v, dict):
        return {k: dash(x) for k, x in v.items()}
    return v


def jsave(obj, path, indent=None):
    if os.path.abspath(path).startswith(DATA):
        obj = dash(obj)
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "wt", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))


def norm(s):
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    return re.sub(r"[\W_]+", " ", s).strip()


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f=None):
    """Formats for {{path|format}} tokens in the page, blog and README."""
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "pc1": return f"{float(v):.1f}%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f0": return f"{float(v):.0f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "x": return f"{round(float(v)):,}"              # "times"
    if f == "x1": return f"{float(v):.1f}"
    if f == "yr": return yr(v)
    if f == "usd": return f"${round(float(v)):,}"            # 2011 international dollars
    if f == "tn": return f"{float(v) / 1e12:.1f}"            # trillions
    if f == "tn2": return f"{float(v) / 1e12:.2f}"
    raise ValueError(f)
