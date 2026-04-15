# Data Schemas
*Update this file as schemas evolve. Export actual schemas from running databases on Lumen.*

## DuckDB (Time-Series Data)
Location: ~/forex-agent/data/forex.duckdb (on Lumen)

### fx_ohlcv
FX pair OHLCV candle data from Polygon.io.
```sql
CREATE TABLE fx_ohlcv (
    pair        VARCHAR NOT NULL,   -- 'EUR/USD', 'GBP/USD', 'USD/JPY'
    timeframe   VARCHAR NOT NULL,   -- '1m', '5m', '1h', '4h', '1d'
    timestamp   TIMESTAMP NOT NULL, -- UTC
    open        DOUBLE NOT NULL,
    high        DOUBLE NOT NULL,
    low         DOUBLE NOT NULL,
    close       DOUBLE NOT NULL,
    volume      DOUBLE,
    vwap        DOUBLE,
    trades      INTEGER,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (pair, timeframe, timestamp)
);
```

### nq_ohlcv
NQ/MNQ futures OHLCV from yfinance (later Tradovate).
```sql
CREATE TABLE nq_ohlcv (
    symbol      VARCHAR NOT NULL,   -- 'NQ=F', 'MNQ=F'
    timeframe   VARCHAR NOT NULL,   -- '1m', '5m', '1h', '4h', '1d'
    timestamp   TIMESTAMP NOT NULL, -- UTC
    open        DOUBLE NOT NULL,
    high        DOUBLE NOT NULL,
    low         DOUBLE NOT NULL,
    close       DOUBLE NOT NULL,
    volume      DOUBLE,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, timeframe, timestamp)
);
```

### macro
Macroeconomic indicators from FRED.
```sql
CREATE TABLE macro (
    series_id   VARCHAR NOT NULL,   -- 'FEDFUNDS', 'WALCL', 'CPIAUCSL', 'PMI'
    date        DATE NOT NULL,
    value       DOUBLE NOT NULL,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (series_id, date)
);
```

### news_sentiment
News sentiment data (source TBD).
```sql
CREATE TABLE news_sentiment (
    id          INTEGER PRIMARY KEY,
    timestamp   TIMESTAMP NOT NULL, -- UTC
    source      VARCHAR,
    headline    VARCHAR,
    pair        VARCHAR,            -- relevant instrument
    sentiment   DOUBLE,             -- -1.0 to 1.0
    confidence  DOUBLE,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## PostgreSQL (Agent Decisions & Trade Log)
Database: forex_agent | User: forex | Host: localhost:5432 (on Lumen)

### agent_decisions
Every agent call logged for audit and training.
```sql
CREATE TABLE agent_decisions (
    id              SERIAL PRIMARY KEY,
    timestamp       TIMESTAMP NOT NULL DEFAULT NOW(),
    agent_name      VARCHAR NOT NULL,   -- 'sentinel', 'strategist', etc.
    session_id      VARCHAR NOT NULL,   -- groups a full pipeline run
    input_json      JSONB NOT NULL,     -- what the agent received
    output_json     JSONB NOT NULL,     -- what the agent produced
    model           VARCHAR,            -- 'llama3.3:70b'
    latency_ms      INTEGER,
    tokens_in       INTEGER,
    tokens_out      INTEGER,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

### trade_log
Actual trades placed and their outcomes.
```sql
CREATE TABLE trade_log (
    id              SERIAL PRIMARY KEY,
    session_id      VARCHAR NOT NULL,
    pair            VARCHAR NOT NULL,
    direction       VARCHAR NOT NULL,   -- 'long', 'short'
    entry_price     DOUBLE PRECISION,
    exit_price      DOUBLE PRECISION,
    stop_loss       DOUBLE PRECISION,
    take_profit     DOUBLE PRECISION,
    position_size   DOUBLE PRECISION,
    entry_time      TIMESTAMP,
    exit_time       TIMESTAMP,
    pnl_usd         DOUBLE PRECISION,
    pnl_pct         DOUBLE PRECISION,
    broker          VARCHAR,            -- 'tradovate', 'oanda'
    order_id        VARCHAR,
    status          VARCHAR,            -- 'open', 'closed', 'cancelled'
    created_at      TIMESTAMP DEFAULT NOW()
);
```

### audit_trail
Auditor agent's review of completed trades.
```sql
CREATE TABLE audit_trail (
    id              SERIAL PRIMARY KEY,
    trade_id        INTEGER REFERENCES trade_log(id),
    session_id      VARCHAR NOT NULL,
    grade           VARCHAR,            -- 'A', 'B', 'C', 'D', 'F'
    lessons         JSONB,
    prompt_suggestions JSONB,
    full_review     JSONB,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

## Redis (Live State Cache)
Host: localhost:6379 (on Lumen)

Used for ephemeral runtime state, not persistent storage:
- `account:equity` — current account balance
- `account:daily_pnl` — today's P&L
- `positions:open` — hash of open positions
- `pipeline:last_run` — timestamp of last agent pipeline execution
- `pipeline:status` — 'idle', 'running', 'error'
- `alerts:queue` — pending alerts for operator
