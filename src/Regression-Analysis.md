--- 
title: Regression Analysis
--- 

## Regression Analysis

```js
import {workbook, polis} from "./components/file-attachments.js";

// Regression Model
const response = "staseis";
const predictors = ["Elevation m", "area 2", "Colonies", "Victors"];
const coefficientNames = ["Intercept", ...predictors];

const isNumber = value =>
  value !== null && value !== undefined && value !== "" && Number.isFinite(+value);

// Use complete cases for all five regression variables.
const regressionData = polis.filter(d =>
  [response, ...predictors].every(column => isNumber(d[column]))
);

const X = regressionData.map(d => [1, ...predictors.map(column => +d[column])]);
const y = regressionData.map(d => +d[response]);

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
      throw new Error("The regression matrix is singular or has perfectly collinear variables.");
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
const residualVariance = ssResidual / (y.length - beta.length);
const standardErrors = beta.map((_, i) => Math.sqrt(residualVariance * XtXInverse[i][i]));
const tStatistics = beta.map((value, i) => value / standardErrors[i]);
const degreesOfFreedom = y.length - beta.length;

// Regularized incomplete beta and Student's t distribution helpers.
// These keep the cell self-contained and avoid another package import.
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

const twoSidedTTestPValue = (t, df) => {
  if (!Number.isFinite(t)) return NaN;
  const x = df / (df + t ** 2);
  return Math.max(0, Math.min(1, regularizedBeta(x, df / 2, 0.5)));
};

const pValues = tStatistics.map(t => twoSidedTTestPValue(t, degreesOfFreedom));

const formatNumber = value => Number.isFinite(value) ? value.toFixed(4) : "—";
const significanceStars = pValue =>
  pValue < 0.01 ? "***" : pValue < 0.05 ? "**" : pValue < 0.1 ? "*" : "";

const formatPValue = value => {
  if (!Number.isFinite(value)) return "—";
  return value < 0.0001 ? "<0.0001" : value.toFixed(4);
};

const tableWrapper = document.createElement("div");
tableWrapper.style.overflowX = "auto";

const table = document.createElement("table");
table.style.borderCollapse = "collapse";
table.style.whiteSpace = "nowrap";
table.style.minWidth = "720px";

const headerRow = table.createTHead().insertRow();
for (const header of ["Term", "Coefficient", "Std. error", "t statistic", "p value"]) {
  const cell = document.createElement("th");
  cell.textContent = header;
  cell.style.textAlign = header === "Term" ? "left" : "right";
  cell.style.padding = "4px 12px";
  cell.style.borderBottom = "1px solid #999";
  headerRow.append(cell);
}

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
      staseis ~ Elevation m + area 2 + Colonies + Victors
    </div>
    <div style="margin-bottom:8px;">
      Complete cases: <strong>${regressionData.length}</strong> ·
      R²: <strong>${formatNumber(rSquared)}</strong> ·
      Adjusted R²: <strong>${formatNumber(adjustedRSquared)}</strong> ·
      Residual df: <strong>${degreesOfFreedom}</strong>
    </div>
    <div style="margin-bottom:8px;">* p &lt; 0.1 · ** p &lt; 0.05 · *** p &lt; 0.01</div>
    <div data-coefficient-table></div>
  </div>
`;

output.querySelector("[data-coefficient-table]").append(tableWrapper);
display(output);

// Correlation matrix for the same complete-case regression sample.
const correlationVariables = [
  {column: "staseis", label: "Staseis"},
  {column: "Elevation m", label: "Elevation m"},
  {column: "area 2", label: "Area 2"},
  {column: "Colonies", label: "Colonies"},
  {column: "Victors", label: "Victors"}
];

const correlationColumns = correlationVariables.map(({column}) =>
  regressionData.map(d => +d[column])
);

const pearsonCorrelation = (left, right) => {
  const leftMean = left.reduce((sum, value) => sum + value, 0) / left.length;
  const rightMean = right.reduce((sum, value) => sum + value, 0) / right.length;
  const numerator = left.reduce((sum, value, i) =>
    sum + (value - leftMean) * (right[i] - rightMean), 0
  );
  const leftSS = left.reduce((sum, value) => sum + (value - leftMean) ** 2, 0);
  const rightSS = right.reduce((sum, value) => sum + (value - rightMean) ** 2, 0);
  return numerator / Math.sqrt(leftSS * rightSS);
};

const correlationMatrix = correlationColumns.map(left =>
  correlationColumns.map(right => pearsonCorrelation(left, right))
);

const correlationDegreesOfFreedom = regressionData.length - 2;
const correlationPValues = correlationMatrix.map((row, i) =>
  row.map((value, j) => {
    if (i === j) return NaN;
    const t = value === 1 || value === -1
      ? Infinity
      : value * Math.sqrt(correlationDegreesOfFreedom / (1 - value ** 2));
    return twoSidedTTestPValue(t, correlationDegreesOfFreedom);
  })
);

const blendCorrelationColor = (from, to, amount) =>
  from.map((value, i) => Math.round(value + amount * (to[i] - value)));

const correlationColor = value => {
  const neutral = [247, 247, 247];
  const positive = [8, 48, 107];
  const negative = [140, 81, 10];
  const rgb = value >= 0
    ? blendCorrelationColor(neutral, positive, value)
    : blendCorrelationColor(neutral, negative, -value);
  return `rgb(${rgb.join(",")})`;
};

const correlationTextColor = value =>
  Math.abs(value) >= 0.55 ? "#ffffff" : "#222222";

const correlationTable = document.createElement("table");
correlationTable.style.borderCollapse = "collapse";
correlationTable.style.font = "13px system-ui, sans-serif";
correlationTable.style.whiteSpace = "nowrap";

const correlationHeader = correlationTable.createTHead().insertRow();
const emptyHeader = document.createElement("th");
emptyHeader.style.padding = "6px";
correlationHeader.append(emptyHeader);

for (const {label} of correlationVariables) {
  const cell = document.createElement("th");
  cell.textContent = label;
  cell.style.padding = "6px";
  cell.style.textAlign = "center";
  cell.style.fontWeight = "600";
  correlationHeader.append(cell);
}

const correlationBody = correlationTable.createTBody();
correlationVariables.forEach(({label}, rowIndex) => {
  const row = correlationBody.insertRow();
  const rowHeader = document.createElement("th");
  rowHeader.textContent = label;
  rowHeader.style.padding = "6px 10px 6px 6px";
  rowHeader.style.textAlign = "left";
  rowHeader.style.fontWeight = "600";
  row.append(rowHeader);

  correlationMatrix[rowIndex].forEach((value, columnIndex) => {
    const cell = row.insertCell();
    const pValue = correlationPValues[rowIndex][columnIndex];
    cell.textContent = `${value.toFixed(2)}${significanceStars(pValue)}`;
    cell.style.minWidth = "68px";
    cell.style.padding = "8px 10px";
    cell.style.textAlign = "center";
    cell.style.background = correlationColor(value);
    cell.style.color = correlationTextColor(value);
    cell.style.fontVariantNumeric = "tabular-nums";
    cell.title = Number.isFinite(pValue)
      ? `Pearson r = ${value.toFixed(3)}; p = ${pValue.toFixed(4)}`
      : `Pearson r = ${value.toFixed(3)}`;
  });
});

const correlationWrapper = document.createElement("div");
correlationWrapper.style.overflowX = "auto";
correlationWrapper.style.marginTop = "18px";
correlationWrapper.append(correlationTable);

const correlationOutput = html`
  <div style="font:13px system-ui, sans-serif; max-width:100%;">
    <div style="margin-bottom:8px;">
      <strong>Pearson correlation matrix</strong>
      · same complete cases: <strong>${regressionData.length}</strong>
    </div>
    <div data-correlation-table></div>
    <div style="display:flex; align-items:center; gap:8px; margin-top:10px;">
      <span>−1 strong negative</span>
      <span style="display:inline-block; width:160px; height:12px; background:linear-gradient(to right, #8c510a, #f7f7f7, #08306b);"></span>
      <span>strong positive +1</span>
    </div>
    <div style="margin-top:6px;">* p &lt; 0.1 · ** p &lt; 0.05 · *** p &lt; 0.01</div>
  </div>
`;

correlationOutput.querySelector("[data-correlation-table]").append(correlationWrapper);
display(correlationOutput);

