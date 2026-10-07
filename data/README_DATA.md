# MarketPilot AI Data Documentation

This directory contains synthetic datasets for the MarketPilot AI project.

## Datasets

### 1. demo_campaign_performance.csv
Campaign performance metrics over time across different channels.
- **Columns**: campaign_id, campaign_name, channel, date, impressions, reach, clicks, engagement, conversions, spend, revenue, ctr, engagement_rate, conversion_rate, cpc, cpa, roas
- **Use case**: ROI analysis, channel attribution, budget optimization.

### 2. demo_customer_feedback.csv
Customer feedback and reviews for campaigns and products.
- **Columns**: feedback_id, customer_id, date, channel, rating, sentiment, review, category, campaign_name
- **Use case**: Sentiment analysis, product/service improvements.

### 3. demo_customer_data.csv
Customer demographic and transactional data.
- **Columns**: customer_id, age, gender, city, state, registration_date, purchase_count, total_spend, avg_order_value, last_purchase_date, preferred_channel, engagement_score, loyalty_tier, lifetime_value, days_since_last_purchase, campaign_response
- **Use case**: Audience segmentation, LTV prediction.

### 4. demo_customer_journey.csv
Event log of customer interactions across touchpoints.
- **Columns**: journey_id, customer_id, timestamp, stage, channel, action, duration_seconds, converted, drop_off, session_id, device, campaign_name
- **Use case**: Funnel analysis, drop-off identification, journey mapping.

## Notes
These datasets include realistic patterns but also deliberate data quality issues (missing values, outliers, duplicates) to test robust data processing capabilities.
