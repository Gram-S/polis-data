---
title: Interactive Regression Model 
--- 

## Pearson Correlation Matrix
```js
import {workbook, polis} from "./components/file-attachments.js";
// Interactive regression model
const response = "staseis";
const defaultPredictors = new Set(["area 1", "Elevation m"]);

const isNumber = value =>
  value !== null && value !== undefined && value !== "" && Number.isFinite(+value);

// Per the codebook, 0 means "unknown" for Democracy and Hellenicity.
// Treat those values as missing when either variable is used as a predictor.
const unknownAsMissing = new Set(["Democracy", "Hellenicity"]);
const isUsableValue = (column, value) =>
  isNumber(value) && !(unknownAsMissing.has(column) && +value === 0);

// Standard OLS requires numeric predictors. Exclude identifiers and geographic fields
// that are not part of this model-selection interface.
const omittedPredictors = new Set([
  response,
  "polis#",
  "Delian L",
  "Region #",
  "Latitude",
  "Longitude",
  "Polisity",
  "prom 1"
]);

const candidatePredictors = [...new Set(["area 2", "Silver", "Brone", "Grid", "In/Out", "prom 2", "prom 3",  ...Object.keys(polis[0])])].filter(column =>
  !omittedPredictors.has(column) &&
  polis.some(d => isUsableValue(column, d[column]))
);

const selectedPredictors = new Set(
  candidatePredictors.filter(column => defaultPredictors.has(column))
);

const filters = {
  polisityOne: false,
  prom1AtLeastOne: false
};

const transpose = matrix => matrix[0].map((_, column) => matrix.map(row => row[column]));

const multiply = (left, right) =>
  left.map(row => right[0].map((_, column) =>
    row.reduce((sum, value, i) => sum + value * right[i][column], 0)
  ));

const solve = (matrix, vector) => {
  const n = matrix.length;
  const augmented = matrix.map((row, i) => [...row, vector[i]]);

  for (let column = 0; column < n; column++) {
    let pivot = column;
    for (let row = column + 1; row < n; row++) {
      if (Math.abs(augmented[row][column]) > Math.abs(augmented[pivot][column])) {
        pivot = row;
      }
    }

    if (Math.abs(augmented[pivot][column]) < 1e-12) {
      throw new Error("The selected predictors are perfectly collinear or have no variation.");
    }

    [augmented[column], augmented[pivot]] = [augmented[pivot], augmented[column]];

    const divisor = augmented[column][column];
    for (let j = column; j <= n; j++) augmented[column][j] /= divisor;

    for (let row = 0; row < n; row++) {
      if (row === column) continue;
      const factor = augmented[row][column];
      for (let j = column; j <= n; j++) {
        augmented[row][j] -= factor * augmented[column][j];
      }
    }
  }

  return augmented.map(row => row[n]);
};

const invert = matrix => {
  const n = matrix.length;
  return matrix[0].map((_, column) =>
    solve(matrix, matrix.map((_, row) => row === column ? 1 : 0))
  );
};

const logGamma = z => {
  const coefficients = [
    676.5203681218851,
    -1259.1392167224028,
    771.32342877765313,
    -176.61502916214059,
    12.507343278686905,
    -0.13857109526572012,
    9.9843695780195716e-6,
    1.5056327351493116e-7
  ];

  if (z < 0.5) {
    return Math.log(Math.PI) - Math.log(Math.sin(Math.PI * z)) - logGamma(1 - z);
  }

  z -= 1;
  let x = 0.99999999999980993;
  for (let i = 0; i < coefficients.length; i++) x += coefficients[i] / (z + i + 1);
  const t = z + coefficients.length - 0.5;
  return 0.5 * Math.log(2 * Math.PI) + (z + 0.5) * Math.log(t) - t + Math.log(x);
};

const betaContinuedFraction = (a, b, x) => {
  const maxIterations = 200;
  const epsilon = 3e-7;
  const minimum = 1e-30;
  const qab = a + b;
  const qap = a + 1;
  const qam = a - 1;
  let c = 1;
  let d = 1 - qab * x / qap;
  if (Math.abs(d) < minimum) d = minimum;
  d = 1 / d;
  let h = d;

  for (let m = 1; m <= maxIterations; m++) {
    const m2 = 2 * m;
    let aa = m * (b - m) * x / ((qam + m2) * (a + m2));
    d = 1 + aa * d;
    if (Math.abs(d) < minimum) d = minimum;
    c = 1 + aa / c;
    if (Math.abs(c) < minimum) c = minimum;
    d = 1 / d;
    h *= d * c;

    aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2));
    d = 1 + aa * d;
    if (Math.abs(d) < minimum) d = minimum;
    c = 1 + aa / c;
    if (Math.abs(c) < minimum) c = minimum;
    d = 1 / d;
    const delta = d * c;
    h *= delta;
    if (Math.abs(delta - 1) < epsilon) break;
  }

  return h;
};

const regularizedBeta = (x, a, b) => {
  if (x <= 0) return 0;
  if (x >= 1) return 1;

  const factor = Math.exp(
    logGamma(a + b) - logGamma(a) - logGamma(b) +
    a * Math.log(x) + b * Math.log1p(-x)
  );

  return x < (a + 1) / (a + b + 2)
    ? factor * betaContinuedFraction(a, b, x) / a
    : 1 - factor * betaContinuedFraction(b, a, 1 - x) / b;
};

const twoSidedTTestPValue = (t, degreesOfFreedom) => {
  if (!Number.isFinite(t)) return NaN;
  const x = degreesOfFreedom / (degreesOfFreedom + t ** 2);
  return Math.max(0, Math.min(1, regularizedBeta(x, degreesOfFreedom / 2, 0.5)));
};

const significanceStars = pValue =>
  pValue < 0.01 ? "***" : pValue < 0.05 ? "**" : pValue < 0.1 ? "*" : "";

const formatNumber = value => Number.isFinite(value) ? value.toFixed(4) : "—";
const formatPValue = value => {
  if (!Number.isFinite(value)) return "—";
  return value < 0.0001 ? "<0.0001" : value.toFixed(4);
};

const pearsonCorrelation = (left, right) => {
  const leftMean = left.reduce((sum, value) => sum + value, 0) / left.length;
  const rightMean = right.reduce((sum, value) => sum + value, 0) / right.length;
  const numerator = left.reduce((sum, value, i) =>
    sum + (value - leftMean) * (right[i] - rightMean), 0
  );
  const leftSumSquares = left.reduce((sum, value) => sum + (value - leftMean) ** 2, 0);
  const rightSumSquares = right.reduce((sum, value) => sum + (value - rightMean) ** 2, 0);
  const denominator = Math.sqrt(leftSumSquares * rightSumSquares);
  return denominator === 0 ? NaN : numerator / denominator;
};

const correlationPValue = (correlation, sampleSize) => {
  if (!Number.isFinite(correlation) || sampleSize <= 2) return NaN;
  if (Math.abs(correlation) >= 1) return 0;
  const t = correlation * Math.sqrt((sampleSize - 2) / (1 - correlation ** 2));
  return twoSidedTTestPValue(t, sampleSize - 2);
};

const correlationColor = correlation => {
  if (!Number.isFinite(correlation)) return "#f3f3f3";
  const base = correlation >= 0 ? [13, 54, 117] : [169, 103, 19];
  const strength = 0.12 + 0.88 * Math.min(1, Math.abs(correlation));
  const rgb = base.map(channel => Math.round(255 + (channel - 255) * strength));
  return `rgb(${rgb.join(",")})`;
};

const renderCorrelationMatrix = (variables, data) => {
  const wrapper = document.createElement("div");
  wrapper.style.overflowX = "auto";

  const title = document.createElement("div");
  title.style.marginBottom = "6px";
  title.innerHTML = `<strong>Pearson correlation matrix</strong> · same complete cases: <strong>${data.length}</strong>`;
  wrapper.append(title);

  if (data.length < 3) {
    const message = document.createElement("div");
    message.textContent = "At least 3 complete cases are needed to calculate correlation significance.";
    wrapper.append(message);
    return wrapper;
  }

  const table = document.createElement("table");
  table.style.borderCollapse = "collapse";
  table.style.fontSize = "12px";
  table.style.whiteSpace = "nowrap";
  table.style.marginBottom = "6px";

  const headerRow = table.createTHead().insertRow();
  const corner = document.createElement("th");
  corner.style.padding = "4px 8px";
  headerRow.append(corner);
  variables.forEach(variable => {
    const cell = document.createElement("th");
    cell.textContent = variable;
    cell.style.padding = "4px 8px";
    cell.style.fontWeight = "600";
    headerRow.append(cell);
  });

  const body = table.createTBody();
  variables.forEach((rowVariable, rowIndex) => {
    const row = body.insertRow();
    const label = row.insertCell();
    label.textContent = rowVariable;
    label.style.fontWeight = "600";
    label.style.padding = "4px 8px";

    variables.forEach((columnVariable, columnIndex) => {
      const cell = row.insertCell();
      cell.style.textAlign = "center";
      cell.style.padding = "6px 8px";
      cell.style.minWidth = "62px";

      if (columnIndex > rowIndex) {
        cell.textContent = "";
        cell.style.border = "0";
        return;
      }

      const left = data.map(d => +d[rowVariable]);
      const right = data.map(d => +d[columnVariable]);
      const correlation = pearsonCorrelation(left, right);
      const pValue = rowIndex === columnIndex ? NaN : correlationPValue(correlation, data.length);
      cell.textContent = `${formatNumber(correlation)}${significanceStars(pValue)}`;
      cell.style.background = correlationColor(correlation);
      cell.style.color = Number.isFinite(correlation) && Math.abs(correlation) >= 0.55 ? "white" : "#222";
    });
  });

  wrapper.append(table);
  const colorLegend = document.createElement("div");
  colorLegend.style.display = "flex";
  colorLegend.style.alignItems = "center";
  colorLegend.style.gap = "8px";
  colorLegend.style.fontSize = "12px";
  colorLegend.innerHTML = `
    <span>−1 strong negative</span>
    <span style="display:inline-block; width:160px; height:12px; background:linear-gradient(to right, #a96713, #f3f3f3, #0d3675);"></span>
    <span>strong positive +1</span>`;
  wrapper.append(colorLegend);

  const significanceLegend = document.createElement("div");
  significanceLegend.style.fontSize = "12px";
  significanceLegend.style.marginTop = "4px";
  significanceLegend.innerHTML = `* p &lt; 0.1 · ** p &lt; 0.05 · *** p &lt; 0.01 · lower triangle shown`;
  wrapper.append(significanceLegend);
  return wrapper;
};

const regressionChartColors = [
  "#2563eb", "#dc2626", "#059669", "#9333ea",
  "#d97706", "#0891b2", "#db2777", "#65a30d"
];

const renderRegressionScatterplots = (predictors, data) => {
  const wrapper = document.createElement("div");
  wrapper.style.fontFamily = "system-ui, sans-serif";

  const title = document.createElement("div");
  title.style.marginBottom = "8px";
  title.innerHTML = `<strong>Regression scatterplots</strong> · points included in the current model: <strong>${data.length}</strong>`;
  wrapper.append(title);

  if (!predictors.length) {
    const message = document.createElement("div");
    message.textContent = "Select at least one independent variable to display the scatterplot.";
    wrapper.append(message);
    return wrapper;
  }

  const legend = document.createElement("div");
  legend.style.display = "flex";
  legend.style.flexWrap = "wrap";
  legend.style.gap = "4px 14px";
  legend.style.marginBottom = "8px";
  legend.style.fontSize = "12px";
  predictors.forEach((variable, index) => {
    const item = document.createElement("span");
    item.style.display = "inline-flex";
    item.style.alignItems = "center";
    item.style.gap = "5px";
    item.innerHTML = `<span style="display:inline-block; width:12px; height:3px; background:${regressionChartColors[index % regressionChartColors.length]};"></span>${variable}`;
    legend.append(item);
  });
  wrapper.append(legend);

  const yValues = data.map(d => +d[response]);
  const yMin = Math.min(...yValues);
  const yMax = Math.max(...yValues);
  const yDomain = yMin === yMax ? [yMin - 1, yMax + 1] : [yMin, yMax];
  const grid = document.createElement("div");
  grid.style.display = "grid";
  grid.style.gridTemplateColumns = "repeat(auto-fit, minmax(320px, 1fr))";
  grid.style.gap = "12px";

  predictors.forEach((variable, index) => {
    const color = regressionChartColors[index % regressionChartColors.length];
    const points = data.map(d => ({
      x: +d[variable],
      y: +d[response]
    }));
    const xValues = points.map(point => point.x);
    const xMin = Math.min(...xValues);
    const xMax = Math.max(...xValues);
    const xDomain = xMin === xMax ? [xMin - 1, xMax + 1] : [xMin, xMax];
    const xMean = xValues.reduce((sum, value) => sum + value, 0) / xValues.length;
    const yMean = yValues.reduce((sum, value) => sum + value, 0) / yValues.length;
    const numerator = points.reduce((sum, point) =>
      sum + (point.x - xMean) * (point.y - yMean), 0
    );
    const denominator = points.reduce((sum, point) => sum + (point.x - xMean) ** 2, 0);
    const slope = denominator === 0 ? 0 : numerator / denominator;
    const intercept = yMean - slope * xMean;
    const trend = [
      {x: xDomain[0], y: intercept + slope * xDomain[0]},
      {x: xDomain[1], y: intercept + slope * xDomain[1]}
    ];

    const panel = document.createElement("div");
    panel.style.border = "1px solid #ddd";
    panel.style.padding = "4px";
    panel.style.overflowX = "auto";
    panel.append(Plot.plot({
      width: 360,
      height: 280,
      marginLeft: 52,
      marginBottom: 48,
      x: {label: variable, domain: xDomain, grid: true},
      y: {type: "symlog", label: `${response} (symlog)`, domain: yDomain, grid: true},
      marks: [
        Plot.dot(points, {x: "x", y: "y", fill: color, fillOpacity: 0.45, r: 3}),
        Plot.line(trend, {x: "x", y: "y", stroke: color, strokeWidth: 2})
      ]
    }));
    grid.append(panel);
  });

  wrapper.append(grid);
  return wrapper;
};

const controls = html`
  <div style="font:13px system-ui, sans-serif; margin-bottom:12px;">
    <div style="margin-bottom:6px;"><strong>Data filters</strong></div>
    <div style="display:flex; flex-wrap:wrap; gap:4px 16px; margin-bottom:12px;">
      <label style="display:flex; align-items:center; gap:5px;">
        <input data-filter-polisity type="checkbox">
        Only include Polisity = 1
      </label>
      <label style="display:flex; align-items:center; gap:5px;">
        <input data-filter-prom1 type="checkbox">
        Only include where prom 1 ≥ 1
      </label>
    </div>
    <div style="margin-bottom:6px;"><strong>Independent variables</strong></div>
    <div data-predictors style="display:grid; grid-template-columns:repeat(auto-fit, minmax(150px, 1fr)); gap:4px 12px;"></div>
    <button data-select-none type="button" style="margin-top:8px;">Select none</button>
    <button data-select-default type="button" style="margin-top:8px; margin-left:6px;">Restore default model</button>
    <div style="margin-top:6px; color:#666;">Dependent variable: <strong>staseis</strong>. Numeric variables only. Democracy/Hellenicity = 0 is treated as unknown; Walls = 0 remains valid.</div>
  </div>
`;

const predictorContainer = controls.querySelector("[data-predictors]");
const correlationHolder = html`<div style="font:13px system-ui, sans-serif; margin-bottom:18px;"></div>`;
const outputHolder = html`<div></div>`;
const container = html`<div></div>`;
container.append(correlationHolder, controls, outputHolder);

const renderModel = () => {
  const predictors = [...selectedPredictors];
  const columns = [response, ...predictors];
  const filteredData = polis.filter(d =>
    (!filters.polisityOne || (isNumber(d["Polisity"]) && +d["Polisity"] === 1)) &&
    (!filters.prom1AtLeastOne || (isNumber(d["prom 1"]) && +d["prom 1"] >= 1))
  );
  const completeCases = filteredData.filter(d => columns.every(column =>
    column === response ? isNumber(d[column]) : isUsableValue(column, d[column])
  ));
  const parameterCount = predictors.length + 1;

  correlationHolder.replaceChildren(renderCorrelationMatrix(columns, completeCases));

  if (completeCases.length <= parameterCount) {
    outputHolder.replaceChildren(html`<div style="font:13px system-ui, sans-serif; color:#9b1c1c;">Not enough complete cases for this model.</div>`);
    return;
  }

  try {
    const X = completeCases.map(d => [1, ...predictors.map(column => +d[column])]);
    const y = completeCases.map(d => +d[response]);
    const XTranspose = transpose(X);
    const XtX = multiply(XTranspose, X);
    const Xty = multiply(XTranspose, y.map(value => [value])).map(row => row[0]);
    const beta = solve(XtX, Xty);
    const XtXInverse = invert(XtX);
    const fitted = X.map(row => row.reduce((sum, value, i) => sum + value * beta[i], 0));
    const residuals = y.map((value, i) => value - fitted[i]);
    const yMean = y.reduce((sum, value) => sum + value, 0) / y.length;
    const ssResidual = residuals.reduce((sum, value) => sum + value ** 2, 0);
    const ssTotal = y.reduce((sum, value) => sum + (value - yMean) ** 2, 0);
    const rSquared = 1 - ssResidual / ssTotal;
    const adjustedRSquared = 1 - (1 - rSquared) * (y.length - 1) / (y.length - beta.length);
    const degreesOfFreedom = y.length - beta.length;
    const residualVariance = ssResidual / degreesOfFreedom;
    const standardErrors = beta.map((_, i) => Math.sqrt(residualVariance * XtXInverse[i][i]));
    const tStatistics = beta.map((value, i) => value / standardErrors[i]);
    const pValues = tStatistics.map(t => twoSidedTTestPValue(t, degreesOfFreedom));
    const coefficientNames = ["Intercept", ...predictors];

    const tableWrapper = document.createElement("div");
    tableWrapper.style.overflowX = "auto";
    const table = document.createElement("table");
    table.style.borderCollapse = "collapse";
    table.style.whiteSpace = "nowrap";
    table.style.minWidth = "720px";

    const headerRow = table.createTHead().insertRow();
    ["Term", "Coefficient", "Std. error", "t statistic", "p value"].forEach((header, i) => {
      const cell = document.createElement("th");
      cell.textContent = header;
      cell.style.textAlign = i === 0 ? "left" : "right";
      cell.style.padding = "4px 12px";
      cell.style.borderBottom = "1px solid #999";
      headerRow.append(cell);
    });

    const body = table.createTBody();
    coefficientNames.forEach((name, i) => {
      const row = body.insertRow();
      const values = [
        name,
        `${formatNumber(beta[i])}${significanceStars(pValues[i])}`,
        formatNumber(standardErrors[i]),
        formatNumber(tStatistics[i]),
        formatPValue(pValues[i])
      ];
      values.forEach((value, column) => {
        const cell = row.insertCell();
        cell.textContent = value;
        cell.style.textAlign = column === 0 ? "left" : "right";
        cell.style.padding = "4px 12px";
      });
    });

    tableWrapper.append(table);
    const output = html`
      <div style="font:13px system-ui, sans-serif; max-width:100%;">
        <div style="margin-bottom:8px;">
          <strong>OLS regression:</strong>
          staseis ~ ${predictors.length ? predictors.join(" + ") : "1"}
        </div>
        <div style="margin-bottom:8px;">
          Complete cases: <strong>${completeCases.length}</strong> ·
          R²: <strong>${formatNumber(rSquared)}</strong> ·
          Adjusted R²: <strong>${formatNumber(adjustedRSquared)}</strong> ·
          Residual df: <strong>${degreesOfFreedom}</strong>
        </div>
        <div style="margin-bottom:8px;">* p &lt; 0.1 · ** p &lt; 0.05 · *** p &lt; 0.01</div>
        <div data-regression-table></div>
        <div data-scatterplots style="margin-top:18px;"></div>
      </div>
    `;
    output.querySelector("[data-scatterplots]").append(
      renderRegressionScatterplots(predictors, completeCases)
    );
    output.querySelector("[data-regression-table]").append(tableWrapper);
    outputHolder.replaceChildren(output);
  } catch (error) {
    outputHolder.replaceChildren(html`<div style="font:13px system-ui, sans-serif; color:#9b1c1c;">${error.message}</div>`);
  }
};

const updatePredictorControls = () => {
  predictorContainer.replaceChildren();

  for (const column of candidatePredictors) {
    const label = document.createElement("label");
    label.style.display = "flex";
    label.style.alignItems = "center";
    label.style.gap = "5px";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = selectedPredictors.has(column);
    checkbox.addEventListener("change", () => {
      if (checkbox.checked) selectedPredictors.add(column);
      else selectedPredictors.delete(column);
      renderModel();
    });

    label.append(checkbox, document.createTextNode(column));
    predictorContainer.append(label);
  }
};

controls.querySelector("[data-filter-polisity]").addEventListener("change", event => {
  filters.polisityOne = event.target.checked;
  renderModel();
});

controls.querySelector("[data-filter-prom1]").addEventListener("change", event => {
  filters.prom1AtLeastOne = event.target.checked;
  renderModel();
});

controls.querySelector("[data-select-none]").addEventListener("click", () => {
  selectedPredictors.clear();
  updatePredictorControls();
  renderModel();
});

controls.querySelector("[data-select-default]").addEventListener("click", () => {
  selectedPredictors.clear();
  for (const column of defaultPredictors) {
    if (candidatePredictors.includes(column)) selectedPredictors.add(column);
  }
  updatePredictorControls();
  renderModel();
});

updatePredictorControls();
renderModel();

display(container);
```
```
