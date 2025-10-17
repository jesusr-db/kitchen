"""Data models for location information."""

from datetime import datetime
from pydantic import BaseModel, Field


class DateRange(BaseModel):
    """Date range for available data."""
    start: datetime = Field(description="Start datetime of available data")
    end: datetime = Field(description="End datetime of available data")


class LocationConfig(BaseModel):
    """Configuration and metadata for a ghost kitchen location."""
    
    location_name: str = Field(description="Internal location identifier (e.g., 'sanfrancisco')")
    display_name: str = Field(description="Human-readable location name (e.g., 'San Francisco')")
    gk_lat: float = Field(description="Kitchen latitude coordinate")
    gk_lon: float = Field(description="Kitchen longitude coordinate")
    radius_mi: float = Field(description="Delivery radius in miles")
    total_orders: int = Field(description="Total orders in available data")
    date_range: DateRange = Field(description="Available data date range")
    
    class Config:
        json_schema_extra = {
            "example": {
                "location_name": "sanfrancisco",
                "display_name": "San Francisco",
                "gk_lat": 37.7749,
                "gk_lon": -122.4194,
                "radius_mi": 4.0,
                "total_orders": 15234,
                "date_range": {
                    "start": "2025-10-14T00:00:00Z",
                    "end": "2025-10-17T23:59:59Z"
                }
            }
        }


class LocationsResponse(BaseModel):
    """Response model for locations endpoint."""
    locations: list[LocationConfig] = Field(description="List of available locations")
    
    class Config:
        json_schema_extra = {
            "example": {
                "locations": [
                    {
                        "location_name": "sanfrancisco",
                        "display_name": "San Francisco",
                        "gk_lat": 37.7749,
                        "gk_lon": -122.4194,
                        "radius_mi": 4.0,
                        "total_orders": 15234,
                        "date_range": {
                            "start": "2025-10-14T00:00:00Z",
                            "end": "2025-10-17T23:59:59Z"
                        }
                    }
                ]
            }
        }
