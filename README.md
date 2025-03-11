# Amazon Order History Extractor

A Python tool using Playwright to extract your Amazon order history and save it to CSV/JSON for analysis.

## Features

- Automated extraction of Amazon order history after manual login
- Search for specific order numbers
- Captures order dates, items purchased, prices, and order status
- Handles pagination to retrieve your complete order history
- Exports data to CSV and JSON formats
- Designed to be robust against Amazon's page structure changes

## Prerequisites

- Python 3.8 or newer
- A valid Amazon account

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/Marx-A00/amazon-order-history-extractor.git
   cd amazon-order-history-extractor
   ```

2. Set up a virtual environment:

   **Option 1: Using venv (Python's built-in tool)**
   ```
   python -m venv venv
   ```

   Activate the venv environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`

   **Option 2: Using conda**
   ```
   conda create -n amazon-extractor python=3.8
   ```

   Activate the conda environment:
   - On Windows/macOS/Linux: `conda activate amazon-extractor`

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Install Playwright browsers:
   ```
   playwright install
   ```

## Usage

### Basic Usage

1. Run the script:
   ```
   python main.py
   ```

2. When the browser opens, manually log in to your Amazon account
   
3. After login, the script will:
   - Wait for you to be logged in
   - Navigate to your orders page
   - Automatically extract your order history
   - Save the data to CSV and JSON files in the `output` directory

### Search for Specific Orders

To search for specific order numbers:

```
python main.py --orders "113-9051212-5641808,113-5645872-2010622"
```

You can provide order numbers in several formats:
- Comma-separated list: `113-9051212-5641808,113-5645872-2010622`
- JSON array of strings: `["113-9051212-5641808", "113-5645872-2010622"]`
- JSON array of objects: `[{"113-9051212-5641808"}, {"113-5645872-2010622"}]`

For testing, you can use the built-in test order numbers:

```
python main.py --test
```

### Additional Options

- `--headless` or `-H`: Run in headless mode (no browser UI)
- `--year` or `-y`: Filter orders by year (e.g., 2023)
- `--max-pages` or `-m`: Maximum number of pages to process

Example:
```
python main.py --orders "113-9051212-5641808" --year 2023 --headless
```

## Configuration

You can customize the script behavior by editing the following parameters in the `config.py` file:

- `ORDERS_PER_PAGE`: Number of orders displayed per page (default: 10)
- `MAX_PAGES`: Maximum number of pages to process (default: all)
- `OUTPUT_DIR`: Directory where output files will be saved (default: 'output')
- `YEAR_FILTER`: Filter orders by year (default: None, all years)
- `ORDER_NUMBERS`: List of specific order numbers to search for

## Output Format

The script generates two files:

1. `amazon_orders.csv`: CSV file with order data
2. `amazon_orders.json`: JSON file with the same data

Each order record contains:
- Order ID
- Order Date
- Order Total
- Items (with name, price, quantity)
- Shipping Address
- Order Status

## Troubleshooting

- **Page structure changes**: If Amazon changes their website structure, the script may need updating. Please open an issue if you encounter problems.
- **Captcha challenges**: If Amazon shows a captcha, the script will pause and wait for you to solve it manually.
- **Login issues**: The script expects you to handle the login process manually for security reasons.
- **Order search not working**: The script will fall back to scanning all orders if specific order search doesn't work.

## License

MIT License

## Disclaimer

This tool is for personal use only. Please ensure you comply with Amazon's Terms of Service when using this script.