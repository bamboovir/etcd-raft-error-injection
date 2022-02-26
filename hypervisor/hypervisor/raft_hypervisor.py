from __future__ import annotations
from time import sleep
from hypervisor.raft_cluster import RaftCluster
from hypervisor.raft_load_tester import RaftLoadTester
from pathlib import Path
from docker import DockerClient
import logging

logger = logging.getLogger(__name__)


class RaftHypervisor:
    def __init__(
        self, raft_cluster: RaftCluster, raft_load_tester: RaftLoadTester
    ) -> None:
        self.raft_cluster = raft_cluster
        self.raft_load_tester = raft_load_tester

    @staticmethod
    def start(
        raft_cluster_size: int,
        raft_test_report_path: Path,
        raft_image: str,
        raft_load_test_image: str,
        raft_load_test_script_path: Path,
        raft_load_test_report_path: Path,
        docker_client: DockerClient,
    ) -> tuple[RaftHypervisor, Exception | None]:
        raft_cluster, err = RaftCluster.start(
            raft_cluster_size, raft_test_report_path, raft_image, docker_client
        )
        if err != None:
            return None, err
        raft_cluster_kv_addrs = raft_cluster.raft_cluster_kv_addrs()
        raft_load_tester, err = RaftLoadTester.start(
            raft_cluster_kv_addrs,
            raft_load_test_image,
            raft_load_test_script_path,
            raft_load_test_report_path,
            docker_client,
        )
        if err != None:
            return None, err
        return RaftHypervisor(raft_cluster, raft_load_tester), None

    def stop(self) -> None:
        self.raft_load_tester.stop()
        self.raft_cluster.stop_all()

    def wait_and_stop(self, timeout_secs: float) -> None:
        sleep(timeout_secs)
        self.stop()
