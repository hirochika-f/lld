from copy import deepcopy
from typing import Any, Protocol
import asyncio

from catalog_api_response import PRODUCT_RESPONSES


class ProductNotFoundError(Exception):
    pass


class CatalogClient:
    def __init__(self, responses: dict[str, dict[str, Any]]) -> None:
        self._responses = responses
        self.calls: list[str] = []

    async def get_product(self, product_id: str) -> dict[str, Any]:
        self.calls.append(product_id)
        await asyncio.sleep(0)

        if product_id not in self._responses:
            raise ProductNotFoundError(f"Invalid product id: {product_id}")

        return deepcopy(self._responses[product_id])


async def collect_related_products(
        client: CatalogClient,
        root_product_id: str,
        max_depth: int,
    ) -> list[dict[str, Any]]:
    pass


async def main() -> None:
    client = CatalogClient(PRODUCT_RESPONSES)

    results = await collect_related_products(
        client=client,
        root_product_id="p100",
        max_depth=3
    )

    for result in results:
        print(result)

    print(client.calls)


if __name__ == "__main__":
    asyncio.run(main())
