import secrets
from hashlib import sha256
from typing import Dict

from fastapi import FastAPI

import sqlite3

from pydantic import BaseModel
from starlette.responses import RedirectResponse

app = FastAPI()
app.secret_key = "There are places I'll remember All my life, though some have changed Some forever, not for better Some have gone, and some remain"
app.last_patient_num = -1
app.patient_db = dict()


@app.get("/")
def root():
    return {"message": "Hello, hello. I don't know why you say goodbye, I say hello"}


@app.get("/welcome")
def welcome_msg():
    return {"message": "Hello, hello. I don't know why you say goodbye, I say hello"}


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
async def tracks(page: int, per_page: int):
    with sqlite3.connect("chinook.db") as connection:
        conn = connection.cursor()
        tracks = conn.execute(f"SELECT *\
                                   FROM Tracks\
                                   ORDER BY TrackId\
                                   LIMIT {per_page} OFFSET {per_page*page}").fetchall()

    return tracks
