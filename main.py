import secrets
from hashlib import sha256
from typing import Dict

from fastapi import FastAPI, Response, status, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

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


@app.post("/login")
def session_login_with_cookies(user: str, password: str, response: Response):

    correct_username = secrets.compare_digest(user, "trudnY")
    correct_password = secrets.compare_digest(password, "PaC13Nt")

    if not(correct_username and correct_password):
        raise HTTPException(status_code=401)
    else:
        session_token = sha256(bytes(f"{user}{password}{app.secret_key}", encoding="utf8")).hexdigest()
        response.set_cookie(key="session_token", value=session_token)

        return RedirectResponse(url="https://daftcode-hw1.herokuapp.com/welcome", status_code=302)


@app.get(f"/tracks")
async def tracks(page: int, per_page: int):
    with sqlite3.connect("chinook.db") as connection:
        conn = connection.cursor()
        conn.row_factory = sqlite3.Row
        tracks = conn.execute(f"SELECT *\
                               FROM Tracks\
                               ORDER BY TrackId\
                               LIMIT {per_page} OFFSET {per_page*page}").fetchall()

        return {
            "TrackId": tracks["TrackId"],
            "Name": tracks["Name"],
            "AlbumId": tracks["AlbumId"],
            "MediaTypeId": tracks["MediaTypeId"],
            "GenreId": tracks["GenreId"],
            "Composer": tracks["Composer"],
            "Milliseconds": tracks["Milliseconds"],
            "Bytes": tracks["Bytes"],
            "UnitPrice": tracks["UnitPrice"]
        }