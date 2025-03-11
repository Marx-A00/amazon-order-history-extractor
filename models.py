"""
Data models for Amazon order information.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    """Represents an individual item in an Amazon order."""
    name: str
    price: Optional[float] = None
    quantity: int = 1
    asin: Optional[str] = None
    url: Optional[str] = None


class Order(BaseModel):
    """Represents a complete Amazon order with its items."""
    order_id: str
    order_date: datetime = Field(...)
    order_total: Optional[float] = None
    items: List[OrderItem] = []
    shipping_address: Optional[str] = None
    status: Optional[str] = None
    
    def to_dict(self):
        """Convert order to a flat dictionary suitable for CSV export."""
        order_dict = {
            "order_id": self.order_id,
            "order_date": self.order_date.strftime("%Y-%m-%d"),
            "order_total": self.order_total,
            "status": self.status,
            "shipping_address": self.shipping_address,
            "item_count": len(self.items)
        }
        
        # Add flattened item information
        for i, item in enumerate(self.items, 1):
            prefix = f"item_{i}_"
            order_dict[f"{prefix}name"] = item.name
            order_dict[f"{prefix}price"] = item.price
            order_dict[f"{prefix}quantity"] = item.quantity
            order_dict[f"{prefix}asin"] = item.asin
            
        return order_dict