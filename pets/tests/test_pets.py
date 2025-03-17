from typing import List
import pytest

from cafeto.responses import codes


@pytest.fixture()
def setup_breed_service_app(setup_app):
    from cafeto import App
    from pets.services.breeds_service import ABreedsService

    class BreedsServiceMockup(ABreedsService):
        async def list_by_breed(self, base_url: str, breed: str) -> List[str]:
            mock_data = {
                'dog': ['Mixed Breed', 'Labrador', 'Golden Retriever', 'Poodle'],
                'cat': ['Domestic Shorthair', 'Abyssinian', 'American Bobtail', 'American Curl']
            }
            return mock_data.get(breed, [])

    client = setup_app
    app: App = client.app
    app.add_scoped(ABreedsService, BreedsServiceMockup, override=True)

    yield client
    

@pytest.mark.asyncio
async def test_create(setup_app):
    client = setup_app

    from pets.models import User, Pet

    user = await User.objects.create(name='John Doe', email='john@doe.com')

    pet_data = {
        'name': 'Oreo',
        'breed': 'Mutt',
        'age': 3,
        'owner': {'id': user.id}
    }
    response = client.post('/pet/pet', json=pet_data)
    assert response.status_code == codes.CODE_200_OK.value

    response = response.json()
    assert response['id'] == 1
    assert response['name'] == pet_data['name']
    assert response['breed'] == pet_data['breed']
    assert response['age'] == pet_data['age']
    assert response['owner']['id'] == user.id

    pet = await Pet.objects.filter(id=1).first_or_none()
    assert pet is not None
    assert pet.name == pet_data['name']
    assert pet.breed == pet_data['breed']
    assert pet.age == pet_data['age']
    assert pet.owner.id == user.id

@pytest.mark.asyncio
async def test_create_validate(setup_app):
    client = setup_app

    from pets.models import User

    await User.objects.create(name='John Doe', email='john@doe.com')

    pet_data = {
        'name': 'Ozzy',
        'breed': 'Golden Retriever',
        'age': 3,
        'owner': {'id': 999}
    }
    response = client.post('/pet/pet', json=pet_data)
    assert response.status_code == codes.CODE_400_BAD_REQUEST.value

    response = response.json()
    assert response == {
        'errorList': [
            {
                'loc': ['owner'],
                'type': 'owner-not-found',
                'msg': 'Owner not found'
            }
        ]
    }

@pytest.mark.asyncio
async def test_view(setup_app):
    client = setup_app

    from pets.models import User, Pet

    user = await User.objects.create(name='John Doe', email='john@doe.com')

    await Pet.objects.create(name='Buddy', breed='Golden Retriever', age=3, owner=user)

    response = client.get('/pet/pet/1')
    assert response.status_code == codes.CODE_200_OK.value

    response = response.json()
    assert response == {
        'id': 1,
        'name': 'Buddy',
        'breed': 'Golden Retriever',
        'age': 3,
        'owner': {
            'id': user.id
        }
    }

@pytest.mark.asyncio
async def test_view_not_found(setup_app):
    client = setup_app

    response = client.get('/pet/pet/1')
    assert response.status_code == codes.CODE_404_NOT_FOUND.value

    response = response.json()
    assert response == [{'type': 'pet-not-found', 'msg': 'Pet not found', 'loc': ['__model__']}]

@pytest.mark.asyncio
async def test_list(setup_app):
    client = setup_app

    from pets.models import User, Pet

    user = await User.objects.create(name='John Doe', email='john@doe.com')

    await Pet.objects.create(name='Buddy', breed='Golden Retriever', age=3, owner=user)
    await Pet.objects.create(name='Max', breed='Labrador', age=5, owner=user)

    response = client.get('/pet/pet')
    assert response.status_code == 200
    assert response.json() == [
        {'id': 1, 'name': 'Buddy', 'breed': 'Golden Retriever', 'age': 3, 'owner': {'id': user.id}},
        {'id': 2, 'name': 'Max', 'breed': 'Labrador', 'age': 5, 'owner': {'id': user.id}}
    ]

@pytest.mark.asyncio
async def test_update(setup_app):
    client = setup_app

    from pets.models import User, Pet

    user = await User.objects.create(name='John Doe', email='john@doe.com')

    await Pet.objects.create(name='Buddy', breed='Golden Retriever', age=3, owner=user)

    # Update the pet
    update_data = {
        'name': 'Buddy Updated',
        'breed': 'Golden Retriever',
        'age': 4,
        'owner': {'id': user.id}
    }
    response = client.put('/pet/pet/1', json=update_data)
    assert response.status_code == codes.CODE_200_OK.value

    response = response.json()
    assert response == {
        'id': 1,
        'name': 'Buddy Updated',
        'breed': 'Golden Retriever',
        'age': 4,
        'owner': {
            'id': user.id
        }
    }

    pet = await Pet.objects.filter(id=1).first_or_none()
    assert pet is not None
    assert pet.name == 'Buddy Updated'
    assert pet.age == 4

@pytest.mark.asyncio
async def test_update_not_found(setup_app):
    client = setup_app

    from pets.models import User

    user = await User.objects.create(name='John Doe', email='john@doe.com')

    update_data = {
        'name': 'Buddy Updated',
        'breed': 'Golden Retriever',
        'age': 4,
        'owner': {'id': user.id}
    }
    response = client.put('/pet/pet/1', json=update_data)
    assert response.status_code == codes.CODE_404_NOT_FOUND.value

    response = response.json()
    assert response == [{'type': 'pet-not-found', 'msg': 'Pet not found', 'loc': ['__model__']}]

@pytest.mark.asyncio
async def test_delete(setup_app):
    client = setup_app

    from pets.models import User, Pet

    user = await User.objects.create(name='John Doe', email='john@doe.com')

    await Pet.objects.create(name='Buddy', breed='Golden Retriever', age=3, owner=user)
    await Pet.objects.create(name='Max', breed='Labrador', age=5, owner=user)

    response = client.delete('/pet/pet/1')
    assert response.status_code == codes.CODE_204_NO_CONTENT.value

    assert await Pet.objects.filter(id=1).first_or_none() is None

@pytest.mark.asyncio
async def test_delete_not_found(setup_app):
    client = setup_app

    response = client.delete('/pet/pet/1')
    assert response.status_code == codes.CODE_404_NOT_FOUND.value

    response = response.json()
    assert response == [{'type': 'pet-not-found', 'msg': 'Pet not found', 'loc': ['__model__']}]

@pytest.mark.asyncio
async def test_get_breeds(setup_breed_service_app):
    client = setup_breed_service_app
    response = client.get('/pet/breeds/dog')
    assert response.status_code == codes.CODE_200_OK.value
    assert response.json() == {'data': ['Mixed Breed', 'Labrador', 'Golden Retriever', 'Poodle']}

@pytest.mark.asyncio
async def test_get_breeds_animal_not_found(setup_breed_service_app):
    client = setup_breed_service_app
    response = client.get('/pet/breeds/dinasour')
    assert response.status_code == codes.CODE_200_OK.value
    assert response.json() == {'data': []}
