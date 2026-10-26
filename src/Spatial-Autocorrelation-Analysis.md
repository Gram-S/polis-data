---
title: Spatial Autocorrelation Analysis
---

```js
import { polis } from "./components/file-attachments.js";
```

# Spatial Autocorrelation Analysis

## Geographic Representation

Then, we use _Leaflet_ in to plot the latitude and longitude of each Polis, as well as color them by their Staseis count. We choose to color them with a range rather than with a gradient, as a notable number of Polies contain 0 Staseis'. We impose a ternary classification with classes None (0), Some (1-9), Many (10+) for each Polis in regards to their Staseis count. Arbitrarily, we choose 10 (inclusive) to be the cutoff for the many category as it seems Staseis events are evenly distributed enough. That is to say, there is not a significant amount of Polies which would cause confusion in this range.

<!-- Figure 2. Leaflet -->

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
  (d) => Number.isFinite(+d.Latitude) && Number.isFinite(+d.Longitude),
);

// define some colors for use throughout the project
const blue = [69, 136, 245];
const purple = [125, 75, 242];
const red = [247, 83, 72];

const staseisColor = (value) => {
  switch (true) {
    case value == 0:
      return `rgb(${blue})`;
    case value < 10:
      return `rgb(${purple})`;
    case value >= 10:
      return `rgb(${red})`;
  }
};

const escapeHtml = (value) =>
  String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

const popupFor = (d) => {
  const hiddenFromTable = new Set(["Name", "Region name"]);

  const tableRows = Object.entries(d)
    .filter(([key]) => !hiddenFromTable.has(key))
    .map(([key, value]) => {
      const renderedValue =
        key === "Pleiades link" && value
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
const map = L.map(mapElement, { preferCanvas: true });

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 12,
  minZoom: 4,
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  crossOrigin: true,
}).addTo(map);

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
    fillOpacity: 0.72,
  }).addTo(map);

  marker.bindPopup(popupFor(d), { minWidth: 260, maxWidth: 320 });
  marker.on("mouseover", () => marker.openPopup());
  marker.on("mouseout", () => marker.closePopup());
}

const legend = L.control({ position: "bottomright" });
legend.onAdd = () => {
  const div = L.DomUtil.create("div");
  div.style.cssText =
    "background:rgba(245, 236, 198,.86); color:#fff; padding:8px; font:12px system-ui, sans-serif; font-weight: bold; border: 1.5px solid #000";
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
            <span style="color:rgba(21, 23, 26)">1 to 9</span>
        </span>
        <span style="display: flex; align-items: center; gap: 8px;">
            <span style="display: inline-block; width: 12px; height: 12px; background-color: rgba(247, 83, 72, 0.5); border-radius: 50%; border: 2px solid rgba(247, 83, 72); box-sizing: border-box;"></span>
            <span style="color:rgba(21, 23, 26)">10 or more</span>
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
      validPolis.map((d) => [+d.Latitude, +d.Longitude]),
      { padding: [40, 40], maxZoom: 6 },
    );
  }
});
```

<figcaption style="color: #666; font-size: 0.85em; margin-top: 4px;">
    Figure 2. Geographic Map of Polies. The gray boarder around landmasses has no relation to our analysis.
</figcaption>

## K-Nearest Neighbors

Each point will get k number of edges drawn between the k closest nodes, so that we can determine the staseis-ness of a point's cloesest neighbors. There is no formula to choosing the perfect k value, but in general 4-8 is commonly used. Starting with 4 we can see that this benefits the remotest points which do not have many neighbors but it will de-emphasize the conenctions between points closer to the center. k=8 suffers form the opposite problem, where it will work well for densely packed regions in Greece, but the remote cities are ahving way too many connections made to cities that are not that close.

<!-- Figure 4. KNN Networks -->

```js
import * as d3 from "npm:d3@7";

const [networkNodes, networkK4, networkK6, networkK8] = await Promise.all([
  FileAttachment("./data/knn-poleis.geojson").json(),
  FileAttachment("./data/knn-k4.geojson").json(),
  FileAttachment("./data/knn-k6.geojson").json(),
  FileAttachment("./data/knn-k8.geojson").json(),
]);

const networksByK = new Map([
  [4, networkK4],
  [6, networkK6],
  [8, networkK8],
]);

const nodeColor = (staseis) => {
  const value = Number(staseis);
  if (value === 0) return "#22c55e";
  if (value >= 10) return "#ef4444";
  return "#ffd60a";
};

const networkControls = html`
  <div
    style="display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin:0 0 10px; font:14px system-ui, sans-serif;"
  >
    <label for="network-k" style="font-weight:650;"
      >Nearest neighbors (k)</label
    >
    <select
      id="network-k"
      style="padding:5px 28px 5px 8px; border:1px solid #aaa; border-radius:4px; background:white; color:#222;"
    >
      <option value="4">4</option>
      <option value="6">6</option>
      <option value="8">8</option>
    </select>
    <span data-network-status style="color:#666;"></span>
    <span aria-hidden="true" style="flex:1;"></span>
    <button data-zoom-in type="button" style="padding:4px 9px;">Zoom in</button>
    <button data-zoom-out type="button" style="padding:4px 9px;">
      Zoom out
    </button>
    <button data-reset type="button" style="padding:4px 9px;">
      Reset view
    </button>
  </div>
`;

const plotWidth = 1100;
const plotHeight = 650;
const networkPlotShell = html`
  <div
    style="position:relative; width:100%; background:#fbfaf6; border:1px solid #d7d1c3; border-radius:4px; overflow:hidden; touch-action:none;"
  >
    <svg
      viewBox="0 0 ${plotWidth} ${plotHeight}"
      role="img"
      aria-label="Zoomable k-nearest-neighbor network plot of ancient Greek poleis"
      style="display:block; width:100%; height:auto; min-height:420px; cursor:grab;"
    ></svg>
    <div
      data-network-tooltip
      style="position:absolute; display:none; z-index:3; pointer-events:none; min-width:180px; padding:8px 10px; background:rgba(255,255,255,.97); color:#222; border:1px solid #777; border-radius:4px; box-shadow:0 2px 10px rgba(0,0,0,.2); font:12px system-ui,sans-serif;"
    ></div>
    <div
      style="position:absolute; right:10px; bottom:10px; padding:9px 11px; background:rgba(255,255,255,.94); color:#222; border:1px solid #777; border-radius:3px; box-shadow:0 1px 5px rgba(0,0,0,.18); font:12px system-ui,sans-serif; line-height:1.35; pointer-events:none;"
    >
      <div style="font-weight:700; margin-bottom:5px;">Nodes · staseis</div>
      <div>
        <span style="color:#22c55e; font-size:18px; vertical-align:-2px;"
          >●</span
        >
        0
      </div>
      <div>
        <span style="color:#ffd60a; font-size:18px; vertical-align:-2px;"
          >●</span
        >
        1–9
      </div>
      <div>
        <span style="color:#ef4444; font-size:18px; vertical-align:-2px;"
          >●</span
        >
        10+
      </div>
      <div style="font-weight:700; margin:7px 0 5px;">Edges · distance</div>
      <div>
        <span
          style="display:inline-block; width:20px; border-top:3px solid #2563eb; margin-right:5px; vertical-align:middle;"
        ></span
        >0–&lt;50 km
      </div>
      <div>
        <span
          style="display:inline-block; width:20px; border-top:3px solid #7c3aed; margin-right:5px; vertical-align:middle;"
        ></span
        >50–&lt;100 km
      </div>
      <div>
        <span
          style="display:inline-block; width:20px; border-top:3px solid #ff2bd6; margin-right:5px; vertical-align:middle;"
        ></span
        >100+ km
      </div>
    </div>
  </div>
`;

const networkSvg = d3.select(networkPlotShell.querySelector("svg"));
const projection = d3.geoMercator().fitExtent(
  [
    [24, 24],
    [plotWidth - 24, plotHeight - 24],
  ],
  networkNodes,
);
const geoPath = d3.geoPath(projection);
const zoomLayer = networkSvg.append("g");

zoomLayer
  .append("path")
  .datum(d3.geoGraticule10())
  .attr("d", geoPath)
  .attr("fill", "none")
  .attr("stroke", "#ddd8cb")
  .attr("stroke-width", 0.7)
  .attr("vector-effect", "non-scaling-stroke");

const edgeLayer = zoomLayer
  .append("g")
  .attr("fill", "none")
  .attr("stroke-linecap", "round");

const edgeBands = [
  { key: "near", color: "#2563eb", matches: (distance) => distance < 50 },
  {
    key: "middle",
    color: "#7c3aed",
    matches: (distance) => distance >= 50 && distance < 100,
  },
  { key: "far", color: "#ff2bd6", matches: (distance) => distance >= 100 },
];

const edgePaths = edgeLayer
  .selectAll("path")
  .data(edgeBands)
  .join("path")
  .attr("stroke", (band) => band.color)
  .attr("stroke-width", 1.15)
  .attr("stroke-opacity", 0.58)
  .attr("vector-effect", "non-scaling-stroke");

const tooltip = networkPlotShell.querySelector("[data-network-tooltip]");
const nodeSelection = zoomLayer
  .append("g")
  .selectAll("circle")
  .data(networkNodes.features)
  .join("circle")
  .attr("cx", (feature) => projection(feature.geometry.coordinates)[0])
  .attr("cy", (feature) => projection(feature.geometry.coordinates)[1])
  .attr("r", 1.05)
  .attr("fill", (feature) => nodeColor(feature.properties.staseis))
  .attr("fill-opacity", 0.93)
  .attr("stroke", "#222")
  .attr("stroke-width", 0.65)
  .attr("vector-effect", "non-scaling-stroke")
  .style("cursor", "crosshair")
  .on("pointerenter pointermove", (event, feature) => {
    const properties = feature.properties;
    tooltip.replaceChildren(
      Object.assign(document.createElement("div"), {
        textContent: properties.name ?? "Unnamed polis",
      }),
      Object.assign(document.createElement("div"), {
        textContent: properties.region ?? "",
      }),
      Object.assign(document.createElement("div"), {
        textContent: `Staseis: ${properties.staseis ?? "—"}`,
      }),
      Object.assign(document.createElement("div"), {
        textContent: `Prominence: ${properties.prom1 ?? "—"}`,
      }),
      Object.assign(document.createElement("div"), {
        textContent: `Polis ID: ${properties.polis_id ?? "—"}`,
      }),
    );
    tooltip.children[0].style.cssText = "font-size:14px; font-weight:700;";
    tooltip.children[1].style.cssText =
      "color:#666; font-style:italic; margin:2px 0 7px;";
    const [x, y] = d3.pointer(event, networkPlotShell);
    tooltip.style.left = `${Math.max(8, Math.min(x + 12, networkPlotShell.clientWidth - 210))}px`;
    tooltip.style.top = `${Math.max(8, y - 18)}px`;
    tooltip.style.display = "block";
    d3.select(event.currentTarget).attr("r", 1.625);
  })
  .on("pointerleave", (event) => {
    tooltip.style.display = "none";
    d3.select(event.currentTarget).attr("r", 1.05);
  });

const networkStatus = networkControls.querySelector("[data-network-status]");

const renderNetwork = (k) => {
  const network = networksByK.get(k);
  edgePaths.attr("d", (band) =>
    geoPath({
      type: "MultiLineString",
      coordinates: network.features
        .filter((feature) =>
          band.matches(Number(feature.properties.distance_km)),
        )
        .map((feature) => feature.geometry.coordinates),
    }),
  );
  networkStatus.textContent = `${network.features.length.toLocaleString()} edges`;
};

networkControls.querySelector("select").addEventListener("change", (event) => {
  renderNetwork(Number(event.target.value));
});

const networkZoom = d3
  .zoom()
  .scaleExtent([1, 18])
  .on("zoom", (event) => {
    zoomLayer.attr("transform", event.transform);
  });

networkSvg.call(networkZoom);
networkSvg.on("dblclick.zoom", null);
networkControls
  .querySelector("[data-zoom-in]")
  .addEventListener("click", () => {
    networkSvg.transition().duration(180).call(networkZoom.scaleBy, 1.5);
  });
networkControls
  .querySelector("[data-zoom-out]")
  .addEventListener("click", () => {
    networkSvg
      .transition()
      .duration(180)
      .call(networkZoom.scaleBy, 1 / 1.5);
  });
networkControls.querySelector("[data-reset]").addEventListener("click", () => {
  networkSvg
    .transition()
    .duration(220)
    .call(networkZoom.transform, d3.zoomIdentity);
});

renderNetwork(4);

const networkFigure = html`<div></div>`;
networkFigure.append(networkControls, networkPlotShell);
display(networkFigure);
```

<figcaption style="color: #666; font-size: 0.85em; margin-top: 4px;">
    Figure 4. Network Visualization of cities' k-nearest cities symbolized by edge distance.
</figcaption>

## Global Moran's I

Using k=6, we calculate Global Moran's I for both original staseis and log(1+staseis), and print the results in a table. Then, we visualize the spatial lag on a Moran Scatterplot.

<!-- Table 2. Global Moran's I Results Table -->

```js
const moranK6 = await FileAttachment("./data/global-moran-k6.json").json();
const moranSummary = moranK6.summary;
const formatMoran = (value) => Number(value).toFixed(4);
const significanceLabel = (value) =>
  value < 0.001 ? "p < 0.001" : `p = ${formatMoran(value)}`;

const moranTableRows = [
  ["Number of cities", moranSummary.number_of_cities.toLocaleString()],
  ["Spatial weights", "Binary symmetric KNN, k = 6, row-standardized"],
  [
    "Unique network connections",
    moranSummary.unique_network_connections.toLocaleString(),
  ],
  ["Global Moran's I", formatMoran(moranSummary.staseis.moran_i), true],
  [
    "Permutation p-value",
    formatMoran(moranSummary.staseis.permutation_p_value),
    true,
  ],
  [
    "Global Moran's I, log(1 + staseis)",
    formatMoran(moranSummary.log1p_staseis.moran_i),
    true,
  ],
  [
    "Permutation p-value, log(1 + staseis)",
    formatMoran(moranSummary.log1p_staseis.permutation_p_value),
    true,
  ],
  [
    "Expected Moran's I under spatial randomness",
    formatMoran(moranSummary.expected_i),
  ],
  ["Random permutations", moranK6.method.permutations.toLocaleString()],
  [
    "Statistical significance",
    `Raw: ${significanceLabel(moranSummary.staseis.permutation_p_value)} · Log: ${significanceLabel(moranSummary.log1p_staseis.permutation_p_value)}`,
    true,
  ],
];

const moranTable = document.createElement("div");
moranTable.style.cssText = "overflow-x:auto; margin:8px 0 4px;";

const moranTableElement = document.createElement("table");
moranTableElement.style.cssText =
  "width:100%; border-collapse:collapse; table-layout:fixed; font:13px system-ui,sans-serif;";

const moranTableHead = moranTableElement.createTHead();
const moranHeaderRow = moranTableHead.insertRow();
moranHeaderRow.style.borderBottom = "1.5px solid #aaa";
for (const [heading, alignment, width] of [
  ["Statistic", "left", "62%"],
  ["Result", "right", "38%"],
]) {
  const cell = document.createElement("th");
  cell.textContent = heading;
  cell.style.cssText = `padding:8px 6px; text-align:${alignment}; width:${width};`;
  moranHeaderRow.append(cell);
}

const moranTableBody = moranTableElement.createTBody();
for (const [label, result, emphasized] of moranTableRows) {
  const row = moranTableBody.insertRow();
  row.style.cssText = `border-bottom:1px solid #e4e4e4; font-weight:${emphasized ? 650 : 400};`;

  const labelCell = row.insertCell();
  labelCell.textContent = label;
  labelCell.style.cssText = "padding:10px 6px; text-align:left;";

  const resultCell = row.insertCell();
  resultCell.textContent = result;
  resultCell.style.cssText =
    "padding:10px 6px; text-align:right; overflow-wrap:anywhere;";
}

moranTable.append(moranTableElement);

display(moranTable);
```

<figcaption style="color: #666; font-size: 0.85em; margin-top: 4px;">
    Table 2. Global Moran's I results table.
</figcaption>

Both statistics are positive and significant at p &lt; 0.001, indicating weak but statistically significant spatial clustering of staseis among the k=6 neighbor network. The slightly larger value after applying log(1 + staseis) shows that the positive autocorrelation persists after reducing the influence of the largest counts.

<!-- Figure 5. Global Moran's I Scatterplot -->

```js
const moranPoints = moranK6.scatterplot;
const moranWidth = 900;
const moranHeight = 590;
const moranMargin = { top: 38, right: 32, bottom: 58, left: 70 };
const moranX = d3
  .scaleLinear()
  .range([moranMargin.left, moranWidth - moranMargin.right]);
const moranY = d3
  .scaleLinear()
  .range([moranHeight - moranMargin.bottom, moranMargin.top]);

const moranMeasures = {
  raw: {
    label: "Original staseis",
    xField: "standardized_staseis",
    lagField: "spatial_lag",
    summary: moranSummary.staseis,
  },
  log: {
    label: "log(1 + staseis)",
    xField: "standardized_log1p_staseis",
    lagField: "spatial_lag_log1p",
    summary: moranSummary.log1p_staseis,
  },
};
let activeMoranMeasure = moranMeasures.raw;

const moranControls = html`
  <div
    style="display:flex; align-items:center; gap:9px; margin:8px 0 10px; font:14px system-ui,sans-serif;"
  >
    <label for="moran-measure" style="font-weight:650;"
      >Scatterplot measure</label
    >
    <select
      id="moran-measure"
      style="padding:5px 28px 5px 8px; border:1px solid #aaa; border-radius:4px; background:white; color:#222;"
    >
      <option value="raw">Original staseis</option>
      <option value="log">log(1 + staseis)</option>
    </select>
  </div>
`;

const moranPlotShell = html`
  <div style="position:relative; width:100%; margin-top:8px;">
    <svg
      viewBox="0 0 ${moranWidth} ${moranHeight}"
      role="img"
      aria-label="Global Moran's I scatterplot of standardized staseis and its k=6 spatial lag"
      style="display:block; width:100%; height:auto; background:#fff; border:1px solid #ddd;"
    ></svg>
    <div
      data-moran-tooltip
      style="position:absolute; display:none; z-index:2; pointer-events:none; min-width:170px; padding:8px 10px; background:rgba(255,255,255,.97); color:#222; border:1px solid #777; border-radius:4px; box-shadow:0 2px 10px rgba(0,0,0,.2); font:12px system-ui,sans-serif;"
    ></div>
  </div>
`;

const moranSvg = d3.select(moranPlotShell.querySelector("svg"));
const moranXAxis = moranSvg
  .append("g")
  .attr("transform", `translate(0,${moranHeight - moranMargin.bottom})`);
const moranYAxis = moranSvg
  .append("g")
  .attr("transform", `translate(${moranMargin.left},0)`);

const moranVerticalZero = moranSvg
  .append("line")
  .attr("y1", moranMargin.top)
  .attr("y2", moranHeight - moranMargin.bottom)
  .attr("stroke", "#777")
  .attr("stroke-dasharray", "4,4");
const moranHorizontalZero = moranSvg
  .append("line")
  .attr("x1", moranMargin.left)
  .attr("x2", moranWidth - moranMargin.right)
  .attr("stroke", "#777")
  .attr("stroke-dasharray", "4,4");

const moranTrendLine = moranSvg
  .append("line")
  .attr("stroke", "#008c95")
  .attr("stroke-width", 2);

const moranQuadrantLabels = moranSvg
  .append("g")
  .selectAll("text")
  .data([
    { label: "LH", corner: "top-left" },
    { label: "HH", corner: "top-right" },
    { label: "LL", corner: "bottom-left" },
    { label: "HL", corner: "bottom-right" },
  ])
  .join("text")
  .attr("fill", "#999")
  .attr("font-size", 12)
  .attr("font-weight", 700)
  .text((label) => label.label);

const moranTooltip = moranPlotShell.querySelector("[data-moran-tooltip]");
const moranPointColor = (staseis) =>
  Number(staseis) >= 10 ? "#e00000" : nodeColor(staseis);
const moranPointSelection = moranSvg
  .append("g")
  .selectAll("circle")
  .data(moranPoints)
  .join("circle")
  .attr("r", 3)
  .attr("fill", (point) => moranPointColor(point.staseis))
  .attr("fill-opacity", 0.62)
  .attr("stroke", "#333")
  .attr("stroke-width", 0.35)
  .on("pointerenter pointermove", (event, point) => {
    moranTooltip.replaceChildren(
      Object.assign(document.createElement("div"), {
        textContent: point.name ?? "Unnamed polis",
      }),
      Object.assign(document.createElement("div"), {
        textContent: point.region ?? "",
      }),
      Object.assign(document.createElement("div"), {
        textContent: `Staseis: ${point.staseis}`,
      }),
      Object.assign(document.createElement("div"), {
        textContent: `Standardized ${activeMoranMeasure.label}: ${point[activeMoranMeasure.xField].toFixed(3)}`,
      }),
      Object.assign(document.createElement("div"), {
        textContent: `Spatial lag: ${point[activeMoranMeasure.lagField].toFixed(3)}`,
      }),
    );
    moranTooltip.children[0].style.cssText = "font-size:14px; font-weight:700;";
    moranTooltip.children[1].style.cssText =
      "color:#666; font-style:italic; margin:2px 0 7px;";
    const [x, y] = d3.pointer(event, moranPlotShell);
    moranTooltip.style.left = `${Math.max(8, Math.min(x + 12, moranPlotShell.clientWidth - 205))}px`;
    moranTooltip.style.top = `${Math.max(8, y - 18)}px`;
    moranTooltip.style.display = "block";
    d3.select(event.currentTarget).attr("r", 5);
  })
  .on("pointerleave", (event) => {
    moranTooltip.style.display = "none";
    d3.select(event.currentTarget).attr("r", 3);
  });

const moranXAxisLabel = moranSvg
  .append("text")
  .attr("x", moranWidth / 2)
  .attr("y", moranHeight - 12)
  .attr("text-anchor", "middle")
  .attr("font", "13px system-ui, sans-serif");
const moranYAxisLabel = moranSvg
  .append("text")
  .attr("transform", "rotate(-90)")
  .attr("x", -moranHeight / 2)
  .attr("y", 18)
  .attr("text-anchor", "middle")
  .attr("font", "13px system-ui, sans-serif");
const moranAnnotation = moranSvg
  .append("text")
  .attr("x", moranWidth - moranMargin.right)
  .attr("y", 22)
  .attr("text-anchor", "end")
  .attr("font", "600 13px system-ui, sans-serif");

const renderMoranScatterplot = (measureKey) => {
  activeMoranMeasure = moranMeasures[measureKey];
  const xField = activeMoranMeasure.xField;
  const lagField = activeMoranMeasure.lagField;
  const xLimit = d3.max(moranPoints, (point) => Math.abs(point[xField])) * 1.04;
  const yLimit =
    d3.max(moranPoints, (point) => Math.abs(point[lagField])) * 1.08;
  moranX.domain([-xLimit, xLimit]).nice();
  moranY.domain([-yLimit, yLimit]).nice();

  moranXAxis.call(d3.axisBottom(moranX).ticks(8).tickSizeOuter(0));
  moranYAxis.call(d3.axisLeft(moranY).ticks(8).tickSizeOuter(0));
  moranVerticalZero.attr("x1", moranX(0)).attr("x2", moranX(0));
  moranHorizontalZero.attr("y1", moranY(0)).attr("y2", moranY(0));

  const slope = activeMoranMeasure.summary.moran_i;
  const lineDomain = moranX.domain();
  moranTrendLine
    .attr("x1", moranX(lineDomain[0]))
    .attr("y1", moranY(slope * lineDomain[0]))
    .attr("x2", moranX(lineDomain[1]))
    .attr("y2", moranY(slope * lineDomain[1]));

  moranQuadrantLabels
    .attr("x", (label) =>
      label.corner.endsWith("left")
        ? moranMargin.left + 12
        : moranWidth - moranMargin.right - 28,
    )
    .attr("y", (label) =>
      label.corner.startsWith("top")
        ? moranMargin.top + 18
        : moranHeight - moranMargin.bottom - 10,
    );

  moranPointSelection
    .transition()
    .duration(240)
    .attr("cx", (point) => moranX(point[xField]))
    .attr("cy", (point) => moranY(point[lagField]));

  moranXAxisLabel.text(`Standardized ${activeMoranMeasure.label}`);
  moranYAxisLabel.text(
    `Spatial lag of standardized ${activeMoranMeasure.label} (k = 6)`,
  );
  moranAnnotation.text(
    `Moran's I = ${formatMoran(slope)} · permutation p = ${formatMoran(activeMoranMeasure.summary.permutation_p_value)}`,
  );
};

moranControls.querySelector("select").addEventListener("change", (event) => {
  moranTooltip.style.display = "none";
  renderMoranScatterplot(event.target.value);
});

renderMoranScatterplot("raw");

const moranFigure = html`<div></div>`;
moranFigure.append(moranControls, moranPlotShell);
display(moranFigure);
```

<figcaption style="color: #666; font-size: 0.85em; margin-top: 4px;">
    Figure 5. Global Moran's I spatial lag scatterplot.
</figcaption>

## Local Moran's I

Local Moran's I identifies individual cities that participate in statistically significant local clusters or spatial outliers. Use the controls below to compare the classifications calculated from original staseis with those calculated after applying log(1 + staseis). The optional k=6 network overlay shows the neighbor relationships used by the analysis.

<!-- Figure 6. Local Moran's I LISA map -->

```js
const [lisaRawData, lisaLogData] = await Promise.all([
  FileAttachment("./data/lisa-k6-raw.geojson").json(),
  FileAttachment("./data/lisa-k6-log.geojson").json()
]);

const lisaDataByMode = new Map([
  ["raw", {label: "Normal LISA", data: lisaRawData}],
  ["log", {label: "Log LISA", data: lisaLogData}]
]);

const lisaClusterColor = classification => {
  const normalized = String(classification ?? "")
    .toLowerCase()
    .replaceAll("–", "-")
    .replaceAll("—", "-");
  switch (normalized) {
    case "high-high": return "#ff1744";
    case "low-high": return "#00e676";
    case "high-low": return "#ff9800";
    case "low-low": return "#2979ff";
    default: return "#9e9e9e";
  }
};

const escapeLisaHtml = value => String(value ?? "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#039;");
const formatLisaNumber = value => Number.isFinite(+value) ? (+value).toFixed(4) : "—";

const lisaControls = html`
  <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin:8px 0 10px; font:14px system-ui,sans-serif;">
    <span style="font-weight:650;">LISA measure</span>
    <button data-lisa-mode="raw" type="button" aria-pressed="true" style="padding:5px 10px; border:1px solid #2563eb; border-radius:4px; background:#2563eb; color:white;">Normal LISA</button>
    <button data-lisa-mode="log" type="button" aria-pressed="false" style="padding:5px 10px; border:1px solid #999; border-radius:4px; background:#f5f5f5; color:#222;">Log LISA</button>
    <label style="display:inline-flex; align-items:center; gap:6px; margin-left:8px; cursor:pointer;">
      <input data-lisa-edges type="checkbox">
      Show k=6 edges
    </label>
    <span data-lisa-status style="color:#666; margin-left:4px;"></span>
  </div>
`;

display(lisaControls);
```

```js
// Leaflet creation — same structure as Figure 2.
const lisaMapElement = html`<div style="height:650px; width:100%;"></div>`;
const lisaMap = L.map(lisaMapElement, { preferCanvas: true });

L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
  maxZoom: 18,
  minZoom: 4,
  attribution:
    'Tiles &copy; Esri, Maxar, Earthstar Geographics, and the GIS User Community',
  crossOrigin: true,
}).addTo(lisaMap);

const lisaEdgeLayer = L.geoJSON(networkK6, {
  interactive: false,
  style: {
    color: "#ff2bd6",
    weight: 0.8,
    opacity: 0.65
  }
});

let activeLisaMode = "raw";
let activeLisaLayer;
const lisaStatus = lisaControls.querySelector("[data-lisa-status]");

const renderLisaLayer = mode => {
  activeLisaMode = mode;
  if (activeLisaLayer) lisaMap.removeLayer(activeLisaLayer);

  const selection = lisaDataByMode.get(mode);
  activeLisaLayer = L.geoJSON(selection.data, {
    pointToLayer: (feature, latlng) => L.circleMarker(latlng, {
      radius: 4.5,
      color: "#222",
      weight: 0.65,
      fillColor: lisaClusterColor(feature.properties.lisa_raw_cluster),
      fillOpacity: 0.92
    }),
    onEachFeature: (feature, layer) => {
      const properties = feature.properties;
      layer.bindPopup(`
        <div style="font:12px system-ui,sans-serif; min-width:210px;">
          <div style="font-size:14px; font-weight:700;">${escapeLisaHtml(properties.name)}</div>
          <div style="color:#666; font-style:italic; margin:2px 0 7px;">${escapeLisaHtml(properties.region)}</div>
          <div><strong>Classification:</strong> ${escapeLisaHtml(properties.lisa_raw_cluster)}</div>
          <div><strong>Local Moran's I:</strong> ${formatLisaNumber(properties.local_moran_i)}</div>
          <div><strong>Permutation p-value:</strong> ${formatLisaNumber(properties.lisa_p_perm_2s)}</div>
          <div><strong>FDR-adjusted q-value:</strong> ${formatLisaNumber(properties.lisa_q_fdr_bh)}</div>
          <div><strong>Staseis:</strong> ${escapeLisaHtml(properties.staseis)}</div>
        </div>
      `, {minWidth: 230, maxWidth: 300});
      layer.on("mouseover", () => layer.openPopup());
      layer.on("mouseout", () => layer.closePopup());
    }
  }).addTo(lisaMap);

  const significantCount = selection.data.features.filter(feature =>
    String(feature.properties.lisa_raw_cluster).toLowerCase() !== "not significant"
  ).length;
  lisaStatus.textContent = `${significantCount.toLocaleString()} significant cities`;

  lisaControls.querySelectorAll("[data-lisa-mode]").forEach(button => {
    const selected = button.dataset.lisaMode === mode;
    button.setAttribute("aria-pressed", selected);
    button.style.background = selected ? "#2563eb" : "#f5f5f5";
    button.style.color = selected ? "white" : "#222";
    button.style.borderColor = selected ? "#2563eb" : "#999";
  });
};

lisaControls.querySelectorAll("[data-lisa-mode]").forEach(button => {
  button.addEventListener("click", () => renderLisaLayer(button.dataset.lisaMode));
});
lisaControls.querySelector("[data-lisa-edges]").addEventListener("change", event => {
  if (event.target.checked) {
    lisaEdgeLayer.addTo(lisaMap);
    lisaEdgeLayer.bringToBack();
  }
  else lisaMap.removeLayer(lisaEdgeLayer);
});

const lisaLegendItems = [
  ["High–High", "#ff1744"],
  ["Low–High", "#00e676"],
  ["High–Low", "#ff9800"],
  ["Low–Low", "#2979ff"],
  ["Not Significant", "#9e9e9e"]
];
const lisaLegend = L.control({position: "bottomright"});
lisaLegend.onAdd = () => {
  const div = L.DomUtil.create("div");
  div.style.cssText = "background:rgba(255,255,255,.94); color:#222; padding:9px 11px; border:1px solid #777; border-radius:3px; box-shadow:0 1px 5px rgba(0,0,0,.22); font:12px system-ui,sans-serif;";
  div.innerHTML = `
    <div style="font-weight:700; margin-bottom:6px;">LISA classification</div>
    ${lisaLegendItems.map(([label, color]) => `
      <div style="display:flex; align-items:center; gap:7px; margin:3px 0;">
        <span style="display:inline-block; width:11px; height:11px; border-radius:50%; background:${color}; border:1px solid #222;"></span>
        <span>${label}</span>
      </div>
    `).join("")}
  `;
  L.DomEvent.disableClickPropagation(div);
  return div;
};
lisaLegend.addTo(lisaMap);
L.control.scale({imperial: false}).addTo(lisaMap);

renderLisaLayer("raw");

display(lisaMapElement);

requestAnimationFrame(() => {
  if (lisaRawData.features.length) {
    lisaMap.invalidateSize();
    lisaMap.fitBounds(
      lisaRawData.features.map(feature => [
        feature.geometry.coordinates[1],
        feature.geometry.coordinates[0]
      ]),
      { padding: [40, 40], maxZoom: 6 },
    );
  }
});
```

<figcaption style="color: #666; font-size: 0.85em; margin-top: 4px;">
    Figure 6. Local Moran's I (LISA) classifications for the k=6 spatial weights network. Toggle between original and log-transformed staseis; optionally display the network edges.
</figcaption>
