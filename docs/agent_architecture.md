# Multi-Agent Architecture

## Agent Overview Table

| Agent Name       | Role Description                                           | Tools Available                                     | Dependencies          |
|------------------|------------------------------------------------------------|-----------------------------------------------------|-----------------------|
| **Orchestrator** | Manages the workflow, routes tasks, compiles final reports | Task routing, State management                      | None                  |
| **Data Analyst** | Cleans, validates, and interprets raw campaign data        | `analyze_csv`, `validate_data`, `generate_stats`    | Data Uploads          |
| **Strategist**   | Formulates marketing strategies, allocates budgets         | `query_rag`, `calculate_roi`, `scenario_simulator`  | Data Analyst Output   |
| **Executor**     | Formats final plans and triggers external automations      | `trigger_webhook`, `format_payload`                 | Strategist Output     |
| **Validator**    | Ensures outputs meet quality and budget constraints        | `check_budget_limits`, `verify_tone`                | Strategist, Executor  |

## Orchestration Flow with Decision Logic

The multi-agent system uses a sequential and hierarchical orchestration model:

1. **Initialization:** The Orchestrator receives the user prompt and context.
2. **Data Processing:** If raw data (CSV) is present, the Orchestrator delegates to the **Data Analyst**. The Analyst returns a structured summary.
3. **Strategy Formulation:** The Orchestrator passes the summary and goals to the **Strategist**. The Strategist queries the RAG system for historical context and generates a plan.
4. **Validation Check:** The Orchestrator sends the plan to the **Validator**. 
   - *Decision Logic:* If the plan exceeds budget or violates rules, the Validator rejects it and sends feedback back to the Strategist for revision (Retry Logic).
5. **Execution Prep:** Once validated, the plan goes to the **Executor** to prepare API payloads and actionable steps.
6. **Human Approval:** System pauses. User reviews.
7. **Execution:** Upon approval, Executor fires webhooks.

## Agent Communication Protocol
Agents communicate by passing serialized state objects (JSON). Each agent receives a `State` containing:
- `user_query`: Original goal.
- `campaign_data`: Extracted metrics.
- `rag_context`: Retrieved documents.
- `current_plan`: The working draft.
- `feedback`: Notes from the Validator or Orchestrator.

## Error Handling and Retry Logic
- **API Failures:** If an LLM call fails (e.g., rate limit), exponential backoff is applied (1s, 2s, 4s, etc.).
- **Validation Failures:** If the Validator finds errors (e.g., budget is $10k but plan spends $15k), the `feedback` field is populated, and the Strategist is invoked again. Maximum retries are set to 3 to prevent infinite loops.
- **Tool Errors:** If a tool fails (e.g., malformed JSON payload), the agent receives a strict system prompt containing the error trace and is asked to fix the arguments.

## Quality Validation Loop
The Validator Agent is a specialized LLM with a strict prompt:
- **Constraints Checklist:** Checks total budget, target audience alignment, and brand voice.
- **Output:** Returns a boolean `is_valid` and a string `reasoning`.

## Dynamic Routing Decisions
The Orchestrator determines the path based on user input. 
- If the user asks a simple historical question: Route directly to **Strategist** (via RAG).
- If the user uploads a dataset: Route to **Data Analyst** first.
- If the user wants to execute: Route to **Executor**.

## Agent Execution Trace Format
The system logs every step to provide transparency in the UI. Format:

```json
{
  "timestamp": "2026-10-06T07:35:00Z",
  "agent": "Strategist",
  "action": "query_rag",
  "input": {"query": "Past successful Q4 campaigns"},
  "output": "Found 3 relevant campaigns...",
  "duration_ms": 1250
}
```
