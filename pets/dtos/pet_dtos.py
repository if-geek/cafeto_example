from cafeto.models import BaseModel, validate
from cafeto.errors import FieldError, Error

from pets.errors import UserNotFound
from pets.services import AUserService


class OwnerDto(BaseModel):
    id: int


class PetBaseDto(BaseModel):
    name: str
    breed: str
    age: int
    owner: OwnerDto


class PetResponseDto(PetBaseDto):
    id: int


class PetRequestDto(PetBaseDto):
    @validate('owner')
    async def validate_owner(value: OwnerDto, _: dict, service: AUserService) -> int:
        try:
            await service.retrieve(value.id)
        except UserNotFound:
            raise FieldError(Error('owner-not-found', 'Owner not found'))
        return value


class PetCreateRequestDto(PetRequestDto):
    ...


class PetUpdateRequestDto(PetRequestDto):
    ...
