from typing import Dict
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()
app.counter = 0


class HelloResp(BaseModel):
    msg: str


@app.get("/counter")
def counter():
    app.counter += 1
    return str(app.counter)


@app.get("/")
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}


@app.get("/hello/{name}", response_model=HelloResp)
async def read_name(name: str):
    return HelloResp(msg=f"Hello {name}")


@app.get("/method")
def method_get():
    return {"method": "GET"}


@app.post("/method")
def method_post():
    return {"method": "POST"}


@app.delete("/method")
def method_delete():
    return {"method": "DELETE"}


@app.put("/method")
def method_put():
    return {"method": "PUT"}

# TODO: Check whether possible to __meta__ parse request to method
# @getattr(app, "get")("/")
# def resp():
# return 1


class GiveMeSomethingRq(BaseModel):
    name: str


class GiveMeSomethingResp(BaseModel):
    received: Dict
    constant_data: str = "Jan Nowak"


@app.post("/db", response_model=GiveMeSomethingResp)
def receive_name(rq: GiveMeSomethingRq):
    return GiveMeSomethingResp(received=rq.dict())
