from database import SessionLocal
from models import ApmcDetail, EnaamRecord
from sqlalchemy import func
import os
import csv
import argparse
from datetime import datetime

def export_missing_apmc_details(output_file: str = None):
    session = SessionLocal()
    print(f"Database: {session.bind}")

    # Fetch all distinct APMC names via SQLAlchemy, excluding null/empty, strip whitespace
    apmc_names_in_enaam = [
        row[0].strip() for row in session.query(EnaamRecord.apmc)
        .filter(EnaamRecord.apmc != '')
        .distinct()
        .all()
    ]

    # Count ApmcDetail records
    print(f"ApmcDetail records: {session.query(ApmcDetail).count()}")

    missing = []
    exists_count = 0
    for apmc_name in apmc_names_in_enaam:
        normalized = apmc_name
        print(f"Checking {normalized}")
        # Check case-insensitive, trimmed match against ApmcDetail
        exists = session.query(ApmcDetail).filter(ApmcDetail.apmc_name == normalized).first() is not None
        # print("🚀 ~ exists:", exists)
        if exists:
            exists_count += 1
        else:
            # Fetch a sample record for context
            record = session.query(EnaamRecord).filter(EnaamRecord.apmc == normalized).first()
            missing.append({
                "apmc_name":   record.apmc if record and record.apmc else normalized,
                "state":       record.state if record else "",
                "sample_date": record.date.isoformat() if record and record.date else ""
            })

    # Debug: show exactly which APMCs we think are missing
    print(f"Exists count: {exists_count}")
    print(f"Missing APMCs count: {len(missing)}")
    
    # Write to CSV if there are missing APMCs
    if missing:
        if not output_file:
            today = datetime.now().date()
            output_file = f'missing_apmc_details_{today}.csv'
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['APMC Name', 'State', 'Sample Date from EnaamRecord'])
            for entry in missing:
                writer.writerow([entry['apmc_name'], entry['state'], entry['sample_date']])
        print(f"✅ Missing APMC details exported to {output_file}")
    else:
        print("✅ No missing APMC details found.")
    
    session.close()
    return missing

def main():
    parser = argparse.ArgumentParser(
        description="Export missing APMC details to CSV"
    )
    parser.add_argument(
        "--output-file",
        type=str,
        help="Optional custom path for the CSV file"
    )
    args = parser.parse_args()
    export_missing_apmc_details(args.output_file)

if __name__ == "__main__":
    main() 