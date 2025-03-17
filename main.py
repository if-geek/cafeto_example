from config import app, base_ormar_config, engine

from pets.controllers import *


base_ormar_config.metadata.create_all(engine)

app.map_controllers()
app.use_schema()
app.use_swagger()
