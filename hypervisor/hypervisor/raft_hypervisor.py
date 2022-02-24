from __future__ import annotations
from contextlib import suppress

import threading
from time import sleep
import time

from .util import SuppressWithLogger
from .vm import VM, VMStarter
from docker.models.containers import Container
import threading
from threading import Thread
from pathlib import Path
import docker
from docker.errors import DockerException, NotFound
import json
from docker import DockerClient
import logging
import requests

logger = logging.getLogger(__name__)


class RaftVM:
    HOST = "127.0.0.1"

    def __init__(self, id: str, vm: VM) -> None:
        self.id = id
        self.vm = vm

    @staticmethod
    def kv_port(id: str) -> int:
        return 9000 + int(id)

    @staticmethod
    def kv_url(id: str) -> str:
        return f"http://{RaftVM.container_ip(id)}:{RaftVM.kv_port(id)}"

    @staticmethod
    def name(id: str) -> str:
        return f"raft_{id}"

    @staticmethod
    def monitor_port(id: str) -> int:
        return 5000 + int(id)

    @staticmethod
    def monitor_local_addr(id: str) -> str:
        return f"http://{RaftVM.HOST}:{RaftVM.monitor_port(id)}"

    @staticmethod
    def monitor_container_addr(id: str) -> str:
        return f"{RaftVM.container_ip(id)}:{RaftVM.monitor_port(id)}"

    @staticmethod
    def container_ip(id: str) -> str:
        return f"192.168.52.{id}"


class RaftHypervisorStarter:
    def __init__(
        self,
        raft_cluster_size: int,
        test_report_path: Path,
        raft_image: str,
    ) -> None:
        self._raft_cluster_size = raft_cluster_size
        self._test_report_path = test_report_path
        self._raft_image = raft_image

    def _start_raft_network(self, docker_client: DockerClient) -> None:
        ipam_pool = docker.types.IPAMPool(
            subnet="192.168.52.0/24", gateway="192.168.52.254"
        )
        ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
        with suppress(DockerException):
            docker_client.networks.create(
                "raft_network", driver="bridge", ipam=ipam_config, check_duplicate=True
            )

    def _start_raft_cluster(
        self, docker_client: DockerClient
    ) -> tuple[list[RaftVM], Exception | None]:
        cmd_cluster = ",".join(
            [
                f"http://192.168.52.{i}:{8000 + i}"
                for i in range(1, self._raft_cluster_size + 1)
            ]
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
                f"/tmp/raft_{id}.json",
                "--monitor_addr",
                RaftVM.monitor_container_addr(id),
            ]
            ports = {f"{RaftVM.monitor_port(id)}/tcp": RaftVM.monitor_port(id)}
            logger.info(f"start {name} with command {' '.join(command)}")
            raft_node, err = VMStarter(
                name=name,
                image=self._raft_image,
                command=command,
                network="raft_network",
                volumes={
                    self._test_report_path.as_posix(): {"bind": "/tmp/", "mode": "rw"}
                },
                ports=ports,
            ).start(docker_client)
            if err != None:
                return None, err
            raft_cluster.append(RaftVM(id, raft_node))
        return raft_cluster, None

    def _start_raft_resource_monitor(
        self, raft_cluster: list[RaftVM]
    ) -> list[ContainerResourceMonitor]:
        raft_resource_monitors: list[ContainerResourceMonitor] = []
        for raft_node in raft_cluster:
            monitor = ContainerResourceMonitor(
                raft_node.vm.container, self._test_report_path
            )
            monitor.start()
            raft_resource_monitors.append(monitor)
        return raft_resource_monitors

    def start(
        self, docker_client: DockerClient
    ) -> tuple[RaftHypervisor, Exception | None]:
        self._start_raft_network(docker_client)
        raft_cluster, err = self._start_raft_cluster(docker_client)
        if err != None:
            return None, err
        raft_resource_monitors = self._start_raft_resource_monitor(raft_cluster)
        if err != None:
            return None, err
        hypervisor = RaftHypervisor(
            raft_cluster, raft_resource_monitors, self._test_report_path
        )
        return hypervisor, None


class RaftHypervisor:
    def __init__(
        self,
        raft_cluster: list[RaftVM],
        raft_resource_monitors: list[ContainerResourceMonitor],
        test_report_path: Path,
    ) -> None:
        self._raft_cluster = {raftVM.id: raftVM.vm for raftVM in raft_cluster}
        self._raft_resource_monitors = raft_resource_monitors
        self._raft_load_tester = None
        self._test_report_path = test_report_path

    def find_raft_node_by_id(self, id: str) -> RaftVM | None:
        if id not in self._raft_cluster:
            return None
        return self._raft_cluster[id]

    def start_load_test(
        self,
        leader_id: str,
        load_test_image: str,
        load_test_script_path: Path,
        docker_client: DockerClient,
    ) -> tuple[VM, Exception | None]:
        leader = self.find_raft_node_by_id(leader_id)
        if leader == None:
            err_msg = f"leader id {leader_id} not exist in raft cluster"
            return None, ValueError(err_msg)
        load_tester, err = VMStarter(
            name="load_tester",
            image=load_test_image,
            command=[
                "run",
                "-e",
                f"BASEURL={RaftVM.kv_url(leader_id)}",
                "--summary-export",
                "/tmp/load_test_summary.json",
                "--out",
                "json=/tmp/load_test.json",
                "/script/load_test.js",
            ],
            network="host",
            volumes={
                self._test_report_path.as_posix(): {"bind": "/tmp/", "mode": "rw"},
                load_test_script_path.as_posix(): {
                    "bind": "/script/load_test.js",
                    "mode": "rw",
                },
            },
            ports={},
        ).start(docker_client)
        if err != None:
            return None, err
        self._raft_load_tester = load_tester
        return load_tester, None

    def leader(self) -> str:
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

    def followers(self) -> list[str]:
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
        for monitor in self._raft_resource_monitors:
            monitor.stop()
        for raft_node in self._raft_cluster.values():
            raft_node.stop()
        if self._raft_load_tester != None:
            self._raft_load_tester.stop()

    def wait_and_stop_all(self, timeout_secs: float) -> None:
        sleep(timeout_secs)
        self.stop_all()


class ContainerResourceMonitor:
    def __init__(self, container: Container, resource_uasge_report_path: Path) -> None:
        self._container = container
        self._name = container.name
        self._resource_uasge_report_path = resource_uasge_report_path
        self._quit = threading.Event()

    def _main(self) -> None:
        stat_stream = self._container.stats(stream=True, decode=True)
        report_path = (
            self._resource_uasge_report_path / f"{self._name}_resourse_usage.json"
        )
        with report_path.open("w") as f:
            for stat_info in stat_stream:
                if self._quit.is_set():
                    return
                json.dump(stat_info, f)

    def start(self) -> None:
        t = Thread(target=self._main, args=(), daemon=True)
        t.start()

    def stop(self) -> None:
        self._quit.set()
