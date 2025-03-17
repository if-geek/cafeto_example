from __future__ import annotations
from typing import List, Optional, overload
from abc import ABC

from pets.models import Pet
from config import app, database

import pets.dtos as dtos
from pets.errors import PetNotFound


class APetService(ABC):
    async def retrieve(self, id: int) -> dtos.PetResponseDto: ...

    async def list(self) -> list[dtos.PetResponseDto]: ...

    async def create(self, pet: dtos.PetCreateRequestDto) -> dtos.PetResponseDto: ...

    async def update(self, id: int, pet: dtos.PetUpdateRequestDto) -> dtos.PetResponseDto: ...

    async def delete(self, pet_id: int) -> None: ...


class PetServiceDB(APetService):
    async def retrieve(self, id: int) -> dtos.PetResponseDto:
        pet: Optional[Pet] = await Pet.objects.filter(id=id).first_or_none()
        if pet:
            return dtos.PetResponseDto(**pet.model_dump())
        raise PetNotFound('Pet not found')

    async def list(self) -> list[dtos.PetResponseDto]:
        pets: List[Pet] = await Pet.objects.all()
        return [dtos.PetResponseDto(**pet.model_dump()) for pet in pets]

    async def create(self, pet_request: dtos.PetCreateRequestDto) -> dtos.PetResponseDto:
        pet: Optional[Pet] = await Pet.objects.create(**pet_request.model_dump())
        return dtos.PetResponseDto(**pet.model_dump())

    async def update(self, id: int, pet_request: dtos.PetUpdateRequestDto) -> dtos.PetResponseDto:
        async with database.transaction():
            pet = await Pet.objects.filter(id=id).first_or_none()
            if pet is None:
                raise PetNotFound('Pet not found')
            await pet.update(**pet_request.model_dump())
            return dtos.PetResponseDto(**pet.model_dump())

    async def delete(self, pet_id: int) -> None:
        async with database.transaction():
            pet_exists: bool = await Pet.objects.filter(id=pet_id).exists()
            if not pet_exists:
                raise PetNotFound('Pet not found')
            await Pet.objects.delete(id=pet_id)


app.add_scoped(APetService, PetServiceDB)
