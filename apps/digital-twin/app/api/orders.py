from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
import logging

from app.services import order_service
from app.models.order import TimeRangeResponse, OrderLifecycle

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/locations/{location}/time-range", response_model=TimeRangeResponse)
async def get_time_range(
    location: str,
    start: str = Query(..., description="Start time (ISO 8601 format)"),
    end: str = Query(..., description="End time (ISO 8601 format)"),
    limit: int = Query(100, ge=1, le=500, description="Max orders to return")
):
    """
    Get orders and metrics for a location within a time range.
    
    Example:
        GET /api/v1/locations/sanfrancisco/time-range?start=2025-10-13T00:00:00&end=2025-10-14T00:00:00
    """
    try:
        start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(end.replace('Z', '+00:00'))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid datetime format: {e}")
    
    try:
        result = order_service.get_orders_in_range(
            location=location,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        return result
    except Exception as e:
        logger.error(f"Error fetching time range data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch orders: {str(e)}")


@router.get("/orders/{order_id}", response_model=OrderLifecycle)
async def get_order(order_id: str):
    """
    Get complete lifecycle for a specific order.
    
    Example:
        GET /api/v1/orders/ORD-12345
    """
    try:
        order = order_service.get_order_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
        return order
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch order: {str(e)}")
