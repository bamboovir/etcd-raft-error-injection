from __future__ import annotations

import threading

from docker.models.containers import Container
import threading
from threading import Thread
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


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
