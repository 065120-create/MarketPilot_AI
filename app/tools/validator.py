import pandas as pd
import numpy as np

class DataQualityReport:
    def __init__(self, score, issues, metadata):
        self.score = score
        self.issues = issues
        self.metadata = metadata

def detect_dataset_type(df: pd.DataFrame) -> str:
    cols = [c.lower() for c in df.columns]
    
    if any(x in cols for x in ['spend', 'impressions', 'clicks', 'cpc', 'roas']):
        return "campaign_performance"
    elif any(x in cols for x in ['feedback', 'review', 'rating', 'sentiment', 'comment']):
        return "customer_feedback"
    elif any(x in cols for x in ['age', 'gender', 'location', 'income', 'lifetime_value']):
        return "customer_data"
    elif any(x in cols for x in ['stage', 'step', 'dropoff', 'conversion_event']):
        return "customer_journey"
    return "unknown"

def check_data_quality_score(df: pd.DataFrame) -> int:
    score = 100
    
    # Missing values penalty
    missing_pct = df.isnull().sum().sum() / (df.shape[0] * df.shape[1])
    score -= (missing_pct * 100) * 0.5
    
    # Duplicates penalty
    duplicate_pct = df.duplicated().sum() / len(df)
    score -= (duplicate_pct * 100) * 0.5
    
    # Ensure score is between 0 and 100
    return int(max(0, min(100, score)))

def validate_dataset(df: pd.DataFrame, dataset_type: str = None) -> DataQualityReport:
    if dataset_type is None:
        dataset_type = detect_dataset_type(df)
        
    issues = []
    
    # Missing values
    missing = df.isnull().sum()
    for col, count in missing[missing > 0].items():
        issues.append(f"Column '{col}' has {count} missing values.")
        
    # Duplicates
    dupes = df.duplicated().sum()
    if dupes > 0:
        issues.append(f"Dataset contains {dupes} duplicate rows.")
        
    # Domain specific validations
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        # Negative spend check
        if 'spend' in col.lower() or 'cost' in col.lower():
            if (df[col] < 0).any():
                issues.append(f"Column '{col}' contains negative values which is invalid for spend/cost.")
        
        # Impossible percentages
        if 'pct' in col.lower() or 'rate' in col.lower() or 'percentage' in col.lower():
            if (df[col] > 100).any() or (df[col] < 0).any():
                # Assuming 0-100 scale, if 0-1 scale it's a different check
                if (df[col] > 1).any():
                    issues.append(f"Column '{col}' contains invalid percentage values.")
                    
    score = check_data_quality_score(df)
    
    return DataQualityReport(
        score=score,
        issues=issues,
        metadata={"rows": len(df), "columns": len(df.columns), "dataset_type": dataset_type}
    )

def auto_fix_issues(df: pd.DataFrame, issues: list) -> tuple:
    fixed_df = df.copy()
    fixes_applied = []
    
    # Simple auto-fixes
    if fixed_df.duplicated().any():
        fixed_df = fixed_df.drop_duplicates()
        fixes_applied.append("Dropped duplicate rows")
        
    for col in fixed_df.select_dtypes(include=[np.number]).columns:
        if 'spend' in col.lower() or 'cost' in col.lower():
            if (fixed_df[col] < 0).any():
                fixed_df[col] = fixed_df[col].clip(lower=0)
                fixes_applied.append(f"Clipped negative values to 0 in {col}")
                
        # Fill missing numeric with median
        if fixed_df[col].isnull().any():
            median_val = fixed_df[col].median()
            fixed_df[col] = fixed_df[col].fillna(median_val)
            fixes_applied.append(f"Filled missing values in {col} with median")
            
    for col in fixed_df.select_dtypes(include=['object']).columns:
        if fixed_df[col].isnull().any():
            mode_val = fixed_df[col].mode()[0] if not fixed_df[col].mode().empty else "Unknown"
            fixed_df[col] = fixed_df[col].fillna(mode_val)
            fixes_applied.append(f"Filled missing values in {col} with mode")
            
    return fixed_df, fixes_applied

def validate_columns(df: pd.DataFrame, expected_columns: list) -> dict:
    missing = [col for col in expected_columns if col not in df.columns]
    return {
        "is_valid": len(missing) == 0,
        "missing_columns": missing
    }

def suggest_column_mapping(df_columns: list, target_schema: list) -> list:
    import difflib
    suggestions = []
    for target in target_schema:
        matches = difflib.get_close_matches(target.lower(), [c.lower() for c in df_columns], n=1, cutoff=0.6)
        if matches:
            original_col = next(c for c in df_columns if c.lower() == matches[0])
            suggestions.append({"target": target, "source": original_col})
        else:
            suggestions.append({"target": target, "source": None})
    return suggestions
