import pytest
import pandas as pd
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.fixture
def sample_campaign_performance_df():
    """Sample campaign performance DataFrame for testing."""
    return pd.DataFrame({
        'campaign_id': ['C001']*7,
        'channel': ['Instagram', 'YouTube', 'Facebook', 'Google Ads', 'Twitter', 'Snapchat', 'Influencer'],
        'date': ['2026-01-15']*7,
        'impressions': [50000, 80000, 30000, 40000, 20000, 25000, 15000],
        'clicks': [2500, 2400, 600, 2000, 400, 1250, 750],
        'conversions': [125, 96, 30, 200, 20, 75, 45],
        'spend': [5000, 8000, 3000, 7000, 2000, 3000, 10000],
        'revenue': [25000, 19200, 6000, 60000, 4000, 15000, 22500]
    })

@pytest.fixture
def sample_customer_feedback_df():
    return pd.DataFrame({
        'feedback_id': range(1, 11),
        'customer_id': [f'CUST{i:03d}' for i in range(1, 11)],
        'rating': [5, 4, 2, 5, 3, 1, 4, 5, 2, 4],
        'review': [
            'Loved the personalized bottles!',
            'Great campaign, very engaging',
            'Could not find my name',
            'Best marketing campaign ever',
            'It was okay',
            'Too many ads everywhere',
            'Fun concept for Gen Z',
            'Shared it with all my friends',
            'Not very original',
            'Instagram content was amazing'
        ],
        'sentiment': ['positive', 'positive', 'negative', 'positive', 'neutral', 'negative', 'positive', 'positive', 'negative', 'positive'],
        'channel': ['Instagram', 'YouTube', 'Store', 'Instagram', 'Facebook', 'YouTube', 'Snapchat', 'Instagram', 'Twitter', 'Instagram']
    })

@pytest.fixture
def sample_customer_data_df():
    return pd.DataFrame({
        'customer_id': [f'CUST{i:03d}' for i in range(1, 21)],
        'age': [22, 19, 25, 31, 28, 20, 23, 27, 18, 35, 24, 21, 29, 26, 33, 22, 19, 30, 25, 28],
        'gender': ['Female', 'Male', 'Female', 'Male', 'Female', 'Non-binary', 'Male', 'Female', 'Male', 'Female'] * 2,
        'city': ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Hyderabad', 'Pune', 'Kolkata', 'Delhi', 'Mumbai', 'Bangalore'] * 2,
        'purchase_count': [5, 2, 8, 1, 4, 3, 6, 2, 7, 1, 4, 3, 5, 2, 6, 1, 8, 3, 4, 2],
        'total_spend': [2500, 800, 5000, 400, 2200, 1500, 3500, 900, 4200, 500, 2100, 1600, 2800, 1000, 3800, 600, 4500, 1400, 2300, 1100],
        'engagement_score': [85, 45, 92, 30, 78, 60, 88, 40, 95, 25, 72, 55, 80, 48, 90, 35, 93, 58, 75, 42],
        'loyalty_tier': ['Gold', 'Bronze', 'Platinum', 'Bronze', 'Silver', 'Silver', 'Gold', 'Bronze', 'Platinum', 'Bronze',
                        'Silver', 'Silver', 'Gold', 'Bronze', 'Platinum', 'Bronze', 'Platinum', 'Silver', 'Silver', 'Bronze']
    })

@pytest.fixture
def sample_journey_df():
    return pd.DataFrame({
        'journey_id': range(1, 11),
        'customer_id': [f'CUST{i:03d}' for i in range(1, 11)],
        'stage': ['awareness', 'interest', 'consideration', 'purchase', 'awareness', 'interest', 'consideration', 'awareness', 'interest', 'purchase'],
        'channel': ['Instagram', 'YouTube', 'Google', 'Website', 'Facebook', 'Instagram', 'Website', 'Snapchat', 'YouTube', 'Website'],
        'converted': [True, True, True, True, True, True, False, True, False, True],
        'drop_off': [False, False, False, False, False, False, True, False, True, False]
    })

@pytest.fixture
def sample_campaign():
    return {
        'brand': 'Coca-Cola',
        'campaign_name': 'Share a Coke',
        'industry': 'FMCG',
        'objective': 'Increase engagement and conversion among Gen Z',
        'target_audience': 'Urban Gen Z (18-25)',
        'geography': 'Delhi NCR',
        'budget': 1000000,
        'channels': ['Instagram', 'YouTube', 'Snapchat', 'Google Ads'],
        'duration': '3 months'
    }
