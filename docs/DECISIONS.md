# Architectural Decision Log

## 2026-04-13: Claudius is external to the Triune Brain
**Context:** Evaluated NemoClaw (NVIDIA), Agent Zero, and "ClaudeClaw" (Claude Code daemon) as potential agent runtimes on Vigil.
**Decision:** Claudius is a separate R&D companion (Claude Project), not a runtime component. The Triune Brain runs autonomously without cloud dependencies.
**Rationale:**
- Separating the "thinker about the system" from "the system" prevents coupling
- Triune Brain must survive without internet/Anthropic API
- Vigil stays lean: only Ollama + trading agents, no competing workloads
- Claudius works from any device (laptop, phone, browser)
**Consequences:** NemoClaw and Agent Zero deferred. Vigil needs no Docker or framework overhead.

## 2026-04-13: NemoClaw and Agent Zero deferred
**Context:** Both frameworks were evaluated for Vigil deployment.
**Decision:** Neither installed now. May revisit NemoClaw for production sandboxing (Phase 8+).
**Rationale:**
- NemoClaw is still alpha with rough edges on DGX Spark
- Agent Zero's role (dev/research assistant) is filled by Claudius externally
- Installing either adds complexity without advancing the trading system
**Consequences:** Vigil remains a clean Ollama inference engine.

## 2026-04-11: Vigil confirmed as primary LLM inference engine
**Context:** Evaluated whether to start Phase 2 setup on Lumen or Vigil.
**Decision:** Vigil (ASUS Ascent GX10) is the correct starting point.
**Rationale:**
- 128GB unified memory runs Llama 3.3 70B at full precision (no quantization)
- Eliminates VRAM constraints (Lumen's 12GB can't run 70B-class models)
- Removes need for cloud fallback entirely
- LLMRouter primary endpoint routes to Vigil's Ollama
**Consequences:** All 6 agent LLM calls route through Vigil. Lumen handles data/RL/execution only.

## 2026-04-11: Triune Brain node assignments
**Context:** Three machines available for the trading system.
**Decision:**
- Vigil → LLM inference (Ollama + Llama 3.3 70B)
- Lumen → Data, RL training, trade execution
- Echelon → Development, monitoring, deployment
**Rationale:** Each machine excels at its assigned workload. GPU types match: GB10 for large model inference, 3080 Ti for RL training, XPS for lightweight dev tasks.

## 2026-04-10: NQ futures via yfinance initially, Tradovate in Phase 8
**Context:** Needed NQ/MNQ futures data source for Phase 3.
**Decision:** Use yfinance for historical NQ data now. Tradovate API integration deferred to Phase 8 (live execution).
**Rationale:** yfinance provides adequate historical data for backtesting. Tradovate integration is complex and only needed for live trading.

## 2026-04-10: 6-agent pipeline architecture
**Context:** Designing the agent structure for the forex trading system.
**Decision:** 6 specialized agents in a sequential pipeline: Sentinel → Strategist → Tactician → Risk → Executor → Auditor.
**Rationale:** Each agent has a focused responsibility. Sequential pipeline is simpler to debug than parallel/mesh. JSON schemas enforce clean interfaces. Some agents (Risk, Executor) may be partially rule-based rather than pure LLM.
