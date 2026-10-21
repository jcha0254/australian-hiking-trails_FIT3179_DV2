"""Builds the small helper files that the charts read, all from data/trails.csv.
Every file is overwritten each time, so it is safe to run again.

Run order:
    python3 tools/build_trails_csv.py     (writes data/trails.csv)
    python3 tools/derive.py               (this file)

Files written to data/:
    trails_clean.csv           one row per trail, with a single number for hours (five charts use this)
    groups.csv                 one row per walking area (the two maps)
    melbourne.csv              the start point of the flow map
    state_summary.csv          average hours per state (the choropleth)
    state_labels.csv           where the state names go on the choropleth
    waffle.csv                 one row per trail, with the position of its square (waffle chart)
    treemap_nodes.csv          the tree of areas and trails (treemap)
    skyline.csv                the three corner points of each peak's triangle (skyline chart)
    australia_states.geojson   the state outlines. Only rebuilt if tools/ne50.json exists (see the bottom of this file)

A note on names: "area" in trails.csv is the park (Mt Barney, Springbrook...), while
"map_group" is the coloured area used on the charts (SE Queensland, Wilsons Promontory...).
Mt Barney and Springbrook are both in the SE Queensland map group.
"""

import csv
import json
import math
import os
import re

# The project folder is one level above tools/, so the script works from any folder.
PROJECT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FOLDER = os.path.join(PROJECT_FOLDER, "data")

# Natural Earth's 50m states and provinces GeoJSON (public domain). Every feature needs
# "admin" and "name" in its properties. Save it here to rebuild australia_states.geojson.
NATURAL_EARTH_FILE = os.path.join(PROJECT_FOLDER, "tools", "ne50.json")


# ---------------------------------------------------------------
# Fixed values used by the maps and charts
# ---------------------------------------------------------------

MELBOURNE = (144.9631, -37.8136)   # (longitude, latitude)

# Where the single symbol for each map group is drawn: (longitude, latitude).
# One symbol per group keeps the maps readable.
AREA_POSITIONS = {
    "SE Queensland": (152.98, -28.26),
    "Wilsons Promontory": (146.355, -39.033),
    "Flinders Ranges": (138.606, -31.526),
    "Stirling Range": (118.256, -34.375),
    "Larapinta Trail": (133.0, -23.62),
}

# Label offsets in pixels for each group: (dx, dy, align) for the symbol map,
# then (fx, fy, falign) for the flow map. They are set by hand so labels do not overlap.
LABEL_OFFSETS = {
    "SE Queensland": (-28, -2, "right", -10, -12, "right"),
    "Wilsons Promontory": (-32, 6, "right", -12, 18, "right"),
    "Flinders Ranges": (-34, -2, "right", -10, 14, "right"),
    "Stirling Range": (16, -2, "left", 14, -8, "left"),
    "Larapinta Trail": (38, -2, "left", 12, -8, "left"),
}

STATE_NAMES = {
    "QLD": "Queensland",
    "VIC": "Victoria",
    "SA": "South Australia",
    "WA": "Western Australia",
    "NT": "Northern Territory",
}

# Where each state's label goes on the choropleth: name -> (longitude, latitude, abbreviation).
# This includes states with no trails, so they still get a label.
STATE_LABEL_POSITIONS = {
    "Northern Territory": (133.4, -19.6, "NT"),
    "Queensland": (144.6, -22.6, "QLD"),
    "South Australia": (135.3, -30.2, "SA"),
    "Western Australia": (122.0, -26.0, "WA"),
    "Victoria": (144.3, -36.6, "VIC"),
    "New South Wales": (146.6, -32.4, "NSW"),
    "Tasmania": (146.6, -42.1, "TAS"),
}

# The order grade bands are shown in on the waffle chart.
BAND_ORDER = ["Easy", "Moderate", "Hard", "Very hard", "Not graded"]

# The peaks drawn on the skyline chart: (name, map group, height in metres).
PEAKS = [
    ("Mt Sonder", "Larapinta Trail", 1379),
    ("Mt Barney", "SE Queensland", 1354),
    ("St Mary Peak", "Flinders Ranges", 1171),
    ("Bluff Knoll", "Stirling Range", 1098),
    ("Mt Maroon", "SE Queensland", 966),
]


# ---------------------------------------------------------------
# Small helper functions
# ---------------------------------------------------------------

def to_number(text):
    """Turn the text of a CSV cell into a number. An empty cell becomes None."""
    if text == "" or text is None:
        return None
    return float(text)


def make_short_name(trail_name):
    """'Section 5: 4/5 Junction to Hugh Gorge' becomes 'Larapinta S5'. Other names stay the same."""
    match = re.match(r"Section (\d+):", trail_name)
    if match:
        return "Larapinta S" + match.group(1)
    return trail_name


def time_bracket(hours):
    """Which time group a trail falls in. A trail sits in the slot of its lower number,
    so a 2 hour walk is in '2 to 4 h'."""
    if hours < 1:
        return "Under 1 h"
    if hours < 2:
        return "1 to 2 h"
    if hours < 4:
        return "2 to 4 h"
    if hours < 8:
        return "4 to 8 h"
    return "8 h or more"


def distance_km(point_a, point_b):
    """Straight-line (great-circle) distance in km between two (longitude, latitude)
    points, using the haversine formula."""
    earth_radius = 6371
    lat_a = math.radians(point_a[1])
    lat_b = math.radians(point_b[1])
    lon_difference = math.radians(point_b[0] - point_a[0])
    lat_difference = lat_b - lat_a
    h = (math.sin(lat_difference / 2) ** 2
         + math.cos(lat_a) * math.cos(lat_b) * math.sin(lon_difference / 2) ** 2)
    return 2 * earth_radius * math.asin(math.sqrt(h))


def total_km(trails):
    """Add up the distances. Trails with no published distance are skipped."""
    total = 0
    for trail in trails:
        if trail["km"] is not None:
            total = total + trail["km"]
    return total


def total_hours(trails):
    """Add up the hours."""
    total = 0
    for trail in trails:
        total = total + trail["hours"]
    return total


def find_longest(trails):
    """The trail with the biggest distance. If two tie, the first one wins."""
    longest = None
    for trail in trails:
        if trail["km"] is None:
            continue
        if longest is None or trail["km"] > longest["km"]:
            longest = trail
    return longest


def band_position(trail):
    """Position of the trail's grade band in BAND_ORDER (0 = Easy). Used for sorting."""
    return BAND_ORDER.index(trail["band"])


def write_csv(file_name, header, rows):
    """Write a CSV file into the data folder."""
    with open(os.path.join(DATA_FOLDER, file_name), "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)


# ---------------------------------------------------------------
# Reading the trails
# ---------------------------------------------------------------

def read_trails():
    """Read data/trails.csv and tidy each row. Returns every trail except the 'whole trail' row."""
    with open(os.path.join(DATA_FOLDER, "trails.csv"), newline="") as file:
        rows = list(csv.DictReader(file))

    trails = []
    for row in rows:
        row["km"] = to_number(row["km"])
        row["peak_m"] = to_number(row["peak_m"])
        row["short"] = make_short_name(row["trail"])

        # Some sources give a range (for example 8 to 10 hours). Use the middle value.
        hours_min = to_number(row["hours_min"])
        hours_max = to_number(row["hours_max"])
        if hours_min is None:
            row["hours"] = None
        else:
            row["hours"] = (hours_min + hours_max) / 2

        # The 'whole Larapinta Trail' row is left out of every total, because its 12
        # sections are already counted one by one.
        if row["role"] != "whole":
            trails.append(row)

    return trails


def group_by_map_group(trails):
    """Put the trails into groups, one per map group, in the order they first appear."""
    groups = {}
    for trail in trails:
        name = trail["map_group"]
        if name not in groups:
            groups[name] = []
        groups[name].append(trail)
    return groups


# ---------------------------------------------------------------
# One function for each file that gets written
# ---------------------------------------------------------------

def write_trails_clean(trails):
    """trails_clean.csv: the main file. Five charts read it."""
    rows = []
    for trail in trails:
        km = trail["km"]
        if km is None:
            km = ""
        rows.append([trail["id"], trail["trail"], trail["short"], trail["area"], trail["map_group"],
                     trail["state"], trail["role"], km, trail["km_basis"], trail["hours"],
                     trail["band"], trail["grade_label"], time_bracket(trail["hours"])])

    write_csv("trails_clean.csv",
              ["id", "trail", "short", "area", "map_group", "state", "role", "km", "km_basis",
               "hours", "band", "grade_label", "bracket"],
              rows)


def write_groups(groups):
    """groups.csv: one row per map group, with totals and the label positions for the two maps."""
    rows = []
    for name, group_trails in groups.items():
        lon, lat = AREA_POSITIONS[name]
        dx, dy, align, fx, fy, falign = LABEL_OFFSETS[name]
        longest = find_longest(group_trails)
        km_from_melbourne = round(distance_km(MELBOURNE, (lon, lat)))

        rows.append([name, group_trails[0]["state"], lon, lat, len(group_trails),
                     round(total_km(group_trails), 1), round(total_hours(group_trails), 1),
                     km_from_melbourne, longest["short"], longest["km"],
                     dx, dy, align, fx, fy, falign])

    write_csv("groups.csv",
              ["map_group", "state", "lon", "lat", "n_trails", "total_km", "total_hours",
               "km_from_melbourne", "longest_trail", "longest_km", "dx", "dy", "align", "fx", "fy", "falign"],
              rows)


def write_melbourne():
    """melbourne.csv: the start point of the flow map."""
    write_csv("melbourne.csv", ["name", "lon", "lat"], [["Melbourne", MELBOURNE[0], MELBOURNE[1]]])


def write_state_summary(trails):
    """state_summary.csv: average hours per trail for each state (the choropleth).
    Also returns the averages by state name, so the labels file can use them."""
    by_state = {}
    for trail in trails:
        state = trail["state"]
        if state not in by_state:
            by_state[state] = []
        by_state[state].append(trail)

    rows = []
    average_hours_by_name = {}
    for state, state_trails in by_state.items():
        name = STATE_NAMES[state]
        average_hours = round(total_hours(state_trails) / len(state_trails), 1)
        average_hours_by_name[name] = average_hours
        rows.append([state, name, len(state_trails), average_hours, round(total_km(state_trails), 1)])

    write_csv("state_summary.csv", ["state", "name", "n_trails", "avg_hours", "total_km"], rows)
    return average_hours_by_name


def write_state_labels(average_hours_by_name):
    """state_labels.csv: the text drawn on each state, such as 'NT' and '7.8 h'."""
    rows = []
    for name, position in STATE_LABEL_POSITIONS.items():
        lon, lat, abbreviation = position
        if name in average_hours_by_name:
            label = str(average_hours_by_name[name]) + " h"
            has_data = 1
        else:
            label = "no data"
            has_data = 0
        rows.append([name, lon, lat, abbreviation, label, has_data])

    write_csv("state_labels.csv", ["name", "lon", "lat", "abbr", "label", "has_data"], rows)


def write_waffle(groups):
    """waffle.csv: one square per trail, 6 squares per row, ordered from Easy to Not graded."""
    squares_per_row = 6
    rows = []
    for name, group_trails in groups.items():
        ordered_trails = sorted(group_trails, key=band_position)
        for position, trail in enumerate(ordered_trails):
            column = position % squares_per_row
            row_number = position // squares_per_row
            rows.append([name, trail["band"], column, row_number, trail["trail"]])

    write_csv("waffle.csv", ["map_group", "band", "col", "row", "trail"], rows)


def write_treemap_nodes(groups):
    """treemap_nodes.csv: a tree with a root, one node per map group and one leaf per trail.
    Each row points at its parent. Trails with no distance are left out."""
    rows = [["root", "", "All trails", "", "", "", ""]]

    for name, group_trails in groups.items():
        rows.append(["g:" + name, "root", name, "", "", name, round(total_km(group_trails), 1)])
        for trail in group_trails:
            if trail["km"] is not None:
                rows.append(["t:" + trail["id"], "g:" + name, trail["short"], trail["km"],
                             trail["band"], trail["trail"], ""])

    write_csv("treemap_nodes.csv", ["id", "parent", "name", "km", "band", "full", "total_km"], rows)


def write_skyline():
    """skyline.csv: each peak is a triangle made of three points (left foot, summit, right foot)."""
    rows = []
    for position, peak in enumerate(PEAKS):
        name, map_group, height = peak
        x = 15 * position                       # peaks are spaced 15 units apart
        rows.append([name, map_group, height, x - 7, 0, 0])        # left foot
        rows.append([name, map_group, height, x, height, 1])       # summit
        rows.append([name, map_group, height, x + 7, 0, 2])        # right foot

    write_csv("skyline.csv", ["peak", "map_group", "height_m", "x", "y", "ord"], rows)


# ---------------------------------------------------------------
# The state outlines (only needs running if the map shapes change)
# ---------------------------------------------------------------

def round_coordinates(coordinates):
    """Round every longitude and latitude to 3 decimals so the file stays small."""
    if isinstance(coordinates[0], (int, float)):
        return [round(coordinates[0], 3), round(coordinates[1], 3)]
    return [round_coordinates(part) for part in coordinates]


def polygon_is_on_map(polygon):
    """True if the middle of the polygon's outer edge is on mainland Australia or Tasmania.
    This drops far-off islands such as Macquarie Island."""
    outer_edge = polygon[0]
    middle_x = sum([point[0] for point in outer_edge]) / len(outer_edge)
    middle_y = sum([point[1] for point in outer_edge]) / len(outer_edge)
    return 112 <= middle_x <= 155 and -44.5 <= middle_y <= -9


def write_states_geojson():
    """australia_states.geojson: the Australian states only, taken from Natural Earth."""
    if not os.path.exists(NATURAL_EARTH_FILE):
        print("Skipped australia_states.geojson: " + NATURAL_EARTH_FILE + " not found (the existing file was left alone).")
        return

    with open(NATURAL_EARTH_FILE) as file:
        natural_earth = json.load(file)

    features = []
    for feature in natural_earth["features"]:
        properties = feature["properties"]
        if properties.get("admin") != "Australia":
            continue

        geometry = feature["geometry"]
        if geometry["type"] == "MultiPolygon":
            polygons = geometry["coordinates"]
        else:
            polygons = [geometry["coordinates"]]

        kept_polygons = []
        for polygon in polygons:
            if polygon_is_on_map(polygon):
                kept_polygons.append(round_coordinates(polygon))

        if kept_polygons:
            features.append({
                "type": "Feature",
                "properties": {"name": properties.get("name")},
                "geometry": {"type": "MultiPolygon", "coordinates": kept_polygons},
            })

    with open(os.path.join(DATA_FOLDER, "australia_states.geojson"), "w") as file:
        json.dump({"type": "FeatureCollection", "features": features}, file, separators=(",", ":"))

    print("states:", [feature["properties"]["name"] for feature in features])


# ---------------------------------------------------------------
# Numbers for the page text
# ---------------------------------------------------------------

def print_file(file_name):
    with open(os.path.join(DATA_FOLDER, file_name)) as file:
        print(file.read())


def print_facts(trails, groups):
    """Print some of the numbers quoted in index.html, so they can be checked against the data."""
    trails_with_km = [trail for trail in trails if trail["km"] is not None]
    print("trails (individual):", len(trails), "| with km:", len(trails_with_km))

    for name, group_trails in groups.items():
        print(name, len(group_trails), "trails;", round(total_hours(group_trails), 1), "h;",
              round(total_km(group_trails), 1), "km")

    print_file("groups.csv")
    print_file("state_summary.csv")

    trails_with_km.sort(key=lambda trail: trail["km"], reverse=True)
    print("longest:", [(trail["trail"][:22], trail["km"]) for trail in trails_with_km[:6]])

    band_counts = {}
    for trail in trails:
        band_counts[trail["band"]] = band_counts.get(trail["band"], 0) + 1
    print("bands:", band_counts)

    under_two_hours = len([trail for trail in trails if trail["hours"] < 2])
    eight_or_more = len([trail for trail in trails if trail["hours"] >= 8])
    print("share under 2h:", round(100 * under_two_hours / len(trails)), "%", "| 8h+:", eight_or_more)

    larapinta = groups["Larapinta Trail"]
    print("larapinta sum hours:", total_hours(larapinta), "sum km:", round(total_km(larapinta), 1))


# ---------------------------------------------------------------
# Run everything
# ---------------------------------------------------------------

def main():
    trails = read_trails()
    groups = group_by_map_group(trails)

    write_trails_clean(trails)
    write_groups(groups)
    write_melbourne()
    average_hours_by_name = write_state_summary(trails)
    write_state_labels(average_hours_by_name)
    write_waffle(groups)
    write_treemap_nodes(groups)
    write_skyline()
    write_states_geojson()
    print_facts(trails, groups)


if __name__ == "__main__":
    main()
