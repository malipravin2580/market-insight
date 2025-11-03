#!/usr/bin/env python3
"""
Bind existing EnaamRecord entries to their ApmcDetail IDs.
Designed to be invoked as a CLI (e.g., via cron).
"""

import os
import argparse
from sqlalchemy.exc import SQLAlchemyError

from main import SessionLocal
from models import ApmcDetail, EnaamRecord

def bind_apmc_details(batch_size: int = 500):
    # Ensure we run from this script’s directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    print("🔎 APMC Scanning has started")
    session = SessionLocal()

    # Build map: apmc_name → ApmcDetail.id
    apmcs = session.query(ApmcDetail).all()
    apmc_map = {a.apmc_name: a.id for a in apmcs}

    total_updated = 0
    mappings = []

    # Stream through records in batches
    for record in session.query(EnaamRecord).yield_per(batch_size):
        apmc_name = record.apmc
        apmc_detail_id = apmc_map.get(apmc_name)
        if apmc_detail_id:
            mappings.append({
                "id": record.id,
                "apmc_detail_id": apmc_detail_id
            })

        if len(mappings) >= batch_size:
            try:
                session.bulk_update_mappings(EnaamRecord, mappings)
                session.commit()
                total_updated += len(mappings)
            except SQLAlchemyError as e:
                session.rollback()
                print(f"Error updating batch: {e}")
            mappings.clear()

    # Final leftover batch
    if mappings:
        try:
            session.bulk_update_mappings(EnaamRecord, mappings)
            session.commit()
            total_updated += len(mappings)
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error updating final batch: {e}")

    session.close()
    print(f"✅ {total_updated} records have been successfully bound with APMC details")

def main():
    parser = argparse.ArgumentParser(
        description="Bind existing EnaamRecord entries to ApmcDetail"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Number of records to process per batch"
    )
    args = parser.parse_args()
    bind_apmc_details(args.batch_size)

if __name__ == "__main__":
    main() 