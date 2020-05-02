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


@app.post("/albums", status_code=201)
async def albums(album: Album):
    with sqlite3.connect("chinook.db") as connection:
        conn = connection.cursor()
        conn.row_factory = sqlite3.Row

        is_artistid_exists = conn.execute(
                f"SELECT artistid\
                FROM albums\
                WHERE artistid = {album.artist_id}\
                LIMIT 1").fetchall()

        if not is_artistid_exists:
            raise HTTPException(status_code=404,
                                detail={"error":
                                        f"ArtistId= {album.artist_id} not found!"})

        query = conn.execute(
                        f"INSERT INTO albums (title, artistId)\
                          VALUES('{album.title}', '{album.artist_id}')",
                        ).fetchall()

        connection.commit()
        new_album_id = conn.lastrowid

        album = conn.execute(
                f"SELECT albumid, title, artistid\
                  FROM albums\
                  WHERE albumid = {new_album_id}").fetchone()

        return album


@app.get("/albums/{album_id}")
def get_albumid(album_id: int):
    with sqlite3.connect("chinook.db") as connection:
        conn = connection.cursor()
        conn.row_factory = sqlite3.Row
        response = conn.execute(f"SELECT albumId, title, artistId\
                                      FROM albums\
                                      WHERE albumid = {album_id}").fetchone()
    return response


class Customer(BaseModel):
    company: str = None
    address: str = None
    city: str = None
    state: str = None
    country: str = None
    postalcode: str = None
    fax: str = None



@app.put("/customers/{customer_id}", status_code= 200)
async def put_customer(customer_id: int, customer: Customer):
    with sqlite3.connect("chinook.db") as connection:
        conn = connection.cursor()
        conn.row_factory = sqlite3.Row

        is_customerid_exists = conn.execute(
                f"SELECT customerid\
                FROM customers\
                WHERE customerid = {customer_id}\
                LIMIT 1").fetchone()

        if not is_customerid_exists:
            raise HTTPException(status_code=404,
                                detail={"error":
                                        f"Customer id {customer_id} not found"})

        update_data = [f"{k} = '{v}'" for k, v in customer.dict(exclude_unset=True).items()]
        update_data_str = ','.join(update_data)

        query = conn.execute(f"UPDATE customers\
                               SET {update_data_str} WHERE customerid=?", (customer_id,)).fetchall()

        connection.commit()

        response = conn.execute(f"SELECT * FROM customers\
                                 WHERE customerid = {customer_id}").fetchone()
        return response



@app.get("/sales", status_code=200)
def sales(category:str):
    with sqlite3.connect("chinook.db") as connection:
        conn = connection.cursor()
        conn.row_factory = sqlite3.Row

        if (category == "customers"):
            response = conn.execute(
                "SELECT i.CustomerId, c.email, c.phone, ROUND(SUM(Total),2) AS Sum\
                 FROM invoices i\
                 JOIN customers c ON i.CustomerId = c.CustomerId\
                 GROUP BY  i.CustomerId\
                 ORDER BY  Sum DESC, i.CustomerId").fetchall()
        elif (category == "genres"):
            response = conn.execute(
                "SELECT g.Name, SUM(Quantity) AS Sum FROM tracks t\
                JOIN invoice_items i ON t.TrackId = i.TrackId\
                JOIN genres g ON t.GenreId = g.GenreId\
                GROUP BY  t.GenreId\
                ORDER BY  Sum DESC, g.Name").fetchall()
        else:
            raise HTTPException(status_code=404, detail={"error": "Inappropriate category"})

        return response
