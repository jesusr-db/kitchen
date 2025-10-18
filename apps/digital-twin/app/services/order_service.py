"""Service layer for order operations."""

import logging
import json
from datetime import datetime
from typing import Optional
from collections import defaultdict

from app.config import settings
from app.db import execute_query
from app.models.order import OrderEvent, OrderLifecycle, OrderMetrics, TimeRangeResponse

logger = logging.getLogger(__name__)


def get_orders_in_range(
    location: str,
    start_time: datetime,
    end_time: datetime,
    limit: int = 100
) -> TimeRangeResponse:
    """
    Get all orders and their events within a time range.
    
    Args:
        location: Location name (e.g., 'sanfrancisco')
        start_time: Start of time range
        end_time: End of time range
    
    Returns:
        TimeRangeResponse with orders and aggregate metrics
    """
    logger.info(f"Fetching orders for {location} from {start_time} to {end_time}")
    
    try:
        query = f"""
        SELECT 
            event_id,
            event_type,
            ts,
            order_id,
            body
        FROM {settings.catalog}.{settings.lakeflow_schema}.all_events
        WHERE location = :location
          AND ts BETWEEN :start_time AND :end_time
        ORDER BY order_id, ts ASC
        """
        
        results = execute_query(query, {
            "location": location,
            "start_time": start_time,
            "end_time": end_time
        })
        
        if not results:
            logger.warning(f"No events found for {location} in specified time range")
            return TimeRangeResponse(
                location=location,
                start_time=start_time,
                end_time=end_time,
                metrics=OrderMetrics(
                    total_orders=0,
                    completed_orders=0,
                    in_progress_orders=0
                ),
                orders=[]
            )
        
        orders_dict = defaultdict(list)
        for row in results:
            order_id = row["order_id"]
            
            body_data = None
            if row["body"]:
                try:
                    body_data = json.loads(row["body"])
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse body JSON for event {row['event_id']}")
            
            event = OrderEvent(
                event_type=row["event_type"],
                timestamp=row["ts"],
                body=body_data
            )
            orders_dict[order_id].append(event)
        
        orders = []
        for order_id, events in orders_dict.items():
            order = _build_order_lifecycle(order_id, location, events)
            orders.append(order)
        
        # Apply limit
        if len(orders) > limit:
            orders = orders[:limit]
        
        metrics = _calculate_metrics(orders)
        
        logger.info(
            f"Found {len(orders)} orders for {location} "
            f"({metrics.completed_orders} completed, {metrics.in_progress_orders} in progress)"
        )
        
        return TimeRangeResponse(
            location=location,
            start_time=start_time,
            end_time=end_time,
            metrics=metrics,
            orders=orders
        )
    
    except Exception as e:
        logger.error(f"Error fetching orders in range: {e}")
        raise


def _build_order_lifecycle(
    order_id: str,
    location: str,
    events: list[OrderEvent]
) -> OrderLifecycle:
    """Build an OrderLifecycle from a list of events."""
    if not events:
        raise ValueError(f"No events provided for order {order_id}")
    
    events = sorted(events, key=lambda e: e.timestamp)
    
    first_event = events[0]
    last_event = events[-1]
    
    brand = "Unknown"
    customer_lat = None
    customer_lon = None
    
    for event in events:
        if event.event_type == "order_created" and event.body:
            brand = event.body.get("brand", "Unknown")
            customer_lat = event.body.get("customer_lat")
            customer_lon = event.body.get("customer_lon")
            break
    
    status = _determine_order_status(events)
    
    completed_at = None
    if status == "completed":
        for event in reversed(events):
            if event.event_type == "delivered":
                completed_at = event.timestamp
                break
    
    return OrderLifecycle(
        order_id=order_id,
        location=location,
        brand=brand,
        customer_lat=customer_lat,
        customer_lon=customer_lon,
        events=events,
        created_at=first_event.timestamp,
        completed_at=completed_at,
        status=status
    )


def _determine_order_status(events: list[OrderEvent]) -> str:
    """Determine order status from events."""
    event_types = {event.event_type for event in events}
    
    if "delivered" in event_types:
        return "completed"
    elif "driver_picked_up" in event_types or "driver_ping" in event_types:
        return "out_for_delivery"
    elif "gk_ready" in event_types:
        return "ready_for_pickup"
    elif "gk_started" in event_types or "gk_finished" in event_types:
        return "preparing"
    elif "order_created" in event_types:
        return "created"
    else:
        return "unknown"


def _calculate_metrics(orders: list[OrderLifecycle]) -> OrderMetrics:
    """Calculate aggregate metrics from a list of orders."""
    total_orders = len(orders)
    completed_orders = sum(1 for o in orders if o.status == "completed")
    in_progress_orders = total_orders - completed_orders
    
    prep_times = []
    delivery_times = []
    total_times = []
    
    for order in orders:
        if order.status != "completed" or not order.completed_at:
            continue
        
        event_map = {event.event_type: event.timestamp for event in order.events}
        
        if "order_created" in event_map and "gk_ready" in event_map:
            prep_time = (event_map["gk_ready"] - event_map["order_created"]).total_seconds() / 60
            prep_times.append(prep_time)
        
        if "gk_ready" in event_map and "delivered" in event_map:
            delivery_time = (event_map["delivered"] - event_map["gk_ready"]).total_seconds() / 60
            delivery_times.append(delivery_time)
        
        total_time = (order.completed_at - order.created_at).total_seconds() / 60
        total_times.append(total_time)
    
    avg_prep_time = sum(prep_times) / len(prep_times) if prep_times else None
    avg_delivery_time = sum(delivery_times) / len(delivery_times) if delivery_times else None
    avg_total_time = sum(total_times) / len(total_times) if total_times else None
    
    return OrderMetrics(
        total_orders=total_orders,
        completed_orders=completed_orders,
        in_progress_orders=in_progress_orders,
        avg_prep_time_minutes=avg_prep_time,
        avg_delivery_time_minutes=avg_delivery_time,
        avg_total_time_minutes=avg_total_time
    )


def get_order_by_id(order_id: str) -> Optional[OrderLifecycle]:
    """
    Get complete lifecycle for a specific order.
    
    Args:
        order_id: Unique order identifier
    
    Returns:
        OrderLifecycle if found, None otherwise
    """
    logger.info(f"Fetching order {order_id}")
    
    try:
        query = f"""
        SELECT 
            event_id,
            event_type,
            ts,
            order_id,
            location,
            body
        FROM {settings.catalog}.{settings.lakeflow_schema}.all_events
        WHERE order_id = :order_id
        ORDER BY ts ASC
        """
        
        results = execute_query(query, {"order_id": order_id})
        
        if not results:
            logger.warning(f"Order {order_id} not found")
            return None
        
        location = results[0]["location"]
        events = []
        
        for row in results:
            body_data = None
            if row["body"]:
                try:
                    body_data = json.loads(row["body"])
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse body JSON for event {row['event_id']}")
            
            event = OrderEvent(
                event_type=row["event_type"],
                timestamp=row["ts"],
                body=body_data
            )
            events.append(event)
        
        order = _build_order_lifecycle(order_id, location, events)
        logger.info(f"Found order {order_id} with {len(events)} events")
        
        return order
    
    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {e}")
        raise
