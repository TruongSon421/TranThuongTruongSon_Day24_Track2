# src/api/main.py
from fastapi import FastAPI, Depends, HTTPException, Response
import pandas as pd
from pathlib import Path
from src.access.rbac import get_current_user, require_permission
from src.pii.anonymizer import MedVietAnonymizer

app = FastAPI(title="MedViet Data API", version="1.0.0")
anonymizer = MedVietAnonymizer()

DATA_DIR = Path(__file__).parent.parent.parent / "data"


@app.get("/api/patients/raw")
@require_permission(resource="patient_data", action="read")
async def get_raw_patients(
    current_user: dict = Depends(get_current_user)
):
    df = pd.read_csv(DATA_DIR / "raw" / "patients_raw.csv")
    return {"records": df.head(10).to_dict(orient="records")}


@app.get("/api/patients/anonymized")
@require_permission(resource="training_data", action="read")
async def get_anonymized_patients(
    current_user: dict = Depends(get_current_user)
):
    df = pd.read_csv(DATA_DIR / "raw" / "patients_raw.csv")
    df_anon = anonymizer.anonymize_dataframe(df)
    return {"records": df_anon.head(10).to_dict(orient="records")}


@app.get("/api/metrics/aggregated")
@require_permission(resource="aggregated_metrics", action="read")
async def get_aggregated_metrics(
    current_user: dict = Depends(get_current_user)
):
    df = pd.read_csv(DATA_DIR / "raw" / "patients_raw.csv")
    metrics = df["benh"].value_counts().to_dict()
    return {
        "metrics": metrics,
        "total_patients": len(df)
    }


@app.delete("/api/patients/{patient_id}")
@require_permission(resource="patient_data", action="delete")
async def delete_patient(
    patient_id: str,
    current_user: dict = Depends(get_current_user)
):
    return {"message": f"Patient {patient_id} deleted", "deleted_by": current_user["username"]}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "MedViet Data API"}


@app.get("/metrics")
async def metrics():
    return Response(
        content="""# HELP medviet_api_requests_total Total API requests
# TYPE medviet_api_requests_total counter
medviet_api_requests_total 0
# HELP medviet_api_health API health status
# TYPE medviet_api_health gauge
medviet_api_health 1
""",
        media_type="text/plain"
    )
