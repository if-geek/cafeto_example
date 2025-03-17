from typing import List

import httpx

from cafeto.mvc import BaseController
from cafeto.responses import Ok, NoContent, NotFound
from cafeto.errors import Error
from cafeto.dtos import GenericResponseDto

import pets.dtos as dtos

from config import app
from pets.errors import PetNotFound
from pets.services import APetService
from pets.services.breeds_service import ABreedsService


@app.controller()
class PetController(BaseController):
    @app.get('/pet')
    async def list(self, service: APetService) -> List[dtos.PetResponseDto]:
        response = await service.list()
        return Ok(response)
    
    @app.get('/pet/{id}')
    async def retrieve(self, id: int, service: APetService) -> dtos.PetResponseDto:
        try:
            response = await service.retrieve(id)
            return Ok(response)
        except PetNotFound as e:
            return NotFound([Error('pet-not-found', e.msg, '__model__')])

    @app.post('/pet')
    async def create(self, pet_request: dtos.PetCreateRequestDto, service: APetService) -> dtos.PetResponseDto:
        pet_response: dtos.UserResponseDto = await service.create(pet_request)
        return Ok(pet_response)

    @app.put('/pet/{id}')
    async def update(self, id: int, pet_request: dtos.PetUpdateRequestDto, service: APetService) -> dtos.PetResponseDto:
        try:
            pet_response: dtos.UserResponseDto = await service.update(id, pet_request)
            return Ok(pet_response)
        except PetNotFound as e:
            return NotFound([Error('pet-not-found', e.msg, '__model__')])

    @app.delete('/pet/{id}')
    async def delete(self, id: int, service: APetService) -> None:
        try:
            await service.delete(id)
            return NoContent()
        except PetNotFound as e:
            return NotFound([Error('pet-not-found', e.msg, '__model__')])

    @app.get('/breeds/{animal}')
    async def breeds(self, animal: str, service: ABreedsService) -> GenericResponseDto[List[str]]:
        '''
        summary: List breeds by animal
        description: List breeds by animal the options are (dog, cat, bird, fish, reptile, rabbit, hamster)
        '''
        base_url  = str(self.request.base_url)

        try:
            list_by_breed = await service.list_by_breed(base_url, animal)
            return Ok(GenericResponseDto(data=list_by_breed))
        except Exception as e:  # pragma: no cover
            return NotFound({"error": str(e)})
