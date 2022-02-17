from logging import Logger
from contextlib import AbstractContextManager, suppress


class SuppressWithLogger(AbstractContextManager):
    def __init__(self, logger: Logger, *exceptions):
        self._logger = logger
        self._exceptions = exceptions

    def __enter__(self):
        pass

    def __exit__(self, exctype, excinst, exctb):
        rst = exctype is not None and issubclass(exctype, self._exceptions)
        if rst:
            self._logger.exception(excinst)
        return rst
