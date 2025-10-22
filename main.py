from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from db import get_db
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str

class Link(BaseModel):
    source: int
    target: int
    name: str 

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


@app.get("/glossary/getAll/")
def get_glossary(db = Depends(get_db)):
    return executeQuery(db, "SELECT * FROM glossary_item ORDER BY id")

@app.post("/glossary/create/")
def create_glossary_item(item: Item, db = Depends(get_db)):
    query = """
    INSERT INTO glossary_item (name, description) 
    VALUES (:name, :description)
    RETURNING *
    """
    return executeQuery(db, query, {"name": item.name, "description": item.description})

@app.delete("/glossary/delete/{id}/")
def delete_glossary_item(id: int, db = Depends(get_db)):
    check_query = "SELECT * FROM glossary_item WHERE id = :id"
    existing = executeQuery(db, check_query, {"id": id})
    
    if not existing:
        return {"error": "Item not found"}
    
    delete_query = "DELETE FROM glossary_item WHERE id = :id RETURNING *"
    result = executeQuery(db, delete_query, {"id": id})
    
    cleanup_links = "DELETE FROM link WHERE source = :id OR target = :id"
    executeQuery(db, cleanup_links, {"id": id})
    
    return result

@app.put("/glossary/update/{id}/")
def update_glossary_item(id: int, item: Item, db = Depends(get_db)):
    query = """
    UPDATE glossary_item 
    SET name = :name, description = :description 
    WHERE id = :id
    RETURNING *
    """
    return executeQuery(db, query, {
        "id": id, 
        "name": item.name, 
        "description": item.description
    })

@app.get("/links/getAll/")
def get_links(db = Depends(get_db)):
    return executeQuery(db, "SELECT * FROM link ORDER BY id")

@app.post("/links/create/")
def create_link(link: Link, db = Depends(get_db)):
    check_source = "SELECT id FROM glossary_item WHERE id = :source"
    check_target = "SELECT id FROM glossary_item WHERE id = :target"
    
    source_exists = executeQuery(db, check_source, {"source": link.source})
    target_exists = executeQuery(db, check_target, {"target": link.target})
    
    if not source_exists or not target_exists:
        return {"error": "Source or target glossary item not found"}
    
    existing_link = """
    SELECT * FROM link 
    WHERE source = :source AND target = :target AND name = :name
    """
    duplicate = executeQuery(db, existing_link, {
        "source": link.source, 
        "target": link.target, 
        "name": link.name
    })
    
    if duplicate:
        return {"error": "Link already exists"}
    
    query = """
    INSERT INTO link (source, target, name) 
    VALUES (:source, :target, :name)
    RETURNING *
    """
    return executeQuery(db, query, {
        "source": link.source, 
        "target": link.target, 
        "name": link.name
    })

@app.delete("/links/delete/{id}/")
def delete_link(id: int, db = Depends(get_db)):
    check_query = "SELECT * FROM link WHERE id = :id"
    existing = executeQuery(db, check_query, {"id": id})
    
    if not existing:
        return {"error": "Link not found"}
    
    delete_query = "DELETE FROM link WHERE id = :id RETURNING *"
    return executeQuery(db, delete_query, {"id": id})

@app.put("/links/update/{id}/") 
def update_link(id: int, link: Link, db = Depends(get_db)):
    check_source = "SELECT id FROM glossary_item WHERE id = :source"
    check_target = "SELECT id FROM glossary_item WHERE id = :target"
    
    source_exists = executeQuery(db, check_source, {"source": link.source})
    target_exists = executeQuery(db, check_target, {"target": link.target})
    
    if not source_exists or not target_exists:
        return {"error": "Source or target glossary item not found"}
    
    query = """
    UPDATE link 
    SET source = :source, target = :target, name = :name 
    WHERE id = :id
    RETURNING *
    """
    return executeQuery(db, query, {
        "id": id,
        "source": link.source, 
        "target": link.target, 
        "name": link.name
    })