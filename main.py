from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from db import get_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def executeQuery(db, str):
    res = db.execute(text(str))
    rows = res.mappings().all()
    return rows


@app.get("/glossary/")
def get_glossary(db = Depends(get_db)):
    return executeQuery(db, "SELECT * FROM glossary_item")

@app.get("/links/")
def get_links(db = Depends(get_db)):
    return executeQuery(db, "SELECT * FROM link")