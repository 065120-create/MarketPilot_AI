def get_campaign_defaults() -> dict:
    """Get default campaign settings."""
    return {
        "budget": 10000,
        "duration_days": 30,
        "target_audience": "General",
        "channels": ["Email", "Social Media"]
    }
