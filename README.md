# London Bikes ML Pipeline – Final Project

## Overview
This project demonstrates an end-to-end machine learning pipeline using Google Cloud Composer (Airflow) to predict London bike trip durations. The pipeline extracts data from BigQuery, performs feature engineering, trains a linear regression model, saves artifacts to Google Cloud Storage, and sends an email notification upon completion.

## Features
- **Data Extraction:** Pulls and engineers features from the London Bikes public dataset in BigQuery.
- **Model Training:** Trains a linear regression model (`scikit-learn`'s `LinearRegression`) to predict trip duration based on time and station features.
- **Artifact Storage:** Saves the trained model and evaluation metrics to a GCS bucket.
- **Notification:** Sends an email notification when the pipeline completes successfully.

## Pipeline Steps
1. **Feature Engineering:**
   - SQL transforms and samples the raw data in BigQuery.
2. **Model Training:**
   - Loads data from BigQuery, trains the model, evaluates MSE, and saves results to GCS.
3. **Notification:**
   - Logs completion and sends an email via Airflow's `EmailOperator`.

## Files
- `Dag/london_bikes_duration_dag.py` – Main Airflow DAG file
- `requirements.txt` – Python dependencies for Composer

## How to Run
1. Deploy the DAG to your Composer environment's DAGs folder.
2. Ensure Airflow Variables and Connections are set (see below).
3. Trigger the DAG from the Airflow UI.

## Airflow Setup
- **Variables:**
  - `PROJECT_ID`, `BQ_DATASET`, `BQ_LOCATION`, `GCS_BUCKET`, `SAMPLE_FRAC`
- **Connections:**
  - `smtp_default` (type: SMTP) for Gmail email notifications (use Gmail app password)

## Demo Checklist
- Show project structure and code
- Show BigQuery SQL and feature engineering
- Explain model choice (linear regression)
- Show GCS bucket with saved files
- Show Airflow UI, trigger DAG, and logs
- Show email notification

## Author
Rozy Patel

## video demo:

Link1:
https://teams.microsoft.com/l/meetingrecap?driveId=b%21-xJBchWYtUiezlA_tqf4atzs6U7WWzBEqHFz35w28JMObufC4W89SYnIGcziE13V&driveItemId=016L3Y65Q7ERTG46BOHNHZ4JXDYNQHI76D&sitePath=https%3A%2F%2Fdconline.sharepoint.com%2Fsites%2Fmyrecords%2FShared%2520Documents%2FGeneral%2FRecordings%2FMeeting%2520in%2520General-20250818_234717-Meeting%2520Recording.mp4%3Fweb%3D1&fileUrl=https%3A%2F%2Fdconline.sharepoint.com%2Fsites%2Fmyrecords%2FShared%2520Documents%2FGeneral%2FRecordings%2FMeeting%2520in%2520General-20250818_234717-Meeting%2520Recording.mp4%3Fweb%3D1&threadId=19%3AoiLueHzuH8ROTdlsa2_EgrZTNYGmkjwnugLwrz-Uel01%40thread.tacv2&organizerId=8%3Aorgid%3A24fb1b23-7983-48d5-9fab-3b4579ae2b29&tenantId=49bba7a4-424b-4070-a70e-886e9dd7caef&callId=25c3737f-f7e9-4103-bb96-f509ba07243a&meetingType=MeetNow&organizerGroupId=48cb60aa-69f5-49b3-b199-4093956ca7d4&channelType=Standard&replyChainId=1755575186547&subType=RecapSharingLink_RecapCore

Link2: https://youtu.be/xfIa2fk7R4I
