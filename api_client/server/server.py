from __future__ import annotations

import asyncio
import random
from collections import defaultdict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(title="Unstable API Mock Server")

# エンドポイントごとの呼び出し回数を記録
request_counts: dict[str, int] = defaultdict(int)


class ResetResponse(BaseModel):
    message: str


@app.get("/health")
async def health() -> dict[str, str]:
    """常に成功するヘルスチェック。"""
    return {"status": "ok"}


@app.get("/success")
async def success() -> dict[str, str]:
    """常に200を返す。"""
    return {"message": "success"}


@app.get("/fail-first/{failure_count}")
async def fail_first(failure_count: int) -> dict[str, int | str]:
    """
    最初の failure_count 回は503を返し、
    その後は200を返す。

    例:
        /fail-first/2
        1回目: 503
        2回目: 503
        3回目: 200
    """
    key = f"fail-first:{failure_count}"
    request_counts[key] += 1
    current_attempt = request_counts[key]

    if current_attempt <= failure_count:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "temporary service failure",
                "attempt": current_attempt,
            },
        )

    return {
        "message": "recovered",
        "attempt": current_attempt,
    }


@app.get("/always-503")
async def always_503() -> None:
    """常に503を返す。リトライ上限の確認に使う。"""
    raise HTTPException(
        status_code=503,
        detail="service unavailable",
    )


@app.get("/rate-limit")
async def rate_limit() -> None:
    """
    常に429を返す。

    Retry-After: 2 を返すため、
    クライアントがこの値を尊重するか確認できる。
    """
    raise HTTPException(
        status_code=429,
        detail="too many requests",
        headers={"Retry-After": "2"},
    )


@app.get("/slow/{seconds}")
async def slow(seconds: float) -> dict[str, float | str]:
    """
    指定秒数だけ待ってから200を返す。
    クライアント側タイムアウトの検証に使う。
    """
    if seconds < 0 or seconds > 60:
        raise HTTPException(
            status_code=400,
            detail="seconds must be between 0 and 60",
        )

    await asyncio.sleep(seconds)

    return {
        "message": "slow response completed",
        "slept_seconds": seconds,
    }


@app.get("/random-failure")
async def random_failure(
    failure_rate: float = 0.5,
) -> dict[str, float | str]:
    """
    指定確率で503を返す。

    例:
        /random-failure?failure_rate=0.7
    """
    if not 0 <= failure_rate <= 1:
        raise HTTPException(
            status_code=400,
            detail="failure_rate must be between 0 and 1",
        )

    if random.random() < failure_rate:
        raise HTTPException(
            status_code=503,
            detail="random temporary failure",
        )

    return {
        "message": "success",
        "failure_rate": failure_rate,
    }


@app.get("/bad-request")
async def bad_request() -> None:
    """
    常に400を返す。
    クライアントがリトライしないことを確認する。
    """
    raise HTTPException(
        status_code=400,
        detail="invalid request",
    )


@app.post("/reset")
async def reset() -> ResetResponse:
    """呼び出し回数をリセットする。"""
    request_counts.clear()
    return ResetResponse(message="request counts reset")
