import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from data_pipeline.utils.db_connector import get_db_connection, close_db_connection, fetch_query, execute_query

def get_active_symbols(connection):
    """
    Fetch list of active stock symbols from database.
    
    Returns:
        list: List of tuples (symbol_id, ticker)
    """
    query = "SELECT symbol_id, ticker FROM symbols WHERE is_active = TRUE"
    results = fetch_query(connection, query)
    print(f"✓ Found {len(results)} active symbols to fetch")
    return results

def fetch_stock_data(ticker, start_date, end_date):
    """
    Fetch stock price data from Yahoo Finance.
    
    Args:
        ticker: Stock symbol (e.g., 'AAPL')
        start_date: Start date for data fetch
        end_date: End date for data fetch
        
    Returns:
        DataFrame: Stock price data or None if error
    """
    try:
        print(f"  Fetching data for {ticker}...")
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)
        
        if df.empty:
            print(f"  ⚠ No data returned for {ticker}")
            return None
            
        print(f"  ✓ Fetched {len(df)} days of data for {ticker}")
        return df
        
    except Exception as e:
        print(f"  ✗ Error fetching {ticker}: {e}")
        return None

def insert_price_data(connection, symbol_id, ticker, df):
    """
    Insert stock price data into raw_prices table.
    
    Args:
        connection: MySQL connection object
        symbol_id: ID from symbols table
        ticker: Stock symbol
        df: DataFrame with stock price data
        
    Returns:
        int: Number of rows inserted
    """
    if df is None or df.empty:
        return 0
    
    insert_query = """
        INSERT INTO raw_prices 
        (symbol_id, trade_date, open_price, high_price, low_price, 
         close_price, adj_close_price, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        open_price = VALUES(open_price),
        high_price = VALUES(high_price),
        low_price = VALUES(low_price),
        close_price = VALUES(close_price),
        adj_close_price = VALUES(adj_close_price),
        volume = VALUES(volume),
        fetched_at = CURRENT_TIMESTAMP
    """
    
    inserted_count = 0
    cursor = connection.cursor()
    
    for date, row in df.iterrows():
        try:
            # Convert date to string format
            trade_date = date.strftime('%Y-%m-%d')
            
            # Prepare data tuple
            data = (
                symbol_id,
                trade_date,
                float(row['Open']),
                float(row['High']),
                float(row['Low']),
                float(row['Close']),
                float(row['Close']),  # Using Close as adj_close for now
                int(row['Volume'])
            )
            
            cursor.execute(insert_query, data)
            inserted_count += 1
            
        except Exception as e:
            print(f"  ⚠ Error inserting row for {ticker} on {date}: {e}")
            continue
    
    connection.commit()
    cursor.close()
    print(f"  ✓ Inserted/Updated {inserted_count} rows for {ticker}")
    return inserted_count

def get_last_fetch_date(connection, symbol_id):
    """
    Get the most recent trade date for a symbol.
    
    Returns:
        date: Last fetch date or None
    """
    query = "SELECT MAX(trade_date) FROM raw_prices WHERE symbol_id = %s"
    result = fetch_query(connection, query, (symbol_id,))
    
    if result and result[0][0]:
        return result[0][0]
    return None

def run_ingestion(days_back=30):
    """
    Main function to run the data ingestion pipeline.
    
    Args:
        days_back: Number of days of historical data to fetch (default 30)
    """
    print("\n" + "="*60)
    print("🚀 STOCK DATA INGESTION PIPELINE STARTED")
    print("="*60)
    
    # Connect to database
    connection = get_db_connection()
    if not connection:
        print("✗ Failed to connect to database. Exiting.")
        return
    
    # Get active symbols
    symbols = get_active_symbols(connection)
    
    if not symbols:
        print("✗ No active symbols found. Exiting.")
        close_db_connection(connection)
        return
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    print(f"\n📅 Fetching data from {start_date.date()} to {end_date.date()}")
    print("-"*60)
    
    total_inserted = 0
    successful_fetches = 0
    
    # Fetch and insert data for each symbol
    for symbol_id, ticker in symbols:
        print(f"\n📊 Processing {ticker}...")
        
        # Check last fetch date
        last_date = get_last_fetch_date(connection, symbol_id)
        if last_date:
            print(f"  Last data: {last_date}")
        
        # Fetch data from Yahoo Finance
        df = fetch_stock_data(ticker, start_date, end_date)
        
        if df is not None:
            # Insert into database
            count = insert_price_data(connection, symbol_id, ticker, df)
            total_inserted += count
            successful_fetches += 1
    
    # Summary
    print("\n" + "="*60)
    print("✅ INGESTION COMPLETE")
    print(f"   Symbols processed: {successful_fetches}/{len(symbols)}")
    print(f"   Total rows inserted/updated: {total_inserted}")
    print("="*60 + "\n")
    
    close_db_connection(connection)

if __name__ == "__main__":
    # Run ingestion for last 30 days
    run_ingestion(days_back=30)
