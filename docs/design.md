# Stock Data Pipeline Design Document

## Project Overview
End-to-end automated data pipeline that fetches real-time stock market data, stores it in MySQL, transforms it using Python/Pandas, and visualizes trends in Tableau Public.

---

## 1. Data Source Selection

### Primary Library: yfinance (Yahoo Finance)
- **Why:** Free, no API key required, reliable historical and real-time data
- **Documentation:** https://pypi.org/project/yfinance/
- **Rate Limits:** None for basic usage
- **Data Quality:** High - sourced directly from Yahoo Finance

### Stock Universe
**Initial Portfolio (5-10 symbols):**
- **Tech:** AAPL (Apple), MSFT (Microsoft), GOOGL (Google), NVDA (NVIDIA)
- **EV/Auto:** TSLA (Tesla)
- **E-commerce:** AMZN (Amazon)
- **Finance:** JPM (JPMorgan)
- **Index:** SPY (S&P 500 ETF)

**Rationale:** Mix of high-volume tech stocks plus market index for comparison

---

## 2. Data Collection Strategy

### Frequency Options
**Phase 1 (MVP):** Daily closing prices
- Fetch once per day after market close (4:00 PM EST / 2:30 AM IST)
- Simpler to implement and test
- Sufficient for trend analysis and portfolio projects

**Phase 2 (Future):** Intraday data
- Fetch every 15-30 minutes during market hours
- Requires more complex scheduling
- Better for real-time dashboards

### Data Fields to Capture
| Field | Description | Data Type |
|-------|-------------|-----------|
| `date` | Trading date | DATE |
| `symbol` | Stock ticker | VARCHAR(10) |
| `open` | Opening price | DECIMAL(10,2) |
| `high` | Highest price of day | DECIMAL(10,2) |
| `low` | Lowest price of day | DECIMAL(10,2) |
| `close` | Closing price | DECIMAL(10,2) |
| `volume` | Number of shares traded | BIGINT |
| `adj_close` | Adjusted closing price (for splits/dividends) | DECIMAL(10,2) |

---

## 3. Database Architecture

### Database: `stock_pipeline`

### Table 1: `symbols`
**Purpose:** Master list of stocks being tracked

| Column | Type | Description |
|--------|------|-------------|
| `symbol_id` | INT AUTO_INCREMENT | Primary key |
| `ticker` | VARCHAR(10) UNIQUE | Stock symbol (e.g., AAPL) |
| `company_name` | VARCHAR(100) | Full company name |
| `sector` | VARCHAR(50) | Industry sector |
| `added_date` | TIMESTAMP | When added to pipeline |
| `is_active` | BOOLEAN | Currently tracking (1) or paused (0) |

### Table 2: `raw_prices`
**Purpose:** Store all fetched stock price data

| Column | Type | Description |
|--------|------|-------------|
| `price_id` | INT AUTO_INCREMENT | Primary key |
| `symbol_id` | INT | Foreign key → symbols.symbol_id |
| `trade_date` | DATE | Trading date |
| `open_price` | DECIMAL(10,2) | Opening price |
| `high_price` | DECIMAL(10,2) | Highest price |
| `low_price` | DECIMAL(10,2) | Lowest price |
| `close_price` | DECIMAL(10,2) | Closing price |
| `adj_close_price` | DECIMAL(10,2) | Adjusted close |
| `volume` | BIGINT | Trading volume |
| `fetched_at` | TIMESTAMP | When data was inserted |

**Indexes:**
- `idx_symbol_date` on (symbol_id, trade_date) - fast queries by stock and date
- UNIQUE constraint on (symbol_id, trade_date) - prevent duplicates

### Table 3: `metrics`
**Purpose:** Transformed/calculated analytics data

| Column | Type | Description |
|--------|------|-------------|
| `metric_id` | INT AUTO_INCREMENT | Primary key |
| `symbol_id` | INT | Foreign key → symbols.symbol_id |
| `metric_date` | DATE | Date of calculation |
| `ma_7` | DECIMAL(10,2) | 7-day moving average |
| `ma_30` | DECIMAL(10,2) | 30-day moving average |
| `daily_return_pct` | DECIMAL(6,3) | Daily % change |
| `volatility_7d` | DECIMAL(6,3) | 7-day price volatility (std dev) |
| `price_high_52w` | DECIMAL(10,2) | 52-week high |
| `price_low_52w` | DECIMAL(10,2) | 52-week low |
| `calculated_at` | TIMESTAMP | When metrics computed |

---

## 4. Pipeline Workflow

┌─────────────────┐
│ yfinance API │
│ (Yahoo Finance)│
└────────┬────────┘
│
▼
┌─────────────────────────┐
│ fetch_prices.py │
│ - Pull daily data │
│ - Validate fields │
│ - Handle errors │
└────────┬────────────────┘
│
▼
┌─────────────────────────┐
│ MySQL: raw_prices │
│ - Store all raw data │
│ - Prevent duplicates │
└────────┬────────────────┘
│
▼
┌─────────────────────────┐
│ transform_prices.py │
│ - Calculate metrics │
│ - Compute moving avgs │
│ - Compute volatility │
└────────┬────────────────┘
│
▼
┌─────────────────────────┐
│ MySQL: metrics │
│ - Store analytics │
└────────┬────────────────┘
│
▼
┌─────────────────────────┐
│ Tableau Public │
│ - Connect to MySQL │
│ - Visualize trends │
│ - Auto-refresh │
└─────────────────────────┘

text

---

## 5. Automation & Scheduling

### Execution Schedule
**Daily Pipeline Run:**
- **Time:** 5:30 PM EST / 3:00 AM IST (30 min after market close)
- **Frequency:** Once per trading day (Mon-Fri)
- **Tool:** Windows Task Scheduler

**Steps:**
1. Run `fetch_prices.py` (fetch today's data)
2. Run `transform_prices.py` (calculate metrics)
3. Tableau auto-refreshes on next connection

### Error Handling
- Log all errors to `logs/pipeline.log`
- Email/notification on failure (future enhancement)
- Retry logic for API failures

---

## 6. Data Retention Policy

- **raw_prices:** Keep ALL historical data (unlimited retention)
- **metrics:** Keep ALL calculated metrics
- **logs:** Rotate weekly, keep last 30 days

**Rationale:** Historical stock data is valuable for backtesting and analysis

---

## 7. Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Language | Python | 3.10+ |
| Database | MySQL | 8.0.44 |
| Data Library | pandas | 2.0+ |
| API Library | yfinance | 0.2.32+ |
| Visualization | Tableau Public | Latest |
| Orchestration | Windows Task Scheduler | Built-in |
| Version Control | Git/GitHub | Latest |

---

## 8. Success Metrics

✅ Pipeline runs successfully every trading day  
✅ Zero duplicate records in raw_prices  
✅ All 8 stocks updated daily  
✅ Tableau dashboard shows latest data within 1 hour of market close  
✅ 99%+ uptime for automated runs  

---

## Future Enhancements (Phase 2+)

1. **Intraday data:** Fetch every 15 minutes during market hours
2. **More metrics:** RSI, MACD, Bollinger Bands
3. **Alerts:** Price threshold notifications
4. **Cloud deployment:** Move to AWS RDS + Lambda
5. **API endpoint:** Flask API to serve data
6. **Airflow:** Replace Task Scheduler with Apache Airflow

---

**Document Version:** 1.0  
**Last Updated:** December 31, 2025  
**Author:**Rohit Divekar