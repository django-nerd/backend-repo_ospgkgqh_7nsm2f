import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import PatientRegistration, RegistrationPublic

app = FastAPI(title="Hospital Portfolio & Online Registration API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hospital API Running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
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
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# Helpers
class RegistrationCreateResponse(BaseModel):
    id: str
    message: str


def _to_public(doc: dict) -> RegistrationPublic:
    return RegistrationPublic(
        id=str(doc.get("_id")),
        full_name=doc.get("full_name"),
        department=doc.get("department"),
        preferred_date=doc.get("preferred_date"),
        status=doc.get("status", "pending"),
        created_at=doc.get("created_at"),
    )


# Public endpoint: create new patient registration
@app.post("/api/registrations", response_model=RegistrationCreateResponse)
async def create_registration(payload: PatientRegistration):
    try:
        new_id = create_document("patientregistration", payload)
        return {"id": new_id, "message": "Registration submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Public endpoint: list recent registrations (masked fields)
@app.get("/api/registrations", response_model=List[RegistrationPublic])
async def list_registrations(limit: int = 20):
    try:
        docs = get_documents("patientregistration", limit=limit)
        return [_to_public(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Admin endpoints (simple, no auth yet; ready for future roles)
@app.get("/api/admin/registrations", response_model=List[RegistrationPublic])
async def admin_list_registrations(limit: int = 100):
    try:
        docs = get_documents("patientregistration", limit=limit)
        return [_to_public(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/admin/registrations/{reg_id}", response_model=RegistrationPublic)
async def admin_get_registration(reg_id: str):
    try:
        if db is None:
            raise Exception("Database not available")
        doc = db["patientregistration"].find_one({"_id": ObjectId(reg_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Registration not found")
        return _to_public(doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class StatusUpdate(BaseModel):
    status: str


@app.patch("/api/admin/registrations/{reg_id}")
async def admin_update_status(reg_id: str, payload: StatusUpdate):
    try:
        if db is None:
            raise Exception("Database not available")
        result = db["patientregistration"].update_one(
            {"_id": ObjectId(reg_id)},
            {"$set": {"status": payload.status}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Registration not found")
        return {"message": "Status updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
