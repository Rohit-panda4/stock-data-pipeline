# stock-data-pipeline
End-to-end automated pipeline: Stock data → MySQL → Python transforms → Tableau visualization

## Project Structure

```
stock-data-pipeline-mysql-tableau/
│
├── .github/
│   └── workflows/
│       └── pipeline-test.yml          # Future: CI/CD automation tests
│
├── config/
│   ├── .env.example                   # Template for environment variables
│   └── database_config.py             # Database connection settings
│
├── data/
│   ├── raw/                           # Raw data from API (gitignored)
│   ├── processed/                     # Intermediate transformed data (gitignored)
│   └── .gitkeep                       # Keep empty folders in git
│
├── data_pipeline/
│   ├── __init__.py                    # Makes it a Python package
│   ├── fetch_prices.py                # Script: API → MySQL ingestion
│   ├── transform_prices.py            # Script: Transform raw → metrics
│   ├── pipeline_runner.py             # Main orchestration script
│   └── utils/
│       ├── __init__.py
│       ├── db_connector.py            # MySQL connection utilities
│       ├── logger.py                  # Logging configuration
│       └── validators.py              # Data validation functions
│
├── sql/
│   ├── schema.sql                     # CREATE DATABASE & TABLES
│   ├── initial_data.sql               # INSERT symbols list
│   └── queries/
│       ├── daily_metrics.sql          # Useful analytical queries
│       └── data_quality_checks.sql    # Quality validation queries
│
├── tableau/
│   ├── stock_dashboard.twbx           # Tableau packaged workbook
│   ├── screenshots/                   # Dashboard screenshots for README
│   └── refresh_instructions.md        # How to refresh Tableau connection
│
├── docs/
│   ├── design.md                      # Pipeline architecture & decisions
│   ├── ingestion_plan.md              # Data source & API details
│   ├── transformation_plan.md         # Metrics calculations logic
│   ├── architecture.md                # System diagram & workflow
│   ├── progress_log.md                # Development journal
│   └── setup_guide.md                 # Local installation instructions
│
├── tests/
│   ├── __init__.py                    # Unit tests for ingestion
│   ├── test_fetch_prices.py           # Unit tests for ingestion
│   ├── test_transform_prices.py       # Unit tests for transformations
│   └── test_db_connector.py           # Database connection tests
│
├── logs/
│   └── .gitkeep                       # Pipeline execution logs (gitignored)
│
├── scripts/
│   ├── setup_database.py              # One-time DB initialization
│   ├── scheduler_setup.bat            # Windows Task Scheduler setup
│   └── backfill_historical.py         # Load historical stock data
│
├── .env                               # Environment variables (gitignored)
├── .gitignore                         # Already configured
├── requirements.txt                   # Python dependencies
├── README.md                          # Main project documentation
├── LICENSE                            # MIT License
└── environment.yml                    # Optional: Conda environment
```
