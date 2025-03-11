#!/usr/bin/env python3
"""
Amazon Order History Extractor - Main Entry Point

This script provides a command-line interface to search for specific Amazon orders
or extract all orders from your order history.
"""
import asyncio
import sys
import json
import argparse
from typing import List, Dict, Any

from config import config
from amazon_order_extractor import AmazonOrderExtractor

# Set of test order numbers for testing
TEST_ORDER_NUMBERS = [
    "111-4868416-8480200",
    "110-8215202-5748241",
    "114-4539098-5260231"
]

def parse_order_numbers(order_input: str) -> List[str]:
    """
    Parse order numbers from various input formats:
    - JSON string (list of dictionaries or strings)
    - Comma-separated list
    - Single order number
    """
    order_numbers = []
    
    if not order_input:
        return order_numbers
        
    # Try to parse as JSON first
    try:
        data = json.loads(order_input)
        
        # Handle list of dictionaries with order numbers as keys
        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
            for item in data:
                # Extract first key from each dictionary (assuming it's the order number)
                if item:
                    order_numbers.append(next(iter(item)))
        
        # Handle list of strings
        elif isinstance(data, list) and all(isinstance(item, str) for item in data):
            order_numbers = data
            
        # Handle single string
        elif isinstance(data, str):
            order_numbers = [data]
    except (json.JSONDecodeError, TypeError):
        # If not valid JSON, try comma-separated list
        if ',' in order_input:
            order_numbers = [num.strip() for num in order_input.split(',')]
        else:
            # Single order number
            order_numbers = [order_input.strip()]
    
    return order_numbers

def setup_argument_parser():
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Extract your Amazon order history or search for specific orders."
    )
    
    parser.add_argument(
        "--orders", "-o",
        help="Specific order numbers to search for (comma-separated, JSON string, or single order)",
        type=str
    )
    
    parser.add_argument(
        "--test", "-t",
        help="Use test order numbers for testing",
        action="store_true"
    )
    
    parser.add_argument(
        "--headless", "-H",
        help="Run in headless mode (no browser UI)",
        action="store_true"
    )
    
    parser.add_argument(
        "--year", "-y",
        help="Filter orders by year (e.g., 2023)",
        type=str
    )
    
    parser.add_argument(
        "--max-pages", "-m",
        help="Maximum number of pages to process",
        type=int
    )
    
    return parser

async def run_extractor():
    """Run the order extractor."""
    extractor = AmazonOrderExtractor()
    await extractor.run()

def main():
    """Main entry point for the script."""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Set headless mode if specified
    if args.headless:
        config.HEADLESS = True
    
    # Set year filter if specified
    if args.year:
        config.YEAR_FILTER = args.year
    
    # Set max pages if specified
    if args.max_pages:
        config.MAX_PAGES = args.max_pages
    
    # Set order numbers if specified
    if args.test:
        config.ORDER_NUMBERS = TEST_ORDER_NUMBERS
        print(f"Using test order numbers: {TEST_ORDER_NUMBERS}")
    elif args.orders:
        order_numbers = parse_order_numbers(args.orders)
        if order_numbers:
            config.ORDER_NUMBERS = order_numbers
            print(f"Searching for specific orders: {order_numbers}")
        else:
            print("No valid order numbers provided. Extracting all orders.")
    
    # Print configuration
    print("\nConfiguration:")
    print(f"- Headless mode: {config.HEADLESS}")
    print(f"- Year filter: {config.YEAR_FILTER or 'All years'}")
    print(f"- Max pages: {config.MAX_PAGES or 'All pages'}")
    print(f"- Order numbers: {config.ORDER_NUMBERS or 'All orders'}")
    print()
    
    # Run the extractor
    try:
        asyncio.run(run_extractor())
    except KeyboardInterrupt:
        print("\nExtracting process interrupted by user")
        sys.exit(0)

if __name__ == "__main__":
    main() 