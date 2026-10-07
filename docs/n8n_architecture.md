# n8n Integration Architecture

MarketPilot AI uses n8n to execute real-world actions, turning AI recommendations into actual marketing operations.

## Workflow Diagram

```text
[ MarketPilot AI ] --(Webhook + JSON Payload)--> [ n8n Webhook Node ]
                                                        |
                                       +----------------+----------------+
                                       |                                 |
                            [ Google Sheets Node ]               [ Gmail Node ]
                            (Log Campaign Draft)                 (Email Team)
                                       |                                 |
                               [ Google Drive Node ]                     |
                               (Save Assets/Copy)                        |
                                       |                                 |
                                       +----------------+----------------+
                                                        |
                                               [ Success Response ]
```

## Webhook Specification
- **Method:** POST
- **URL:** `https://<your-n8n-instance>/webhook/marketpilot-execute`
- **Authentication:** Header `X-MarketPilot-Token`

## Payload Format
The Executor Agent constructs this payload upon user approval:
```json
{
  "campaign_id": "cmp_12345",
  "campaign_name": "Q4 Holiday Push",
  "budget": 50000,
  "allocations": {
    "google_ads": 20000,
    "meta_ads": 20000,
    "email": 10000
  },
  "generated_copy": "Don't miss our biggest sale of the year...",
  "status": "approved",
  "timestamp": "2026-10-06T10:00:00Z"
}
```

## Google Sheets Integration
- **Node:** Google Sheets
- **Action:** Append Row
- **Mapping:** Maps `campaign_id`, `campaign_name`, and `budget` to columns A, B, and C in the "Approved Campaigns" sheet. Used for audit trails and finance tracking.

## Google Drive Integration
- **Node:** Google Drive
- **Action:** Create File
- **Mapping:** Takes the `generated_copy` and creates a Google Doc in the "Marketing Assets" folder named after the `campaign_name`.

## Email Integration
- **Node:** Gmail
- **Action:** Send Email
- **Mapping:** Sends an alert to the marketing team alias: "New campaign [campaign_name] has been approved by AI Orchestrator and is ready for final review."

## Error Handling
- If n8n fails (e.g., Google API limits), the webhook node should return a `500` status with an error message.
- MarketPilot AI catches the `500`, alerts the user in the UI, and logs the payload so it can be retried manually.

## Setup Steps
1. Install n8n (Docker or Cloud).
2. Import the provided `marketpilot_workflow.json` (available in the repo).
3. Connect your Google and Gmail credentials inside n8n.
4. Activate the workflow.
5. Copy the Test/Production Webhook URL.
6. Paste the URL into MarketPilot AI's `.env` file under `N8N_WEBHOOK_URL`.
