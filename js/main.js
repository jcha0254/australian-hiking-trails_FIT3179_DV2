// main.js
// Draws every chart on the page.
//
// How it works: each chart has its own spec file in the specs/ folder, and an empty
// <div> in index.html. This script finds each <div> and asks Vega-Embed to draw the
// spec file inside it. Vega-Embed comes from the <script> tags in index.html.

"use strict";


// ---------------------------------------------------------------
// 1. Settings shared by every chart
// ---------------------------------------------------------------
// Fonts, text colours and gridline colours are set once here, so the spec files
// only need to hold the choices that are specific to that one chart.

const FONT = "Overpass";
const DARK_TEXT = "#14231F";
const MID_TEXT = "#3B4A45";

const sharedConfig = {
  background: null,        // transparent, so the white card shows through
  font: FONT,
  view: { stroke: null },  // no outline around the plot area

  axis: {
    labelFont: FONT,
    titleFont: FONT,
    labelFontSize: 11,
    titleFontSize: 12,
    titleFontWeight: 600,
    labelColor: MID_TEXT,
    titleColor: DARK_TEXT,
    gridColor: "#DDE3DD",
    domainColor: "#9AA6A0",
    tickColor: "#9AA6A0"
  },

  legend: {
    labelFont: FONT,
    titleFont: FONT,
    labelFontSize: 11,
    titleFontSize: 12,
    titleFontWeight: 600,
    labelColor: MID_TEXT,
    titleColor: DARK_TEXT
  },

  header: { labelFont: FONT, titleFont: FONT },  // facet headers (the waffle chart)
  text: { font: FONT }                           // text marks drawn inside charts
};


// ---------------------------------------------------------------
// 2. The list of charts
// ---------------------------------------------------------------
// selector = the id of the <div> in index.html
// specFile = the file that describes the chart
// The treemap is the only plain Vega spec (".vg.json"). All the others are Vega-Lite.

const charts = [
  { selector: "#vis-symbols",    specFile: "specs/map_symbols.vl.json" },
  { selector: "#vis-flow",       specFile: "specs/map_flow.vl.json" },
  { selector: "#vis-scatter",    specFile: "specs/scatter.vl.json" },
  { selector: "#vis-longest",    specFile: "specs/longest.vl.json" },
  { selector: "#vis-treemap",    specFile: "specs/treemap.vg.json" },
  { selector: "#vis-timesplit",  specFile: "specs/time_split.vl.json" },
  { selector: "#vis-timerange",  specFile: "specs/time_range.vl.json" },
  { selector: "#vis-choropleth", specFile: "specs/map_choropleth.vl.json" },
  { selector: "#vis-waffle",     specFile: "specs/waffle.vl.json" },
  { selector: "#vis-skyline",    specFile: "specs/skyline.vl.json" },
  { selector: "#vis-rank",       specFile: "specs/larapinta_rank.vl.json" }
];

// The "..." menu on every chart only offers Save as SVG and Save as PNG.
const menuActions = {
  export: { svg: true, png: true },
  source: false,
  compiled: false,
  editor: false
};


// ---------------------------------------------------------------
// 3. Functions
// ---------------------------------------------------------------

// Vega-Embed needs to be told if a spec is Vega-Lite or plain Vega.
function getMode(specFile) {
  if (specFile.includes(".vg.")) {
    return "vega";
  }
  return "vega-lite";
}

// If a chart fails to load, show a short message in its place instead of an empty box.
// The most common cause is opening index.html straight from the folder: browsers
// block the chart from reading the data files unless the folder is served.
function showError(selector, error) {
  const box = document.querySelector(selector);
  if (!box) {
    return;
  }

  box.innerHTML =
    '<p class="chart-error">This chart could not load. If you opened the file directly, serve the folder instead ' +
    '(VS Code Live Server, or <code>python3 -m http.server</code>) so the browser can read the data files.</p>';

  console.error(selector, error);
}

// Draw one chart.
function drawChart(chart) {
  const options = {
    actions: menuActions,
    renderer: "svg",
    mode: getMode(chart.specFile),
    config: sharedConfig,
    tooltip: { theme: "custom" }
  };

  vegaEmbed(chart.selector, chart.specFile, options).catch(function (error) {
    showError(chart.selector, error);
  });
}

// Draw every chart in the list.
function drawAllCharts() {
  for (const chart of charts) {
    drawChart(chart);
  }
}

// Wait for the web fonts before drawing, so text is measured correctly inside the charts.
// If the fonts fail to load, carry on anyway and the charts use a fallback font.
function waitForFonts() {
  if (!document.fonts || !document.fonts.load) {
    return Promise.resolve();
  }

  const semibold = document.fonts.load("600 12px Overpass");
  const bold = document.fonts.load("700 14px Overpass");

  return Promise.all([semibold, bold]).catch(function () {});
}


// ---------------------------------------------------------------
// 4. Start
// ---------------------------------------------------------------
waitForFonts().then(drawAllCharts);
