---
title: Exploratory Data Analysis 
---

## Exploratory Data Analysis

```js
// table
import {workbook, polis} from "./components/file-attachments.js";
display(Inputs.table(polis, {select: false}));
```

```js
// Leaflet Map
import L from "npm:leaflet@1.9.4";

// Load Leaflet's CSS as a stylesheet rather than as a JavaScript module. Sets the color of the leaflet.
if (!document.head.querySelector("link[data-leaflet-css]")) {
  const leafletCss = document.createElement("link");
  leafletCss.rel = "stylesheet";
  leafletCss.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
  leafletCss.dataset.leafletCss = "true";
  document.head.append(leafletCss);
}

/*  // Dark mode figure
if (!document.head.querySelector("style[data-dark-osm]")) {
  const darkOsmCss = document.createElement("style");
  darkOsmCss.dataset.darkOsm = "true";
  darkOsmCss.textContent = `
    .dark-osm-basemap .leaflet-tile-pane {
      filter: invert(90%) hue-rotate(180deg) brightness(0.65) saturate(0.7);
    }
  `;
  document.head.append(darkOsmCss);
}
*/

const validPolis = polis.filter(
  d => Number.isFinite(+d.Latitude) && Number.isFinite(+d.Longitude)
);

// define some colors for use throughout the project
const blue = [69, 136, 245];
const purple = [125, 75, 242]; 
const red = [247, 83, 72];

const staseisColor = value => {

  switch(true){
    case(value == 0):
        return `rgb(${blue})`
    case(value <= 10):
        return `rgb(${purple})`
    case(value >= 0):
        return `rgb(${red})`
  }
};


const escapeHtml = value => String(value ?? "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#039;");

const popupFor = d => {
  const hiddenFromTable = new Set([
    "Name",
    "Region name"
  ]);

  const tableRows = Object.entries(d)
    .filter(([key]) => !hiddenFromTable.has(key))
    .map(([key, value]) => {
      const renderedValue = key === "Pleiades link" && value
        ? `<a href="${escapeHtml(value)}" target="_blank" rel="noopener noreferrer">Open Pleiades record</a>`
        : escapeHtml(value);

      return `
        <tr>
          <th style="text-align:left; padding:2px 8px 2px 0; vertical-align:top;">${escapeHtml(key)}</th>
          <td style="padding:2px 0; vertical-align:top;">${renderedValue}</td>
        </tr>
      `;
    })
    .join("");

  return `
    <div style="font:12px system-ui, sans-serif; min-width:220px;">
      <div style="padding-bottom:7px; border-bottom:1px solid #ccc;">
        <div style="font-weight:700; font-size:14px;">${escapeHtml(d.Name)}</div>
        <div style="font-style:italic; color:#666; margin-top:2px;">${escapeHtml(d["Region name"])}</div>
      </div>
      <div style="max-height:120px; overflow-y:auto; margin-top:6px;">
        <table style="border-collapse:collapse; width:100%;">
          ${tableRows}
        </table>
      </div>
    </div>
  `;
};

// Leaflet creation
const mapElement = html`<div style="height:650px; width:100%;"></div>`;
const map = L.map(mapElement, {preferCanvas: true});

L.tileLayer(
  "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
  {
    maxZoom: 12,
    minZoom: 4,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    crossOrigin: true
  }
).addTo(map);

for (const d of validPolis) {
  const staseis = Number(d.staseis);
  const pointColor = Number.isFinite(staseis)
    ? staseisColor(staseis)
    : "#999999";

  const marker = L.circleMarker([+d.Latitude, +d.Longitude], {
    radius: 4,
    color: pointColor,
    weight: 1,
    fillColor: pointColor,
    fillOpacity: 0.72
  }).addTo(map);

  marker.bindPopup(popupFor(d), {minWidth: 260, maxWidth: 320});
  marker.on("mouseover", () => marker.openPopup());
  marker.on("mouseout", () => marker.closePopup());
}

const legend = L.control({position: "bottomright"});
legend.onAdd = () => {
  const div = L.DomUtil.create("div");
  div.style.cssText = "background:rgba(245, 236, 198,.86); color:#fff; padding:8px; font:12px system-ui, sans-serif; border: 1.5px solid #000";
  // Controls what's inside the legend
  div.innerHTML = `
    <div style="margin-bottom:4px; color:rgba(21, 23, 26)">Staseis count per Polis</div>
    <div style="display: flex; flex-direction: column; gap: 12px;">
        <span style="display: flex; align-items: center; gap: 8px;">
            <span style="display: inline-block; width: 12px; height: 12px; background-color: rgba(69, 136, 245, 0.5); border-radius: 50%; border: 2px solid rgba(69, 136, 245); box-sizing: border-box;"></span>
            <span style="color:rgba(21, 23, 26)">0</span>
        </span>
        <span style="display: flex; align-items: center; gap: 8px;">
            <span style="display: inline-block; width: 12px; height: 12px; background-color: rgba(125, 75, 242, 0.5); border-radius: 50%; border: 2px solid rgba(125, 75, 242); box-sizing: border-box;"></span>
            <span style="color:rgba(21, 23, 26)">0 to 10</span>
        </span>
        <span style="display: flex; align-items: center; gap: 8px;">
            <span style="display: inline-block; width: 12px; height: 12px; background-color: rgba(247, 83, 72, 0.5); border-radius: 50%; border: 2px solid rgba(247, 83, 72); box-sizing: border-box;"></span>
            <span style="color:rgba(21, 23, 26)">More than 10</span>
        </span>
    </div>
  `;
  return div;
};
legend.addTo(map);

L.control.scale().addTo(map);
display(mapElement);

// Fit after the map has been rendered so Leaflet can measure its dimensions.
requestAnimationFrame(() => {
  if (validPolis.length) {
    map.invalidateSize();
    map.fitBounds(
      validPolis.map(d => [+d.Latitude, +d.Longitude]),
      {padding: [40, 40], maxZoom: 6}
    );
  }
});

```

## Scatterplot

```js
// Scatterplot
import * as Plot from "npm:@observablehq/plot";

const xVariables = [
  {column: "staseis", label: "Staseis"},
  {column: "area 1", label: "Area 1"},
  {column: "area 2", label: "Area 2 (hectares)"},
  {column: "Elevation m", label: "Elevation (m)"},
  {column: "Victors", label: "Victors"}
];

const yVariables = [
  {column: "staseis", label: "Staseis"},
  {column: "Elevation m", label: "Elevation (m)"},
  {column: "area 2", label: "Area 2 (hectares)"},
  {column: "Colonies", label: "Colonies"}
];

const isNumber = value =>
  value !== null && value !== undefined && value !== "" && Number.isFinite(+value);

const filterState = {
  Democracy: null,
  Walls: null,
  Hellenicity: null,
  Polisity: null,
  promMin: 0,
  promMax: 21
};

const categoricalFilters = [
  {
    key: "Democracy",
    label: "Democracy",
    options: [
      {label: "All", value: null},
      {label: "Non-democracy", value: 1},
      {label: "Democracy", value: 2}
    ]
  },
  {
    key: "Walls",
    label: "Walls",
    options: [
      {label: "All", value: null},
      {label: "No walls", value: 0},
      {label: "Walled", value: 1}
    ]
  },
  {
    key: "Hellenicity",
    label: "Hellenicity",
    options: [
      {label: "All", value: null},
      {label: "Very Greek", value: 1},
      {label: "Mixed", value: 2},
      {label: "Barbarian", value: 3}
    ]
  },
  {
    key: "Polisity",
    label: "Polisity",
    options: [
      {label: "All", value: null},
      {label: "Certain", value: 1},
      {label: "Almost Certain", value: 1.5},
      {label: "Less Certain", value: 2},
      {label: "Not Certain", value: 3}
    ]
  }
];

const filterControls = html`<div style="margin:4px 0 12px; font:13px system-ui, sans-serif;"></div>`;

const makeButton = (label, selected, onClick) => {
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = label;
  button.style.margin = "2px 4px 2px 0";
  button.style.padding = "3px 7px";
  button.style.border = "1px solid #999";
  button.style.borderRadius = "3px";
  button.style.background = selected ? "#2c7fb8" : "#f4f4f4";
  button.style.color = selected ? "white" : "#222";
  button.setAttribute("aria-pressed", selected);
  button.addEventListener("click", onClick);
  return button;
};

for (const filter of categoricalFilters) {
  const row = document.createElement("div");
  row.style.marginBottom = "4px";

  const label = document.createElement("strong");
  label.textContent = `${filter.label}: `;
  row.append(label);

  for (const option of filter.options) {
    row.append(makeButton(option.label, filterState[filter.key] === option.value, () => {
      filterState[filter.key] = option.value;
      updateFilterButtons();
      renderPlot();
    }));
  }

  filterControls.append(row);
}

const prominenceRow = document.createElement("div");
prominenceRow.style.marginTop = "6px";

const prominenceLabel = document.createElement("strong");
prominenceLabel.textContent = "Prominence (prom 1): ";
prominenceRow.append(prominenceLabel);

const promMinInput = document.createElement("input");
promMinInput.type = "range";
promMinInput.min = 0;
promMinInput.max = 21;
promMinInput.step = 0.01;
promMinInput.value = 0;
promMinInput.style.verticalAlign = "middle";

const promMaxInput = document.createElement("input");
promMaxInput.type = "range";
promMaxInput.min = 0;
promMaxInput.max = 21;
promMaxInput.step = 0.01;
promMaxInput.value = 21;
promMaxInput.style.verticalAlign = "middle";

const promValue = document.createElement("span");
promValue.style.margin = "0 6px";

const promAllButton = makeButton("All", true, () => {
  filterState.promMin = 0;
  filterState.promMax = 21;
  promMinInput.value = 0;
  promMaxInput.value = 21;
  updateFilterButtons();
  renderPlot();
});

prominenceRow.append(
  document.createTextNode("min "),
  promMinInput,
  document.createTextNode(" max "),
  promMaxInput,
  promValue,
  promAllButton
);
filterControls.append(prominenceRow);

const updateFilterButtons = () => {
  for (const filter of categoricalFilters) {
    const row = [...filterControls.children].find(
      element => element.firstChild?.textContent === `${filter.label}: `
    );
    if (!row) continue;
    [...row.querySelectorAll("button")].forEach((button, i) => {
      const selected = filterState[filter.key] === filter.options[i].value;
      button.style.background = selected ? "#2c7fb8" : "#f4f4f4";
      button.style.color = selected ? "white" : "#222";
      button.setAttribute("aria-pressed", selected);
    });
  }

  promValue.textContent = ` ${filterState.promMin.toFixed(2)}–${filterState.promMax.toFixed(2)} `;
  const allProminence = filterState.promMin === 0 && filterState.promMax === 21;
  promAllButton.style.background = allProminence ? "#2c7fb8" : "#f4f4f4";
  promAllButton.style.color = allProminence ? "white" : "#222";
  promAllButton.setAttribute("aria-pressed", allProminence);
};

const updateProminence = (which, value) => {
  const numericValue = +value;
  if (which === "min") {
    filterState.promMin = Math.min(numericValue, filterState.promMax);
    promMinInput.value = filterState.promMin;
  } else {
    filterState.promMax = Math.max(numericValue, filterState.promMin);
    promMaxInput.value = filterState.promMax;
  }
  updateFilterButtons();
  renderPlot();
};

promMinInput.addEventListener("input", event => updateProminence("min", event.target.value));
promMaxInput.addEventListener("input", event => updateProminence("max", event.target.value));

const controls = html`
  <div style="display:flex; gap:18px; flex-wrap:wrap; margin-bottom:8px; font:14px system-ui, sans-serif;">
    <label>
      X-axis variable
      <select data-axis="x" style="margin-left:8px;">
        ${xVariables.map(({column, label}) => html`<option value=${column}>${label}</option>`)}
      </select>
    </label>
    <label>
      Y-axis variable
      <select data-axis="y" style="margin-left:8px;">
        ${yVariables.map(({column, label}) => html`<option value=${column}>${label}</option>`)}
      </select>
    </label>
  </div>
`;

const xSelect = controls.querySelector('select[data-axis="x"]');
const ySelect = controls.querySelector('select[data-axis="y"]');
xSelect.value = "area 2";
const stats = html`<div style="margin:4px 0 8px; font:13px system-ui, sans-serif;"></div>`;
const plotHolder = html`<div></div>`;
const container = html`<div></div>`;
container.append(controls, filterControls, stats, plotHolder);

const renderPlot = () => {
  const selectedX = xVariables.find(({column}) => column === xSelect.value);
  const selectedY = yVariables.find(({column}) => column === ySelect.value);

  const passesFilters = d => {
    const categoricalPass = categoricalFilters.every(filter =>
      filterState[filter.key] === null ||
      (isNumber(d[filter.key]) && +d[filter.key] === filterState[filter.key])
    );
    const prominencePass =
      (filterState.promMin === 0 && filterState.promMax === 21) ||
      (isNumber(d["prom 1"]) &&
        +d["prom 1"] >= filterState.promMin &&
        +d["prom 1"] <= filterState.promMax);

    return categoricalPass && prominencePass;
  };

  const filterMatched = polis.filter(passesFilters);
  const data = filterMatched.filter(
    d => isNumber(d[selectedX.column]) && isNumber(d[selectedY.column])
  );

  const points = data.map(d => ({
    x: +d[selectedX.column],
    y: +d[selectedY.column]
  }));

  const xMean = points.length ? points.reduce((sum, d) => sum + d.x, 0) / points.length : NaN;
  const yMean = points.length ? points.reduce((sum, d) => sum + d.y, 0) / points.length : NaN;
  const ssXX = points.reduce((sum, d) => sum + (d.x - xMean) ** 2, 0);
  const ssXY = points.reduce((sum, d) => sum + (d.x - xMean) * (d.y - yMean), 0);
  const slope = ssXX ? ssXY / ssXX : NaN;
  const intercept = Number.isFinite(slope) ? yMean - slope * xMean : NaN;
  const ssTot = points.reduce((sum, d) => sum + (d.y - yMean) ** 2, 0);
  const ssRes = Number.isFinite(slope)
    ? points.reduce((sum, d) => sum + (d.y - (intercept + slope * d.x)) ** 2, 0)
    : NaN;
  const rSquared = ssTot ? 1 - ssRes / ssTot : NaN;
  const xExtent = points.length
    ? [Math.min(...points.map(d => d.x)), Math.max(...points.map(d => d.x))]
    : [];
  const trendline = Number.isFinite(slope)
    ? xExtent.map(x => ({x, y: intercept + slope * x}))
    : [];

  stats.textContent = Number.isFinite(rSquared)
    ? `Linear trendline · R² = ${rSquared.toFixed(3)} · plotted n = ${points.length} · filter matches = ${filterMatched.length}`
    : `Linear trendline · R² unavailable · plotted n = ${points.length} · filter matches = ${filterMatched.length}`;

  const plot = Plot.plot({
    width: 850,
    height: 560,
    marginLeft: 70,
    marginBottom: 65,
    grid: true,
    x: {label: selectedX.label},
    y: {label: selectedY.label, nice: true},
    marks: [
      Plot.dot(data, {
        x: d => +d[selectedX.column],
        y: d => +d[selectedY.column],
        r: 4,
        fill: "#2c7fb8",
        fillOpacity: 0.62,
        stroke: "#123b5d",
        strokeOpacity: 0.35,
        title: d =>
          `${d.Name}\n${selectedX.label}: ${d[selectedX.column]}\n${selectedY.label}: ${d[selectedY.column]}`,
        tip: true
      }),
      Plot.line(trendline, {
        x: "x",
        y: "y",
        stroke: "#d7191c",
        strokeWidth: 2.5
      })
    ]
  });

  plotHolder.replaceChildren(plot);
};

xSelect.addEventListener("input", renderPlot);
ySelect.addEventListener("input", renderPlot);
updateFilterButtons();
renderPlot();
display(container);
```
