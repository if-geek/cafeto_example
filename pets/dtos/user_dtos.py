from cafeto.models import BaseModel, validate
from cafeto.errors import FieldError, Error

from pets.services import AUserService


class UserBaseDto(BaseModel):
    name: str
    email: str


class UserRequestDto(UserBaseDto):
    ...


class UserCreateRequestDto(UserRequestDto):
    @validate('email')
    async def validate_email(value: str, _: dict, service: AUserService) -> str:
        user = await service.user_exists(value)
        if user:
            raise FieldError(Error('email-exists', 'Email already exists'))
        return value


class UserUpdateRequestDto(UserRequestDto):
    id: int

    @validate('email')
    async def validate_email(value: str, data: dict, service: AUserService) -> str:
        user = await service.user_exists(value, data.get('id'))
        if user:
            raise FieldError(Error('email-exists', 'Email already exists'))
        return value


class UserResponseDto(UserBaseDto):
    id: int
