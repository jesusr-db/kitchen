"""Service layer for location operations."""

import logging
import json
from datetime import datetime
from typing import Dict

from app.config import settings
from app.db import execute_query
from app.models.location import LocationConfig, DateRange

logger = logging.getLogger(__name__)

# Location display names mapping
LOCATION_DISPLAY_NAMES = {
    "sanfrancisco": "San Francisco",
    "chicago": "Chicago",
    "houston": "Houston",
    "houston_westside": "Houston Westside",
}

# Default coordinates from generator configs (actual kitchen addresses)
DEFAULT_COORDINATES = {
    "sanfrancisco": (37.7913, -122.3937, 4.0),  # 160 Spear St, San Francisco, CA 94105
    "chicago": (41.8781, -87.6298, 5.0),
    "houston": (29.7604, -95.3698, 5.0),
    "houston_westside": (29.7604, -95.5698, 5.0),
}


def get_available_locations() -> list[LocationConfig]:
    """
    Get list of available locations with metadata.
    
    Queries the lakeflow.all_events table to find distinct locations,
    then enriches with order counts and date ranges.
    
    Returns:
        List of LocationConfig objects
    """
    logger.info("Fetching available locations")
    
    try:
        # Query for distinct locations with counts and date ranges
        query = f"""
        SELECT 
            location,
            COUNT(DISTINCT order_id) as total_orders,
            MIN(ts) as start_date,
            MAX(ts) as end_date
        FROM {settings.catalog}.{settings.lakeflow_schema}.all_events
        WHERE location IS NOT NULL
        GROUP BY location
        ORDER BY location
        """
        
        results = execute_query(query)
        
        if not results:
            logger.warning("No locations found in database")
            return []
        
        locations = []
        for row in results:
            location_name = row["location"]
            
            # Get display name
            display_name = LOCATION_DISPLAY_NAMES.get(
                location_name,
                location_name.replace("_", " ").title()
            )
            
            # Get coordinates (try to extract from data, fallback to defaults)
            gk_lat, gk_lon, radius_mi = _get_location_coordinates(location_name)
            
            # Create location config
            location_config = LocationConfig(
                location_name=location_name,
                display_name=display_name,
                gk_lat=gk_lat,
                gk_lon=gk_lon,
                radius_mi=radius_mi,
                total_orders=row["total_orders"],
                date_range=DateRange(
                    start=row["start_date"],
                    end=row["end_date"]
                )
            )
            
            locations.append(location_config)
            logger.info(
                f"Found location: {location_name} "
                f"({row['total_orders']} orders, "
                f"{row['start_date']} to {row['end_date']})"
            )
        
        return locations
    
    except Exception as e:
        logger.error(f"Error fetching locations: {e}")
        raise


def _get_location_coordinates(location_name: str) -> tuple[float, float, float]:
    """
    Get coordinates for a location from order_created events.
    
    Extracts gk_location from the first order_created event for this location.
    Falls back to default coordinates if not found.
    
    Args:
        location_name: Location identifier
    
    Returns:
        Tuple of (latitude, longitude, radius_mi)
    """
    try:
        # Try to get coordinates from order_created events
        query = f"""
        SELECT body
        FROM {settings.catalog}.{settings.lakeflow_schema}.all_events
        WHERE location = :location
          AND event_type = 'order_created'
        LIMIT 1
        """
        
        results = execute_query(query, {"location": location_name})
        
        if results and results[0]["body"]:
            # Parse JSON body
            body = json.loads(results[0]["body"])
            
            # Try to extract gk coordinates if available
            # Note: This assumes generator includes gk_location in body
            # If not available, we'll use defaults
            if "gk_lat" in body and "gk_lon" in body:
                return (
                    float(body["gk_lat"]),
                    float(body["gk_lon"]),
                    float(body.get("radius_mi", 4.0))
                )
    
    except Exception as e:
        logger.warning(f"Could not extract coordinates for {location_name}: {e}")
    
    # Fallback to default coordinates
    if location_name in DEFAULT_COORDINATES:
        logger.info(f"Using default coordinates for {location_name}")
        return DEFAULT_COORDINATES[location_name]
    
    # Ultimate fallback
    logger.warning(f"No coordinates found for {location_name}, using generic defaults")
    return (0.0, 0.0, 5.0)
