/* Beyond the Distance: embeds each chart from its JSON spec and builds the trail table. */
(function () {
  "use strict";

  // Shared look for every chart (fonts, grid, legends). Specs only hold chart-specific choices.
  const config = {
    background: null,
    font: "Overpass",
    view: { stroke: null },
    axis: { labelFont: "Overpass", titleFont: "Overpass", labelFontSize: 11, titleFontSize: 12, titleFontWeight: 600,
            labelColor: "#3B4A45", titleColor: "#14231F", gridColor: "#DDE3DD", domainColor: "#9AA6A0", tickColor: "#9AA6A0" },
    legend: { labelFont: "Overpass", titleFont: "Overpass", labelFontSize: 11, titleFontSize: 12, titleFontWeight: 600, labelColor: "#3B4A45", titleColor: "#14231F" },
    header: { labelFont: "Overpass", titleFont: "Overpass" },
    text: { font: "Overpass" }
  };

  const charts = [
    ["#vis-symbols",    "specs/map_symbols.vl.json"],
    ["#vis-flow",       "specs/map_flow.vl.json"],
    ["#vis-scatter",    "specs/scatter.vl.json"],
    ["#vis-longest",    "specs/longest.vl.json"],
    ["#vis-treemap",    "specs/treemap.vg.json"],
    ["#vis-heatmap",    "specs/heatmap.vl.json"],
    ["#vis-timerange",  "specs/time_range.vl.json"],
    ["#vis-choropleth", "specs/map_choropleth.vl.json"],
    ["#vis-waffle",     "specs/waffle.vl.json"],
    ["#vis-skyline",    "specs/skyline.vl.json"],
    ["#vis-radial",     "specs/radial.vl.json"]
  ];

  function showError(selector, err) {
    const el = document.querySelector(selector);
    if (!el) return;
    el.innerHTML = '<p class="chart-error">This chart could not load. If you opened the file directly, serve the folder instead ' +
      '(VS Code Live Server, or <code>python3 -m http.server</code>) so the browser can read the data files.</p>';
    console.error(selector, err);
  }

  function embedAll() {
    charts.forEach(function (c) {
      const mode = c[1].indexOf(".vg.") > -1 ? "vega" : "vega-lite";
      vegaEmbed(c[0], c[1], { actions: false, renderer: "svg", mode: mode, config: config, tooltip: { theme: "custom" } })
        .catch(function (err) { showError(c[0], err); });
    });
  }

  // Wait for the web fonts so text is measured correctly inside the charts.
  const fontsReady = document.fonts && document.fonts.load
    ? Promise.all([document.fonts.load("600 12px Overpass"), document.fonts.load("700 14px Overpass")]).catch(function () {})
    : Promise.resolve();
  fontsReady.then(embedAll);

  // ---------- Trail table ----------
  const COLORS = { "SE Queensland": "#2F6E8E", "Wilsons Promontory": "#D98E04", "Flinders Ranges": "#B5472E", "Stirling Range": "#5F8A3C", "Larapinta Trail": "#8C3B72" };
  const AREA_LABEL = { "Mt Barney": "SE Queensland", "Springbrook": "SE Queensland", "Bluff Knoll": "Stirling Range" };
  const SOURCES = { S1: "QPWS Mount Barney", S2: "QPWS summit routes", S3: "Parks Victoria guide", S4: "Parks Victoria Sealers Cove", S5: "NT Parks sections",
                    S6: "Larapinta Trail Snapshot", S7: "Walking SA", S8: "SA Government", S9: "Trails WA", S10: "QPWS Springbrook" };
  const tbody = document.getElementById("rows"), count = document.getElementById("count"), q = document.getElementById("q"), areaSel = document.getElementById("area");
  let rows = [];

  function fmt(n) { return n === "" || n == null ? "not published" : String(n); }
  function timeText(r) { return r.hours_min === "" ? "not published" : (r.hours_min === r.hours_max ? r.hours_min : r.hours_min + " to " + r.hours_max); }
  function kmText(r) { return r.km === "" ? "not published" : r.km + (r.km_basis ? " (" + r.km_basis + ")" : ""); }

  function render() {
    const term = q.value.trim().toLowerCase(), area = areaSel.value;
    const shown = rows.filter(function (r) {
      const text = (r.trail + " " + r.area + " " + r.map_group + " " + r.grade_label).toLowerCase();
      return (!area || r.map_group === area) && (!term || text.indexOf(term) > -1);
    });
    tbody.innerHTML = shown.map(function (r) {
      const src = r.source_ids.split(";").map(function (s) { return SOURCES[s] || s; }).join("; ");
      return '<tr class="' + (r.role === "whole" ? "row-whole" : "") + '"><td><span class="dot" style="background:' + (COLORS[r.map_group] || "#888") + '"></span>' +
        r.trail + (r.role === "whole" ? " (not added to totals)" : "") + "</td><td>" + r.area + ", " + r.state + '</td><td class="num">' + kmText(r) +
        '</td><td class="num">' + timeText(r) + "</td><td>" + r.grade_label + "</td><td>" + src + "</td></tr>";
    }).join("");
    count.textContent = "Showing " + shown.length + " of " + rows.length + " rows.";
  }

  fetch("data/trails.csv").then(function (r) { return r.text(); }).then(function (text) {
    rows = vega.read(text, { type: "csv" });
    Array.from(new Set(rows.map(function (r) { return r.map_group; }))).forEach(function (g) {
      const o = document.createElement("option"); o.value = g; o.textContent = g; areaSel.appendChild(o);
    });
    q.addEventListener("input", render); areaSel.addEventListener("change", render);
    render();
  }).catch(function (err) { count.textContent = "The trail table could not load. Serve the folder with a local web server."; console.error(err); });
})();
