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

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Literal

# Cheaterstats core schema
class Cheater(BaseModel):
    """
    Cheaters collection schema
    Collection name: "cheater" (lowercase of class name)
    """
    discord_id: str = Field(..., description="Discord User ID")
    username: Optional[str] = Field(None, description="Discord username#discriminator if known")
    reason: Optional[str] = Field(None, description="Why the user was flagged")
    evidence_url: Optional[HttpUrl] = Field(None, description="Link to evidence (image/video/paste)")
    flagged_by: Optional[str] = Field(None, description="Moderator or system that flagged this user")
    status: Literal["flagged", "cleared", "under_review"] = Field("flagged", description="Current status")

# Example schemas (kept for reference)
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
