from fastapi import FastAPI
from enum import StrEnum

class ModelName(StrEnum):
    alex_net = "alex_net"
    resnet = "resnet"
    le_net = "le_net"
app = FastAPI()

@app.get("/items/{item_id}")
async def get_item(item_id:int):
    return {"item_id":item_id}

@app.get("/")
async def root():
    return {"message": "Hello there"}

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    return {"model_name": model_name, "message": "Hello there"}


# noinspection PathParameterInspection
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}

fake_things_db = [{"thing_name": "Foo"}, {"thing_name": "Bar"}, {"thing_name": "Baz"}]


@app.get("/things/")
async def read_things(skip: int = 0, limit: int = 10):
    return fake_things_db[skip : skip + limit]

#Testing neovim for git commit