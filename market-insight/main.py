from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from sqlalchemy import distinct, func
from database import SessionLocal
from sqlalchemy.exc import IntegrityError
import requests
import json
from datetime import datetime, timedelta, date
import csv
import os
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from fetch_enam_data import fetch_and_store
from bind_enam_details import bind_apmc_details
from export_missing_apmc_details import export_missing_apmc_details

# Assuming models are defined in a separate file (models.py)
from models import Base, ApmcDetail, EnaamRecord

# Tables are initialized in `database.py`

# FastAPI app
app = FastAPI(
     title="Market Insights API",
    description="Market Insights API for fetching and storing eNAM data",
    version="1.0.0"
)   
scheduler = BackgroundScheduler()

def run_daily_pipeline():
    """
    Run the complete daily pipeline:
    1. Fetch and store eNAM data
    2. Bind APMC details to records
    3. Export missing APMC details
    """
    try:
        print("=" * 60)
        print("Starting daily pipeline...")
        print("=" * 60)
        
        # Step 1: Fetch and store eNAM data
        print("\n[Step 1/3] Fetching and storing eNAM data...")
        fetch_and_store()
        print("✅ Step 1 completed\n")
        
        # Step 2: Bind APMC details
        print("[Step 2/3] Binding APMC details to records...")
        bind_apmc_details()
        print("✅ Step 2 completed\n")
        
        # Step 3: Export missing APMC details
        print("[Step 3/3] Exporting missing APMC details...")
        today = datetime.now().date()
        output_file = f'missing_apmc_details_{today}.csv'
        export_missing_apmc_details(output_file=output_file)
        print("✅ Step 3 completed\n")
        
        print("=" * 60)
        print("✅ Daily pipeline completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"❌ Error in daily pipeline: {str(e)}")
        raise

@app.on_event("startup")
def start_scheduler():
    # Schedule daily pipeline at 00:45 (12:45 AM)
    scheduler.add_job(
        func=run_daily_pipeline,
        trigger="cron",
        # trigger="interval",
        hour=0,
        minute=45,
        # minutes=1,
        id="daily_enam_pipeline",
        replace_existing=True,
    )
    scheduler.start()

@app.on_event("shutdown")
def stop_scheduler():
    scheduler.shutdown(wait=False)

# Pydantic model for input validation
class APMCOutput(BaseModel):
    output_file: Optional[str] = None

@app.post("/enaam_data")
def enaam_data(from_date: Optional[date] = None, to_date: Optional[date] = None):
    # Determine date range to fetch (default to yesterday if not provided)
    today = datetime.today().date()
    yesterday = today - timedelta(days=1)
    fdate = from_date or yesterday
    tdate = to_date or fdate
    str_from = fdate.isoformat()
    str_to = tdate.isoformat()

    # First, check if data already exists for this date range
    session = SessionLocal()
    try:
        # Check if any records exist for this date range
        existing_records = session.query(EnaamRecord).filter(
            EnaamRecord.date >= fdate,
            EnaamRecord.date <= tdate
        ).count()
        
        if existing_records > 0:
            # Get more details about existing data
            distinct_dates = session.query(EnaamRecord.date).filter(
                EnaamRecord.date >= fdate,
                EnaamRecord.date <= tdate
            ).distinct().all()
            date_list = [d[0].isoformat() for d in distinct_dates if d[0]]
            
            session.close()
            return {
                "detail": f"Data for date range {str_from} to {str_to} already exists in the database.",
                "existing_records": existing_records,
                "dates_with_data": sorted(date_list),
                "message": f"✅ Found {existing_records} existing records. Skipping fetch to avoid duplicates."
            }
    except Exception as e:
        session.close()
        raise HTTPException(
            status_code=500,
            detail=f"Error checking existing data: {str(e)}"
        )
    
    session.close()
    
    # If no data exists, proceed with fetching from eNAM API
    url = "https://enam.gov.in/web/Ajax_ctrl/trade_data_list"
    payload = {
        "language": "en",
        "stateName": "-- All --",
        "apmcName": "-- Select APMCs --",
        "commodityName": "-- Select Commodity --",
        "fromDate": str_from,
        "toDate": str_to,
    }
    headers = {
        "Cookie": "SERVERID=node1; ci_session=kc3ngjdgdk10n2a28pbptdc8ir500qb7"
    }
    try:
        resp = requests.post(url, headers=headers, data=payload, timeout=30)
        resp.raise_for_status()
        response_data = resp.json()
        data_list = response_data.get("data", [])
        
        # Check if we got any data
        if not data_list:
            return {
                "detail": f"No data found from eNAM API for {str_from} to {str_to}. The API returned an empty data list.",
                "response": response_data
            }
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail=f"Connection timeout: Unable to reach eNAM API (enam.gov.in). Please check your internet connection or try again later."
        )
    except requests.exceptions.ConnectionError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Connection error: Unable to connect to eNAM API. Error: {str(e)}"
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching data from eNAM API: {str(e)}"
        )

    session = SessionLocal()
    duplication_flag = False
    date_val = None
    records_added = 0
    records_skipped = 0

    # Build map of existing APMC details
    apmc_details = session.query(ApmcDetail).all()
    apmc_map = {ad.apmc_name: ad.id for ad in apmc_details}

    for d in data_list:
        # Unpack fields
        state = d.get("state")
        apmc = d.get("apmc")
        commodity = d.get("commodity")
        min_price = d.get("min_price")
        modal_price = d.get("modal_price")
        max_price = d.get("max_price")
        commodity_arrivals = d.get("commodity_arrivals")
        commodity_traded = d.get("commodity_traded")
        commodity_unit = d.get("Commodity_Uom", "").replace("Qui", "Quintal")
        date_str = d.get("created_at")

        # Parse date
        try:
            parsed_date = datetime.fromisoformat(date_str).date()
        except (TypeError, ValueError):
            try:
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except:
                parsed_date = None

        date_val = parsed_date or fdate

        # Create record
        record = EnaamRecord(
            state=state,
            apmc=apmc,
            apmc_detail_id=apmc_map.get(apmc),
            commodity=commodity,
            min_price=min_price,
            modal_price=modal_price,
            max_price=max_price,
            commodity_arrivals=commodity_arrivals,
            commodity_traded=commodity_traded,
            commodity_unit=commodity_unit,
            date=parsed_date
        )
        session.add(record)

        # Commit or rollback on duplicate
        try:
            session.commit()
            records_added += 1
        except IntegrityError:
            session.rollback()
            duplication_flag = True
            records_skipped += 1

    session.close()

    # Return JSON status with detailed information
    if records_added == 0 and records_skipped > 0:
        return {
            "detail": f"All records for {str_from} to {str_to} already exist in the database. Skipped {records_skipped} duplicate records."
        }
    elif records_added > 0 and records_skipped > 0:
        return {
            "detail": f"Imported {records_added} new records for {str_from} to {str_to}. Skipped {records_skipped} duplicate records."
        }
    elif records_added > 0:
        return {
            "detail": f"Successfully imported {records_added} records for {str_from} to {str_to}."
        }
    else:
        return {
            "detail": f"No data found for {str_from} to {str_to}."
        }

@app.post("/check-missing-apmcs", response_class=FileResponse)
async def check_missing_apmcs(output: APMCOutput):
    # Handle path issues by changing to the correct directory
    try:
        os.chdir('/opt/enaam_data_collection')
    except:
        pass

    # Get today's date for default filename
    today = datetime.now().date()
    output_file = output.output_file or f'missing_apmc_details_{today}.csv'

    # Create a database session
    db = SessionLocal()
    try:
        # exactly like Django’s values_list(...).distinct()
        raw_rows = db\
          .query(EnaamRecord.apmc)\
          .distinct()\
          .all()
        apmc_names = [name for (name,) in raw_rows]
        print("raw distinct apmc count:", len(apmc_names))

        # Prepare a list for missing entries
        missing_apmcs = []

        for apmc_name in apmc_names:
            # Case-insensitive, trimmed lookup in ApmcDetail
            exists = db.query(ApmcDetail.id) \
                       .filter(func.lower(func.trim(ApmcDetail.apmc_name)) == apmc_name) \
                       .first()
            if not exists:
                # Fetch a sample record from EnaamRecord using same normalization
                record = db.query(EnaamRecord) \
                           .filter(func.lower(func.trim(EnaamRecord.apmc)) == apmc_name) \
                           .order_by(EnaamRecord.id) \
                           .first()
                if record:
                    missing_apmcs.append({
                        'apmc_name': record.apmc.strip(),
                        'state': record.state,
                        'sample_date': record.date.strftime('%Y-%m-%d') if record.date else ''
                    })

        if not missing_apmcs:
            return JSONResponse(status_code=200, content={"detail": "No missing APMC details found!"})

        # Save to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['APMC Name', 'State', 'Sample Date from EnaamRecord'])
            for entry in missing_apmcs:
                writer.writerow([entry['apmc_name'], entry['state'], entry['sample_date']])

        # Return the CSV file as a response
        return FileResponse(
            path=output_file,
            filename=output_file,
            media_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename={output_file}'}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
    finally:
        db.close()

# Endpoint to bind existing records with APMC details
@app.post("/bind_apmc_details")
def bind_apmc_details():
    session = SessionLocal()
    try:
        # Build map of (apmc_name, state_name) → detail ID
        apmc_details = session.query(ApmcDetail).all()
        apmc_map = {(ad.apmc_name.strip().lower(), ad.state_name.strip().lower()): ad.id for ad in apmc_details}

        batch_size = 500
        mappings = []
        newly_bound = set()

        # Fetch all records at once to avoid invalidating the cursor on commit
        records = session.query(EnaamRecord).all()
        for record in records:
            key = (record.apmc.strip().lower(), record.state.strip().lower())
            detail_id = apmc_map.get(key)
            if detail_id and record.apmc_detail_id is None:
                mappings.append({"id": record.id, "apmc_detail_id": detail_id})
                newly_bound.add(record.apmc.strip())

            if len(mappings) >= batch_size:
                session.bulk_update_mappings(EnaamRecord, mappings)
                session.commit()
                mappings.clear()

        # Commit any remaining mappings
        if mappings:
            session.bulk_update_mappings(EnaamRecord, mappings)
            session.commit()

        # Prepare response message
        detail_msg = "Records successfully bound."
        if newly_bound:
            detail_msg += " Newly bound APMCs: " + ", ".join(sorted(newly_bound))
        return {"detail": detail_msg}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()