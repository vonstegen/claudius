# Trading Agent Definitions
*Skeleton — to be fleshed out in Phase 4 (Agent Prompt Engineering)*

## Agent Architecture Overview

The system uses 6 specialized agents that operate in a pipeline. Each agent receives structured input, calls Llama 3.3 70B via Ollama on Vigil, and produces structured JSON output that feeds into the next agent.

All prompts must be optimized for Llama 3.3 70B (not Claude). This means:
- Explicit, structured instructions (the model benefits from clear formatting)
- JSON output schemas defined in the prompt
- Chain-of-thought reasoning requested explicitly
- Few-shot examples included where helpful

## Agent Pipeline

```
Market Data (from DuckDB on Lumen)
    │
    ▼
[1] Sentinel ──── macro scan, regime detection
    │
    ▼
[2] Strategist ── directional bias, pair selection
    │
    ▼
[3] Tactician ─── entry/exit timing, price levels
    │
    ▼
[4] Risk ──────── position sizing, drawdown limits
    │
    ▼
[5] Executor ──── order placement, fill management
    │
    ▼
[6] Auditor ───── post-trade review, performance logging
```

## Agent 1: Sentinel (Macro Scanner)

**Purpose:** Scan macroeconomic conditions and determine the current market regime.

**Inputs:**
- FRED macro data: FEDFUNDS, WALCL, CPIAUCSL, PMI
- Recent news sentiment (TBD)
- Multi-timeframe OHLCV summary (daily, 4h)

**Output Schema (JSON):**
```json
{
  "regime": "risk_on | risk_off | transitional",
  "confidence": 0.0-1.0,
  "key_factors": ["factor1", "factor2"],
  "pairs_favored": ["EUR/USD", "NQ"],
  "pairs_avoid": ["USD/JPY"],
  "reasoning": "brief explanation"
}
```

**Prompt Status:** Not yet written (Phase 4)

## Agent 2: Strategist (Directional Bias)

**Purpose:** Determine directional bias for selected instruments based on regime and technical analysis.

**Inputs:**
- Sentinel output (regime, favored pairs)
- Multi-timeframe OHLCV (4h, 1h)
- Key technical indicators (RSI, MACD, moving averages)

**Output Schema (JSON):**
```json
{
  "pair": "EUR/USD",
  "bias": "long | short | neutral",
  "confidence": 0.0-1.0,
  "timeframe": "4h",
  "key_levels": {"support": 1.0820, "resistance": 1.0910},
  "reasoning": "brief explanation"
}
```

**Prompt Status:** Not yet written (Phase 4)

## Agent 3: Tactician (Entry/Exit)

**Purpose:** Determine precise entry and exit points, stop-loss and take-profit levels.

**Inputs:**
- Strategist output (bias, key levels)
- Lower timeframe OHLCV (5m, 1m)
- Order flow / volume data if available

**Output Schema (JSON):**
```json
{
  "action": "enter_long | enter_short | wait | exit",
  "entry_price": 1.0855,
  "stop_loss": 1.0830,
  "take_profit": [1.0890, 1.0910],
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}
```

**Prompt Status:** Not yet written (Phase 4)

## Agent 4: Risk (Position Sizing)

**Purpose:** Calculate position size based on account equity, drawdown limits, and prop eval rules.

**Inputs:**
- Tactician output (entry, SL, TP)
- Current account state (equity, open positions, daily P&L)
- Lucid Trading rules (max drawdown, daily loss limit)

**Output Schema (JSON):**
```json
{
  "approved": true,
  "position_size": 0.5,
  "risk_amount_usd": 250,
  "risk_percent": 0.5,
  "max_loss_today_remaining": 750,
  "reasoning": "brief explanation"
}
```

**Prompt Status:** Not yet written (Phase 4)
**Note:** This agent may be partially or fully rule-based (no LLM needed) for reliability.

## Agent 5: Executor (Order Management)

**Purpose:** Place and manage orders via broker API.

**Inputs:**
- Risk output (approved, size)
- Tactician output (prices)
- Broker API state (available margin, open orders)

**Output Schema (JSON):**
```json
{
  "order_placed": true,
  "order_type": "limit | market",
  "broker": "tradovate | oanda",
  "order_id": "abc123",
  "fill_price": 1.0856,
  "status": "filled | pending | rejected",
  "reasoning": "brief explanation"
}
```

**Prompt Status:** Not yet written (Phase 4)
**Note:** Executor is primarily code (API calls), with LLM used only for edge-case decisions.

## Agent 6: Auditor (Trade Review)

**Purpose:** Review completed trades, log performance, and generate improvement signals.

**Inputs:**
- Complete trade record (entry, exit, P&L)
- Market data during trade
- Original agent reasoning chain

**Output Schema (JSON):**
```json
{
  "trade_id": "t_20260413_001",
  "outcome": "win | loss | breakeven",
  "pnl_usd": 150.00,
  "grade": "A | B | C | D | F",
  "lessons": ["lesson1", "lesson2"],
  "prompt_adjustment_suggestions": ["suggestion1"],
  "reasoning": "brief explanation"
}
```

**Prompt Status:** Not yet written (Phase 4)

## Inter-Agent Communication

Agents communicate via structured JSON passed through a pipeline orchestrator on Lumen. Each agent's output is:
1. Validated against its schema
2. Logged to PostgreSQL (agent_decisions table)
3. Passed as input to the next agent in the pipeline

The orchestrator is a Python process on Lumen that:
- Reads market data from DuckDB
- Calls each agent sequentially via Ollama API on Vigil
- Handles retries and fallbacks
- Logs everything to PostgreSQL
- Triggers Executor's broker API calls on Lumen
