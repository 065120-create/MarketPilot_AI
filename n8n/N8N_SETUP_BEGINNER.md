# MarketPilot AI - n8n Cloud Setup Guide (Complete Beginner Guide)

Welcome to the beginner-friendly setup guide for **n8n** in MarketPilot AI! If you have no programming background, don't worry. This guide will walk you through every step as if we are sitting side-by-side.

## 1. What is n8n?
### The Simple Explanation
Think of n8n as a digital postman that connects different apps. When MarketPilot AI finishes creating a campaign, n8n grabs that information and automatically puts it into a Google Sheet, saves a file in Google Drive, and sends an email to your boss.

### Why We Use It
Instead of manually copying and pasting campaign data, n8n automates it instantly.

### What It Does in Our Project
1. Receives data from MarketPilot AI.
2. Checks if the data is correct.
3. Saves it to a spreadsheet.
4. Uploads reports to Google Drive.
5. Sends an executive email.

---

## 2. Create an n8n Cloud Account
*If you already have an account, skip this step.*

1. **Go to the website:** Open your browser and go to [n8n.cloud](https://n8n.cloud/).
2. **Sign up:** Click on the "Start free trial" or "Sign up" button.
3. **Create Account:** Enter your email address and a strong password, then click "Sign Up".
4. **Verify Email:** Check your inbox for a verification email and click the link inside.
5. **Log In:** Log into your new n8n Cloud dashboard.

*(Screenshot: The n8n.cloud homepage with the Sign Up button highlighted)*

---

## 3. Import the Workflow
We've already created the "blueprint" (workflow) for you. You just need to import it into your n8n account.

1. In your n8n dashboard, click on **Workflows** on the left menu.
2. Click the **Add Workflow** button (usually at the top right).
3. Look for a button or menu option that says **Import from File**. 
   - *Tip: Sometimes it's located under a gear icon (⚙️) or a three-dot menu (⋮) at the top right of the canvas.*
4. Select the file named `MarketPilot_n8n_workflow.json` located in your project's `n8n` folder.
5. The nodes (little boxes) will magically appear on your screen!

*(Screenshot: The n8n canvas showing the imported workflow nodes)*

---

## 4. Configure the Webhook
A **Webhook** is like a dedicated mailbox where MarketPilot drops off the campaign data.

1. Double-click the very first node named **Webhook**.
2. A side panel will open. Look for the **Webhook URL** (it should look like `https://your-name.app.n8n.cloud/webhook/marketpilot-webhook`).
3. **Important:** Click on the "Test" tab to get the Test Webhook URL. It will have `/webhook-test/` in it. Copy this URL.
4. Open the `.env` file in your MarketPilot AI project folder.
5. Find the line that says `N8N_WEBHOOK_URL=` and paste your URL there. It should look like this:
   `N8N_WEBHOOK_URL=https://your-name.app.n8n.cloud/webhook-test/marketpilot-webhook`
6. Make sure `N8N_ENABLED=true` is also in your `.env` file.

*(Screenshot: Webhook node configuration panel with URL highlighted)*

---

## 5. Set Up Google Sheets
Let's tell n8n where to save the data.

1. **Create a Spreadsheet:** Go to Google Sheets and create a new blank spreadsheet. Name it "MarketPilot Campaign Insights".
2. **Create Columns:** In the first row, type these exactly in each column from A to I:
   - Job ID
   - Brand
   - Campaign
   - Date
   - Budget
   - Confidence Score
   - Key Findings
   - Recommendations
   - Status
3. **Connect to n8n:** Go back to n8n and double-click the **Google Sheets** node.
4. Under "Credential for Google Sheets API", click "Create New Credential".
5. Follow the pop-up instructions to sign in with your Google account and grant n8n access.
6. Once connected, select your "MarketPilot Campaign Insights" sheet from the dropdown menu in the node configuration.

*(Screenshot: Google Sheets node setup and the Google Sheet headers)*

---

## 6. Set Up Google Drive
We want to save reports here automatically.

1. Go to Google Drive and create a folder named "MarketPilot Reports".
2. Back in n8n, double-click the **Google Drive** node.
3. Under Credentials, you can usually reuse the Google credential you just created for Sheets, or create a new one if prompted.
4. Make sure the node is set to "Upload" and select your "MarketPilot Reports" folder.

*(Screenshot: Google Drive node configuration)*

---

## 7. Set Up Email
Let's configure the automatic email.

1. Double-click the **Send Email** node.
2. Create new credentials (e.g., Gmail API or an SMTP server). If using Gmail, follow the OAuth sign-in steps just like you did for Sheets.
3. In the node settings, change the "From Email" to your email address.
4. Change the "To Email" to the person who should receive the reports (e.g., your professor or yourself for testing).
5. You don't need to change the subject or message body—they are already set up to pull data automatically!

*(Screenshot: Email node configuration showing To and From fields)*

---

## 8. Test the Workflow
Before making it live, let's test it.

1. In n8n, click the **Execute Workflow** button at the bottom (or click "Listen for Test Event" on the Webhook node).
2. The workflow will now wait for data.
3. You can either run MarketPilot (see Step 9) or use an app like Postman to send test data to the webhook URL.
4. When data arrives, you will see green checkmarks on each node!
5. Check your Google Sheet—a new row should be there.
6. Check your email—you should have a new message.

*(Screenshot: Workflow showing green success checkmarks)*

---

## 9. Connect to MarketPilot
Time to link everything up!

1. Make sure you copied the **Production URL** from the Webhook node (the one with just `/webhook/`, not `/webhook-test/`).
2. Update your `.env` file in MarketPilot:
   ```
   N8N_WEBHOOK_URL=https://your-name.app.n8n.cloud/webhook/marketpilot-webhook
   N8N_ENABLED=true
   ```
3. Restart your MarketPilot AI server.
4. In n8n, toggle the switch at the top right to **Active** to make the workflow run in the background forever.
5. In MarketPilot AI, generate a new campaign and click "Approve". 
6. Watch the magic happen automatically!

*(Screenshot: Activating the workflow in n8n)*

---

## 10. Troubleshooting
Things don't always work perfectly the first time. Here are common fixes:

### Webhook Not Receiving Data
- **Fix:** Did you restart MarketPilot after updating the `.env` file? Check that `N8N_ENABLED=true`. Also, ensure you are using the correct Webhook URL (Test vs. Production).

### Google Sheets Authentication Error
- **Fix:** Double-click the node, click on credentials, and try to "Reconnect" or "Re-authenticate". Make sure you checked all the boxes allowing n8n access when signing in to Google.

### Email Not Sending
- **Fix:** Check your email credentials. If using standard Gmail (SMTP), you might need to generate an "App Password" in your Google Account Security settings instead of using your normal password.

### Workflow Stuck on "Validate JSON"
- **Fix:** This means MarketPilot sent bad data. Check the MarketPilot logs to see what was sent. Ensure MarketPilot is sending valid JSON matching the expected format.
