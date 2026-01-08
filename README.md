# Stock Trading Python App

A data pipeline application that fetches real-time stock ticker data from the Polygon.io API and loads it into Snowflake for data warehousing and analysis.

## Overview

This application is designed to automate the collection of stock market data at regular intervals. It retrieves comprehensive stock ticker information including company names, market types, exchanges, and metadata from the Polygon.io financial data API, then persists this data to a Snowflake data warehouse.

## Features

- **Automated Data Collection**: Fetches active stock tickers from Polygon.io API with pagination support
- **Rate Limiting**: Built-in pause mechanism to respect API rate limits (pauses every 5 requests)
- **Snowflake Integration**: Loads data directly into Snowflake with type-safe schema validation
- **Scheduled Execution**: Runs on a configurable schedule (default: every minute)
- **Comprehensive Metadata**: Captures ticker symbols, company names, exchanges, FIGI codes, and more

## Project Structure

```
stock-trading-python-app/
├── script.py              # Main ETL logic for data extraction and loading
├── scheduler.py           # Job scheduler that runs scripts at intervals
├── requirements.txt       # Python package dependencies
├── tickers.csv           # Sample output data with stock ticker information
└── pythonenv/            # Python virtual environment
```

## Data Schema

The application captures the following fields for each ticker:

| Field | Type | Description |
|-------|------|-------------|
| ticker | VARCHAR | Stock ticker symbol |
| name | VARCHAR | Company name |
| market | VARCHAR | Market type (e.g., stocks) |
| locale | VARCHAR | Market locale (e.g., us) |
| primary_exchange | VARCHAR | Primary exchange code (XNYS, XNAS, etc.) |
| type | VARCHAR | Security type (CS, ETF, WARRANT, etc.) |
| active | BOOLEAN | Whether the ticker is currently active |
| currency_name | VARCHAR | Currency denomination |
| cik | VARCHAR | SEC Central Index Key |
| composite_figi | VARCHAR | OpenFIGI composite identifier |
| share_class_figi | VARCHAR | OpenFIGI share class identifier |
| last_updated_utc | VARCHAR | Last update timestamp |
| ds | VARCHAR | Data snapshot date (YYYY-MM-DD) |

## Requirements

- Python 3.8+
- Polygon.io API key
- Snowflake account with appropriate credentials and warehouse

## Dependencies

```
requests                    # HTTP client for API calls
openai                      # OpenAI API integration
python-dotenv              # Environment variable management
schedule                   # Job scheduling
snowflake-connector-python # Snowflake database connector
```

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd stock-trading-python-app
   ```

2. **Create and activate a Python virtual environment**:
   ```bash
   python -m venv pythonenv
   source pythonenv/Scripts/activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in the project root with the following variables:
   ```
   POLYGON_API_KEY=your_polygon_api_key
   SNOWFLAKE_ACCOUNT=your_account_identifier
   SNOWFLAKE_USER=your_username
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_WAREHOUSE=your_warehouse_name
   SNOWFLAKE_DATABASE=your_database_name
   SNOWFLAKE_SCHEMA=your_schema_name
   SNOWFLAKE_ROLE=your_role_name
   SNOWFLAKE_TABLE=stock_tickers  # Optional, defaults to 'stock_tickers'
   ```

## Usage

### Run One-Time Data Extraction

Execute the main data extraction script:
```bash
python script.py
```

### Run Scheduled Jobs

Start the scheduler to run jobs at regular intervals:
```bash
python scheduler.py
```

The scheduler runs the stock data job every minute by default and will continuously check for pending tasks.

## How It Works

### script.py

1. **Authentication**: Retrieves Polygon.io API key from environment variables
2. **Pagination**: Iterates through all active stock tickers using the Polygon.io reference API
3. **Rate Limiting**: Implements a pause (70 seconds) after every 5 API requests to respect rate limits
4. **Data Enrichment**: Adds a data snapshot date (`ds`) to each record
5. **Snowflake Loading**: 
   - Establishes secure connection to Snowflake
   - Creates or updates the target table with proper type casting
   - Inserts ticker data in batches using Snowflake's `write_pandas` method

### scheduler.py

Implements a simple job scheduler that:
- Runs the `run_stock_job()` function every minute
- Provides basic logging of job execution
- Maintains a continuous loop to check for pending tasks

## Data Volume

The tickers.csv sample file contains metadata for thousands of active stock tickers (11,743+ records), each with comprehensive company and trading information.

## API Integration

### Polygon.io API

- **Endpoint**: `https://api.polygon.io/v3/reference/tickers`
- **Parameters**: 
  - `market=stocks`: Stocks market only
  - `active=true`: Only active tickers
  - `limit=1000`: Batch size per request
  - Supports pagination with `next_url`

## Error Handling

The application includes error handling for:
- Snowflake connection failures
- API request errors
- Missing or invalid environment variables

## Future Enhancements

- Add logging to file for audit trails
- Implement data validation and quality checks
- Add support for incremental data loading
- Create data lineage and monitoring dashboards
- Support for additional data sources (quotes, aggregates, etc.)
- Implement retry logic with exponential backoff

## Contributing

When contributing to this project:
1. Ensure all dependencies are listed in `requirements.txt`
2. Follow Python PEP 8 style guidelines
3. Add appropriate logging for debugging
4. Update environment variable documentation

## License

[Add your license information here]

## Support

For issues with:
- **Polygon.io API**: Check [Polygon.io documentation](https://polygon.io/docs)
- **Snowflake**: Consult [Snowflake documentation](https://docs.snowflake.com)
- **Project**: Review code comments and inline documentation
