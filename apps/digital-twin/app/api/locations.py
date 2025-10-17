"""API endpoints for location management."""

import logging
from fastapi import APIRouter, HTTPException

from app.models.location import LocationsResponse
from app.services import location_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/locations", response_model=LocationsResponse)
async def get_locations():
    """
    Get list of available ghost kitchen locations.
    
    Returns metadata including:
    - Location name and display name
    - Kitchen coordinates (lat/lon)
    - Delivery radius
    - Total order count
    - Available data date range
    
    This endpoint is typically called once on app load to populate
    the location selector dropdown.
    """
    try:
        locations = location_service.get_available_locations()
        return LocationsResponse(locations=locations)
    
    except Exception as e:
        logger.error(f"Error in get_locations endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch locations: {str(e)}"
        )
