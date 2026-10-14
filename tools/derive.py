"""Builds the small helper files the charts read from data/trails.csv (transparent, re-runnable).
Also writes data/australia_states.geojson from Natural Earth (state boundaries, public domain)."""
import csv, json, math, collections

rows = list(csv.DictReader(open("data/trails.csv")))
def num(x): return float(x) if x not in ("", None) else None
for r in rows:
    r["km"] = num(r["km"]); r["hmin"] = num(r["hours_min"]); r["hmax"] = num(r["hours_max"])
    r["hours"] = None if r["hmin"] is None else (r["hmin"] + r["hmax"]) / 2
    r["peak_m"] = num(r["peak_m"])
trails = [r for r in rows if r["role"] != "whole"]          # whole-trail row is never added to totals
import re
for r in rows:
    m = re.match(r"Section (\d+):", r["trail"])
    r["short"] = ("Larapinta S" + m.group(1)) if m else r["trail"]

def bracket(h):
    if h < 1: return "Under 1 h"
    if h < 2: return "1 to 2 h"
    if h < 4: return "2 to 4 h"
    if h < 8: return "4 to 8 h"
    return "8 h or more"
ORDER = ["Under 1 h", "1 to 2 h", "2 to 4 h", "4 to 8 h", "8 h or more"]

MEL = (144.9631, -37.8136)
GROUPS = {  # lon, lat of one symbol per group (maps stay uncluttered)
 "SE Queensland": (152.98, -28.26), "Wilsons Promontory": (146.355, -39.033), "Flinders Ranges": (138.606, -31.526),
 "Stirling Range": (118.256, -34.375), "Larapinta Trail": (133.0, -23.62)}
# label offsets (dx, dy, align) for the symbol map, then for the flow map
OFFS = {"SE Queensland": (-28,-2,"right",-10,-12,"right"), "Wilsons Promontory": (-32,6,"right",-12,18,"right"),
        "Flinders Ranges": (36,-2,"left",-10,14,"right"), "Stirling Range": (16,-2,"left",14,-8,"left"),
        "Larapinta Trail": (38,-2,"left",12,-8,"left")}
def hav(a, b):
    R = 6371; p1, p2 = math.radians(a[1]), math.radians(b[1]); dl = math.radians(b[0]-a[0]); dp = p2-p1
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(h))

def w(name, header, data):
    with open("data/"+name, "w", newline="") as f:
        cw = csv.writer(f); cw.writerow(header); cw.writerows(data)

# trails_clean.csv: numeric hours (midpoint of ranges) for scatter/bars
w("trails_clean.csv", ["id","trail","short","area","map_group","state","role","km","km_basis","hours","band","grade_label","bracket"],
  [[r["id"], r["trail"], r["short"], r["area"], r["map_group"], r["state"], r["role"], r["km"] if r["km"] is not None else "",
    r["km_basis"], r["hours"], r["band"], r["grade_label"], bracket(r["hours"])] for r in trails])

# one symbol per group
G = collections.OrderedDict()
for r in trails: G.setdefault(r["map_group"], []).append(r)
out = []
for g, rs in G.items():
    km = sum(r["km"] for r in rs if r["km"] is not None); hrs = sum(r["hours"] for r in rs)
    longest = max((r for r in rs if r["km"] is not None), key=lambda r: r["km"])
    lon, lat = GROUPS[g]
    dx, dy, al, fx, fy, fal = OFFS[g]
    out.append([g, rs[0]["state"], lon, lat, len(rs), round(km,1), round(hrs,1), round(hav(MEL,(lon,lat))), longest["short"], longest["km"], dx, dy, al, fx, fy, fal])
w("groups.csv", ["map_group","state","lon","lat","n_trails","total_km","total_hours","km_from_melbourne","longest_trail","longest_km","dx","dy","align","fx","fy","falign"], out)
w("melbourne.csv", ["name","lon","lat"], [["Melbourne", MEL[0], MEL[1]]])

# state summary for the choropleth (average walking time per trail)
S = collections.defaultdict(list)
for r in trails: S[r["state"]].append(r)
NAME = {"QLD":"Queensland","VIC":"Victoria","SA":"South Australia","WA":"Western Australia","NT":"Northern Territory"}
w("state_summary.csv", ["state","name","n_trails","avg_hours","total_km"],
  [[s, NAME[s], len(rs), round(sum(r["hours"] for r in rs)/len(rs),1), round(sum(r["km"] for r in rs if r["km"] is not None),1)] for s, rs in S.items()])

# heatmap: group x time bracket
H = collections.Counter((r["map_group"], bracket(r["hours"])) for r in trails)
w("heatmap.csv", ["map_group","bracket","n","bracket_order"], [[g, b, H.get((g,b),0), ORDER.index(b)] for g in G for b in ORDER])

# waffle: 1 square = 1 trail, 6 per row
BO = ["Easy","Moderate","Hard","Very hard","Not graded"]
wf = []
for g, rs in G.items():
    rs2 = sorted(rs, key=lambda r: BO.index(r["band"]))
    for i, r in enumerate(rs2): wf.append([g, r["band"], i % 6, i // 6, r["trail"]])
w("waffle.csv", ["map_group","band","col","row","trail"], wf)

# treemap nodes (km known, whole-trail row excluded)
nodes = [["root","","All trails","","","",""]]
for g, rs in G.items():
    nodes.append(["g:"+g, "root", g, "", "", g, round(sum(r["km"] for r in rs if r["km"] is not None),1)])
    for r in rs:
        if r["km"] is not None: nodes.append(["t:"+r["id"], "g:"+g, r["short"], r["km"], r["band"], r["trail"], ""])
w("treemap_nodes.csv", ["id","parent","name","km","band","full","total_km"], nodes)

# skyline: triangles for peaks that the sources give
peaks = [("Mt Sonder","Larapinta Trail",1379),("Mt Barney","SE Queensland",1354),
         ("St Mary Peak","Flinders Ranges",1171),("Bluff Knoll","Stirling Range",1098),("Mt Maroon","SE Queensland",966)]
sk = []
for i,(n,g,h) in enumerate(peaks):
    x = 15*i
    sk += [[n,g,h,x-7,0,0],[n,g,h,x,h,1],[n,g,h,x+7,0,2]]
w("skyline.csv", ["peak","map_group","height_m","x","y","ord"], sk)

# Larapinta radial
lar = [r for r in rows if r["role"]=="section"]
w("larapinta_radial.csv", ["i","i2","section","trail","km","hours","band"],
  [[i, i+1, "S"+str(i+1), r["trail"], r["km"], r["hours"], r["band"]] for i, r in enumerate(lar)])

# Natural Earth -> Australia states only, 3-decimal coordinates
ne = json.load(open("/home/claude/ne50.json"))
def rnd(c): return [round(c[0],3), round(c[1],3)] if isinstance(c[0], (int,float)) else [rnd(x) for x in c]
feats = []
for f in ne["features"]:
    p = f["properties"]
    if p.get("admin") == "Australia":
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        keep = []
        for poly in polys:                      # drop far-off islands (e.g. Macquarie Island) so the map fits the mainland + Tasmania
            xs = [c[0] for c in poly[0]]; ys = [c[1] for c in poly[0]]
            cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)
            if 112 <= cx <= 155 and -44.5 <= cy <= -9: keep.append(rnd(poly))
        if keep:
            feats.append({"type":"Feature","properties":{"name":p.get("name")},
                          "geometry":{"type":"MultiPolygon","coordinates":keep}})
json.dump({"type":"FeatureCollection","features":feats}, open("data/australia_states.geojson","w"), separators=(",",":"))
print("states:", [f["properties"]["name"] for f in feats])

# ---- facts for the page text ----
print("trails (individual):", len(trails), "| with km:", sum(1 for r in trails if r["km"] is not None))
for g, rs in G.items(): print(g, len(rs), "trails;", round(sum(r['hours'] for r in rs),1), "h;", round(sum(r['km'] for r in rs if r['km'] is not None),1), "km")
print(open("data/groups.csv").read()); print(open("data/state_summary.csv").read())
longest = sorted([r for r in trails if r["km"] is not None], key=lambda r:-r["km"])[:6]
print("longest:", [(r["trail"][:22], r["km"]) for r in longest])
print("bands:", collections.Counter(r["band"] for r in trails))
print("share under 2h:", round(100*sum(1 for r in trails if r["hours"]<2)/len(trails)), "%", "| 8h+:", sum(1 for r in trails if r["hours"]>=8))
print("larapinta sum hours:", sum(r['hours'] for r in lar), "sum km:", round(sum(r['km'] for r in lar),1))

SL = {"Northern Territory":(133.4,-19.6,"NT"),"Queensland":(144.6,-22.6,"QLD"),"South Australia":(135.3,-30.2,"SA"),
      "Western Australia":(122.0,-26.0,"WA"),"Victoria":(143.6,-36.9,"VIC"),"New South Wales":(146.6,-32.4,"NSW"),"Tasmania":(146.6,-42.1,"TAS")}
avg = {r[1]: r[3] for r in csv.reader(open("data/state_summary.csv")) if r[1] != "name"}
w("state_labels.csv", ["name","lon","lat","abbr","label","has_data"],
  [[n, lo, la, ab, (avg[n] + " h") if n in avg else "", 1 if n in avg else 0] for n,(lo,la,ab) in SL.items()])
