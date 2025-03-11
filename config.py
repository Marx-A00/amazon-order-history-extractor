"""
Configuration settings for the Amazon Order History Extractor.
"""
import os
from typing import ClassVar, Dict, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config(BaseSettings):
    # Amazon URLs
    AMAZON_DOMAIN: str = os.getenv("AMAZON_DOMAIN", "www.amazon.com")
    ORDERS_URL: str = f"https://{AMAZON_DOMAIN}/gp/css/order-history"
    
    # Extraction settings
    ORDERS_PER_PAGE: int = 10
    MAX_PAGES: Optional[int] = None  # None means extract all pages
    YEAR_FILTER: Optional[str] = None  # None means all years, or specify a year like "2023"
    TIMEOUT: int = 30000  # Page load timeout in milliseconds
    HEADLESS: bool = False  # Set to True to run browser in headless mode
    
    # Output settings
    OUTPUT_DIR: str = "output"
    CSV_FILENAME: str = "amazon_orders.csv"
    JSON_FILENAME: str = "amazon_orders.json"
    
    # Selectors (can be updated if Amazon changes their page structure)
    SELECTORS: ClassVar[Dict[str, str]] = {
        "orders_container": ".js-yo-main-content",
        "order_card": ".js-order-card",
        "order_id": ".yohtmlc-order-id",
        "order_date": ".a-color-secondary.value",
        "order_total": ".a-color-price.value",
        "order_items_container": ".js-shipment-info, .a-box-group.a-spacing-base.js-shipment",
        "item_name": ".a-link-normal[href*='/gp/product/']",
        "item_price": ".a-color-price",
        "item_quantity": ".item-view-qty",
        "order_status": ".shipment-top-row .a-color-secondary",
        "pagination_next": ".a-pagination .a-last a",
        "login_success": "#nav-link-accountList"
    }

# Create an instance of the config
config = Config()

# Create output directory if it doesn't exist
os.makedirs(config.OUTPUT_DIR, exist_ok=True)