#!/usr/bin/env python3
"""
Amazon Order History Extractor

This script extracts your Amazon order history after manual login and saves it to CSV/JSON files.
"""
import asyncio
import re
import sys
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, parse_qs

from playwright.async_api import async_playwright, Browser, Page, ElementHandle
from tqdm import tqdm

from config import config
from models import Order, OrderItem
from utils import (
    clean_text, extract_price, extract_order_id, extract_date,
    extract_quantity, extract_asin_from_url, save_to_csv, save_to_json
)


class AmazonOrderExtractor:
    """
    A class to extract order history from Amazon using Playwright.
    """
    
    def __init__(self):
        self.browser = None
        self.page = None
        self.orders = []
    
    async def setup(self):
        """Set up the browser and page."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=config.HEADLESS)
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({"width": 1280, "height": 800})
    
    async def navigate_to_orders(self):
        """Navigate to the Amazon orders page and wait for manual login."""
        print("Navigating to Amazon Orders page...")
        await self.page.goto(config.ORDERS_URL)
        
        # Check if we need to login
        if await self.page.title() == "Amazon Sign-In":
            print("\n⚠️ Please log in to your Amazon account in the browser window")
            print("The script will continue automatically after you log in\n")
            
            # Wait for successful login
            await self.page.wait_for_selector(config.SELECTORS["login_success"], 
                                              timeout=300000)  # 5 minute timeout for login
        
        print("Login successful! Now extracting orders...")
        
        # If year filter is specified, navigate to that year's orders
        if config.YEAR_FILTER:
            year_dropdown = await self.page.query_selector("select[name='timeFilter']")
            if year_dropdown:
                # Select the year from the dropdown
                await year_dropdown.select_option(value=config.YEAR_FILTER)
                # Wait for the page to load with the filtered orders
                await self.page.wait_for_load_state("networkidle")
    
    async def extract_item_info(self, item_element: ElementHandle) -> OrderItem:
        """Extract information about an individual item from its element."""
        # Get the item name
        name_element = await item_element.query_selector(config.SELECTORS["item_name"])
        name = ""
        url = ""
        
        if name_element:
            name = await name_element.text_content()
            url = await name_element.get_attribute("href")
        
        # Get the item price
        price_element = await item_element.query_selector(config.SELECTORS["item_price"])
        price = None
        if price_element:
            price_text = await price_element.text_content()
            price = extract_price(price_text)
        
        # Get the item quantity
        quantity_element = await item_element.query_selector(config.SELECTORS["item_quantity"])
        quantity = 1
        if quantity_element:
            quantity_text = await quantity_element.text_content()
            quantity = extract_quantity(quantity_text)
        
        # Create an OrderItem object
        return OrderItem(
            name=clean_text(name),
            price=price,
            quantity=quantity,
            asin=extract_asin_from_url(url),
            url=url
        )
    
    async def extract_order_info(self, order_element: ElementHandle) -> Optional[Order]:
        """Extract information about an order from its element."""
        try:
            # Extract order ID
            order_id_element = await order_element.query_selector(config.SELECTORS["order_id"])
            if not order_id_element:
                return None
            
            order_id_text = await order_id_element.text_content()
            order_id = extract_order_id(order_id_text)
            
            # Extract order date
            date_elements = await order_element.query_selector_all(config.SELECTORS["order_date"])
            order_date = None
            
            if date_elements and len(date_elements) > 0:
                date_text = await date_elements[0].text_content()
                order_date = extract_date(date_text)
            
            if not order_date:
                # Try fallback date extraction
                date_text = await order_element.evaluate(
                    "(element) => element.innerText.match(/(?:January|February|March|April|May|June|July|August|September|October|November|December)\\s+\\d+,\\s+\\d{4}/)"
                )
                if date_text:
                    order_date = extract_date(date_text[0])
                else:
                    # Use current date as fallback
                    order_date = datetime.now()
            
            # Extract order total
            total_elements = await order_element.query_selector_all(config.SELECTORS["order_total"])
            order_total = None
            
            if total_elements and len(total_elements) > 0:
                total_text = await total_elements[0].text_content()
                order_total = extract_price(total_text)
            
            # Extract order status
            status_element = await order_element.query_selector(config.SELECTORS["order_status"])
            status = ""
            if status_element:
                status = await status_element.text_content()
            
            # Extract order items
            items = []
            items_container = await order_element.query_selector_all(config.SELECTORS["order_items_container"])
            
            for container in items_container:
                # Each container can have multiple items
                item_elements = await container.query_selector_all("div.a-box-group")
                
                if not item_elements or len(item_elements) == 0:
                    # Try alternate selector if the first one doesn't work
                    item_elements = [container]
                
                for item_element in item_elements:
                    item = await self.extract_item_info(item_element)
                    if item and item.name:
                        items.append(item)
            
            # Create Order object
            return Order(
                order_id=order_id,
                order_date=order_date,
                order_total=order_total,
                items=items,
                status=clean_text(status),
                shipping_address=""  # We're not extracting shipping address for privacy
            )
        except Exception as e:
            print(f"Error extracting order: {e}")
            return None
    
    async def extract_orders_from_page(self) -> List[Order]:
        """Extract all orders from the current page."""
        orders = []
        
        # Wait for the orders container to be visible
        await self.page.wait_for_selector(config.SELECTORS["orders_container"], 
                                          timeout=config.TIMEOUT)
        
        # Get all order cards on the page
        order_elements = await self.page.query_selector_all(config.SELECTORS["order_card"])
        
        for order_element in order_elements:
            order = await self.extract_order_info(order_element)
            if order:
                orders.append(order)
        
        return orders
    
    async def has_next_page(self) -> bool:
        """Check if there is a next page of orders."""
        next_button = await self.page.query_selector(config.SELECTORS["pagination_next"])
        if not next_button:
            return False
            
        # Check if the next button is disabled
        is_disabled = await next_button.get_attribute("aria-disabled")
        if is_disabled == "true":
            return False
            
        return True
    
    async def go_to_next_page(self) -> bool:
        """Navigate to the next page of orders."""
        next_button = await self.page.query_selector(config.SELECTORS["pagination_next"])
        if not next_button:
            return False
            
        # Click the next button
        await next_button.click()
        
        # Wait for the page to load
        await self.page.wait_for_load_state("networkidle")
        await self.page.wait_for_selector(config.SELECTORS["orders_container"], 
                                          timeout=config.TIMEOUT)
        
        return True
    
    async def extract_all_orders(self) -> List[Order]:
        """Extract orders from all pages."""
        all_orders = []
        page_num = 1
        
        with tqdm(desc="Extracting orders", unit="page") as pbar:
            while True:
                # Check if we've reached the maximum number of pages
                if config.MAX_PAGES and page_num > config.MAX_PAGES:
                    print(f"Reached maximum page limit ({config.MAX_PAGES})")
                    break
                
                # Extract orders from the current page
                page_orders = await self.extract_orders_from_page()
                all_orders.extend(page_orders)
                
                pbar.set_postfix({"orders": len(all_orders), "page": page_num})
                pbar.update(1)
                
                # Check if there's a next page
                if not await self.has_next_page():
                    print("No more pages to process")
                    break
                
                # Go to the next page
                success = await self.go_to_next_page()
                if not success:
                    print("Failed to navigate to next page")
                    break
                
                page_num += 1
        
        return all_orders
    
    async def close(self):
        """Close the browser."""
        if self.browser:
            await self.browser.close()
    
    async def run(self):
        """Run the entire extraction process."""
        try:
            await self.setup()
            await self.navigate_to_orders()
            self.orders = await self.extract_all_orders()
            
            # Save the orders to files
            if self.orders:
                print(f"\nExtracted {len(self.orders)} orders in total")
                
                # Save to CSV
                csv_file = save_to_csv(self.orders)
                
                # Save to JSON
                json_file = save_to_json(self.orders)
                
                print(f"\nOrder data saved to:")
                print(f"  - CSV: {csv_file}")
                print(f"  - JSON: {json_file}")
            else:
                print("No orders were found. Please check your Amazon account or try again.")
            
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Add a delay to allow user to see results before closing
            await asyncio.sleep(2)
            await self.close()


async def main():
    """Run the main program."""
    print("=" * 60)
    print("Amazon Order History Extractor")
    print("=" * 60)
    print("\nThis script will extract your order history from Amazon")
    print("You will need to log in to your Amazon account manually when prompted")
    print("\nPress Ctrl+C at any time to exit\n")
    
    extractor = AmazonOrderExtractor()
    await extractor.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExtracting process interrupted by user")
        sys.exit(0)