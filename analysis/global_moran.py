"""Reproduce the k=6 Global Moran's I analysis used by the site."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
NODES_PATH = ROOT / "src" / "data" / "knn-poleis.geojson"
EDGES_PATH = ROOT / "src" / "data" / "knn-k6.geojson"
OUTPUT_PATH = ROOT / "src" / "data" / "global-moran-k6.json"
PERMUTATIONS = 9_999
RANDOM_SEED = 444


def load_feature_collection(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["features"]


nodes = load_feature_collection(NODES_PATH)
edges = load_feature_collection(EDGES_PATH)
node_index = {
    int(feature["properties"]["polis_id"]): index
    for index, feature in enumerate(nodes)
}

neighbors: list[set[int]] = [set() for _ in nodes]
for feature in edges:
    properties = feature["properties"]
    left = node_index[int(properties["polis1_id"])]
    right = node_index[int(properties["polis2_id"])]
    neighbors[left].add(right)
    neighbors[right].add(left)

if any(not values for values in neighbors):
    raise RuntimeError("Every polis must have at least one k=6 neighbor.")


def spatial_lag(values: np.ndarray) -> np.ndarray:
    return np.array([
        values[np.fromiter(indices, dtype=np.int64)].mean()
        for indices in neighbors
    ])


def moran(values: np.ndarray) -> tuple[float, np.ndarray, np.ndarray]:
    centered = values - values.mean()
    standard_deviation = centered.std(ddof=0)
    if standard_deviation == 0:
        raise ValueError("Moran's I is undefined for a constant variable.")
    standardized = centered / standard_deviation
    lag = spatial_lag(standardized)
    statistic = float(np.dot(standardized, lag) / np.dot(standardized, standardized))
    return statistic, standardized, lag


staseis = np.array([float(feature["properties"]["staseis"]) for feature in nodes])
log_staseis = np.log1p(staseis)
observed, standardized, lag = moran(staseis)
observed_log, standardized_log, lag_log = moran(log_staseis)

rng = np.random.default_rng(RANDOM_SEED)
permuted = np.empty(PERMUTATIONS)
permuted_log = np.empty(PERMUTATIONS)
for index in range(PERMUTATIONS):
    order = rng.permutation(len(nodes))
    randomized = standardized[order]
    randomized_log = standardized_log[order]
    permuted[index] = np.dot(randomized, spatial_lag(randomized)) / np.dot(randomized, randomized)
    permuted_log[index] = (
        np.dot(randomized_log, spatial_lag(randomized_log))
        / np.dot(randomized_log, randomized_log)
    )


def permutation_p_value(observed_value: float, distribution: np.ndarray) -> float:
    if observed_value >= distribution.mean():
        extreme = np.count_nonzero(distribution >= observed_value)
    else:
        extreme = np.count_nonzero(distribution <= observed_value)
    return float((extreme + 1) / (len(distribution) + 1))


result = {
    "method": {
        "weights": "Binary, symmetric KNN (k = 6), row-standardized",
        "permutations": PERMUTATIONS,
        "random_seed": RANDOM_SEED,
    },
    "summary": {
        "number_of_cities": len(nodes),
        "unique_network_connections": len(edges),
        "expected_i": -1 / (len(nodes) - 1),
        "staseis": {
            "moran_i": observed,
            "permutation_p_value": permutation_p_value(observed, permuted),
        },
        "log1p_staseis": {
            "moran_i": observed_log,
            "permutation_p_value": permutation_p_value(observed_log, permuted_log),
        },
    },
    "scatterplot": [
        {
            "polis_id": int(feature["properties"]["polis_id"]),
            "name": feature["properties"]["name"],
            "region": feature["properties"]["region"],
            "staseis": int(feature["properties"]["staseis"]),
            "standardized_staseis": float(standardized[index]),
            "spatial_lag": float(lag[index]),
            "standardized_log1p_staseis": float(standardized_log[index]),
            "spatial_lag_log1p": float(lag_log[index]),
        }
        for index, feature in enumerate(nodes)
    ],
}

OUTPUT_PATH.write_text(
    json.dumps(result, ensure_ascii=False, separators=(",", ":")),
    encoding="utf-8",
)

print(json.dumps(result["summary"], indent=2))
