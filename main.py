from typing import Dict
from fastapi import FastAPI, HTTPException
import sqlite3
from pydantic import BaseModel

app = FastAPI()
app.last_patient_num = -1
app.patient_db = dict()


@app.get("/")
def root():
    return {"message": "Hello, hello.\
                        I don't know why you say goodbye, I say hello"}


@app.get("/welcome")
def welcome_msg():
    return {"message": "Hello, hello.\
             I don't know why you say goodbye, I say hello"}


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
    return Patient_response(id=app.last_patient_num, patient=rq)


@app.get("/patient/{pk}")
def read_patient(pk: int):
    if pk not in app.patient_db:
        raise HTTPException(status_code=204)
    return app.patient_db[pk]


@app.get(f"/tracks")
async def tracks(page: int = 0, per_page: int = 10):
    with sqlite3.connect("chinook.db") as connection:
        connection.row_factory = sqlite3.Row
        conn = connection.cursor()
        tracks = conn.execute(f"SELECT *\
                                   FROM Tracks\
                                   ORDER BY TrackId\
                                   LIMIT {per_page} OFFSET {per_page*page}").fetchall()
    return tracks


@app.get("/tracks/composers")
async def composers(composer_name: str):
    with sqlite3.connect("chinook.db") as connection:
        conn = connection.cursor()
        conn.row_factory = lambda cursor, x: x[0]
        response = conn.execute(f"SELECT name FROM tracks \
                                WHERE composer= '{composer_name}'\
                                ORDER BY name ASC").fetchall()
    if not response:
        raise HTTPException(status_code=404, detail={"error": "Item not found"})

    return response
