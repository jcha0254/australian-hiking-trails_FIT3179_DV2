"""Writes the human-readable chart specs in specs/ (Vega-Lite, plus one Vega treemap)."""
import json
VL = "https://vega.github.io/schema/vega-lite/v5.json"
GROUPS = ["SE Queensland", "Wilsons Promontory", "Flinders Ranges", "Stirling Range", "Larapinta Trail"]
GCOL = ["#2F6E8E", "#D98E04", "#B5472E", "#5F8A3C", "#8C3B72"]
BANDS = ["Easy", "Moderate", "Hard", "Very hard", "Not graded"]
BCOL = ["#7DB38A", "#E2B73F", "#DB6B2D", "#8E2B3A", "#C3C9C4"]
LAND, INK = "#E3E8E2", "#14231F"
PROJ = {"type": "conicEqualArea", "parallels": [-18, -36], "rotate": [-132, 0, 0]}
STATES = {"data": {"url": "data/australia_states.geojson", "format": {"property": "features"}}}
gscale = {"domain": GROUPS, "range": GCOL}
bscale = {"domain": BANDS, "range": BCOL}

NUMERIC = {  # numeric columns per CSV, so longitude/latitude and values are real numbers
 "groups.csv": ["lon","lat","n_trails","total_km","total_hours","km_from_melbourne","longest_km","dx","dy","fx","fy"],
 "melbourne.csv": ["lon","lat"], "state_summary.csv": ["n_trails","avg_hours","total_km"],
 "state_labels.csv": ["lon","lat","has_data"], "trails_clean.csv": ["km","hours"],
 "heatmap.csv": ["n","bracket_order"], "waffle.csv": ["col","row"],
 "skyline.csv": ["height_m","x","y","ord"], "larapinta_radial.csv": ["i","i2","km","hours"]}
def csv(f):
    return {"url": "data/" + f, "format": {"type": "csv", "parse": {c: "number" for c in NUMERIC[f]}}}

def save(name, spec):
    json.dump(spec, open("specs/" + name, "w"), indent=2, ensure_ascii=False)

# 1 ── proportional symbol map (one symbol per area, so combined trails do not clutter the map)
save("map_symbols.vl.json", {
 "$schema": VL, "width": "container", "height": 430, "projection": PROJ,
 "layer": [
  {**STATES, "mark": {"type": "geoshape", "fill": LAND, "stroke": "#fff", "strokeWidth": 1}},
  {"data": csv("groups.csv"),
   "mark": {"type": "circle", "opacity": 0.88, "stroke": "#fff", "strokeWidth": 1.5},
   "encoding": {
    "longitude": {"field": "lon", "type": "quantitative"}, "latitude": {"field": "lat", "type": "quantitative"},
    "size": {"field": "total_km", "type": "quantitative", "scale": {"type": "sqrt", "domain": [0, 240], "range": [60, 3600]},
             "legend": {"title": "Distance (km)", "titleLimit": 200, "orient": "top-left", "values": [10, 50, 100, 200], "symbolFillColor": "#9aa6a0"}},
    "color": {"field": "map_group", "type": "nominal", "scale": gscale, "legend": None},
    "tooltip": [{"field": "map_group", "title": "Area"}, {"field": "n_trails", "title": "Trails listed"},
                {"field": "total_km", "title": "Combined distance (km)"}, {"field": "total_hours", "title": "Combined time (hours)"},
                {"field": "longest_trail", "title": "Longest trail"}]}},
  {"data": csv("groups.csv"),
   "mark": {"type": "text", "fontSize": 12, "fontWeight": 700, "color": INK, "dx": {"expr": "datum.dx"}, "dy": {"expr": "datum.dy"}, "align": {"expr": "datum.align"}},
   "encoding": {"longitude": {"field": "lon", "type": "quantitative"}, "latitude": {"field": "lat", "type": "quantitative"},
                "text": {"field": "map_group", "type": "nominal"}}}]})

# 2 ── choropleth: average time a trail takes, by state
save("map_choropleth.vl.json", {
 "$schema": VL, "width": "container", "height": 430, "projection": PROJ,
 "layer": [
  {**STATES,
   "transform": [{"lookup": "properties.name", "from": {"data": csv("state_summary.csv"), "key": "name", "fields": ["avg_hours", "n_trails"]}}],
   "mark": {"type": "geoshape", "stroke": "#fff", "strokeWidth": 1.2},
   "encoding": {
    "color": {"condition": {"test": "!isValid(datum.avg_hours)", "value": "#EDF0EC"},
              "field": "avg_hours", "type": "quantitative",
              "scale": {"domain": [1, 8], "range": ["#F8E2CE", "#E8590C", "#8E2B3A"]},
              "legend": {"title": "Average hours per trail", "titleLimit": 220, "orient": "bottom-left", "gradientLength": 150, "values": [2, 4, 6, 8]}},
    "tooltip": [{"field": "properties.name", "title": "State"}, {"field": "n_trails", "title": "Trails listed"},
                {"field": "avg_hours", "title": "Average hours per trail"}]}},
  {"data": csv("state_labels.csv"),
   "mark": {"type": "text", "fontSize": 12, "fontWeight": 700, "lineBreak": "\n"},
   "encoding": {"longitude": {"field": "lon", "type": "quantitative"}, "latitude": {"field": "lat", "type": "quantitative"},
                "text": {"field": "abbr", "type": "nominal"},
                "color": {"condition": {"test": "datum.has_data == 1 && datum.abbr != 'VIC'", "value": "#ffffff"}, "value": "#14231F"}}},
  {"data": csv("state_labels.csv"), "transform": [{"filter": "datum.has_data == 1"}],
   "mark": {"type": "text", "fontSize": 11, "dy": 15},
   "encoding": {"longitude": {"field": "lon", "type": "quantitative"}, "latitude": {"field": "lat", "type": "quantitative"},
                "text": {"field": "label", "type": "nominal"},
                "color": {"condition": {"test": "datum.abbr != 'VIC'", "value": "#ffffff"}, "value": "#14231F"}}}]})

# 3 ── flow map: straight-line distance from Melbourne
save("map_flow.vl.json", {
 "$schema": VL, "width": "container", "height": 430, "projection": PROJ,
 "layer": [
  {**STATES, "mark": {"type": "geoshape", "fill": LAND, "stroke": "#fff", "strokeWidth": 1}},
  {"data": csv("groups.csv"),
   "transform": [{"calculate": "144.9631", "as": "lon0"}, {"calculate": "-37.8136", "as": "lat0"}],
   "mark": {"type": "rule", "strokeWidth": 2.2, "strokeDash": [5, 4], "opacity": 0.9},
   "encoding": {"longitude": {"field": "lon", "type": "quantitative"}, "latitude": {"field": "lat", "type": "quantitative"},
                "longitude2": {"field": "lon0"}, "latitude2": {"field": "lat0"},
                "color": {"field": "map_group", "type": "nominal", "scale": gscale, "legend": None}}},
  {"data": csv("groups.csv"),
   "mark": {"type": "circle", "size": 110, "stroke": "#fff", "strokeWidth": 1.5},
   "encoding": {"longitude": {"field": "lon", "type": "quantitative"}, "latitude": {"field": "lat", "type": "quantitative"},
                "color": {"field": "map_group", "type": "nominal", "scale": gscale, "legend": None},
                "tooltip": [{"field": "map_group", "title": "Area"}, {"field": "km_from_melbourne", "title": "Straight-line km from Melbourne", "format": ","}]}},
  {"data": csv("groups.csv"),
   "transform": [{"calculate": "datum.map_group + ': ' + format(datum.km_from_melbourne, ',') + ' km'", "as": "lab"}],
   "mark": {"type": "text", "fontSize": 11.5, "fontWeight": 600, "color": INK, "dx": {"expr": "datum.fx"}, "dy": {"expr": "datum.fy"}, "align": {"expr": "datum.falign"}},
   "encoding": {"longitude": {"field": "lon", "type": "quantitative"}, "latitude": {"field": "lat", "type": "quantitative"}, "text": {"field": "lab", "type": "nominal"}}},
  {"data": csv("melbourne.csv"),
   "mark": {"type": "point", "shape": "diamond", "size": 170, "filled": True, "color": "#E8590C", "stroke": "#fff", "strokeWidth": 1.5},
   "encoding": {"longitude": {"field": "lon", "type": "quantitative"}, "latitude": {"field": "lat", "type": "quantitative"},
                "tooltip": [{"field": "name", "title": "Start"}]}},
  {"data": csv("melbourne.csv"),
   "mark": {"type": "text", "fontSize": 12, "fontWeight": 700, "color": "#E8590C", "dx": -12, "dy": -12, "align": "right"},
   "encoding": {"longitude": {"field": "lon", "type": "quantitative"}, "latitude": {"field": "lat", "type": "quantitative"}, "text": {"field": "name", "type": "nominal"}}}]})

# 4 ── scatter: distance vs time, with pace guide lines
pace = [{"v": 4, "x2": 30, "y2": 7.5, "lx": 29.2, "ly": 7.9, "lab": "4 km per hour"},
        {"v": 2, "x2": 26, "y2": 13, "lx": 24.2, "ly": 13.0, "lab": "2 km per hour"},
        {"v": 1, "x2": 13, "y2": 13, "lx": 11.4, "ly": 13.0, "lab": "1 km per hour"}]
PACE_LINES = [{"v": p["v"], "x": 0, "y": 0} for p in pace] + [{"v": p["v"], "x": p["x2"], "y": p["y2"]} for p in pace]
X = {"field": "km", "type": "quantitative", "title": "Distance (km, as published)", "scale": {"domain": [0, 30], "nice": False}}
Y = {"field": "hours", "type": "quantitative", "title": "Time (hours, as published)", "scale": {"domain": [0, 13], "nice": False}}
SC_TRANSFORM = [{"filter": "isValid(datum.km) && datum.km > 0"},
  {"calculate": "datum.km_basis == 'one way' ? 'One way' : 'Return, loop or as listed'", "as": "kind"},
  {"calculate": "datum.trail == 'Section 9: Serpentine Chalet Dam to Ormiston Gorge' ? 'Larapinta S9' : datum.trail == 'St Mary Peak Hike' ? 'St Mary Peak' : datum.trail == 'Warrie Circuit' ? 'Warrie Circuit' : null", "as": "tag"}]
save("scatter.vl.json", {
 "$schema": VL, "width": "container", "height": 400,
 "layer": [
  {"data": {"values": PACE_LINES}, "mark": {"type": "line", "stroke": "#9aa6a0", "strokeDash": [4, 4], "strokeWidth": 1.2, "clip": True},
   "encoding": {"x": {"field": "x", "type": "quantitative", "scale": X["scale"]}, "y": {"field": "y", "type": "quantitative", "scale": Y["scale"]},
                "detail": {"field": "v", "type": "nominal"}}},
  {"data": {"values": pace}, "mark": {"type": "text", "fontSize": 10.5, "color": "#6b7873", "align": "right", "baseline": "bottom", "dy": -2},
   "encoding": {"x": {"field": "lx", "type": "quantitative", "scale": X["scale"]}, "y": {"field": "ly", "type": "quantitative", "scale": Y["scale"]},
                "text": {"field": "lab", "type": "nominal"}}},
  {"data": csv("trails_clean.csv"), "transform": SC_TRANSFORM,
   "params": [{"name": "grp", "select": {"type": "point", "fields": ["map_group"]}, "bind": "legend"}],
   "mark": {"type": "point", "filled": True, "size": 85, "stroke": "#fff", "strokeWidth": 0.8},
   "encoding": {"x": X, "y": Y,
    "color": {"field": "map_group", "type": "nominal", "scale": gscale, "legend": {"title": "Area (click to focus)", "titleLimit": 220, "orient": "top-left"}},
    "shape": {"field": "kind", "type": "nominal", "scale": {"domain": ["Return, loop or as listed", "One way"], "range": ["circle", "triangle-up"]},
              "legend": {"title": "How it is measured", "titleLimit": 220, "labelLimit": 220, "orient": "top-left"}},
    "opacity": {"condition": {"param": "grp", "value": 0.92}, "value": 0.15},
    "tooltip": [{"field": "trail", "title": "Trail"}, {"field": "map_group", "title": "Area"}, {"field": "km", "title": "Distance (km)"},
                {"field": "hours", "title": "Time (hours)"}, {"field": "kind", "title": "Measured"}]}},
  {"data": csv("trails_clean.csv"), "transform": SC_TRANSFORM + [{"filter": "isValid(datum.tag)"}],
   "mark": {"type": "text", "fontSize": 11, "fontWeight": 600, "color": INK, "dx": -9, "align": "right"},
   "encoding": {"x": X, "y": Y, "text": {"field": "tag", "type": "nominal"}}}]})

# 5 ── ranked bars: ten longest trails
save("longest.vl.json", {
 "$schema": VL, "width": "container", "height": 330,
 "data": csv("trails_clean.csv"),
 "transform": [{"filter": "isValid(datum.km)"},
               {"window": [{"op": "row_number", "as": "rk"}], "sort": [{"field": "km", "order": "descending"}]},
               {"filter": "datum.rk <= 10"}],
 "encoding": {"y": {"field": "short", "type": "nominal", "sort": {"field": "km", "op": "max", "order": "descending"}, "title": None, "axis": {"labelLimit": 210}},
              "x": {"field": "km", "type": "quantitative", "title": "Distance (km)", "scale": {"domain": [0, 32]}}},
 "layer": [
  {"mark": {"type": "bar", "cornerRadiusEnd": 2, "height": {"band": 0.72}},
   "encoding": {"color": {"field": "map_group", "type": "nominal", "scale": gscale, "legend": None},
                "tooltip": [{"field": "trail", "title": "Trail"}, {"field": "map_group", "title": "Area"}, {"field": "km", "title": "Distance (km)"},
                            {"field": "hours", "title": "Time (hours)"}]}},
  {"mark": {"type": "text", "align": "left", "dx": 5, "fontSize": 11, "fontWeight": 600},
   "encoding": {"text": {"field": "km", "type": "quantitative", "format": ".1f"}}}]})

# 6 ── heatmap: how many trails fit each time slot
save("heatmap.vl.json", {
 "$schema": VL, "width": "container", "height": 230,
 "data": csv("heatmap.csv"),
 "encoding": {"x": {"field": "bracket", "type": "ordinal", "sort": {"field": "bracket_order"}, "title": "Time the trail takes", "axis": {"labelAngle": 0, "orient": "top", "titleOrient": "top"}},
              "y": {"field": "map_group", "type": "nominal", "title": None, "sort": GROUPS}},
 "layer": [
  {"mark": {"type": "rect", "stroke": "#fff", "strokeWidth": 2},
   "encoding": {"color": {"field": "n", "type": "quantitative", "scale": {"domain": [0, 10], "range": ["#EEF1EC", "#2F6E8E", "#14231F"], "clamp": True},
                          "legend": {"title": "Number of trails", "orient": "right", "values": [0, 2, 4, 6, 8, 10]}},
                "tooltip": [{"field": "map_group", "title": "Area"}, {"field": "bracket", "title": "Time"}, {"field": "n", "title": "Trails"}]}},
  {"mark": {"type": "text", "fontSize": 13, "fontWeight": 700},
   "encoding": {"text": {"condition": {"test": "datum.n == 0", "value": ""}, "field": "n", "type": "quantitative"},
                "color": {"condition": {"test": "datum.n >= 4", "value": "#fff"}, "value": INK}}}]})

# 7 ── waffle small multiples: grade of each trail (1 square = 1 trail)
save("waffle.vl.json", {
 "$schema": VL,
 "data": csv("waffle.csv"),
 "facet": {"column": {"field": "map_group", "type": "nominal", "sort": GROUPS, "title": None, "header": {"labelFontSize": 13, "labelFontWeight": 700, "labelOrient": "top"}}},
 "spec": {"width": 168, "height": 90,
  "mark": {"type": "square", "size": 560, "stroke": "#fff", "strokeWidth": 1},
  "encoding": {"x": {"field": "col", "type": "ordinal", "axis": None}, "y": {"field": "row", "type": "ordinal", "axis": None},
               "color": {"field": "band", "type": "nominal", "scale": bscale, "legend": {"title": "Grade band", "orient": "bottom", "direction": "horizontal", "columns": 5}},
               "tooltip": [{"field": "trail", "title": "Trail"}, {"field": "band", "title": "Grade band"}]}},
 "config": {"view": {"stroke": None}}})

# 8 ── mountain skyline of the summits the sources give
save("skyline.vl.json", {
 "$schema": VL, "width": "container", "height": 380,
 "data": csv("skyline.csv"),
 "layer": [
  {"mark": {"type": "area", "interpolate": "linear", "opacity": 0.92},
   "encoding": {"x": {"field": "x", "type": "quantitative", "axis": None, "scale": {"domain": [-9, 69]}},
                "y": {"field": "y", "type": "quantitative", "title": "Height above sea level (m)", "scale": {"domain": [0, 1500]}, "axis": {"values": [0, 500, 1000, 1500]}},
                "detail": {"field": "peak", "type": "nominal"},
                "color": {"field": "map_group", "type": "nominal", "scale": gscale, "legend": None},
                "tooltip": [{"field": "peak", "title": "Peak"}, {"field": "height_m", "title": "Height (m)"}, {"field": "map_group", "title": "Area"}]}},
  {"transform": [{"filter": "datum.ord == 1"}, {"calculate": "[datum.peak, format(datum.height_m, ',') + ' m']", "as": "lab"}],
   "mark": {"type": "text", "dy": -6, "baseline": "bottom", "lineHeight": 14, "fontSize": 12, "fontWeight": 700, "color": INK},
   "encoding": {"x": {"field": "x", "type": "quantitative"}, "y": {"field": "y", "type": "quantitative"}, "text": {"field": "lab", "type": "nominal"}}}]})

# 9 ── radial bars: the twelve Larapinta sections
save("radial.vl.json", {
 "$schema": VL, "width": "container", "height": 430,
 "data": csv("larapinta_radial.csv"),
 "encoding": {"theta": {"field": "i", "type": "quantitative", "scale": {"domain": [0, 12], "range": [0, 6.283185]}, "stack": None},
              "radius": {"field": "km", "type": "quantitative", "scale": {"type": "sqrt", "zero": True, "rangeMin": 30, "rangeMax": 185}, "stack": None}},
 "layer": [
  {"mark": {"type": "arc", "stroke": "#fff", "strokeWidth": 2},
   "encoding": {"theta2": {"field": "i2"}, "radius2": {"value": 30}, "color": {"field": "band", "type": "nominal", "scale": {"domain": ["Moderate", "Hard", "Very hard"], "range": ["#E2B73F", "#DB6B2D", "#8E2B3A"]},
                          "legend": {"title": "Section grade", "orient": "bottom", "direction": "horizontal"}},
                "tooltip": [{"field": "trail", "title": "Section"}, {"field": "km", "title": "Distance (km)"}, {"field": "hours", "title": "Time (hours)"}, {"field": "band", "title": "Grade"}]}},
  {"transform": [{"calculate": "datum.i + 0.5", "as": "mid"}],
   "mark": {"type": "text", "radiusOffset": 13, "fontSize": 12, "fontWeight": 700, "color": INK},
   "encoding": {"theta": {"field": "mid", "type": "quantitative", "scale": {"domain": [0, 12], "range": [0, 6.283185]}, "stack": None},
                "radius": {"field": "km", "type": "quantitative", "scale": {"type": "sqrt", "zero": True, "rangeMin": 30, "rangeMax": 185}, "stack": None},
                "text": {"field": "section", "type": "nominal"}}}]})

# 10 ── time range: every trail as a dot, with the shortest-to-longest span and the average for each area
ORDER_T = ["Larapinta Trail", "SE Queensland", "Flinders Ranges", "Stirling Range", "Wilsons Promontory"]
XS = {"domain": [0, 19], "nice": False}
save("time_range.vl.json", {
 "$schema": VL, "width": "container", "height": 300,
 "encoding": {"y": {"field": "map_group", "type": "nominal", "title": None, "sort": ORDER_T, "axis": {"labelLimit": 150, "labelFontWeight": 600}}},
 "layer": [
  {"data": csv("trails_clean.csv"),
   "transform": [{"aggregate": [{"op": "min", "field": "hours", "as": "lo"}, {"op": "max", "field": "hours", "as": "hi"}], "groupby": ["map_group"]}],
   "mark": {"type": "rule", "strokeWidth": 7, "strokeCap": "round", "opacity": 0.28},
   "encoding": {"x": {"field": "lo", "type": "quantitative", "title": "Time the trail takes (hours, as published)", "axis": {"values": [0, 2, 4, 6, 8, 10, 12]}, "scale": XS},
                "x2": {"field": "hi"}, "color": {"field": "map_group", "type": "nominal", "scale": gscale, "legend": None}}},
  {"data": csv("trails_clean.csv"),
   "mark": {"type": "circle", "size": 70, "opacity": 0.65, "stroke": "#fff", "strokeWidth": 0.8},
   "encoding": {"x": {"field": "hours", "type": "quantitative", "scale": XS},
                "color": {"field": "map_group", "type": "nominal", "scale": gscale, "legend": None},
                "tooltip": [{"field": "trail", "title": "Trail"}, {"field": "hours", "title": "Time (hours)"}, {"field": "km", "title": "Distance (km)"}]}},
  {"data": csv("trails_clean.csv"),
   "transform": [{"aggregate": [{"op": "mean", "field": "hours", "as": "avg"}, {"op": "max", "field": "hours", "as": "hi"}, {"op": "count", "as": "n"}], "groupby": ["map_group"]},
                 {"calculate": "'avg ' + format(datum.avg, '.1f') + ' h, ' + datum.n + (datum.n == 1 ? ' trail' : ' trails')", "as": "lab"}],
   "mark": {"type": "text", "align": "left", "dx": 10, "fontSize": 11.5, "fontWeight": 700, "color": INK},
   "encoding": {"x": {"field": "hi", "type": "quantitative", "scale": XS}, "text": {"field": "lab", "type": "nominal"}}},
  {"data": csv("trails_clean.csv"),
   "transform": [{"aggregate": [{"op": "mean", "field": "hours", "as": "avg"}], "groupby": ["map_group"]}],
   "mark": {"type": "tick", "color": INK, "thickness": 3, "size": 22},
   "encoding": {"x": {"field": "avg", "type": "quantitative", "scale": XS}}}]})

# 11 ── Vega treemap: every trail with a published distance, sized by km
col_dom = ["g:" + g for g in GROUPS]
save("treemap.vg.json", {
 "$schema": "https://vega.github.io/schema/vega/v5.json", "padding": 0,
 "autosize": {"type": "fit", "contains": "padding"},
 "signals": [{"name": "width", "init": "containerSize()[0]", "on": [{"events": "window:resize", "update": "containerSize()[0]"}]},
             {"name": "height", "value": 470}],
 "data": [
  {"name": "tree", "url": "data/treemap_nodes.csv", "format": {"type": "csv", "parse": {"km": "number", "total_km": "number"}},
   "transform": [{"type": "stratify", "key": "id", "parentKey": "parent"},
                 {"type": "treemap", "field": "km", "sort": {"field": "value", "order": "descending"}, "round": True, "method": "squarify",
                  "ratio": 1.2, "paddingInner": 1.5, "paddingOuter": 2, "paddingTop": 19, "size": [{"signal": "width"}, {"signal": "height"}]}]},
  {"name": "leaves", "source": "tree", "transform": [{"type": "filter", "expr": "!datum.children"}]},
  {"name": "groups", "source": "tree", "transform": [{"type": "filter", "expr": "datum.depth == 1"}]}],
 "scales": [{"name": "color", "type": "ordinal", "domain": col_dom, "range": GCOL}],
 "marks": [
  {"type": "rect", "from": {"data": "groups"},
   "encode": {"enter": {"fill": {"scale": "color", "field": "id"}, "fillOpacity": {"value": 0.18}},
              "update": {"x": {"field": "x0"}, "y": {"field": "y0"}, "x2": {"field": "x1"}, "y2": {"field": "y1"}}}},
  {"type": "rect", "from": {"data": "leaves"},
   "encode": {"enter": {"stroke": {"value": "#fff"}, "strokeWidth": {"value": 1}, "cursor": {"value": "pointer"}},
              "update": {"x": {"field": "x0"}, "y": {"field": "y0"}, "x2": {"field": "x1"}, "y2": {"field": "y1"},
                         "fill": {"scale": "color", "field": "parent"}, "fillOpacity": {"value": 0.92},
                         "tooltip": {"signal": "{'Trail': datum.full, 'Distance': datum.km + ' km', 'Grade band': datum.band}"}},
              "hover": {"fillOpacity": {"value": 1}, "stroke": {"value": "#14231F"}, "strokeWidth": {"value": 2}}}},
  {"type": "text", "from": {"data": "groups"},
   "encode": {"enter": {"font": {"value": "Overpass"}, "fontWeight": {"value": "bold"}, "fontSize": {"value": 12}, "fill": {"value": "#14231F"}, "baseline": {"value": "top"}},
              "update": {"x": {"signal": "datum.x0 + 5"}, "y": {"signal": "datum.y0 + 3"}, "limit": {"signal": "datum.x1 - datum.x0 - 8"},
                         "text": {"signal": "datum.name + '  ·  ' + format(datum.total_km, '.0f') + ' km'"}}}},
  {"type": "text", "from": {"data": "leaves"},
   "encode": {"enter": {"font": {"value": "Overpass"}, "fontSize": {"value": 11}, "fill": {"value": "#ffffff"}, "baseline": {"value": "top"}, "fontWeight": {"value": "600"}},
              "update": {"x": {"signal": "datum.x0 + 5"}, "y": {"signal": "datum.y0 + 4"}, "limit": {"signal": "datum.x1 - datum.x0 - 8"},
                         "text": {"signal": "(datum.x1 - datum.x0) > 46 && (datum.y1 - datum.y0) > 28 ? datum.name : ''"}}}}]})
print("specs written")
