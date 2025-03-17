from abc import ABC
from typing import List

from config import app
from cafeto.responses.codes import CODE_200_OK

import httpx


class ABreedsService(ABC):
    async def list_by_breed(self, base_url: str, breed: str) -> List[str]: # pragma: no cover
        ...


class BreedsService(ABreedsService):
    async def list_by_breed(self, base_url: str, breed: str) -> List[str]:  # pragma: no cover
        json_url = f"{base_url}static/breeds.json"

        async with httpx.AsyncClient() as client:
            response = await client.get(json_url)
            if response.status_code == CODE_200_OK.value:
                breeds = response.json()
                return breeds.get(breed, [])
            raise Exception('Breeds file not found')


app.add_scoped(ABreedsService, BreedsService)
