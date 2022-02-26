from __future__ import annotations
from contextlib import suppress
from time import sleep

from .container_resource_monitor import ContainerResourceMonitor
from .raft_vm import RaftVM
from .vm import VMStarter
from pathlib import Path
import docker
from docker.errors import DockerException
from docker import DockerClient
import logging
import requests

logger = logging.getLogger(__name__)


class RaftClusterStarter:
    def __init__(
        self,
        raft_cluster_size: int,
        raft_test_report_path: Path,
        raft_image: str,
    ) -> None:
        self._raft_cluster_size = raft_cluster_size
        self._raft_test_report_path = raft_test_report_path
        self._raft_image = raft_image

    def _start_raft_network(self, docker_client: DockerClient) -> None:
        ipam_pool = docker.types.IPAMPool(
            subnet=RaftVM.CONTAINER_SUBNET, gateway=RaftVM.CONTAINER_GATEWAY
        )
        ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
        with suppress(DockerException):
            docker_client.networks.create(
                RaftVM.CONTAINER_NETWORK,
                driver="bridge",
                ipam=ipam_config,
                check_duplicate=True,
            )

    def _start_raft_cluster(
        self, docker_client: DockerClient
    ) -> tuple[list[RaftVM], Exception | None]:
        cmd_cluster = ",".join(
            [RaftVM.raft_url(str(id)) for id in range(1, self._raft_cluster_size + 1)]
        )
        raft_cluster = []
        for id in range(1, self._raft_cluster_size + 1):
            id = str(id)
            name = RaftVM.name(id)
            command = [
                "--id",
                id,
                "--cluster",
                cmd_cluster,
                "--port",
                str(RaftVM.kv_port(id)),
                "--metrics_log_path",
                f"/tmp/raft_{id}_metrics.json",
                "--monitor_addr",
                RaftVM.monitor_container_addr(id),
            ]
            ports = {f"{RaftVM.monitor_port(id)}/tcp": RaftVM.monitor_port(id)}
            logger.info(f"start {name} with command {' '.join(command)}")
            raft_node, err = VMStarter(
                name=name,
                image=self._raft_image,
                command=command,
                network=RaftVM.CONTAINER_NETWORK,
                volumes={
                    self._raft_test_report_path.as_posix(): {
                        "bind": "/tmp/",
                        "mode": "rw",
                    }
                },
                ports=ports,
            ).start(docker_client)
            if err != None:
                return None, err
            monitor = ContainerResourceMonitor(
                raft_node.container, self._raft_test_report_path
            )
            monitor.start()
            raft_cluster.append(RaftVM(id, raft_node, monitor))
        return raft_cluster, None

    def start(
        self, docker_client: DockerClient
    ) -> tuple[RaftCluster, Exception | None]:
        self._start_raft_network(docker_client)
        raft_cluster, err = self._start_raft_cluster(docker_client)
        if err != None:
            return None, err
        return RaftCluster(raft_cluster), None


class RaftCluster:
    def __init__(
        self,
        raft_cluster: list[RaftVM],
    ) -> None:
        self._raft_cluster = {raftVM.id: raftVM for raftVM in raft_cluster}

    @staticmethod
    def start(
        raft_cluster_size: int,
        test_report_path: Path,
        raft_image: str,
        docker_client: DockerClient,
    ) -> tuple[RaftCluster, Exception | None]:
        starter = RaftClusterStarter(raft_cluster_size, test_report_path, raft_image)
        return starter.start(docker_client)

    def raft_cluster_kv_addrs(self) -> list[str]:
        return [RaftVM.kv_url(id) for id in self._raft_cluster.keys()]

    def find_raft_node_by_id(self, id: str) -> RaftVM | None:
        if id not in self._raft_cluster:
            return None
        return self._raft_cluster[id]

    def leader(self) -> RaftVM | None:
        leader_id = self.leader_id()
        return self.find_raft_node_by_id(leader_id)

    def followers(self) -> list[RaftVM | None]:
        follower_ids = self.follower_ids()
        return [self.find_raft_node_by_id(id) for id in follower_ids]

    def leader_id(self) -> str:
        while True:
            for node_id in self._raft_cluster.keys():
                with suppress(requests.exceptions.RequestException):
                    res = requests.get(
                        url=f"{RaftVM.monitor_local_addr(node_id)}/raft/state"
                    )
                    if res.ok:
                        raft_state = res.json()
                        logger.info(raft_state)
                        if "lead" in raft_state:
                            leader_id = raft_state["lead"]
                            if leader_id == "0":
                                continue
                            logger.info(f"leader: {leader_id}")
                            return leader_id
            sleep(1)

    def follower_ids(self) -> list[str]:
        while True:
            for node_id in self._raft_cluster.keys():
                with suppress(requests.exceptions.RequestException, LookupError):
                    res = requests.get(
                        url=f"{RaftVM.monitor_local_addr(node_id)}/raft/state"
                    )
                    if res.ok:
                        raft_state = res.json()
                        if "lead" in raft_state:
                            leader_id = raft_state["lead"]
                            if leader_id == "0":
                                continue
                            logger.info(f"leader: {leader_id}")
                            if raft_state["raftState"] == "StateFollower":
                                return [raft_state["id"]]
            sleep(1)

    def stop(self, id: str) -> None:
        if id not in self._raft_cluster:
            return
        vm = self._raft_cluster[id]
        vm.stop()
        del self._raft_cluster[id]

    def stop_all(self) -> None:
        for raft_node in self._raft_cluster.values():
            raft_node.stop()
