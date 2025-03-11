"""
Utility functions for the Amazon Order History Extractor.
"""
import os
import json
import csv
import re
from typing import List, Dict, Any
from datetime import datetime
import pandas as pd
from models import Order
from config import config


def clean_text(text: str) -> str:
    """Clean and normalize text from web scraping."""
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove non-breaking spaces and other invisible characters
    text = text.replace('\xa0', ' ').strip()
    return text


def extract_price(price_text: str) -> float:
    """Extract numerical price from text like '$123.45'."""
    if not price_text:
        return None
    # Remove currency symbol and commas, then convert to float
    match = re.search(r'[\d,]+\.\d+', price_text.replace(',', ''))
    if match:
        return float(match.group(0))
    return None


def extract_order_id(order_id_text: str) -> str:
    """Extract order ID from text like 'Order # 123-4567890-1234567'."""
    if not order_id_text:
        return ""
    match = re.search(r'(?:\d+-){2}\d+', order_id_text)
    if match:
        return match.group(0)
    return clean_text(order_id_text)


def extract_date(date_text: str) -> datetime:
    """Convert date text to datetime object."""
    if not date_text:
        return None
    # Try different date formats
    date_formats = [
        "%B %d, %Y",  # January 1, 2023
        "%b %d, %Y",  # Jan 1, 2023
        "%d %B %Y",   # 1 January 2023
        "%d %b %Y",   # 1 Jan 2023
        "%Y-%m-%d",   # 2023-01-01
        "%m/%d/%Y"    # 01/01/2023
    ]
    
    for date_format in date_formats:
        try:
            return datetime.strptime(clean_text(date_text), date_format)
        except ValueError:
            continue
    return None


def extract_quantity(quantity_text: str) -> int:
    """Extract quantity from text like 'Quantity: 2'."""
    if not quantity_text:
        return 1
    match = re.search(r'\d+', quantity_text)
    if match:
        return int(match.group(0))
    return 1


def extract_asin_from_url(url: str) -> str:
    """Extract ASIN from Amazon product URL."""
    if not url:
        return None
    match = re.search(r'/([A-Z0-9]{10})(?:/|\?|$)', url)
    if match:
        return match.group(1)
    return None


def save_to_csv(orders: List[Order], filename: str = None) -> str:
    """Save orders to CSV file."""
    if not filename:
        filename = os.path.join(config.OUTPUT_DIR, config.CSV_FILENAME)
    
    # Convert orders to dictionary format
    order_dicts = [order.to_dict() for order in orders]
    
    # Create DataFrame
    df = pd.DataFrame(order_dicts)
    
    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"Saved {len(orders)} orders to {filename}")
    return filename


def save_to_json(orders: List[Order], filename: str = None) -> str:
    """Save orders to JSON file."""
    if not filename:
        filename = os.path.join(config.OUTPUT_DIR, config.JSON_FILENAME)
    
    # Convert to JSON serializable format
    serializable_orders = []
    for order in orders:
        order_dict = order.dict()
        order_dict["order_date"] = order_dict["order_date"].strftime("%Y-%m-%d")
        serializable_orders.append(order_dict)
    
    # Save to JSON
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(serializable_orders, f, indent=2)
    
    print(f"Saved {len(orders)} orders to {filename}")
    return filename