from pathlib import Path

import fire
from .raft_hypervisor import RaftHypervisor, RaftHypervisorStarter
from .vm import VM, VMStarter
import docker
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


class RaftTest:
    def __init__(
        self,
        test_report_path: str,
        load_test_script_path: str,
        raft_cluster_size: int = 3,
        raft_image: str = "docker.io/library/raft:dev",
        load_test_image: str = "docker.io/grafana/k6:latest",
        timeout_secs: int = 100,
    ) -> None:
        self._docker_client = docker.from_env()
        self._test_report_path = Path(test_report_path)
        self._load_test_script_path = Path(load_test_script_path)
        self._raft_image = raft_image
        self._load_test_image = load_test_image
        self._raft_cluster_size = raft_cluster_size
        self._timeout_secs = timeout_secs

    def _start_raft_hypervisor(self) -> tuple[RaftHypervisor, Exception | None]:
        return RaftHypervisorStarter(
            self._raft_cluster_size,
            self._test_report_path,
            self._raft_image,
        ).start(self._docker_client)

    def _start_raft_load_tester(
        self, hypervisor: RaftHypervisor, leader_id: str
    ) -> tuple[VM, Exception | None]:
        return hypervisor.start_load_test(
            leader_id,
            self._load_test_image,
            self._load_test_script_path,
            self._docker_client,
        )

    def baseline(self) -> None:
        hypervisor, err = self._start_raft_hypervisor()
        if err != None:
            raise err
        leader_id = hypervisor.leader()
        _, err = self._start_raft_load_tester(
            hypervisor,
            leader_id,
        )
        if err != None:
            raise err
        hypervisor.wait_and_stop_all(self._timeout_secs)

    def crashing_behavior_on_leader(self) -> None:
        hypervisor, err = self._start_raft_hypervisor()
        if err != None:
            raise err
        leader_id = hypervisor.leader()
        hypervisor.stop(leader_id)
        leader_id = hypervisor.leader()
        _, err = self._start_raft_load_tester(
            hypervisor,
            leader_id,
        )
        if err != None:
            raise err
        hypervisor.wait_and_stop_all(self._timeout_secs)

    def crashing_behavior_on_follower(self) -> None:
        hypervisor, err = self._start_raft_hypervisor()
        if err != None:
            raise err
        followers = hypervisor.followers()
        if len(followers) == 0:
            raise ValueError("no followers")
        hypervisor.stop(followers[0])
        leader_id = hypervisor.leader()
        _, err = self._start_raft_load_tester(
            hypervisor,
            leader_id,
        )
        if err != None:
            raise err
        hypervisor.wait_and_stop_all(self._timeout_secs)

    def slow_cpu_on_leader(self) -> None:
        hypervisor, err = self._start_raft_hypervisor()
        if err != None:
            raise err

        leader_id = hypervisor.leader()
        leader = hypervisor.find_raft_node_by_id(leader_id)
        if leader == None:
            raise ValueError("no leader")
        leader.vm.with_slow_cpu()

        _, err = self._start_raft_load_tester(
            hypervisor,
            leader_id,
        )
        if err != None:
            raise err
        hypervisor.wait_and_stop_all(self._timeout_secs)

    def slow_cpu_on_follower(self) -> None:
        hypervisor, err = self._start_raft_hypervisor()
        if err != None:
            raise err
        followers = hypervisor.followers()
        if len(followers) == 0:
            raise ValueError("no followers")

        follower = hypervisor.find_raft_node_by_id(followers[0])
        if follower == None:
            raise ValueError("no follower")
        follower.vm.with_slow_cpu()
        leader_id = hypervisor.leader()
        _, err = self._start_raft_load_tester(
            hypervisor,
            leader_id,
        )
        if err != None:
            raise err
        hypervisor.wait_and_stop_all(self._timeout_secs)

    def memory_contention_on_leader(self) -> None:
        hypervisor, err = self._start_raft_hypervisor()
        if err != None:
            raise err

        leader_id = hypervisor.leader()
        leader = hypervisor.find_raft_node_by_id(leader_id)
        if leader == None:
            raise ValueError("no leader")
        leader.vm.with_memory_contention()

        _, err = self._start_raft_load_tester(
            hypervisor,
            leader_id,
        )
        if err != None:
            raise err
        hypervisor.wait_and_stop_all(self._timeout_secs)

    def memory_contention_on_follower(self) -> None:
        hypervisor, err = self._start_raft_hypervisor()
        if err != None:
            raise err
        followers = hypervisor.followers()
        if len(followers) == 0:
            raise ValueError("no followers")

        follower = hypervisor.find_raft_node_by_id(followers[0])
        if follower == None:
            raise ValueError("no follower")
        follower.vm.with_memory_contention()
        leader_id = hypervisor.leader()
        _, err = self._start_raft_load_tester(
            hypervisor,
            leader_id,
        )
        if err != None:
            raise err
        hypervisor.wait_and_stop_all(self._timeout_secs)


def main():
    fire.Fire(RaftTest)


if __name__ == "__main__":
    main()
