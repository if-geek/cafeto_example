from __future__ import annotations
from typing import List, Optional, overload
from abc import ABC

from pets.models import User, Pet
from config import app, database

import pets.dtos as dtos
from pets.errors import UserNotFound


class AUserService(ABC):
    async def retrieve(self, id: int) -> dtos.UserResponseDto: ...

    async def list(self) -> list[dtos.UserResponseDto]: ...

    async def create(self, user: dtos.UserCreateRequestDto) -> dtos.UserResponseDto: ...

    async def update(self, id: int, user: dtos.UserUpdateRequestDto) -> dtos.UserResponseDto: ...

    async def delete(self, id: int) -> bool: ...

    @overload
    async def user_exists(self, email: str) -> bool: ...

    @overload
    async def user_exists(self, email: str, id: int=None) -> bool: ...

    async def user_exists(self, email: str, id: int=None) -> bool: ...


class UserServiceDB(AUserService):
    async def retrieve(self, id: int) -> dtos.UserResponseDto:
        user: Optional[User] = await User.objects.filter(id=id).first_or_none()
        if user:
            return dtos.UserResponseDto(**user.model_dump())
        raise UserNotFound('User not found')

    async def list(self) -> list[dtos.UserResponseDto]:
        users: List[User] = await User.objects.all()
        return [dtos.UserResponseDto(**user.model_dump()) for user in users]

    async def create(self, user_request: dtos.UserCreateRequestDto) -> dtos.UserResponseDto:
        user: Optional[User] = await User.objects.create(**user_request.model_dump())
        return dtos.UserResponseDto(**user.model_dump())

    async def update(self, id: int, user_request: dtos.UserUpdateRequestDto) -> dtos.UserResponseDto:
        async with database.transaction():
            user = await User.objects.filter(id=id).first_or_none()
            if user is None:
                raise UserNotFound('User not found')
            await user.update(**user_request.model_dump())
            return dtos.UserResponseDto(**user.model_dump())

    async def delete(self, id: int) -> None:
        async with database.transaction():
            user_exists: bool = await User.objects.filter(id=id).exists()
            if not user_exists:
                raise UserNotFound('User not found')
            await Pet.objects.delete(owner=id)
            await User.objects.delete(id=id)
    
    @overload
    async def user_exists(self, email: str) -> bool: ...

    @overload
    async def user_exists(self, email: str, id: int=None) -> bool: ...

    async def user_exists(self, email: str, id: int=None) -> bool:
        if id is not None:
            return await User.objects.filter(email=email).exclude(id=id).exists()
        return await User.objects.filter(email=email).exists()


app.add_scoped(AUserService, UserServiceDB)
