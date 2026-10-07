# MarketPilot AI Complete User Guide

Welcome to MarketPilot AI, your autonomous marketing strategy and execution platform.

## Getting Started
1. Launch the application.
2. Navigate to the **Settings** page.
3. Ensure your API keys (OpenAI) are configured.
4. Familiarize yourself with the main dashboard which shows active campaigns and agent status.

## Creating a Campaign
1. Click **New Campaign**.
2. Fill out the brief: Campaign Name, Objective (e.g., Brand Awareness, Lead Gen), Total Budget, and Target Audience.
3. Click **Initialize**. The Orchestrator agent will take over.

## Using Demo Mode
- Toggle "Demo Mode" in the top right corner.
- This bypasses real API calls and uses mocked agent responses and datasets, perfect for presentations or testing the UI layout without incurring LLM costs.

## Uploading Data
- In the campaign setup, you can upload a CSV file containing past performance data (Spend, Clicks, Conversions per channel).
- The Data Analyst agent will automatically process this file.

## Understanding Data Quality
- Upon upload, the system runs a Data Quality Engine.
- If data is missing (e.g., blank ROI columns) or malformed, the Analyst agent will flag it, clean what it can, and ask for confirmation before proceeding.

## Viewing Agent Execution
- As agents work, the **Execution Trace** panel on the right updates in real-time.
- You can watch the Data Analyst summarize data, the Strategist formulate a plan, and the Validator check limits.
- This transparency ensures you understand exactly *how* the AI arrived at its conclusions.

## Reading Recommendations
- The final output is presented as a Strategy Card.
- It includes: Recommended budget allocations, target audience adjustments, generated ad copy, and expected ROI.

## Using Scenario Simulator
- Want to test "What if we double the budget?"
- Click **Scenario Simulator**. Enter new variables, and the Strategist agent will recalculate the plan and predict new outcomes instantly.

## Approving Actions (Human-in-the-Loop)
- The system will NOT spend money automatically.
- Review the final strategy. If acceptable, click **Approve & Execute**.
- This triggers the Executor agent to send the data to n8n for real-world deployment.

## RAG Explorer
- Navigate to the **Knowledge Base** tab to upload company PDFs or guidelines.
- The RAG Explorer lets you search your documents exactly how the AI does, allowing you to verify what context the AI has access to.

## Reports
- The **Reports** tab aggregates data from all past campaigns (both AI-generated and manually tracked) to show overarching performance metrics and agent accuracy over time.

## Settings
- Manage API keys.
- Update n8n Webhook URLs.
- Adjust Agent temperature (creativity vs. precision).
