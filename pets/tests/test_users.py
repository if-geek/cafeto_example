import pytest
from cafeto.responses import codes


@pytest.mark.asyncio
async def test_create(setup_app):
    client = setup_app

    from pets.models import User

    data = {
        'name': 'John Doe',
        'email': 'john@jffon.com',
    }
    response = client.post('/user/user', json=data)
    assert response.status_code == codes.CODE_200_OK.value

    response = response.json()
    assert response['id'] == 1
    assert response['name'] == data['name']
    assert response['email'] == data['email']

    user = await User.objects.filter(id=1).first_or_none()
    assert user is not None
    assert user.name == data['name']
    assert user.email == data['email']
    
@pytest.mark.asyncio
async def test_create_validate(setup_app):
    client = setup_app

    from pets.models import User

    await User.objects.create(name='John Doe', email='john@doe.com')

    data = {
        'name': 'John Doe',
        'email': 'john@doe.com',
    }
    response = client.post('/user/user', json=data)
    assert response.status_code == codes.CODE_400_BAD_REQUEST.value

    response = response.json()
    assert response == {
        'errorList': [
            {
                'loc': ['email'],
                'type': 'email-exists',
                'msg': 'Email already exists'
            }
        ]
    }

@pytest.mark.asyncio
async def test_view(setup_app):
    client = setup_app

    from pets.models import User

    await User.objects.create(name='John Doe', email='john@doe.com')

    response = client.get('/user/user/1')
    assert response.status_code == codes.CODE_200_OK.value

    response = response.json()
    
    assert response == {
        'id': 1,
        'name': 'John Doe',
        'email': 'john@doe.com'
    }

@pytest.mark.asyncio
async def test_view_not_found(setup_app):
    client = setup_app

    response = client.get('/user/user/1')
    assert response.status_code == codes.CODE_404_NOT_FOUND.value

    response = response.json()
    assert response == [{'type': 'user-not-found', 'msg': 'User not found', 'loc': ['__model__']}]

@pytest.mark.asyncio
async def test_list(setup_app):
    client = setup_app

    from pets.models import User

    await User.objects.create(name='John Doe', email='john@doe.com')
    await User.objects.create(name='Jane Doe', email='jane@doe.com')

    response = client.get('/user/user')
    assert response.status_code == 200
    assert response.json() == [
        {'id': 1, 'name': 'John Doe', 'email': 'john@doe.com'},
        {'id': 2, 'name': 'Jane Doe', 'email': 'jane@doe.com'}
    ]

@pytest.mark.asyncio
async def test_update(setup_app):
    client = setup_app

    from pets.models import User

    user = await User.objects.create(name='John Doe', email='john@doe.com')

    data = {
        'id': user.id,
        'name': 'New John Doe',
        'email': 'john@doe.com'
    }
    response = client.put(f'/user/user/{user.id}', json=data)
    assert response.status_code == codes.CODE_200_OK.value

    response = response.json()
    assert response == {
        'id': 1,
        'name': 'New John Doe',
        'email': 'john@doe.com'
    }

    user = await User.objects.filter(id=1).first_or_none()
    assert user is not None
    assert user.name == 'New John Doe'


@pytest.mark.asyncio
async def test_update_validate(setup_app):
    client = setup_app

    from pets.models import User

    await User.objects.create(name='John Doe', email='john@doe.com')
    await User.objects.create(name='Jane Doe', email='jane@doe.com')

    data = {
        'id': 1,
        'name': 'Jane Doe',
        'email': 'jane@doe.com'
    }
    response = client.put(f'/user/user/1', json=data)

    assert response.status_code == codes.CODE_400_BAD_REQUEST.value

    response = response.json()
    assert response == {
        'errorList': [
            {
                'loc': ['email'],
                'type': 'email-exists',
                'msg': 'Email already exists'
            }
        ]
    }


@pytest.mark.asyncio
async def test_update_not_found(setup_app):
    client = setup_app

    id: int = 1

    data = {
        'id': id,
        'name': 'New John Doe',
        'email': 'john@doe.com'
    }
    response = client.put(f'/user/user/{id}', json=data)
    assert response.status_code == codes.CODE_404_NOT_FOUND.value

    response = response.json()
    assert response == [{'type': 'user-not-found', 'msg': 'User not found', 'loc': ['__model__']}]

@pytest.mark.asyncio
async def test_delete(setup_app):
    client = setup_app

    from pets.models import User, Pet

    await User.objects.create(name='John Doe', email='john@doe.com')
    await Pet.objects.create(name='Pinto', breed='Mutt', age=5, owner={'id': 1})
    await Pet.objects.create(name='Dante', breed='Shih tzu', age=2, owner={'id': 1})
    
    response = client.delete('/user/user/1')
    assert response.status_code == codes.CODE_204_NO_CONTENT.value

    assert await User.objects.filter(id=1).first_or_none() is None
    assert await Pet.objects.filter(owner=1).first_or_none() is None


@pytest.mark.asyncio
async def test_delete_not_found(setup_app):
    client = setup_app

    response = client.delete('/user/user/1')
    assert response.status_code == codes.CODE_404_NOT_FOUND.value

    response = response.json()
    assert response == [{'type': 'user-not-found', 'msg': 'User not found', 'loc': ['__model__']}]
