from typing import List

from cafeto.mvc import BaseController
from cafeto.responses import Ok, NoContent, NotFound
from cafeto.errors import Error

import pets.dtos as dtos

from config import app
from pets.errors import UserNotFound
from pets.services import AUserService


@app.controller()
class UserController(BaseController):
    @app.get('/user')
    async def list(self, service: AUserService) -> List[dtos.UserResponseDto]:
        response = await service.list()
        return Ok(response)
    
    @app.get('/user/{id}')
    async def retrieve(self, id: int, service: AUserService) -> dtos.UserResponseDto:
        try:
            response = await service.retrieve(id)
            return Ok(response)
        except UserNotFound as e:
            return NotFound([Error('user-not-found', e.msg, '__model__')])

    @app.post('/user')
    async def create(self, user_request: dtos.UserCreateRequestDto, service: AUserService) -> dtos.UserResponseDto:
        user_response: dtos.UserResponseDto = await service.create(user_request)
        return Ok(user_response)

    @app.put('/user/{id}')
    async def update(self, id: int, user_request: dtos.UserUpdateRequestDto, service: AUserService) -> dtos.UserResponseDto:
        try:
            user_response: dtos.UserResponseDto = await service.update(id, user_request)
            return Ok(user_response)
        except UserNotFound as e:
            return NotFound([Error('user-not-found', e.msg, '__model__')])

    @app.delete('/user/{id}')
    async def delete(self, id: int, service: AUserService) -> None:
        try:
            await service.delete(id)
            return NoContent()
        except UserNotFound as e:
            return NotFound([Error('user-not-found', e.msg, '__model__')])
