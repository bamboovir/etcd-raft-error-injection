from pathlib import Path
from time import sleep

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

    def _wait_for_inject(self) -> None:
        sleep(self._timeout_secs // 2)

    def _start_raft_hypervisor(self) -> RaftHypervisor:
        self._raft_test_report_path.mkdir(parents=True, exist_ok=True)
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
        self._wait_for_inject()
        leader_id = hypervisor.raft_cluster.leader_id()
        hypervisor.raft_cluster.stop(leader_id)
        hypervisor.wait_and_stop(self._timeout_secs // 2)

    def crashing_behavior_on_follower(self) -> None:
        hypervisor = self._start_raft_hypervisor()
        self._wait_for_inject()
        follower_ids = hypervisor.raft_cluster.follower_ids()
        if len(follower_ids) == 0:
            raise ValueError("no followers")
        hypervisor.raft_cluster.stop(follower_ids[0])
        hypervisor.wait_and_stop(self._timeout_secs // 2)

    def slow_cpu_on_leader(self) -> None:
        hypervisor = self._start_raft_hypervisor()
        self._wait_for_inject()
        leader = hypervisor.raft_cluster.leader()
        leader.vm.with_slow_cpu()
        hypervisor.wait_and_stop(self._timeout_secs // 2)

    def slow_cpu_on_follower(self) -> None:
        hypervisor = self._start_raft_hypervisor()
        self._wait_for_inject()
        followers = hypervisor.raft_cluster.followers()
        if len(followers) == 0:
            raise ValueError("no followers")
        follower = followers[0]
        follower.vm.with_slow_cpu()
        hypervisor.wait_and_stop(self._timeout_secs // 2)

    def memory_contention_on_leader(self) -> None:
        hypervisor = self._start_raft_hypervisor()
        self._wait_for_inject()
        leader = hypervisor.raft_cluster.leader()
        leader.vm.with_memory_contention()
        hypervisor.wait_and_stop(self._timeout_secs // 2)

    def memory_contention_on_follower(self) -> None:
        hypervisor = self._start_raft_hypervisor()
        self._wait_for_inject()
        followers = hypervisor.raft_cluster.followers()
        if len(followers) == 0:
            raise ValueError("no followers")
        follower = followers[0]
        follower.vm.with_memory_contention()
        hypervisor.wait_and_stop(self._timeout_secs // 2)


    def slow_cpu_on_leader_0_2(self) -> None:
        hypervisor = self._start_raft_hypervisor()
        self._wait_for_inject()
        leader = hypervisor.raft_cluster.leader()
        leader.vm.with_slow_cpu(0.2)
        hypervisor.wait_and_stop(self._timeout_secs // 2)

    def slow_cpu_on_follower_0_2(self) -> None:
        hypervisor = self._start_raft_hypervisor()
        self._wait_for_inject()
        followers = hypervisor.raft_cluster.followers()
        if len(followers) == 0:
            raise ValueError("no followers")
        follower = followers[0]
        follower.vm.with_slow_cpu(0.2)
        hypervisor.wait_and_stop(self._timeout_secs // 2)
    
    def slow_cpu_on_leader_0_4(self) -> None:
        hypervisor = self._start_raft_hypervisor()
        self._wait_for_inject()
        leader = hypervisor.raft_cluster.leader()
        leader.vm.with_slow_cpu(0.4)
        hypervisor.wait_and_stop(self._timeout_secs // 2)

    def slow_cpu_on_follower_0_4(self) -> None:
        hypervisor = self._start_raft_hypervisor()
        self._wait_for_inject()
        followers = hypervisor.raft_cluster.followers()
        if len(followers) == 0:
            raise ValueError("no followers")
        follower = followers[0]
        follower.vm.with_slow_cpu(0.4)
        hypervisor.wait_and_stop(self._timeout_secs // 2)

    def slow_cpu_on_leader_0_8(self) -> None:
        hypervisor = self._start_raft_hypervisor()
        self._wait_for_inject()
        leader = hypervisor.raft_cluster.leader()
        leader.vm.with_slow_cpu(0.8)
        hypervisor.wait_and_stop(self._timeout_secs // 2)

    def slow_cpu_on_follower_0_8(self) -> None:
        hypervisor = self._start_raft_hypervisor()
        self._wait_for_inject()
        followers = hypervisor.raft_cluster.followers()
        if len(followers) == 0:
            raise ValueError("no followers")
        follower = followers[0]
        follower.vm.with_slow_cpu(0.8)
        hypervisor.wait_and_stop(self._timeout_secs // 2)

    def memory_contention_on_leader_15(self) -> None:
        hypervisor = self._start_raft_hypervisor()
        self._wait_for_inject()
        leader = hypervisor.raft_cluster.leader()
        leader.vm.with_memory_contention(mem_limit="15m", memswap_limit="25m")
        hypervisor.wait_and_stop(self._timeout_secs // 2)

    def memory_contention_on_follower_15(self) -> None:
        hypervisor = self._start_raft_hypervisor()
        self._wait_for_inject()
        followers = hypervisor.raft_cluster.followers()
        if len(followers) == 0:
            raise ValueError("no followers")
        follower = followers[0]
        follower.vm.with_memory_contention(mem_limit="15m", memswap_limit="25m")
        hypervisor.wait_and_stop(self._timeout_secs // 2)
    
    def memory_contention_on_leader_20(self) -> None:
        hypervisor = self._start_raft_hypervisor()
        self._wait_for_inject()
        leader = hypervisor.raft_cluster.leader()
        leader.vm.with_memory_contention(mem_limit="20m", memswap_limit="30m")
        hypervisor.wait_and_stop(self._timeout_secs // 2)

    def memory_contention_on_follower_20(self) -> None:
        hypervisor = self._start_raft_hypervisor()
        self._wait_for_inject()
        followers = hypervisor.raft_cluster.followers()
        if len(followers) == 0:
            raise ValueError("no followers")
        follower = followers[0]
        follower.vm.with_memory_contention(mem_limit="20m", memswap_limit="30m")
        hypervisor.wait_and_stop(self._timeout_secs // 2)

    def memory_contention_on_leader_25(self) -> None:
        hypervisor = self._start_raft_hypervisor()
        self._wait_for_inject()
        leader = hypervisor.raft_cluster.leader()
        leader.vm.with_memory_contention(mem_limit="25m", memswap_limit="35m")
        hypervisor.wait_and_stop(self._timeout_secs // 2)

    def memory_contention_on_follower_25(self) -> None:
        hypervisor = self._start_raft_hypervisor()
        self._wait_for_inject()
        followers = hypervisor.raft_cluster.followers()
        if len(followers) == 0:
            raise ValueError("no followers")
        follower = followers[0]
        follower.vm.with_memory_contention(mem_limit="25m", memswap_limit="35m")
        hypervisor.wait_and_stop(self._timeout_secs // 2)
def main():
    fire.Fire(RaftTest)


if __name__ == "__main__":
    main()
