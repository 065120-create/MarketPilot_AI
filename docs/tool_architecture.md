# Tool Architecture

MarketPilot AI relies on a set of precise tools (functions) that agents can invoke to interact with the environment, process data, and take actions.

## List of All Tools with Descriptions

| Tool Name                 | Owner          | Description                                                                 |
|---------------------------|----------------|-----------------------------------------------------------------------------|
| `analyze_csv_data`        | Data Analyst   | Parses uploaded CSV data, calculates key metrics (CPA, ROI, CTR, Spend).    |
| `search_knowledge_base`   | Strategist     | Queries the ChromaDB RAG vector store for historical context and rules.     |
| `simulate_scenario`       | Strategist     | Runs mathematical simulations to predict outcomes based on budget shifts.   |
| `check_budget_limits`     | Validator      | Verifies that proposed allocations do not exceed the total user budget.     |
| `trigger_n8n_webhook`     | Executor       | Sends a formatted JSON payload to an external n8n webhook URL.              |

## Input/Output Schemas

Tools use Pydantic models to enforce strict input/output validation.

### `analyze_csv_data`
**Input Schema:**
```json
{
  "file_path": "string",
  "columns_to_analyze": ["spend", "clicks", "conversions"]
}
```
**Output Schema:**
```json
{
  "total_spend": "float",
  "average_cpa": "float",
  "top_performing_channel": "string"
}
```

### `trigger_n8n_webhook`
**Input Schema:**
```json
{
  "campaign_name": "string",
  "allocations": {"channel": "budget_amount"},
  "target_audience": "string"
}
```
**Output Schema:**
```json
{
  "status": "success | error",
  "webhook_response": "string"
}
```

## Tool Selection Logic
The LLM underlying the agent is provided with tool descriptions in its system prompt (via OpenAI's function calling API). 
- The agent reasons about its current task.
- If it needs to calculate ROI, it emits a tool call for `analyze_csv_data`.
- The Orchestrator intercepts the tool call, executes the Python function, and returns the result to the agent.
- The agent then continues its reasoning with the new data.

## Tool Error Handling
If a tool execution fails (e.g., file not found, API timeout, validation error):
1. The tool catches the exception.
2. It returns a formatted error string instead of crashing the system: `{"error": "File not found. Please verify the path."}`
3. The agent receives this error as observation and is prompted to try again or ask the user for clarification.
