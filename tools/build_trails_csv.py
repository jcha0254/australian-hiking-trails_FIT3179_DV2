"""Writes data/trails.csv: one row per trail, as published by the sources listed in data/sources.csv.
km and hours are the figures printed by each source; km_basis records how the source measured the walk."""
import csv

R = []
def add(*a): R.append(a)

# --- Mt Barney National Park (QPWS) ---
for t, km, h in [("Yellow Pinch lookout", 2, 1), ("Lower Portals track", 7.4, 3),
                 ("Upper Portals track", 8, 3), ("Cronan Creek Falls track", 12, 4)]:
    add("Mt Barney", "SE Queensland", "QLD", t, "individual", km, "return", h, h, "Grade 4", "Hard", "", "S1")
add("Mt Barney", "SE Queensland", "QLD", "South Ridge summit route", "individual", "", "return", 8, 10, "Summit route (not graded)", "Very hard", 1354, "S1;S2")
add("Mt Barney", "SE Queensland", "QLD", "South East Ridge summit route", "individual", "", "return", 7, 9, "Summit route (not graded)", "Very hard", 1354, "S1;S2")
add("Mt Barney", "SE Queensland", "QLD", "Mount Maroon summit route", "individual", "", "return", 6, 6, "Summit route (not graded)", "Very hard", 966, "S1;S2")

# --- Springbrook National Park (QPWS) ---
add("Springbrook", "SE Queensland", "QLD", "Warrie Circuit", "individual", 14, "return", 5, 6, "Grade 4", "Hard", "", "S10")

# --- Wilsons Promontory (Parks Victoria visitor guide + Sealers Cove page) ---
P = [("Loo-Errn Track", 1, "one way", 0.5, "Grade 2.1", "Easy"),
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
     ("Shallow Inlet", 0.4, "return", 0.5, "Grade 2.2", "Easy")]
for t, km, b, h, g, band in P:
    add("Wilsons Promontory", "Wilsons Promontory", "VIC", t, "individual", km, b, h, h, g, band, "", "S3")
add("Wilsons Promontory", "Wilsons Promontory", "VIC", "Sealers Cove Walk", "individual", 10, "one way", 3, 3, "Grade 4", "Hard", "", "S4")

# --- Ikara-Flinders Ranges National Park (Walking SA) ---
F = [("Sacred Canyon Walk", 0.8, 0.5), ("Wilpena Solar Power Station Walk", 1.2, 0.5), ("Boom and Bust Hike", 3.0, 2),
     ("Arkaroo Rock Hike", 3.1, 2), ("Living with Land Walk", 3.2, 1), ("Mount Ohlssen Bagge Hike", 5.6, 4),
     ("Hills Homestead Walk", 6.6, 2), ("Wangara Lookout Hike", 7, 3.5), ("Bunyeroo Gorge Hike", 7.5, 3.5),
     ("Trezona Hike", 8, 4), ("Yuluna Hike", 8, 4), ("Red Hill Lookout Hike", 8.4, 4),
     ("Bunyeroo and Wilcolo Creeks Hike", 9.2, 2.5), ("Wilkawillina Gorge Hike", 12.7, 7),
     ("Aroona to Youngoona Hike", 13.4, 7), ("Bridle Gap Hike", 18.6, 6),
     ("St Mary Peak Hike", 19, 9), ("Malloga Falls Hike", 23.2, 9)]
for t, km, h in F:
    pk = 1171 if t == "St Mary Peak Hike" else ""
    add("Flinders Ranges", "Flinders Ranges", "SA", t, "individual", km, "as listed", h, h,
        "Not graded in source", "Not graded", pk, "S7;S8" if pk else "S7")

# --- Bluff Knoll (Trails WA) ---
add("Bluff Knoll", "Stirling Range", "WA", "Bluff Knoll (Bular Mial)", "individual", 6.8, "return", 3, 4, "Grade 4", "Hard", 1098, "S9")

# --- Larapinta Trail (NT Parks distances; hours and grades from larapintatrail.com.au) ---
L = [("Section 1: Telegraph Station to Simpsons Gap", 24.7, 9, "Hard"),
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
     ("Section 12: Redbank Gorge to Mount Sonder (return)", 15, 6, "Hard")]
for t, km, h, band in L:
    s12 = t.startswith("Section 12")
    add("Larapinta Trail", "Larapinta Trail", "NT", t, "section", km, "return" if s12 else "one way", h, h,
        band, band, 1379 if s12 else "", "S5;S6")
add("Larapinta Trail", "Larapinta Trail", "NT", "Larapinta Trail (whole trail)", "whole", 223, "one way", "", "", "Sections graded Moderate to Very hard", "Mixed", 1379, "S5;S6")

with open("data/trails.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "area", "map_group", "state", "trail", "role", "km", "km_basis", "hours_min", "hours_max",
                "grade_label", "band", "peak_m", "source_ids"])
    for i, r in enumerate(R, 1):
        w.writerow([i] + list(r))
print(len(R), "rows written")
