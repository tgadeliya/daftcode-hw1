from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello Wow!"}

@app.get("/hello/{name}")
async def read_name(name:str):
    return f"Hello {name}"
