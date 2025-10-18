from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class OrderEvent(BaseModel):
    """Single event in order lifecycle."""
    event_type: str = Field(description="Event type: order_created, gk_started, delivered, etc.")
    timestamp: datetime = Field(description="Event timestamp")
    body: Optional[Dict[str, Any]] = Field(default=None, description="Event body JSON")


class OrderLifecycle(BaseModel):
    """Complete order lifecycle with all events."""
    order_id: str = Field(description="Unique order identifier")
    location: str = Field(description="Location name")
    brand: str = Field(description="Restaurant brand")
    customer_lat: Optional[float] = Field(default=None, description="Customer delivery latitude")
    customer_lon: Optional[float] = Field(default=None, description="Customer delivery longitude")
    events: list[OrderEvent] = Field(description="All events for this order")
    created_at: datetime = Field(description="Order creation timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Order completion timestamp")
    status: str = Field(description="Current order status")


class OrderMetrics(BaseModel):
    """Aggregate metrics for a time range."""
    total_orders: int = Field(description="Total orders in time range")
    completed_orders: int = Field(description="Completed orders")
    in_progress_orders: int = Field(description="Orders currently in progress")
    avg_prep_time_minutes: Optional[float] = Field(default=None, description="Average kitchen prep time")
    avg_delivery_time_minutes: Optional[float] = Field(default=None, description="Average delivery time")
    avg_total_time_minutes: Optional[float] = Field(default=None, description="Average total order time")


class TimeRangeResponse(BaseModel):
    """Response for time-range query."""
    location: str = Field(description="Location name")
    start_time: datetime = Field(description="Query start time")
    end_time: datetime = Field(description="Query end time")
    metrics: OrderMetrics = Field(description="Aggregate metrics")
    orders: list[OrderLifecycle] = Field(description="Orders in time range")
