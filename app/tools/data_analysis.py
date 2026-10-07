"""MarketPilot AI - Data Analysis Tools

Provides core data analysis functions for processing campaign,
customer, and marketing datasets. Used by agent modules for
quantitative analysis.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging

logger = logging.getLogger("marketpilot.tools.data_analysis")


def analyze_dataframe(df: pd.DataFrame, dataset_type: str = "unknown") -> Dict[str, Any]:
    """
    Comprehensive DataFrame analysis with summary statistics.
    
    Args:
        df: Input DataFrame to analyze
        dataset_type: Type of dataset (campaign_performance, customer_feedback, etc.)
    
    Returns:
        Dictionary with comprehensive analysis results
    """
    if df is None or df.empty:
        return {"error": "Empty or null DataFrame", "row_count": 0}
    
    analysis = {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": df.isnull().sum().to_dict(),
        "missing_percentage": (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
        "duplicates": int(df.duplicated().sum()),
        "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 3),
        "dataset_type": dataset_type,
    }
    
    # Numeric column statistics
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        desc = df[numeric_cols].describe().round(4).to_dict()
        analysis["numeric_summary"] = desc
        analysis["numeric_columns"] = numeric_cols
    
    # Categorical column statistics
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if cat_cols:
        cat_summary = {}
        for col in cat_cols:
            value_counts = df[col].value_counts().head(10).to_dict()
            cat_summary[col] = {
                "unique_count": int(df[col].nunique()),
                "top_values": value_counts,
                "null_count": int(df[col].isnull().sum()),
            }
        analysis["categorical_summary"] = cat_summary
        analysis["categorical_columns"] = cat_cols
    
    # Date column detection
    date_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()
    # Also check object columns that might be dates
    for col in cat_cols:
        try:
            pd.to_datetime(df[col].dropna().head(5))
            date_cols.append(col)
        except (ValueError, TypeError):
            pass
    analysis["date_columns"] = list(set(date_cols))
    
    return analysis


def calculate_metrics(df: pd.DataFrame, metric_columns: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Calculate marketing KPIs from campaign performance data.
    
    Dynamically identifies available metrics and calculates KPIs.
    """
    if df is None or df.empty:
        return {"error": "No data available for metric calculation"}
    
    metrics = {}
    cols = [c.lower() for c in df.columns]
    col_map = {c.lower(): c for c in df.columns}
    
    def get_col(name_variants: List[str]) -> Optional[str]:
        """Find column by name variants."""
        for variant in name_variants:
            if variant.lower() in cols:
                return col_map[variant.lower()]
        return None
    
    # Core metrics
    impressions_col = get_col(["impressions", "imps", "impression"])
    clicks_col = get_col(["clicks", "click", "total_clicks"])
    spend_col = get_col(["spend", "cost", "ad_spend", "budget_spent", "amount_spent"])
    conversions_col = get_col(["conversions", "conversion", "purchases", "orders"])
    revenue_col = get_col(["revenue", "total_revenue", "sales", "income"])
    reach_col = get_col(["reach", "unique_reach"])
    engagement_col = get_col(["engagement", "engagements", "interactions", "total_engagement"])
    
    # Calculate totals
    if impressions_col:
        total_impressions = pd.to_numeric(df[impressions_col], errors="coerce").sum()
        metrics["total_impressions"] = int(total_impressions)
    
    if clicks_col:
        total_clicks = pd.to_numeric(df[clicks_col], errors="coerce").sum()
        metrics["total_clicks"] = int(total_clicks)
    
    if spend_col:
        total_spend = pd.to_numeric(df[spend_col], errors="coerce").sum()
        metrics["total_spend"] = round(float(total_spend), 2)
    
    if conversions_col:
        total_conversions = pd.to_numeric(df[conversions_col], errors="coerce").sum()
        metrics["total_conversions"] = int(total_conversions)
    
    if revenue_col:
        total_revenue = pd.to_numeric(df[revenue_col], errors="coerce").sum()
        metrics["total_revenue"] = round(float(total_revenue), 2)
    
    if reach_col:
        total_reach = pd.to_numeric(df[reach_col], errors="coerce").sum()
        metrics["total_reach"] = int(total_reach)
    
    if engagement_col:
        total_engagement = pd.to_numeric(df[engagement_col], errors="coerce").sum()
        metrics["total_engagement"] = int(total_engagement)
    
    # Derived KPIs
    if impressions_col and clicks_col:
        total_imp = metrics.get("total_impressions", 0)
        total_clk = metrics.get("total_clicks", 0)
        metrics["overall_ctr"] = round(safe_divide(total_clk, total_imp) * 100, 2)
    
    if clicks_col and spend_col:
        metrics["overall_cpc"] = round(safe_divide(metrics.get("total_spend", 0), metrics.get("total_clicks", 0)), 2)
    
    if conversions_col and spend_col:
        metrics["overall_cpa"] = round(safe_divide(metrics.get("total_spend", 0), metrics.get("total_conversions", 0)), 2)
    
    if revenue_col and spend_col:
        metrics["overall_roas"] = round(safe_divide(metrics.get("total_revenue", 0), metrics.get("total_spend", 0)), 2)
    
    if impressions_col and conversions_col:
        metrics["overall_conversion_rate"] = round(
            safe_divide(metrics.get("total_conversions", 0), metrics.get("total_impressions", 0)) * 100, 4
        )
    
    if clicks_col and conversions_col:
        metrics["click_to_conversion_rate"] = round(
            safe_divide(metrics.get("total_conversions", 0), metrics.get("total_clicks", 0)) * 100, 2
        )
    
    if engagement_col and impressions_col:
        metrics["overall_engagement_rate"] = round(
            safe_divide(metrics.get("total_engagement", 0), metrics.get("total_impressions", 0)) * 100, 2
        )
    
    return metrics


def detect_trends(df: pd.DataFrame, date_col: str, metric_col: str) -> Dict[str, Any]:
    """
    Detect trends in a metric over time.
    
    Args:
        df: DataFrame with time series data
        date_col: Column name containing dates
        metric_col: Column name containing the metric to analyze
    
    Returns:
        Dictionary with trend analysis results
    """
    if date_col not in df.columns or metric_col not in df.columns:
        return {"error": f"Required columns not found: {date_col}, {metric_col}"}
    
    try:
        df_clean = df.copy()
        df_clean[date_col] = pd.to_datetime(df_clean[date_col], errors="coerce")
        df_clean[metric_col] = pd.to_numeric(df_clean[metric_col], errors="coerce")
        df_clean = df_clean.dropna(subset=[date_col, metric_col])
        
        if df_clean.empty:
            return {"error": "No valid data after cleaning"}
        
        # Sort by date
        df_clean = df_clean.sort_values(date_col)
        
        # Daily aggregation
        daily = df_clean.groupby(df_clean[date_col].dt.date)[metric_col].sum().reset_index()
        daily.columns = ["date", "value"]
        
        # Weekly aggregation
        df_clean["week"] = df_clean[date_col].dt.isocalendar().week
        weekly = df_clean.groupby("week")[metric_col].sum()
        
        # Calculate trend direction
        if len(daily) >= 2:
            first_half = daily["value"].iloc[:len(daily)//2].mean()
            second_half = daily["value"].iloc[len(daily)//2:].mean()
            change_pct = safe_divide(second_half - first_half, first_half) * 100
            
            if change_pct > 5:
                trend_direction = "increasing"
            elif change_pct < -5:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "insufficient_data"
            change_pct = 0
        
        # Moving average
        if len(daily) >= 7:
            ma_7 = daily["value"].rolling(window=7).mean().dropna().tolist()
        else:
            ma_7 = daily["value"].tolist()
        
        # Volatility (coefficient of variation)
        cv = safe_divide(daily["value"].std(), daily["value"].mean()) * 100
        
        return {
            "trend_direction": trend_direction,
            "change_percentage": round(change_pct, 2),
            "start_value": round(float(daily["value"].iloc[0]), 2),
            "end_value": round(float(daily["value"].iloc[-1]), 2),
            "mean_value": round(float(daily["value"].mean()), 2),
            "max_value": round(float(daily["value"].max()), 2),
            "min_value": round(float(daily["value"].min()), 2),
            "volatility_cv": round(cv, 2),
            "data_points": len(daily),
            "moving_average_7d": [round(v, 2) for v in ma_7[-10:]],  # Last 10 values
            "daily_values": [
                {"date": str(row["date"]), "value": round(float(row["value"]), 2)}
                for _, row in daily.tail(30).iterrows()
            ],
        }
    except Exception as e:
        logger.error(f"Trend detection error: {e}")
        return {"error": str(e)}


def compare_channels(
    df: pd.DataFrame,
    channel_col: str,
    metric_cols: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Compare performance across marketing channels.
    
    Args:
        df: DataFrame with channel data
        channel_col: Column containing channel names
        metric_cols: List of metric columns to compare
    
    Returns:
        Dictionary with channel comparison analysis
    """
    if channel_col not in df.columns:
        return {"error": f"Channel column '{channel_col}' not found"}
    
    # Auto-detect numeric metric columns if not specified
    if not metric_cols:
        metric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Ensure all metric columns exist
    valid_metrics = [c for c in metric_cols if c in df.columns]
    if not valid_metrics:
        return {"error": "No valid metric columns found"}
    
    channels = df[channel_col].dropna().unique().tolist()
    comparison = {}
    
    for channel in channels:
        ch_data = df[df[channel_col] == channel]
        ch_metrics = {}
        
        for metric in valid_metrics:
            values = pd.to_numeric(ch_data[metric], errors="coerce").dropna()
            if len(values) > 0:
                ch_metrics[metric] = {
                    "total": round(float(values.sum()), 2),
                    "mean": round(float(values.mean()), 2),
                    "median": round(float(values.median()), 2),
                    "min": round(float(values.min()), 2),
                    "max": round(float(values.max()), 2),
                    "count": len(values),
                }
        
        # Calculate derived metrics if possible
        spend = pd.to_numeric(ch_data.get("spend", pd.Series()), errors="coerce").sum()
        clicks = pd.to_numeric(ch_data.get("clicks", pd.Series()), errors="coerce").sum()
        conversions = pd.to_numeric(ch_data.get("conversions", pd.Series()), errors="coerce").sum()
        revenue = pd.to_numeric(ch_data.get("revenue", pd.Series()), errors="coerce").sum()
        impressions = pd.to_numeric(ch_data.get("impressions", pd.Series()), errors="coerce").sum()
        
        if spend > 0:
            ch_metrics["cpc"] = round(safe_divide(spend, clicks), 2)
            ch_metrics["cpa"] = round(safe_divide(spend, conversions), 2)
            ch_metrics["roas"] = round(safe_divide(revenue, spend), 2)
        
        if impressions > 0:
            ch_metrics["ctr"] = round(safe_divide(clicks, impressions) * 100, 2)
            ch_metrics["conversion_rate"] = round(safe_divide(conversions, impressions) * 100, 4)
        
        comparison[str(channel)] = ch_metrics
    
    # Rank channels by key metrics
    rankings = {}
    for metric in ["roas", "ctr", "conversion_rate", "cpa"]:
        channel_scores = []
        for ch, ch_data in comparison.items():
            if metric in ch_data:
                score = ch_data[metric] if not isinstance(ch_data[metric], dict) else ch_data[metric].get("total", 0)
                channel_scores.append({"channel": ch, "value": score})
        
        if channel_scores:
            reverse = metric != "cpa"  # Lower CPA is better
            channel_scores.sort(key=lambda x: x["value"], reverse=reverse)
            rankings[metric] = channel_scores
    
    return {
        "channels": comparison,
        "channel_count": len(channels),
        "metrics_analyzed": valid_metrics,
        "rankings": rankings,
    }


def calculate_correlation(df: pd.DataFrame, col1: str, col2: str) -> Dict[str, Any]:
    """
    Calculate correlation between two numeric columns.
    
    Args:
        df: Input DataFrame
        col1: First column name
        col2: Second column name
    
    Returns:
        Dictionary with correlation analysis
    """
    if col1 not in df.columns or col2 not in df.columns:
        return {"error": f"Columns not found: {col1}, {col2}"}
    
    try:
        s1 = pd.to_numeric(df[col1], errors="coerce").dropna()
        s2 = pd.to_numeric(df[col2], errors="coerce").dropna()
        
        # Align indices
        common_idx = s1.index.intersection(s2.index)
        s1 = s1.loc[common_idx]
        s2 = s2.loc[common_idx]
        
        if len(s1) < 3:
            return {"error": "Insufficient data points for correlation (minimum 3)"}
        
        correlation = float(s1.corr(s2))
        
        # Interpret correlation
        abs_corr = abs(correlation)
        if abs_corr >= 0.8:
            strength = "very strong"
        elif abs_corr >= 0.6:
            strength = "strong"
        elif abs_corr >= 0.4:
            strength = "moderate"
        elif abs_corr >= 0.2:
            strength = "weak"
        else:
            strength = "very weak"
        
        direction = "positive" if correlation > 0 else "negative" if correlation < 0 else "none"
        
        return {
            "column_1": col1,
            "column_2": col2,
            "correlation": round(correlation, 4),
            "strength": strength,
            "direction": direction,
            "data_points": len(s1),
            "interpretation": f"{strength.capitalize()} {direction} correlation ({correlation:.3f}) between {col1} and {col2}",
        }
    except Exception as e:
        return {"error": str(e)}


def generate_summary_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate comprehensive statistical summary of a DataFrame.
    
    Args:
        df: Input DataFrame
    
    Returns:
        Dictionary with comprehensive statistics
    """
    if df is None or df.empty:
        return {"error": "Empty DataFrame"}
    
    summary = {
        "shape": {"rows": len(df), "columns": len(df.columns)},
        "columns": [],
    }
    
    for col in df.columns:
        col_info = {
            "name": col,
            "dtype": str(df[col].dtype),
            "null_count": int(df[col].isnull().sum()),
            "null_percentage": round(df[col].isnull().sum() / len(df) * 100, 2),
            "unique_count": int(df[col].nunique()),
        }
        
        if pd.api.types.is_numeric_dtype(df[col]):
            values = pd.to_numeric(df[col], errors="coerce").dropna()
            if len(values) > 0:
                col_info.update({
                    "mean": round(float(values.mean()), 4),
                    "median": round(float(values.median()), 4),
                    "std": round(float(values.std()), 4),
                    "min": round(float(values.min()), 4),
                    "max": round(float(values.max()), 4),
                    "q25": round(float(values.quantile(0.25)), 4),
                    "q75": round(float(values.quantile(0.75)), 4),
                    "skewness": round(float(values.skew()), 4),
                    "has_negatives": bool((values < 0).any()),
                    "has_zeros": bool((values == 0).any()),
                })
        else:
            value_counts = df[col].value_counts().head(5)
            col_info["top_values"] = value_counts.to_dict()
        
        summary["columns"].append(col_info)
    
    return summary


def identify_outliers(df: pd.DataFrame, column: str, method: str = "iqr") -> Dict[str, Any]:
    """
    Identify outliers in a numeric column.
    
    Args:
        df: Input DataFrame
        column: Column to check for outliers
        method: Detection method ('iqr' or 'zscore')
    
    Returns:
        Dictionary with outlier analysis
    """
    if column not in df.columns:
        return {"error": f"Column '{column}' not found"}
    
    values = pd.to_numeric(df[column], errors="coerce").dropna()
    
    if len(values) < 4:
        return {"error": "Insufficient data for outlier detection"}
    
    if method == "iqr":
        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = values[(values < lower_bound) | (values > upper_bound)]
    else:  # z-score
        mean = values.mean()
        std = values.std()
        z_scores = (values - mean) / std if std > 0 else pd.Series(0, index=values.index)
        outliers = values[z_scores.abs() > 3]
        lower_bound = mean - 3 * std
        upper_bound = mean + 3 * std
    
    return {
        "column": column,
        "method": method,
        "outlier_count": len(outliers),
        "outlier_percentage": round(len(outliers) / len(values) * 100, 2),
        "lower_bound": round(float(lower_bound), 2),
        "upper_bound": round(float(upper_bound), 2),
        "outlier_indices": outliers.index.tolist()[:20],  # Limit to 20
        "outlier_values": [round(float(v), 2) for v in outliers.values[:20]],
    }


def aggregate_by_period(
    df: pd.DataFrame,
    date_col: str,
    metric_cols: List[str],
    period: str = "W"
) -> Dict[str, Any]:
    """
    Aggregate metrics by time period.
    
    Args:
        df: Input DataFrame
        date_col: Date column name
        metric_cols: Columns to aggregate
        period: Aggregation period ('D', 'W', 'M')
    
    Returns:
        Dictionary with period-aggregated data
    """
    if date_col not in df.columns:
        return {"error": f"Date column '{date_col}' not found"}
    
    df_clean = df.copy()
    df_clean[date_col] = pd.to_datetime(df_clean[date_col], errors="coerce")
    df_clean = df_clean.dropna(subset=[date_col])
    
    valid_metrics = [c for c in metric_cols if c in df_clean.columns]
    if not valid_metrics:
        return {"error": "No valid metric columns found"}
    
    # Convert metrics to numeric
    for col in valid_metrics:
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
    
    aggregated = df_clean.set_index(date_col).resample(period)[valid_metrics].sum()
    
    result = {
        "period": period,
        "periods": [],
    }
    
    for idx, row in aggregated.iterrows():
        period_data = {"date": str(idx.date())}
        for col in valid_metrics:
            period_data[col] = round(float(row[col]), 2) if pd.notna(row[col]) else 0
        result["periods"].append(period_data)
    
    return result


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    try:
        if denominator == 0 or pd.isna(denominator) or pd.isna(numerator):
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default


def calculate_growth_rate(current: float, previous: float) -> float:
    """Calculate growth rate between two periods."""
    if previous == 0:
        return 0.0 if current == 0 else 100.0
    return round(((current - previous) / abs(previous)) * 100, 2)


def detect_anomalies(
    df: pd.DataFrame,
    date_col: str,
    metric_col: str,
    threshold: float = 2.0
) -> List[Dict[str, Any]]:
    """
    Detect anomalous data points in time series data.
    
    Args:
        df: Input DataFrame
        date_col: Date column
        metric_col: Metric column to check
        threshold: Standard deviations from mean to flag (default 2.0)
    
    Returns:
        List of anomalous data points
    """
    if date_col not in df.columns or metric_col not in df.columns:
        return []
    
    df_clean = df.copy()
    df_clean[date_col] = pd.to_datetime(df_clean[date_col], errors="coerce")
    df_clean[metric_col] = pd.to_numeric(df_clean[metric_col], errors="coerce")
    df_clean = df_clean.dropna(subset=[date_col, metric_col])
    
    if len(df_clean) < 5:
        return []
    
    mean = df_clean[metric_col].mean()
    std = df_clean[metric_col].std()
    
    if std == 0:
        return []
    
    anomalies = []
    for _, row in df_clean.iterrows():
        z_score = (row[metric_col] - mean) / std
        if abs(z_score) > threshold:
            anomalies.append({
                "date": str(row[date_col].date()) if hasattr(row[date_col], "date") else str(row[date_col]),
                "value": round(float(row[metric_col]), 2),
                "z_score": round(float(z_score), 2),
                "expected_range": f"{round(mean - threshold * std, 2)} - {round(mean + threshold * std, 2)}",
                "type": "spike" if z_score > 0 else "dip",
            })
    
    return anomalies
