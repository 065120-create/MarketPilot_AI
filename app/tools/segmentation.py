import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def rfm_analysis(df: pd.DataFrame, customer_id_col: str, date_col: str, amount_col: str) -> dict:
    if not all(col in df.columns for col in [customer_id_col, date_col, amount_col]):
        return {"error": "Missing required columns for RFM"}
        
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    latest_date = df[date_col].max() + pd.Timedelta(days=1)
    
    rfm = df.groupby(customer_id_col).agg({
        date_col: lambda x: (latest_date - x.max()).days,
        customer_id_col: 'count',
        amount_col: 'sum'
    }).rename(columns={
        date_col: 'Recency',
        customer_id_col: 'Frequency',
        amount_col: 'Monetary'
    }).reset_index()
    
    # Simple scoring (1-4)
    r_labels = range(4, 0, -1)
    f_labels = range(1, 5)
    m_labels = range(1, 5)
    
    rfm['R'] = pd.qcut(rfm['Recency'], q=4, labels=r_labels, duplicates='drop')
    rfm['F'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=4, labels=f_labels)
    rfm['M'] = pd.qcut(rfm['Monetary'], q=4, labels=m_labels)
    
    rfm['RFM_Score'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)
    
    def rfm_segment(df):
        if df['RFM_Score'] == '444':
            return 'Champions'
        elif df['F'] == 4:
            return 'Loyal Customers'
        elif str(df['M']) == '4':
            return 'Big Spenders'
        elif df['R'] == 1:
            return 'Lost'
        else:
            return 'Average'
            
    rfm['Segment'] = rfm.apply(rfm_segment, axis=1)
    return rfm.to_dict('records')

def demographic_segmentation(df: pd.DataFrame, demographic_cols: list) -> dict:
    valid_cols = [col for col in demographic_cols if col in df.columns]
    if not valid_cols:
        return {"error": "No valid demographic columns found"}
        
    segments = df.groupby(valid_cols).size().reset_index(name='count')
    return segments.to_dict('records')

def behavioral_clustering(df: pd.DataFrame, feature_cols: list, n_clusters: int = 4) -> dict:
    valid_cols = [col for col in feature_cols if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]
    if len(valid_cols) < 2:
        return {"error": "Need at least 2 numeric feature columns for clustering"}
        
    X = df[valid_cols].fillna(0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    
    result_df = df.copy()
    result_df['Cluster'] = clusters
    
    cluster_centers = scaler.inverse_transform(kmeans.cluster_centers_)
    centers_dict = {f"Cluster {i}": dict(zip(valid_cols, center)) for i, center in enumerate(cluster_centers)}
    
    return {
        "assignments": result_df['Cluster'].tolist(),
        "cluster_centers": centers_dict
    }

def calculate_segment_metrics(df: pd.DataFrame, segment_col: str) -> dict:
    if segment_col not in df.columns:
        return {"error": "Segment column not found"}
        
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    metrics = df.groupby(segment_col)[numeric_cols].mean().reset_index()
    metrics['count'] = df.groupby(segment_col).size().values
    
    return metrics.to_dict('records')

def profile_segments(df: pd.DataFrame, segment_col: str, feature_cols: list) -> dict:
    valid_cols = [col for col in feature_cols if col in df.columns]
    if not valid_cols or segment_col not in df.columns:
        return {"error": "Invalid columns provided"}
        
    profiles = {}
    for segment in df[segment_col].unique():
        segment_df = df[df[segment_col] == segment]
        profile = {}
        for col in valid_cols:
            if pd.api.types.is_numeric_dtype(segment_df[col]):
                profile[col] = float(segment_df[col].mean())
            else:
                profile[col] = segment_df[col].mode()[0] if not segment_df[col].mode().empty else None
        profiles[str(segment)] = profile
        
    return profiles
