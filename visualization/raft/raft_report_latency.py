from collections import defaultdict
import sys
import numpy as np
import plotly.express as px
from IPython.display import display
import pandas as pd
import json
import os
import pathlib
from pathlib import Path
import logging
from dataclasses import dataclass
import statistics

@dataclass
class LatencyEntry:
    timestamp: int
    latency: int

NANO_SECOND_UNIT = 1_000_000_000
MILLI_SECOND_UNIT = 1000

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

cwd = pathlib.Path(os.getcwd())


def test_data_path(test_case: str) -> Path:
    return cwd / "data" / test_case / "load_test.json"

def time_to_unix_timestamp(t: str) -> int:
    t = str(t[:-1]).ljust(29, "0")
    # if int(np.datetime64(t[:-1]).astype('int')) == 1647818150718250:
    #     print(t)
    
    return int(np.datetime64(t[:-1]).astype('int'))

def parse_metrics(line: str) -> LatencyEntry | None:
    obj = json.loads(line)
    obj_type = obj["type"]
    if obj_type != "Point":
        return None
    if obj["metric"] != "http_req_duration":
        return None
    obj = obj["data"]

    timestamp = obj["time"]
    timestamp = time_to_unix_timestamp(timestamp)
    latency = obj["value"]
    return LatencyEntry(timestamp, latency)


def read_raft_metrics(
    metrics_path: Path,
) -> list[LatencyEntry]:
    latency_metrics = []
    with metrics_path.open() as f:
        for line in f:
            metric = parse_metrics(line)
            if metric != None:
                latency_metrics.append(metric)
    return latency_metrics


def window_metrics(metrics: list, timestamp_func, unit: int) -> list[list]:
    if len(metrics) == 0:
        return []

    begin, end = metrics[0], metrics[-1]
    # print(f"begin {begin}")
    # print(f"end {end}")
    begin_time, end_time = timestamp_func(begin), timestamp_func(end)
    time_diff = end_time - begin_time
    time_diff_sec = int(time_diff // unit)
    # print(time_diff)
    # print(time_diff_sec)
    buckets_size = int(time_diff_sec + 1)
    rst = [[] for _ in range(buckets_size)]

    for metric in metrics:
        timestamp = timestamp_func(metric)
        buckets_index = int((timestamp - begin_time) // unit)
        rst[buckets_index].append(metric)

    return rst


def reduce_latency_metrics_unit(metrics: list[LatencyEntry]) -> float:
    if len(metrics) == 0:
        return None
    return statistics.median(x.latency for x in metrics)


def reduce_latency_metrics(metrics: list[list[LatencyEntry]]) -> list[LatencyEntry]:
    rst = []

    for index, bucket in enumerate(metrics):
        x = reduce_latency_metrics_unit(bucket)
        if x != None:
            rst.append(LatencyEntry(index, x))

    return rst

def test(test_case: str) -> None:
    root_path = test_data_path(test_case)
    latency_metrics = read_raft_metrics(root_path)
    latency_metrics.sort(key=lambda x: x.timestamp)
    latency_metrics = window_metrics(
        latency_metrics, lambda x: x.timestamp, NANO_SECOND_UNIT
    )

    latency_metrics = reduce_latency_metrics(latency_metrics)

    latency_metrics = pd.DataFrame(data=latency_metrics)
    latency_metrics = latency_metrics[latency_metrics["latency"] > 0.005]

    display(latency_metrics)

    time_latency_fig = px.line(
        latency_metrics,
        x="timestamp",
        y="latency",
        markers=True,
    )
    time_latency_fig.update_layout(
        title="raft_time_latency",
        xaxis_title="time (sec)",
        yaxis_title="latency p50 (ms)",
    )
    time_latency_fig.show()


if __name__ == "__main__":
    test(sys.argv[1])
