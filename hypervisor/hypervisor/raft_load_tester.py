from __future__ import annotations
from .raft_vm import RaftVM
from .vm import VM, VMStarter
from pathlib import Path
from docker import DockerClient
import logging

logger = logging.getLogger(__name__)


class RaftLoadTester:
    def __init__(
        self,
        raft_load_tester_vm: VM,
    ) -> None:
        self._raft_load_tester_vm = raft_load_tester_vm

    @staticmethod
    def start(
        raft_cluster_addrs: list[str],
        load_test_image: str,
        load_test_script_path: Path,
        load_test_report_path: Path,
        docker_client: DockerClient,
    ) -> tuple[RaftLoadTester, Exception | None]:
        raft_load_tester_vm, err = VMStarter(
            name="load_tester",
            image=load_test_image,
            command=[
                "run",
                "-e",
                f"RAFT_CLUSTER_ADDRS={','.join(raft_cluster_addrs)}",
                "--summary-export",
                "/tmp/load_test_summary.json",
                "--out",
                "json=/tmp/load_test.json",
                "/script/load_test.js",
            ],
            network="host",
            volumes={
                load_test_report_path.as_posix(): {"bind": "/tmp/", "mode": "rw"},
                load_test_script_path.as_posix(): {
                    "bind": "/script/load_test.js",
                    "mode": "rw",
                },
            },
            ports={},
        ).start(docker_client)
        if err != None:
            return None, err
        return RaftLoadTester(raft_load_tester_vm), None

    def stop(self) -> None:
        self._raft_load_tester_vm.stop()
