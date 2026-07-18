from typing import Any
import time
import random

import httpx


RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

class ApiClient:
    def __init__(
        self,
        base_url: str ="http://localhost:8000",
        timeout_seconds: float = 5.0,
        max_attempts: int = 5,
        retry_delay_seconds: float = 1.0,
        max_retry_delay_seconds: float = 30.0
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url,
            timeout=httpx.Timeout(timeout_seconds)
        )
        self.max_attempts = max_attempts
        self.retry_delay_seconds = retry_delay_seconds
        self.max_retry_delay_seconds = max_retry_delay_seconds

    def get(
        self,
        path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self._request(
            method="GET",
            path=path,
            **kwargs,
        )

    def post(
        self,
        path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self._request(
            method="POST",
            path=path,
            **kwargs,
        )

    def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        for attempt in range(1, self.max_attempts + 1):
            try:
                response = self._client.request(
                    method=method,
                    url=path,
                    **kwargs,
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code

                if status_code not in RETRYABLE_STATUS_CODES:
                    raise
                if attempt == self.max_attempts:
                    raise
                
                delay = self._get_retry_delay(e.response, attempt)
                print(
                    f"Request failed with HTTP {status_code}. "
                    f"Attempt {attempt}/{self.max_attempts}. "
                    f"Retrying in {delay:.1f} seconds."
                )
                self._sleep_before_retry(delay)

            except (
                httpx.NetworkError,
                httpx.TimeoutException,
            ):
                if attempt == self.max_attempts:
                    raise

                print(
                    "Network error. "
                    f"Attempt {attempt}/{self.max_attempts}. "
                    f"Retrying in {self.retry_delay_seconds:.1f} seconds."
                )
                self._sleep_before_retry(self.retry_delay_seconds)
        raise RuntimeError("Unreachable")

    def _get_retry_delay(
        self,
        response: httpx.Response,
        attempt: int,
    ) -> float:
        backoff_cap = min(
            (2 ** (attempt - 1)) * self.retry_delay_seconds,
            self.max_retry_delay_seconds,
        )
        jittered_backoff = random.uniform(0.0, backoff_cap)
        response_retry_after = response.headers.get("Retry-After")
        if response_retry_after is None:
            return jittered_backoff

        try:
            # assume response_retry_after as float
            return max(0.0, float(response_retry_after), jittered_backoff)
        except ValueError:
            return jittered_backoff
        
    @staticmethod
    def _sleep_before_retry(seconds: float) -> None:
        time.sleep(seconds)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> None:
        return self


if __name__ == "__main__":
    client = ApiClient()
    response = client.get("/rate-limit")
    print(response)
