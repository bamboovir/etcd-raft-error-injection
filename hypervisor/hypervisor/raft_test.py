from pathlib import Path

import fire
from .raft_hypervisor import RaftHypervisor
import docker
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


class RaftTest:
    def __init__(
        self,
        raft_test_report_path: str,
        raft_load_test_script_path: str,
        raft_cluster_size: int = 3,
        raft_image: str = "docker.io/library/raft:dev",
        raft_load_test_image: str = "docker.io/grafana/k6:latest",
        timeout_secs: int = 100,
    ) -> None:
        self._docker_client = docker.from_env()
        self._raft_test_report_path = Path(raft_test_report_path)
        self._raft_load_test_script_path = Path(raft_load_test_script_path)
        self._raft_image = raft_image
        self._raft_load_test_image = raft_load_test_image
        self._raft_cluster_size = raft_cluster_size
        self._timeout_secs = timeout_secs

    def _start_raft_hypervisor(self) -> RaftHypervisor:
        hypervisor, err = RaftHypervisor.start(
            self._raft_cluster_size,
            self._raft_test_report_path,
            self._raft_image,
            self._raft_load_test_image,
            self._raft_load_test_script_path,
            self._raft_test_report_path,
            self._docker_client,
        )
        if err != None:
            raise err
        return hypervisor

    def baseline(self) -> None:
        hypervisor = self._start_raft_hypervisor()
        hypervisor.wait_and_stop(self._timeout_secs)

    def crashing_behavior_on_leader(self) -> None:
        hypervisor = self._start_raft_hypervisor()
        leader_id = hypervisor.raft_cluster.leader_id()
        hypervisor.raft_cluster.stop(leader_id)
        hypervisor.wait_and_stop(self._timeout_secs)

    def crashing_behavior_on_follower(self) -> None:
        hypervisor = self._start_raft_hypervisor()
        follower_ids = hypervisor.raft_cluster.follower_ids()
        if len(follower_ids) == 0:
            raise ValueError("no followers")
        hypervisor.raft_cluster.stop(follower_ids[0])
        hypervisor.wait_and_stop(self._timeout_secs)

    def slow_cpu_on_leader(self) -> None:
        hypervisor = self._start_raft_hypervisor()
        leader = hypervisor.raft_cluster.leader()
        leader.vm.with_slow_cpu()
        hypervisor.wait_and_stop(self._timeout_secs)

    def slow_cpu_on_follower(self) -> None:
        hypervisor = self._start_raft_hypervisor()
        followers = hypervisor.raft_cluster.followers()
        if len(followers) == 0:
            raise ValueError("no followers")
        follower = followers[0]
        follower.vm.with_slow_cpu()
        hypervisor.wait_and_stop(self._timeout_secs)

    def memory_contention_on_leader(self) -> None:
        hypervisor = self._start_raft_hypervisor()
        leader = hypervisor.raft_cluster.leader()
        leader.vm.with_memory_contention()
        hypervisor.wait_and_stop(self._timeout_secs)

    def memory_contention_on_follower(self) -> None:
        hypervisor = self._start_raft_hypervisor()
        followers = hypervisor.raft_cluster.followers()
        if len(followers) == 0:
            raise ValueError("no followers")
        follower = followers[0]
        follower.vm.with_memory_contention()
        hypervisor.wait_and_stop(self._timeout_secs)


def main():
    fire.Fire(RaftTest)


if __name__ == "__main__":
    main()
