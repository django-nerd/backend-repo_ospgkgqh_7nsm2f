"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from datetime import datetime

# Core schemas for the Hospital Portfolio + Online Registration

class PatientRegistration(BaseModel):
    """
    Patient registration form data
    Collection name: "patientregistration"
    """
    full_name: str = Field(..., min_length=3, description="Patient full name")
    email: EmailStr = Field(..., description="Contact email")
    phone: str = Field(..., min_length=8, max_length=20, description="Phone number")
    birth_date: Optional[str] = Field(None, description="Birth date (YYYY-MM-DD)")
    gender: Optional[Literal['male','female','other']] = Field(None, description="Gender")
    address: Optional[str] = Field(None, description="Home address")
    department: str = Field(..., description="Target department/polyclinic, e.g., Cardiology")
    preferred_date: Optional[str] = Field(None, description="Preferred visit date (YYYY-MM-DD)")
    symptoms: Optional[str] = Field(None, description="Short description of symptoms")
    status: Literal['pending','confirmed','cancelled'] = Field('pending', description="Registration status")

class AdminUser(BaseModel):
    """
    Admin user model (for future extension)
    Collection name: "adminuser"
    """
    name: str = Field(...)
    role: Literal['admin','superadmin'] = Field('admin')
    email: Optional[EmailStr] = None
    is_active: bool = Field(True)

# Example schemas retained for reference and potential future features
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True


# Response models
class RegistrationPublic(BaseModel):
    id: str
    full_name: str
    department: str
    preferred_date: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
