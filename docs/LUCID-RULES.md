# Lucid Trading 50K LucidFlex Rules
*Reference for all trading agent decisions. The Risk agent must enforce these constraints.*

## Account Type
- Plan: LucidFlex 50K
- One-time cost: ~$130 (with discount codes available)
- Platform: Tradovate (TradingView accessible via Tradovate credentials)
- Not subscription-based — single payment

## Evaluation Phase Rules

### Profit Target
- **$3,000** (6% of $50,000 account balance)
- No time limit — take as long as needed
- Must stay above Max Loss Limit while reaching target

### Max Loss Limit (Drawdown)
- **$2,500 trailing drawdown** (EOD calculation)
- Starting MLL: $47,500 ($50,000 - $2,500)
- MLL trails upward based on highest end-of-day closing balance
- MLL never moves back down
- **Critical:** While MLL only UPDATES at end-of-day, if balance drops below MLL at ANY point during trading, account is immediately liquidated

**Example:**
- Day 1 close: $50,000 → MLL = $47,500
- Day 2 close: $51,200 → MLL = $48,700 ($51,200 - $2,500)
- Day 3 close: $50,800 → MLL stays $48,700 (never drops)
- This means effective cushion = current balance - MLL, NOT always $2,500

### Daily Loss Limit
- **None** — LucidFlex has NO daily loss limit
- You can lose any amount in a single session as long as you don't breach MLL
- This is the key advantage of Flex over Pro

### Consistency Rule (Evaluation Only)
- **50% rule:** Largest single-day profit cannot exceed 50% of total profit
- On $50K targeting $3,000: best single day ≤ $1,500
- Minimum 2 trading days to pass (practically 3-7 recommended)
- This rule is REMOVED once funded

### Trading Hours
- Sunday 6:00 PM EST through Thursday 4:45 PM EST
- All positions must close by 4:45 PM EST daily
- CME futures market hours

### Allowed Instruments
- All CME futures contracts
- NQ (Nasdaq 100 E-mini), MNQ (Micro Nasdaq)
- ES (S&P 500 E-mini), MES (Micro S&P)
- News trading fully allowed (NFP, FOMC, CPI, etc.)

### Scaling Plan (Contract Limits)
Account profit determines max contracts:
- $0-$999 profit: Limited contracts (check current Lucid scaling table)
- $1,000-$1,999: Increased
- $2,000+: Further increased
- Exact numbers vary — check Lucid's current scaling table

## Funded Phase Rules (After Passing Eval)

### Key Changes from Evaluation
- **Consistency rule REMOVED** — no limit on single-day profits
- Profit split: **90/10** (you keep 90%)
- Payout minimum: $500
- 5 winning trading days required before first payout
- 6 total payouts before automatic transition to LucidLive (real capital)
- EOD trailing drawdown continues with same mechanics
- MLL locks at starting balance - $100 once closing balance exceeds Initial Trail Balance ($53,000 for 50K)

## Risk Agent Constraints (Hardcoded Rules)

These rules must be enforced programmatically, NOT by LLM judgment:

```python
# Absolute constraints
MAX_DRAWDOWN_USD = 2500        # Account-level, EOD trailing
PROFIT_TARGET_USD = 3000       # Evaluation target
CONSISTENCY_MAX_PCT = 0.50     # Max single-day profit / total profit (eval only)
POSITION_CLOSE_TIME = "16:45"  # EST, all positions flat

# Recommended risk limits (tunable)
MAX_RISK_PER_TRADE_PCT = 0.20  # 20% of available drawdown per trade
MAX_RISK_PER_TRADE_USD = 500   # Hard cap regardless of drawdown
SELF_IMPOSED_DAILY_LOSS = 600  # Stop trading for the day
MAX_OPEN_POSITIONS = 2         # Concurrent positions
```

## Implications for Agent Design

1. **Risk agent must track EOD MLL in real-time** — maintain running high-water mark of closing balances
2. **Position sizing must account for shrinking cushion** — after a winning day, effective cushion decreases
3. **Consistency tracking during eval** — reject trades that would create >50% single-day concentration
4. **Forced position closure** — hard timer at 4:45 PM EST, no exceptions
5. **No overnight holds** — all positions flat before session close
6. **Scaling awareness** — check contract limits against current account profit tier
