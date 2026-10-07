import os
from pathlib import Path
from fastapi import UploadFile
import pandas as pd
from app.config import settings
import shutil

def save_upload(file: UploadFile, job_id: str) -> str:
    upload_dir = Path(settings.UPLOAD_DIR) / job_id
    os.makedirs(upload_dir, exist_ok=True)
    
    filepath = upload_dir / file.filename
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return str(filepath)

def load_dataset(filepath: str) -> pd.DataFrame:
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.csv':
        return pd.read_csv(filepath)
    elif ext in ['.xls', '.xlsx']:
        return pd.read_excel(filepath)
    elif ext == '.json':
        return pd.read_json(filepath)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

def detect_format(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.csv':
        return 'csv'
    elif ext in ['.xls', '.xlsx']:
        return 'excel'
    elif ext == '.json':
        return 'json'
    return 'unknown'
