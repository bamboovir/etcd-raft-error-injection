from pathlib import Path

import fire
from .raft_hypervisor import RaftHypervisor
from .vm import VM, VMStarter
import docker
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


class RaftTest:
    def __init__(
        self,
        raft_cluster_size: int,
        test_report_path: str,
        raft_image: str = "docker.io/library/raft:dev",
    ) -> None:
        self._docker_client = docker.from_env()
        self._test_report_path = Path(test_report_path)
        self._raft_image = raft_image
        self._raft_cluster_size = raft_cluster_size

    def _start_raft_cluster(self) -> tuple[list[VM], Exception | None]:
        cmd_cluster = ",".join(
            [f"http://127.0.0.1:{8001 + i}" for i in range(self._raft_cluster_size)]
        )
        raft_cluster = []
        for id in range(1, self._raft_cluster_size + 1):
            raft_node, err = VMStarter(
                name=f"raft_{id}",
                image=self._raft_image,
                command=[
                    "--id",
                    f"{id}",
                    "--cluster",
                    cmd_cluster,
                    "--port",
                    f"{9000 + id}",
                ],
                network="host",
            ).start(self._docker_client)
            if err != None:
                return None, err
            raft_cluster.append(raft_node)
        return raft_cluster, None

    def baseline(self) -> None:
        raft_cluster, err = self._start_raft_cluster()
        if err != None:
            raise err
        hypervisor = RaftHypervisor(raft_cluster, self._test_report_path)
        hypervisor.wait()

    def crashing_behavior_on_leader(self) -> None:
        raft_cluster, err = self._start_raft_cluster()
        if err != None:
            raise err
        hypervisor = RaftHypervisor(raft_cluster, self._test_report_path)
        leader = hypervisor.leader()
        leader.stop()

    def crashing_behavior_on_follower(self) -> None:
        raft_cluster, err = self._start_raft_cluster()
        if err != None:
            raise err
        hypervisor = RaftHypervisor(raft_cluster, self._test_report_path)
        followers = hypervisor.followers()
        if len(followers) == 0:
            raise ValueError("no followers")
        followers[0].stop()

    def slow_cpu_on_leader(self) -> None:
        raft_cluster, err = self._start_raft_cluster()
        if err != None:
            raise err
        hypervisor = RaftHypervisor(raft_cluster, self._test_report_path)
        leader = hypervisor.leader()
        leader.with_slow_cpu()

    def slow_cpu_on_follower(self) -> None:
        raft_cluster, err = self._start_raft_cluster()
        if err != None:
            raise err
        hypervisor = RaftHypervisor(raft_cluster)
        followers = hypervisor.followers()
        if len(followers) == 0:
            raise ValueError("no followers")
        followers[0].with_slow_cpu()

    def memory_contention_on_leader(self) -> None:
        raft_cluster, err = self._start_raft_cluster()
        if err != None:
            raise err
        hypervisor = RaftHypervisor(raft_cluster, self._test_report_path)
        leader = hypervisor.leader()
        leader.with_memory_contention()

    def memory_contention_on_follower(self) -> None:
        raft_cluster, err = self._start_raft_cluster()
        if err != None:
            raise err
        hypervisor = RaftHypervisor(raft_cluster, self._test_report_path)
        followers = hypervisor.followers()
        if len(followers) == 0:
            raise ValueError("no followers")
        followers[0].with_memory_contention()


def main():
    fire.Fire(RaftTest)


if __name__ == "__main__":
    main()
