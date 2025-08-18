
from __future__ import annotations
from datetime import datetime
import json, os, tempfile, logging

from airflow import DAG
from airflow.models import Variable
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.operators.python import get_current_context


# Config (use Airflow Variables in UI if you prefer) 
PROJECT_ID   = Variable.get("PROJECT_ID", "penguin-ml-api")
BQ_DATASET   = Variable.get("BQ_DATASET", "ml_staging")

# London Bikes Duration ML Pipeline DAG
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.operators.email import EmailOperator
from airflow.models import Variable
from datetime import datetime
import logging

# Config
PROJECT_ID = Variable.get("PROJECT_ID", "penguin-ml-api")
BQ_DATASET = Variable.get("BQ_DATASET", "ml_staging")
BQ_LOCATION = Variable.get("BQ_LOCATION", "EU")
GCS_BUCKET = Variable.get("GCS_BUCKET", "europe-west2-ml-composer-en-a0e5b8cb-bucket")
DAG_ID = "london_bikes_duration_pipeline_v1"
SAMPLE_FRAC = float(Variable.get("SAMPLE_FRAC", "0.001"))

# SQL for feature engineering and sampling
FEATURE_SQL = f"""
CREATE SCHEMA IF NOT EXISTS `{PROJECT_ID}.{BQ_DATASET}`;
CREATE OR REPLACE TABLE `{PROJECT_ID}.{BQ_DATASET}.duration_feature_sampled` AS
WITH base AS (
  SELECT
    duration AS duration_sec,
    start_date,
    start_station_name,
    end_station_name
  FROM `bigquery-public-data.london_bicycles.cycle_hire`
  WHERE duration BETWEEN 60 AND 3600
    AND start_date IS NOT NULL
    AND start_station_name IS NOT NULL
    AND end_station_name IS NOT NULL
    AND RAND() < {SAMPLE_FRAC}
)
SELECT
  duration_sec,
  EXTRACT(HOUR FROM start_date) AS hour,
  EXTRACT(DAYOFWEEK FROM start_date) AS dow,
  EXTRACT(MONTH FROM start_date) AS month,
  CASE WHEN EXTRACT(DAYOFWEEK FROM start_date) IN (1,7) THEN 1 ELSE 0 END AS is_weekend,
  start_station_name,
  end_station_name
FROM base;
"""

def train_model(**context):
    import pandas as pd, joblib, json, tempfile, os
    from google.cloud import bigquery, storage
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_squared_error

    # Load data from BigQuery
    bq = bigquery.Client(project=PROJECT_ID)
    sql = f"SELECT * FROM `{PROJECT_ID}.{BQ_DATASET}.duration_feature_sampled`"
    df = bq.query(sql, location=BQ_LOCATION).to_dataframe()
    logging.info(f"Loaded {len(df)} rows from BigQuery.")

    # Features and target
    X = df[["hour", "dow", "month", "is_weekend"]]
    y = df["duration_sec"]

    # Train model
    model = LinearRegression()
    model.fit(X, y)

    # Evaluate
    preds = model.predict(X)
    mse = mean_squared_error(y, preds)
    metrics = {"mse": mse}
    logging.info(f"Model MSE: {mse}")

    # Save model and metrics to GCS
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(GCS_BUCKET)
    with tempfile.TemporaryDirectory() as d:
        model_path = os.path.join(d, "model.joblib")
        joblib.dump(model, model_path)
        bucket.blob("model.joblib").upload_from_filename(model_path)

        metrics_path = os.path.join(d, "metrics.json")
        with open(metrics_path, "w") as f:
            json.dump(metrics, f)
        bucket.blob("metrics.json").upload_from_filename(metrics_path)

    return metrics

def log_completion(**context):
    metrics = context["ti"].xcom_pull(task_ids="train_model")
    logging.info(f"🎉 Model training complete! {metrics}")

with DAG(
    dag_id=DAG_ID,
    start_date=datetime(2024, 1, 1),
    schedule_interval="0 0 * * 0",
    catchup=False,
    tags=["composer", "bikes", "regression"],
) as dag:
    build_features = BigQueryInsertJobOperator(
        task_id="build_features",
        configuration={"query": {"query": FEATURE_SQL, "useLegacySql": False}},
        location=BQ_LOCATION,
        gcp_conn_id="google_cloud_default",
    )

    train = PythonOperator(
        task_id="train_model",
        python_callable=train_model,
    )

    notify = PythonOperator(
        task_id="notify_completion_log",
        python_callable=log_completion,
    )

    email_task = EmailOperator(
            task_id="send_email",
            to="rozypatel94243@gmail.com",
            subject="London Bikes Model Training Complete",
            html_content="Model training complete! Check GCS for model and metrics."
        )

    build_features >> train >> [notify, email_task]