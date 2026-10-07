import pandas as pd
import numpy as np

def build_funnel(df: pd.DataFrame, stage_col: str, customer_col: str) -> dict:
    if stage_col not in df.columns or customer_col not in df.columns:
        return {"error": "Required columns not found"}
        
    # Count unique customers per stage
    funnel = df.groupby(stage_col)[customer_col].nunique().reset_index()
    funnel = funnel.rename(columns={customer_col: 'users'})
    # Sort descending by users to approximate funnel order
    funnel = funnel.sort_values(by='users', ascending=False)
    
    return {
        "stages": funnel[stage_col].tolist(),
        "counts": funnel['users'].tolist()
    }

def calculate_stage_conversion(funnel_data: dict) -> list:
    stages = funnel_data.get("stages", [])
    counts = funnel_data.get("counts", [])
    
    if not stages or not counts or len(stages) != len(counts):
        return []
        
    conversions = []
    for i in range(len(counts)):
        if i == 0:
            rate = 100.0
        else:
            rate = (counts[i] / counts[i-1]) * 100 if counts[i-1] > 0 else 0.0
        
        conversions.append({
            "stage": stages[i],
            "count": counts[i],
            "conversion_from_previous": float(rate)
        })
        
    return conversions

def identify_dropoffs(funnel_data: dict) -> list:
    stages = funnel_data.get("stages", [])
    counts = funnel_data.get("counts", [])
    
    dropoffs = []
    for i in range(1, len(counts)):
        dropoff_count = counts[i-1] - counts[i]
        dropoff_rate = (dropoff_count / counts[i-1]) * 100 if counts[i-1] > 0 else 0.0
        
        dropoffs.append({
            "from_stage": stages[i-1],
            "to_stage": stages[i],
            "dropoff_count": dropoff_count,
            "dropoff_rate_pct": float(dropoff_rate)
        })
        
    return sorted(dropoffs, key=lambda x: x['dropoff_rate_pct'], reverse=True)

def analyze_time_in_stage(df: pd.DataFrame, stage_col: str, time_col: str) -> dict:
    if stage_col not in df.columns or time_col not in df.columns:
        return {"error": "Required columns not found"}
        
    if not pd.api.types.is_numeric_dtype(df[time_col]):
        try:
            df[time_col] = pd.to_numeric(df[time_col])
        except:
            return {"error": "Time column must be numeric"}
            
    avg_time = df.groupby(stage_col)[time_col].mean().reset_index()
    return avg_time.to_dict('records')

def calculate_journey_metrics(df: pd.DataFrame) -> dict:
    metrics = {
        "total_events": len(df),
        "unique_users": df['user_id'].nunique() if 'user_id' in df.columns else None,
        "stages_present": df['stage'].nunique() if 'stage' in df.columns else None
    }
    return metrics
