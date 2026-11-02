"""Map geometry for the page and the figures.

data/map_countries.geojson   Natural Earth 50m countries (Antarctica dropped), simplified with mapshaper, with
                             id (Natural Earth ADM0_A3), m (the Maddison unit whose value colours it, or null), name, and
                             label point; plus three dissolved features for the former USSR, Yugoslavia and Czechoslovakia
                             (former=1), shown up to the year each broke up.
data/hist/hb_<year>.json     historical-basemaps snapshots (GPL-3.0), simplified, NAME only, for the "borders of the
                             time" backdrop; data/hist/index.json lists the years.
Needs mapshaper (npm); set MAPSHAPER to its path.
"""
import subprocess, shutil, glob
from shapely.geometry import shape
from common import *

MS = os.environ.get("MAPSHAPER", "/tmp/claude-0/-home-claude/9791f396-0812-550b-8fd1-2ad33918f115/scratchpad/node_modules/.bin/mapshaper")
assert os.path.exists(MS), "install mapshaper (npm i mapshaper) and set MAPSHAPER"
MPD = set(jload(f"{WORK}/meta.json")["names"])
tmp = os.path.join(WORK, "geo"); os.makedirs(tmp, exist_ok=True)

# ---------------- modern countries ----------------
G = jload(f"{GEO}/ne_50m_admin_0_countries.geojson")
feats = []
for f in G["features"]:
    p = f["properties"]; a = p["ADM0_A3"]
    if a == "ATA": continue
    m = NE_TO_MPD.get(a, a if a in MPD else None)
    feats.append({"type": "Feature", "geometry": f["geometry"],
                  "properties": {"id": a, "m": m, "name": p["NAME"], "lx": round(p["LABEL_X"], 2), "ly": round(p["LABEL_Y"], 2),
                                 "pop": p["POP_EST"], "former": 0}})
json.dump({"type": "FeatureCollection", "features": feats}, open(f"{tmp}/ne.json", "w"))
subprocess.run([MS, f"{tmp}/ne.json", "-simplify", "8%", "keep-shapes", "weighted", "-clean", "-o", f"{tmp}/ne_s.json", "precision=0.01", "format=geojson"], check=True, capture_output=True)
S = jload(f"{tmp}/ne_s.json")
# dissolved former states
for a, f in FORMER.items():
    members = set(f["succ"]) | set(f.get("extra_poly", []))
    sub = {"type": "FeatureCollection", "features": [x for x in S["features"] if x["properties"]["id"] in members]}
    assert len(sub["features"]) == len(members), (a, len(sub["features"]))
    json.dump(sub, open(f"{tmp}/{a}.json", "w"))
    subprocess.run([MS, f"{tmp}/{a}.json", "-dissolve", "-o", f"{tmp}/{a}_d.json", "precision=0.01", "format=geojson", "geojson-type=FeatureCollection"], check=True, capture_output=True)
    g = jload(f"{tmp}/{a}_d.json")["features"][0]["geometry"]
    big = max((x for x in S["features"] if x["properties"]["id"] in f["succ"]), key=lambda x: x["properties"]["pop"])["properties"]
    S["features"].append({"type": "Feature", "geometry": g, "properties": {"id": a, "m": a, "name": f["name"], "lx": big["lx"], "ly": big["ly"], "pop": 0, "former": 1}})
for x in S["features"]:
    x["properties"].pop("pop", None)
jsave(S, f"{DATA}/map_countries.geojson")
n_m = sum(1 for x in S["features"] if x["properties"]["m"] and not x["properties"]["former"])
n_none = sorted(x["properties"]["name"] for x in S["features"] if not x["properties"]["m"])
print("countries", len(S["features"]), "with a Maddison unit", n_m, "without", len(n_none), os.path.getsize(f"{DATA}/map_countries.geojson") // 1024, "KB")


# ---------------- Maddison (2010) regions, AD 1 to 1820 ----------------
FSU = set(FORMER["SUN"]["succ"]); YUG = set(FORMER["YUG"]["succ"]) | {"KOS"}
WASIA = {"BHR", "IRN", "IRQ", "ISR", "JOR", "KWT", "LBN", "OMN", "QAT", "SAU", "SYR", "TUR", "ARE", "YEM", "PSX", "CYN"}
EEUR = {"ALB", "BGR", "CZE", "SVK", "HUN", "POL", "ROU"} | YUG
SUBC = {"IND", "PAK", "BGD", "KAS"}
def region_of(p):
    a, c, sr = p["ADM0_A3"], p["CONTINENT"], p["SUBREGION"]
    if a in FSU: return "FSU"
    if a in EEUR: return "EEUR"
    if a in WASIA: return "WASIA"
    if a in SUBC: return "IND"
    if a in ("CHN",): return "CHN"
    if a == "JPN": return "JPN"
    if a in ("USA", "CAN", "AUS", "NZL"): return "WOFF"
    if a == "GRL": return None          # in Maddison's Western Europe, but left undrawn so the map does not exaggerate it
    if c == "Europe": return "WEUR"
    if c == "Africa" or sr in ("Eastern Africa", "Western Africa"): return "AFR"
    if c == "South America" or sr in ("Caribbean", "Central America") or a == "MEX": return "LATAM"
    if c in ("Asia", "Oceania") or sr == "Southern Asia": return "OASIA"
    return None
RF = []
for f in G["features"]:
    p = f["properties"]
    if p["ADM0_A3"] == "ATA": continue
    k = region_of(p)
    if k: RF.append({"type": "Feature", "geometry": f["geometry"], "properties": {"r": k}})
json.dump({"type": "FeatureCollection", "features": RF}, open(f"{tmp}/reg.json", "w"))
subprocess.run([MS, f"{tmp}/reg.json", "-simplify", "6%", "keep-shapes", "weighted", "-clean", "-dissolve", "r", "-o", f"{tmp}/reg_d.json", "precision=0.01", "format=geojson", "geojson-type=FeatureCollection"], check=True, capture_output=True)
RD = jload(f"{tmp}/reg_d.json")
LBL = {"WEUR": (2, 47), "WOFF": (-100, 40), "EEUR": (22, 48), "FSU": (75, 60), "LATAM": (-62, -12), "CHN": (103, 34), "IND": (77, 21),
       "JPN": (138, 37), "OASIA": (112, 2), "WASIA": (45, 30), "AFR": (20, 5)}
for f in RD["features"]:
    k = f["properties"]["r"]; f["properties"].update({"name": M2010_NAMES[k], "lx": LBL[k][0], "ly": LBL[k][1]})
assert sorted(f["properties"]["r"] for f in RD["features"]) == sorted(M2010_REGIONS), [f["properties"]["r"] for f in RD["features"]]
jsave(RD, f"{DATA}/map_regions_maddison2010.geojson")
print("regions", len(RD["features"]), os.path.getsize(f"{DATA}/map_regions_maddison2010.geojson") // 1024, "KB")

# ---------------- historical borders (backdrop only) ----------------
HD = os.path.join(DATA, "hist"); os.makedirs(HD, exist_ok=True)
for fn in glob.glob(f"{HD}/*"): os.remove(fn)
years = []
for fn in sorted(glob.glob(f"{HB}/world_*.geojson")):
    k = os.path.basename(fn)[6:-8]
    y = -int(k[2:]) if k.startswith("bc") else int(k)
    g = jload(fn)
    keep = []
    for f in g["features"]:
        nm = (f["properties"].get("NAME") or "").strip()
        if not f.get("geometry"): continue
        keep.append({"type": "Feature", "geometry": f["geometry"], "properties": {"n": nm}})
    json.dump({"type": "FeatureCollection", "features": keep}, open(f"{tmp}/h.json", "w"))
    subprocess.run([MS, f"{tmp}/h.json", "-clip", "bbox=-180,-60,180,85", "-simplify", "6%", "keep-shapes", "weighted", "-filter-slivers", "min-area=2000km2",
                    "-o", f"{tmp}/h_s.json", "precision=0.02", "format=geojson"], check=True, capture_output=True)
    h = jload(f"{tmp}/h_s.json")
    h["features"] = [f for f in h["features"] if f.get("geometry")]
    for f in h["features"]:      # a label point and area (thousand km2, rough) for "names of the time"
        sh = shape(f["geometry"]).buffer(0)
        big = max(sh.geoms, key=lambda q: q.area) if sh.geom_type == "MultiPolygon" else sh
        pt = big.representative_point()
        f["properties"].update({"lx": round(pt.x, 2), "ly": round(pt.y, 2), "a": int(sh.area * 111 * 111 * np.cos(np.radians(pt.y)) / 1000)})
    jsave(h, f"{HD}/hb_{y}.json")
    years.append(y)
years.sort()
jsave({"years": years, "source": "historical-basemaps (Andre Ourednik), GPL-3.0, github.com/aourednik/historical-basemaps"}, f"{HD}/index.json")
shutil.copy(f"{HB}/LICENSE", f"{HD}/LICENSE_GPL-3.0.txt")
tot = sum(os.path.getsize(p) for p in glob.glob(f"{HD}/hb_*.json"))
print("historical snapshots", len(years), years[:5], "...", years[-3:], tot // 1024, "KB")
jsave({"no_unit": n_none}, f"{WORK}/geo_meta.json")
