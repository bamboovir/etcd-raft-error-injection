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
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

sns.set_theme(style="darkgrid")


@dataclass
class ThroughputEntry:
    timestamp: int
    bytes_size: int


@dataclass
class LatencyEntry:
    timestamp: int
    latency: int


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

cwd = pathlib.Path(os.getcwd())

NANO_SECOND_UNIT = 1_000_000_000
MILLI_SECOND_UNIT = 1000


def test_data_path(test_case: str) -> Path:
    return cwd / "data" / test_case


def raft_node_metrics_path(root: Path, node_id: str) -> Path:
    return root / f"raft_{node_id}_metrics.json"


def parse_metrics(line: str) -> tuple[ThroughputEntry | LatencyEntry]:
    obj = json.loads(line)
    obj_type = obj["src"]
    obj = obj["data"]
    if obj_type == "metrics.throughput":
        return ThroughputEntry(obj["timestamp"], obj["bytes_size"])
    elif obj_type == "metrics.latency":
        return LatencyEntry(obj["timestamp"], obj["latency"])
    else:
        logger.error(obj)
        raise Exception("impossible")


def read_raft_metrics(
    metrics_path: Path,
) -> tuple[list[ThroughputEntry], list[LatencyEntry]]:
    throughput_metrics = []
    latency_metrics = []
    with metrics_path.open() as f:
        for line in f:
            metric = parse_metrics(line)
            if isinstance(metric, ThroughputEntry):
                throughput_metrics.append(metric)
            elif isinstance(metric, LatencyEntry):
                latency_metrics.append(metric)
            else:
                raise Exception("impossible")
    return throughput_metrics, latency_metrics


def read_all_raft_metrics(
    root: Path, raft_cluster_size: int
) -> tuple[list[ThroughputEntry], list[LatencyEntry]]:
    throughput_metrics = []
    latency_metrics = []
    for node_id in range(1, raft_cluster_size + 1):
        node_id = str(node_id)
        metrics_path = raft_node_metrics_path(root, node_id)
        curr_throughput_metrics, curr_latency_metrics = read_raft_metrics(metrics_path)
        throughput_metrics.extend(curr_throughput_metrics)
        latency_metrics.extend(curr_latency_metrics)
    throughput_metrics.sort(key=lambda x: x.timestamp)
    latency_metrics.sort(key=lambda x: x.timestamp)
    return throughput_metrics, latency_metrics


def get_raft_cluster_size(root: Path) -> int:
    return len([*root.glob("raft_*_metrics.json")])


def window_metrics(metrics: list, timestamp_func, unit: int) -> list[list]:
    if len(metrics) == 0:
        return []

    begin, end = metrics[0], metrics[-1]
    begin_time, end_time = timestamp_func(begin), timestamp_func(end)
    time_diff = end_time - begin_time
    time_diff_sec = int(time_diff // unit)
    buckets_size = int(time_diff_sec + 1)
    rst = [[] for _ in range(buckets_size)]

    for metric in metrics:
        timestamp = timestamp_func(metric)
        buckets_index = int((timestamp - begin_time) // unit)
        rst[buckets_index].append(metric)

    return rst


def reduce_latency_metrics_unit(metrics: list[LatencyEntry]) -> float:
    if len(metrics) == 0:
        return 0.0
    return statistics.median(x.latency for x in metrics)


def reduce_throughtput_metrics_unit(metrics: list[ThroughputEntry]) -> float:
    return sum(x.bytes_size for x in metrics)


def reduce_latency_metrics(metrics: list[list[LatencyEntry]]) -> list[LatencyEntry]:
    return [
        LatencyEntry(index, reduce_latency_metrics_unit(bucket))
        for index, bucket in enumerate(metrics)
    ]


def reduce_throughtput_metrics(
    metrics: list[list[ThroughputEntry]],
) -> list[ThroughputEntry]:
    return [
        ThroughputEntry(index, reduce_throughtput_metrics_unit(bucket))
        for index, bucket in enumerate(metrics)
    ]


def group_latency_by_throughput(
    throughput_metrics: list[ThroughputEntry],
    latency_metrics: list[LatencyEntry],
) -> dict[float, list[LatencyEntry]]:
    if len(throughput_metrics) != len(latency_metrics):
        raise ValueError("metric not joined")
    rst = defaultdict(list)

    for throughput_metric, latency_metric in zip(throughput_metrics, latency_metrics):
        rst[throughput_metric.bytes_size].append(latency_metric)

    return rst


def reduce_throughput_latency(metrics: dict[float, list[LatencyEntry]]) -> list[dict]:
    return [
        {
            "throughput": throughput,
            "latency": reduce_latency_metrics_unit(latency_window),
        }
        for throughput, latency_window in metrics.items()
    ]


def latency_ns_to_ms(metrics: list[LatencyEntry]) -> list[LatencyEntry]:
    return [
        LatencyEntry(x.timestamp, x.latency / (NANO_SECOND_UNIT / MILLI_SECOND_UNIT))
        for x in metrics
    ]


def test(test_case: str) -> None:
    root_path = test_data_path(test_case)
    raft_cluster_size = get_raft_cluster_size(root_path)
    print(raft_cluster_size)
    throughput_metrics, latency_metrics = read_all_raft_metrics(
        root_path, raft_cluster_size
    )
    latency_metrics = latency_ns_to_ms(latency_metrics)
    throughput_metrics = window_metrics(
        throughput_metrics, lambda x: x.timestamp, NANO_SECOND_UNIT
    )
    latency_metrics = window_metrics(
        latency_metrics, lambda x: x.timestamp, NANO_SECOND_UNIT
    )

    throughput_metrics = reduce_throughtput_metrics(throughput_metrics)
    latency_metrics = reduce_latency_metrics(latency_metrics)

    throughput_latency_metrics = group_latency_by_throughput(
        throughput_metrics, latency_metrics
    )
    throughput_latency_metrics = reduce_throughput_latency(throughput_latency_metrics)

    throughput_metrics = pd.DataFrame(data=throughput_metrics)
    latency_metrics = pd.DataFrame(data=latency_metrics)
    throughput_latency_metrics = pd.DataFrame(data=throughput_latency_metrics)
    throughput_latency_metrics = throughput_latency_metrics.sort_values(
        by=["throughput"], ascending=True
    )

    # throughput_min = throughput_latency_metrics.iloc[0]["throughput"]
    # throughput_max = throughput_latency_metrics.iloc[-1]["throughput"]

    # print(throughput_min)
    # print(throughput_max)
    # for i in range(int(throughput_min), int(throughput_max)):
    #     throughput_latency_metrics = pd.concat(
    #         [
    #             throughput_latency_metrics,
    #             pd.DataFrame([{"throughput": i, "latency": np.nan}]),
    #         ]
    #     )
    # throughput_latency_metrics["throughput"] = throughput_latency_metrics[
    #     "throughput"
    # ].interpolate(method="linear")
    # throughput_latency_metrics["latency"] = throughput_latency_metrics[
    #     "latency"
    # ].interpolate(method="linear")

    # throughput_latency_metrics = throughput_latency_metrics[(throughput_latency_metrics > 0.05)]
    latency_metrics = latency_metrics[latency_metrics["latency"] > 0.005]
    throughput_metrics = throughput_metrics[throughput_metrics["bytes_size"] > 500]

    display(throughput_metrics)
    display(latency_metrics)
    display(throughput_latency_metrics)

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

    time_throughput_fig = px.line(
        throughput_metrics, x="timestamp", y="bytes_size", markers=True
    )

    time_throughput_fig.update_layout(
        title="raft_time_throughput",
        xaxis_title="time (sec)",
        yaxis_title="throughput (bytes/sec)",
    )

    time_throughput_fig.show()
    throughput_latency_fig = px.line(
        throughput_latency_metrics, x="throughput", y="latency", markers=True
    )
    throughput_latency_fig.update_layout(
        title="raft_throughput_latency",
        xaxis_title="throughput (bytes/sec)",
        yaxis_title="latency (ms)",
    )
    throughput_latency_fig.show()
    # throughput_latency_fig_sns = sns.lineplot(
    #     x="throughput",
    #     y="latency",
    #     err_style="band",
    #     ci=68,
    #     data=throughput_latency_metrics,
    # )
    # throughput_latency_fig_sns.set_xlabel("throughput (bytes/sec)")
    # throughput_latency_fig_sns.set_ylabel("latency (ms)")
    # plt.show()


if __name__ == "__main__":
    test(sys.argv[1])
