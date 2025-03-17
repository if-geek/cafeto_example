import ormar

from config import base_ormar_config

class User(ormar.Model):
    ormar_config = base_ormar_config.copy(tablename='users')

    id: int = ormar.Integer(primary_key=True)
    name: str = ormar.String(max_length=100)
    email: str = ormar.String(max_length=100)
