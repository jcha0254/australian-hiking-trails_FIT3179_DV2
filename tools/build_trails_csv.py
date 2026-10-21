"""Writes data/trails.csv: one row per trail, as published by the sources listed in data/sources.csv.

km and hours are the numbers printed by each source. km_basis says how the source measured
the walk: "return", "one way", or "as listed" when the source does not say.

Run it with:   python3 tools/build_trails_csv.py
(derive.py reads trails.csv, so run this one first.)
"""

import csv
import os

# The project folder is one level above tools/, so the script works from any folder.
PROJECT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(PROJECT_FOLDER, "data", "trails.csv")

# The column names of trails.csv. "id" is added when the file is written.
COLUMNS = ["id", "area", "map_group", "state", "trail", "role", "km", "km_basis",
           "hours_min", "hours_max", "grade_label", "band", "peak_m", "source_ids"]

# Every trail is added to this list as one row (without its id).
all_trails = []


def add_trail(area, map_group, state, trail, role, km, km_basis,
              hours_min, hours_max, grade_label, band, peak_m, source_ids):
    """Save one trail. The values are in the same order as COLUMNS (after the id)."""
    all_trails.append([area, map_group, state, trail, role, km, km_basis,
                       hours_min, hours_max, grade_label, band, peak_m, source_ids])


# ---------------------------------------------------------------
# One function per park (or group of parks)
# ---------------------------------------------------------------

def add_mt_barney():
    """Mt Barney National Park. Source S1 (and S2 for the summit routes), Queensland Parks."""

    # Four formed tracks. Each has a distance, a time and a grade.
    tracks = [
        # name, km, hours
        ("Yellow Pinch lookout", 2, 1),
        ("Lower Portals track", 7.4, 3),
        ("Upper Portals track", 8, 3),
        ("Cronan Creek Falls track", 12, 4),
    ]
    for name, km, hours in tracks:
        add_trail("Mt Barney", "SE Queensland", "QLD", name, "individual", km, "return",
                  hours, hours, "Grade 4", "Hard", "", "S1")

    # Three summit routes. The source gives a time range but no distance, and does not grade them.
    # I put them in the "Very hard" band myself. The last number is the height of the peak.
    summit_routes = [
        # name, hours_min, hours_max, peak height in metres
        ("South Ridge summit route", 8, 10, 1354),
        ("South East Ridge summit route", 7, 9, 1354),
        ("Mount Maroon summit route", 6, 6, 966),
    ]
    for name, hours_min, hours_max, peak in summit_routes:
        add_trail("Mt Barney", "SE Queensland", "QLD", name, "individual", "", "return",
                  hours_min, hours_max, "Summit route (not graded)", "Very hard", peak, "S1;S2")


def add_springbrook():
    """Springbrook National Park. Source S10, Queensland Parks. Just one trail."""
    add_trail("Springbrook", "SE Queensland", "QLD", "Warrie Circuit", "individual", 14, "return",
              5, 6, "Grade 4", "Hard", "", "S10")


def add_wilsons_prom():
    """Wilsons Promontory. Source S3 (Parks Victoria visitor guide) and S4 (Sealers Cove page)."""

    walks = [
        # name, km, how it is measured, hours, grade, band
        ("Loo-Errn Track", 1, "one way", 0.5, "Grade 2.1", "Easy"),
        ("Pillar Point", 3.6, "return", 1.5, "Grade 3", "Moderate"),
        ("Tidal Overlook Circuit", 3.8, "return", 1.5, "Grade 3", "Moderate"),
        ("Squeaky Beach walk", 4.2, "return", 1.5, "Grade 3", "Moderate"),
        ("Three Bays Walk", 12.4, "return", 4, "Grade 3", "Moderate"),
        ("Little Oberon Bay", 8.2, "return", 3, "Grade 3", "Moderate"),
        ("Mount Oberon Summit Walk", 6.8, "return", 2, "Grade 4", "Hard"),
        ("Lilly Pilly Nature Walk", 5.2, "return", 1.5, "Not graded in source", "Not graded"),
        ("Lilly Pilly Circuit", 5.8, "return", 2, "Grade 3", "Moderate"),
        ("Mount Bishop Summit Track", 7.4, "return", 2.5, "Grade 3", "Moderate"),
        ("Tongue Point from Darby Saddle", 5.6, "one way", 2.5, "Grade 4", "Hard"),
        ("Tongue Point from Darby River", 3.8, "one way", 2, "Grade 4", "Hard"),
        ("Prom Wildlife Walk", 2.3, "return", 0.75, "Grade 2.2", "Easy"),
        ("Cotters Lake and Beach", 2.4, "return", 1, "Grade 2.2", "Easy"),
        ("Millers Landing Nature Walk", 4, "return", 1.5, "Grade 2.2", "Easy"),
        ("Vereker Outlook", 6, "return", 2, "Grade 3", "Moderate"),
        ("Shallow Inlet", 0.4, "return", 0.5, "Grade 2.2", "Easy"),
    ]
    for name, km, km_basis, hours, grade, band in walks:
        add_trail("Wilsons Promontory", "Wilsons Promontory", "VIC", name, "individual", km, km_basis,
                  hours, hours, grade, band, "", "S3")

    # Sealers Cove comes from its own page (S4).
    add_trail("Wilsons Promontory", "Wilsons Promontory", "VIC", "Sealers Cove Walk", "individual", 10, "one way",
              3, 3, "Grade 4", "Hard", "", "S4")


def add_flinders_ranges():
    """Ikara-Flinders Ranges National Park. Source S7 (Walking SA), S8 for the St Mary Peak height.
    Walking SA gives a distance and a time but no grade."""

    walks = [
        # name, km, hours
        ("Sacred Canyon Walk", 0.8, 0.5),
        ("Wilpena Solar Power Station Walk", 1.2, 0.5),
        ("Boom and Bust Hike", 3.0, 2),
        ("Arkaroo Rock Hike", 3.1, 2),
        ("Living with Land Walk", 3.2, 1),
        ("Mount Ohlssen Bagge Hike", 5.6, 4),
        ("Hills Homestead Walk", 6.6, 2),
        ("Wangara Lookout Hike", 7, 3.5),
        ("Bunyeroo Gorge Hike", 7.5, 3.5),
        ("Trezona Hike", 8, 4),
        ("Yuluna Hike", 8, 4),
        ("Red Hill Lookout Hike", 8.4, 4),
        ("Bunyeroo and Wilcolo Creeks Hike", 9.2, 2.5),
        ("Wilkawillina Gorge Hike", 12.7, 7),
        ("Aroona to Youngoona Hike", 13.4, 7),
        ("Bridle Gap Hike", 18.6, 6),
        ("St Mary Peak Hike", 19, 9),
        ("Malloga Falls Hike", 23.2, 9),
    ]
    for name, km, hours in walks:
        peak = ""
        source_ids = "S7"
        if name == "St Mary Peak Hike":
            peak = 1171
            source_ids = "S7;S8"
        add_trail("Flinders Ranges", "Flinders Ranges", "SA", name, "individual", km, "as listed",
                  hours, hours, "Not graded in source", "Not graded", peak, source_ids)


def add_bluff_knoll():
    """Bluff Knoll in the Stirling Range. Source S9, Trails WA."""
    add_trail("Bluff Knoll", "Stirling Range", "WA", "Bluff Knoll (Bular Mial)", "individual", 6.8, "return",
              3, 4, "Grade 4", "Hard", 1098, "S9")


def add_larapinta():
    """Larapinta Trail. Distances come from NT Parks (S5). Hours and grades come from larapintatrail.com.au (S6)."""

    sections = [
        # name, km, hours, grade (the grade is also used as the band)
        ("Section 1: Telegraph Station to Simpsons Gap", 24.7, 9, "Hard"),
        ("Section 2: Simpsons Gap to Jay Creek", 26.2, 8.5, "Hard"),
        ("Section 3: Jay Creek to Standley Chasm", 13.6, 5.5, "Hard"),
        ("Section 4: Standley Chasm to 4/5 Junction", 17.9, 8.5, "Very hard"),
        ("Section 5: 4/5 Junction to Hugh Gorge", 14.9, 9.5, "Very hard"),
        ("Section 6: Hugh Gorge to Ellery Creek North", 28.9, 10.5, "Hard"),
        ("Section 7: Ellery Creek North to Serpentine Gorge", 12.8, 5, "Hard"),
        ("Section 8: Serpentine Gorge to Serpentine Chalet Dam", 13, 5.5, "Hard"),
        ("Section 9: Serpentine Chalet Dam to Ormiston Gorge", 28.9, 12, "Very hard"),
        ("Section 10: Ormiston Gorge to Finke River", 8.9, 4, "Moderate"),
        ("Section 11: Finke River to Redbank Gorge", 26.3, 9.5, "Hard"),
        ("Section 12: Redbank Gorge to Mount Sonder (return)", 15, 6, "Hard"),
    ]
    for name, km, hours, grade in sections:
        km_basis = "one way"
        peak = ""
        if name.startswith("Section 12"):
            km_basis = "return"   # Section 12 is a return trip up Mt Sonder
            peak = 1379
        add_trail("Larapinta Trail", "Larapinta Trail", "NT", name, "section", km, km_basis,
                  hours, hours, grade, grade, peak, "S5;S6")

    # The whole trail as one row. It has no time, and derive.py leaves it out of every total
    # so the sections are not counted twice.
    add_trail("Larapinta Trail", "Larapinta Trail", "NT", "Larapinta Trail (whole trail)", "whole", 223, "one way",
              "", "", "Sections graded Moderate to Very hard", "Mixed", 1379, "S5;S6")


# ---------------------------------------------------------------
# Writing the file
# ---------------------------------------------------------------

def write_trails_csv():
    """Write every trail to data/trails.csv, numbering them from 1."""
    with open(OUTPUT_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(COLUMNS)
        for number, trail in enumerate(all_trails, 1):
            writer.writerow([number] + trail)
    print(len(all_trails), "rows written")


def main():
    add_mt_barney()
    add_springbrook()
    add_wilsons_prom()
    add_flinders_ranges()
    add_bluff_knoll()
    add_larapinta()
    write_trails_csv()


if __name__ == "__main__":
    main()
