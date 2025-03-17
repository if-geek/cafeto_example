import ormar

from config import base_ormar_config
from .user_model import User



class Pet(ormar.Model):
    ormar_config = base_ormar_config.copy(tablename='pets')

    id: int = ormar.Integer(primary_key=True)
    name: str = ormar.String(max_length=100)
    breed: str = ormar.String(max_length=100)
    age: int = ormar.Integer()
    owner: User = ormar.ForeignKey(User, name='owner_id')
