from __future__ import annotations
from docker import DockerClient
from docker.models.containers import Container
from docker.errors import DockerException, NotFound
import logging
from contextlib import AbstractContextManager, suppress
import atexit

from .util import SuppressWithLogger

logger = logging.getLogger(__name__)


class VMStarter:
    def __init__(
        self, name: str, image: str, command: list[str], network: str, volumes: dict, ports: dict
    ) -> VMStarter:
        self.name = name
        self.image = image
        self.command = [*command]
        self.network = network
        self.volumes = {**volumes}
        self.ports = {**ports}

    def start(self, docker_client: DockerClient) -> tuple[VM, Exception | None]:
        vm = None
        try:
            container: Container = docker_client.containers.run(
                self.image,
                command=[*self.command],
                remove=True,
                detach=True,
                name=self.name,
                network=self.network,
                oom_kill_disable=True,
                volumes=self.volumes,
                ports=self.ports,
            )
            vm = VM(self.name, self.image, self.command, self.network, container)
        except DockerException as err:
            return None, err
        return vm, None


class VM:
    def __init__(
        self,
        name: str,
        image: str,
        command: list[str],
        network: str,
        container: Container,
    ) -> VM:
        self.name = name
        self.image = image
        self.command = [*command]
        self.network = network
        self.container = container
        self.id = self.container.id
        atexit.register(self.stop)

    # https://docs.docker.com/config/containers/resource_constraints/#cpu
    def with_slow_cpu(self, cpus: float = 0.1) -> None:
        cpu_period = 100000
        cpu_quota = cpu_period * cpus
        with SuppressWithLogger(logger, DockerException):
            self.container.update(cpu_period=cpu_period, cpu_quota=cpu_quota)
        return None

    # https://docs.docker.com/config/containers/resource_constraints/#--memory-swap-details
    def with_memory_contention(
        self, mem_limit: str = "10m", memswap_limit: str = "20m"
    ) -> None:
        with SuppressWithLogger(logger, DockerException):
            self.container.update(mem_limit=mem_limit, memswap_limit=memswap_limit)
        return None

    def stop(self) -> None:
        with suppress(NotFound):
            self.container.remove(force=True)
        return None
