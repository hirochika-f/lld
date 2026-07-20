from enum import Enum
from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar
import asyncio
import time


P = ParamSpec("P")
T = TypeVar("T")


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(Exception):
    pass


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
    ):
        self.state = CircuitState.CLOSED
        self.failure_threshold = failure_threshold
        self.failure_count = 0
        self.success_count = 0
        self.recovery_timeout = recovery_timeout
        self.last_failure_time = None

        self._lock = asyncio.Lock()
        self._half_open_request_in_progress = False

    async def call(
        self,
        func: Callable[P, Awaitable[T]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:
        await self._before_call()

        try:
            result = await func(*args, **kwargs)
        except asyncio.CancelledError:
            await self._clear_half_open_request()
            raise
        except Exception:
            await self._on_failure()
            raise
        else:
            await self._on_success()
            return result

    async def _before_call(self) -> None:
        async with self._lock:
            if self.state == CircuitState.CLOSED:
                return
            if self.state == CircuitState.OPEN:
                if not self._recovery_timeout_elapsed():
                    raise CircuitOpenError("Circuit is OPEN.")
                self.state = CircuitState.HALF_OPEN
            if self.state == CircuitState.HALF_OPEN:
                if self._half_open_request_in_progress:
                    raise CircuitOpenError(
                        "Circuit is HALF_OPEN and a probe request is already running."
                    )
                self._half_open_request_in_progress = True

    async def _on_failure(self) -> None:
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self._open_circuit()
                return

            self.failure_count += 1

            if self.failure_count >= self.failure_threshold:
                self._open_circuit()

    async def _on_success(self) -> None:
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self._close_circuit()
            else:
                # handle as continuous failure
                self.failure_count = 0

    async def _clear_half_open_request(self) -> None:
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self._half_open_request_in_progress = False

    def _open_circuit(self):
        self.state = CircuitState.OPEN
        self.failure_count = 0
        self.last_failure_time = time.monotonic()
        self._half_open_request_in_progress = False

    def _close_circuit(self):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = time.monotonic()
        self._half_open_request_in_progress = False

    def _recovery_timeout_elapsed(self) -> bool:
        if self.last_failure_time is None:
            return False

        return (
            time.monotonic() - self.last_failure_time >= self.recovery_timeout
        )
