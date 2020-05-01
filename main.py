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
        raise HTTPException(status_code=404, detail={"error":
                                                     "Composer not found"})

    return response

class Album(BaseModel):
    title: str
    artist_id: str


@app.post("/albums")
async def albums(album: Album):
    is_artid_exists = app.db_connection(
            f"SELECT artistid\
            FROM albums\
            WHERE artistid = {album.artist_id}\
            LIMIT 1").fetchall()

    if not is_artid_exists:
        raise HTTPException(status_code=404,
                            detail={"error":
                                    f"ArtistId= {album.artist_id} not found!"})

    query = await app.db_connection.execute(
                    f"INSERT INTO albums (title) VALUES (?)",
                    (album.title, album.artist_id)).fetchall()
    app.db_connection.commit()
    new_album_id = query.lastrowid

    artist = app.db_connection.execute(
            "SELECT albumid, title, artistid FROM albums WHERE albumid = ?",
            (new_album_id)).fetchone()
    return artist



@app.get("/albums/{album_id}")
def get_albumid(album_id: int):
    with sqlite3.connect("chinook.db") as connection:
        conn = connection.cursor()
        conn.row_factory = sqlite3.Row
        response = conn.execute(f"SELECT albumId, title, artistId\
                                      FROM albums\
                                      WHERE albumid = {album_id}").fetchall()
    return response
