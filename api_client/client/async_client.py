from typing import Any
import random

import asyncio
import httpx


RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

class AsyncApiClient:
    def __init__(
        self,
        base_url: str ="http://localhost:8000",
        timeout_seconds: float = 5.0,
        max_attempts: int = 5,
        retry_delay_seconds: float = 1.0,
        max_retry_delay_seconds: float = 30.0,
        max_concurrency: int = 10,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=httpx.Timeout(timeout_seconds)
        )
        self.max_attempts = max_attempts
        self.retry_delay_seconds = retry_delay_seconds
        self.max_retry_delay_seconds = max_retry_delay_seconds
        self._semaphore = asyncio.Semaphore(max_concurrency)

    async def get(
        self,
        path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return await self._request(
            method="GET",
            path=path,
            **kwargs,
        )

    async def post(
        self,
        path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return await self._request(
            method="POST",
            path=path,
            **kwargs,
        )

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        # POST retries are only safe when the operation is idempotent,
        # for example when using an idempotency key
        for attempt in range(1, self.max_attempts + 1):
            try:
                async with self._semaphore:
                # limit concurrency per http request with semaphore
                # release semaphore after getting response while sleeping
                    response = await self._client.request(
                        method=method,
                        url=path,
                        **kwargs,
                    )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code

                if status_code not in RETRYABLE_STATUS_CODES:
                    raise
                if attempt == self.max_attempts:
                    raise
                
                delay = self._get_retry_delay(exc.response, attempt)
                print(
                    f"Request failed with HTTP {status_code}. "
                    f"Attempt {attempt}/{self.max_attempts}. "
                    f"Retrying in {delay:.1f} seconds."
                )
                await self._sleep_before_retry(delay)

            except (
                httpx.NetworkError,
                httpx.TimeoutException,
            ) as exc:
                if attempt == self.max_attempts:
                    raise

                delay = self._get_retry_delay(None, attempt)
                print(
                    f"{type(exc).__name__}: {exc}. "
                    f"Attempt {attempt}/{self.max_attempts}. "
                    f"Retrying in {delay:.1f} seconds."
                )
                await self._sleep_before_retry(delay)
        raise RuntimeError("Unreachable")

    def _get_retry_delay(
        self,
        response: httpx.Response | None,
        attempt: int,
    ) -> float:
        backoff_cap = min(
            (2 ** (attempt - 1)) * self.retry_delay_seconds,
            self.max_retry_delay_seconds,
        )
        jittered_backoff = random.uniform(0.0, backoff_cap)
        if response is None:
            return jittered_backoff
        response_retry_after = response.headers.get("Retry-After")
        if response_retry_after is None:
            return jittered_backoff

        try:
            # assume response_retry_after as float
            return max(0.0, float(response_retry_after), jittered_backoff)
        except ValueError:
            return jittered_backoff
        
    @staticmethod
    async def _sleep_before_retry(seconds: float) -> None:
        await asyncio.sleep(seconds)

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncApiClient":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()


async def main() -> None:
    async with AsyncApiClient(max_concurrency=2) as client:
        results = await asyncio.gather(
            *[
                client.get("/slow/1")
                for _ in range(10)
            ]
        )
        print(results)
        await client.post("/reset")


if __name__ == "__main__":
    asyncio.run(main())
