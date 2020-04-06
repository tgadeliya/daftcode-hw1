from typing import Dict
from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel


app = FastAPI()

app.last_patient_num = 0
app.patient_db = dict()


@app.get("/")
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}


# TODO: Check whether possible to __meta__ parse request to method
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


class GiveMeSomethingRq(BaseModel):
    name: str


class GiveMeSomethingResp(BaseModel):
    received: Dict
    constant_data: str = "Jan Nowak"

@app.post("/db", response_model=GiveMeSomethingResp)
def receive_name(rq: GiveMeSomethingRq):
    return GiveMeSomethingResp(received=rq.dict())


class Patient_request(BaseModel):
    name: str
    surename: str


class Patient_response(BaseModel):
    id: int
    patient: Dict

@app.post("/patient", response_model=Patient_response)
def patient(rq: Patient_request):
    app.last_patient_num += 1
    app.patient_db[app.last_patient_num] = rq.dict()
    return Patient_response(id=app.last_patient_num, patient=rq.dict())

@app.get("/patient/{pk}")
def read_patient(pk: int):
        if pk not in app.patient_db:
            raise  HTTPException(status_code=204)
        return app.patient_db[pk]