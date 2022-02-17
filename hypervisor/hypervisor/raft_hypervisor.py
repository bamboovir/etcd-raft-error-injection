import threading
from time import sleep
from typing import NoReturn
from .vm import VM
from docker.models.containers import Container
import threading
from threading import Thread
from pathlib import Path
from docker.errors import DockerException, NotFound
import json


class RaftHypervisor:
    def __init__(self, raft_vms: list[VM], resource_uasge_report_path: Path) -> None:
        self._leader = None
        self._followers = []
        self._resource_uasge_report_path = resource_uasge_report_path
        self._vms = raft_vms
        self._resource_monitors = []
        for vm in raft_vms:
            monitor = ContainerResourceMonitor(vm.container, resource_uasge_report_path)
            monitor.start()
            self._resource_monitors.append(monitor)
        # supervisor_sidecar = VMStarter().start(self._docker_client)

    def leader(self) -> VM:
        pass

    def followers(self) -> list[VM]:
        pass

    def wait(self) -> NoReturn:
        sleep(1000000)


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
