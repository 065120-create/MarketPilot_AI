import random
import string
import pandas as pd
from datetime import datetime
from dateutil import parser

def format_currency(amount: float, currency: str = 'INR') -> str:
    if currency == 'INR':
        return f"₹{amount:,.2f}"
    return f"{currency} {amount:,.2f}"

def format_percentage(value: float) -> str:
    return f"{value * 100:.2f}%"

def safe_divide(a: float, b: float) -> float:
    if b == 0:
        return 0.0
    return a / b

def generate_job_id() -> str:
    random_num = random.randint(100000, 999999)
    return f"MP-2026-{random_num}"

def calculate_confidence_score(factors: list) -> float:
    if not factors:
        return 0.0
    return sum(factors) / len(factors)

def truncate_text(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len-3] + "..."

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df_clean = df.copy()
    df_clean = df_clean.dropna(how='all')
    df_clean.columns = [str(col).strip().lower().replace(' ', '_') for col in df_clean.columns]
    return df_clean

def detect_outliers(series: pd.Series) -> list:
    if not pd.api.types.is_numeric_dtype(series):
        return []
    
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 - 1.5 * iqr
    
    outliers = series[(series < lower_bound) | (series > upper_bound)]
    return list(outliers.index)

def parse_date_flexible(date_str: str) -> datetime:
    try:
        return parser.parse(date_str)
    except Exception:
        return datetime.utcnow()

def sanitize_filename(name: str) -> str:
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    cleaned = ''.join(c for c in name if c in valid_chars)
    cleaned = cleaned.replace(' ', '_')
    return cleaned
