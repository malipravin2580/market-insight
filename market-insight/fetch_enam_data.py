#!/usr/bin/env python3
"""
Fetch trading data from the eNam website and store it in Postgres.
Designed to be invoked as a CLI (e.g. via cron).
"""

import requests
import json
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
import os
from dotenv import load_dotenv
from database import SessionLocal     # re-uses your SessionLocal from database.py
from models import ApmcDetail, EnaamRecord

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables
ENAM_API_URL = os.getenv("ENAM_API_URL", "https://enam.gov.in/web/Ajax_ctrl/trade_data_list")
ENAM_COOKIE = os.getenv("ENAM_COOKIE", "SERVERID=node1; ci_session=kc3ngjdgdk10n2a28pbptdc8ir500qb7")

def fetch_and_store():
    # Determine yesterday’s date
    today = datetime.today().date()
    yesterday = today - timedelta(days=1)
    str_yesterday = yesterday.isoformat()

    # Prepare the POST
    url = ENAM_API_URL
    payload = {
        "language": "en",
        "stateName": "-- All --",
        "apmcName": "-- Select APMCs --",
        "commodityName": "-- Select Commodity --",
        "fromDate": str_yesterday,
        "toDate":   str_yesterday,
    }
    headers = {
        "Cookie": ENAM_COOKIE
    }

    try:
        resp = requests.post(url, headers=headers, data=payload, timeout=30)
        resp.raise_for_status()
        data_list = resp.json().get("data", [])
    except requests.exceptions.Timeout:
        print(f"❌ Connection timeout: Unable to reach eNAM API (enam.gov.in)")
        print("   Please check your internet connection or try again later.")
        raise
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: Unable to connect to eNAM API")
        print(f"   Error: {str(e)}")
        raise
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data from eNAM API: {str(e)}")
        raise

    session = SessionLocal()
    duplication_flag = False

    # Build map of existing APMC names → IDs
    apmcs = session.query(ApmcDetail).all()
    apmc_map = {a.apmc_name: a.id for a in apmcs}

    for d in data_list:
        # Extract fields
        state              = d.get("state")
        apmc               = d.get("apmc")
        commodity          = d.get("commodity")
        min_price          = d.get("min_price")
        modal_price        = d.get("modal_price")
        max_price          = d.get("max_price")
        arrivals           = d.get("commodity_arrivals")
        traded             = d.get("commodity_traded")
        unit               = d.get("Commodity_Uom", "").replace("Qui", "Quintal")
        date_str           = d.get("created_at")

        # Parse the date (fallback to yesterday)
        try:
            parsed_date = datetime.fromisoformat(date_str).date()
        except Exception:
            parsed_date = yesterday

        # Create & add
        record = EnaamRecord(
            state              = state,
            apmc               = apmc,
            apmc_detail_id     = apmc_map.get(apmc),
            commodity          = commodity,
            min_price          = min_price,
            modal_price        = modal_price,
            max_price          = max_price,
            commodity_arrivals = arrivals,
            commodity_traded   = traded,
            commodity_unit     = unit,
            date               = parsed_date
        )
        session.add(record)

        # Commit or rollback on duplicate
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            duplication_flag = True

    session.close()

    # Final status
    if duplication_flag:
        print(f"❌ Data for {str_yesterday} already exists.")
    else:
        print(f"✅ Data for {str_yesterday} imported successfully.")

if __name__ == "__main__":
    fetch_and_store() 