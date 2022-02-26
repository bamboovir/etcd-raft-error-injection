from __future__ import annotations
from .vm import VM
from .container_resource_monitor import ContainerResourceMonitor
import logging

logger = logging.getLogger(__name__)


class RaftVM:
    LOCAL_HOST = "127.0.0.1"
    CONTAINER_HOST = "192.168.52"
    CONTAINER_SUBNET = "192.168.52.0/24"
    CONTAINER_GATEWAY = "192.168.52.254"
    CONTAINER_NETWORK = "raft_network"

    def __init__(
        self, id: str, vm: VM, monitor: ContainerResourceMonitor = None
    ) -> None:
        self.id = id
        self.vm = vm
        self.monitor = monitor

    def stop(self) -> None:
        self.vm.stop()
        if self.monitor != None:
            self.monitor.stop()

    @staticmethod
    def raft_port(id: str) -> int:
        return 8000 + int(id)

    @staticmethod
    def raft_url(id: str) -> str:
        return f"http://{RaftVM.container_ip(id)}:{RaftVM.raft_port(id)}"

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
        return f"http://{RaftVM.LOCAL_HOST}:{RaftVM.monitor_port(id)}"

    @staticmethod
    def monitor_container_addr(id: str) -> str:
        return f"{RaftVM.container_ip(id)}:{RaftVM.monitor_port(id)}"

    @staticmethod
    def container_ip(id: str) -> str:
        return f"{RaftVM.CONTAINER_HOST}.{id}"
