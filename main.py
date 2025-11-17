import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Cheater

app = FastAPI(title="Cheaterstats API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "name": "Cheaterstats API",
        "message": "Cheaterstats backend is running",
        "endpoints": [
            {"GET": "/api/cheaters?discord_id=..."},
            {"POST": "/api/cheaters"},
            {"GET": "/test"},
        ],
    }

class CheaterCreate(BaseModel):
    discord_id: str
    username: Optional[str] = None
    reason: Optional[str] = None
    evidence_url: Optional[str] = None
    flagged_by: Optional[str] = None
    status: Optional[str] = "flagged"

@app.get("/api/cheaters")
def query_cheaters(discord_id: Optional[str] = None, username: Optional[str] = None, status: Optional[str] = None):
    """Query cheaters by discord_id, username, or status"""
    filters = {}
    if discord_id:
        filters["discord_id"] = discord_id
    if username:
        filters["username"] = username
    if status:
        filters["status"] = status

    try:
        results = get_documents("cheater", filters)
        # Normalize ObjectId to string
        for r in results:
            r["_id"] = str(r.get("_id"))
        return {"count": len(results), "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cheaters")
def create_cheater(payload: CheaterCreate):
    """Create a new cheater record"""
    try:
        cheater = Cheater(**payload.model_dump())
        inserted_id = create_document("cheater", cheater)
        return {"inserted_id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
