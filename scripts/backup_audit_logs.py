#!/usr/bin/env python
import os
import sqlite3
import csv
import json
from datetime import datetime, timedelta
import gzip
import shutil
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("audit_backup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("audit_backup")

# Add the parent directory to the path so we can import our app modules
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Import the database URL
from app.database import SQLALCHEMY_DATABASE_URL

def backup_audit_logs():
    """
    Backup audit logs older than 30 days to CSV and compress them
    """
    # Extract SQLite database path from the URL
    db_path = SQLALCHEMY_DATABASE_URL.replace("sqlite:///", "")
    if not os.path.exists(db_path):
        logger.error(f"Database file not found at {db_path}")
        return
    
    # Create backup directory if it doesn't exist
    backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "audit_backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    # Calculate cutoff date (30 days ago)
    retention_days = 30
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    cutoff_str = cutoff_date.strftime("%Y-%m-%d %H:%M:%S")
    
    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if app_settings table exists, create if not
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='app_settings'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE app_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.commit()
        
        # Set archiving flag to allow deletion via triggers
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES ('archiving_in_progress', 'true')")
        conn.commit()
        
        try:
            # Get logs older than cutoff date
            cursor.execute("""
                SELECT * FROM audit_logs
                WHERE timestamp < ?
            """, (cutoff_str,))
            
            logs = cursor.fetchall()
            log_count = len(logs)
            
            if log_count == 0:
                logger.info("No audit logs to archive")
                return
            
            logger.info(f"Found {log_count} audit logs to archive")
            
            # Create a CSV file for backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_file = f"{backup_dir}/audit_logs_{timestamp}.csv"
            
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write header
                column_names = [col[0] for col in cursor.description]
                writer.writerow(column_names)
                
                # Write data
                for log in logs:
                    # Convert any JSON strings in details to readable format
                    row_data = list(log)
                    details_idx = column_names.index("details") if "details" in column_names else -1
                    if details_idx >= 0 and row_data[details_idx]:
                        try:
                            # Just to make it more readable in the CSV
                            details_dict = json.loads(row_data[details_idx])
                            row_data[details_idx] = json.dumps(details_dict, ensure_ascii=False, indent=2)
                        except:
                            pass  # Keep original if can't parse
                    
                    writer.writerow(row_data)
            
            logger.info(f"Wrote audit logs to {csv_file}")
            
            # Compress the CSV file
            with open(csv_file, 'rb') as f_in:
                with gzip.open(f"{csv_file}.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove the original CSV file
            os.remove(csv_file)
            logger.info(f"Compressed to {csv_file}.gz")
            
            # Get IDs to delete
            log_ids = [log['id'] for log in logs]
            
            # Delete backed up logs from database
            chunks = [log_ids[i:i+100] for i in range(0, len(log_ids), 100)]
            total_deleted = 0
            
            for chunk in chunks:
                placeholders = ','.join('?' for _ in chunk)
                cursor.execute(f"DELETE FROM audit_logs WHERE id IN ({placeholders})", chunk)
                conn.commit()
                total_deleted += len(chunk)
                logger.info(f"Deleted {total_deleted}/{log_count} logs")
            
            logger.info(f"Successfully archived and deleted {total_deleted} audit log entries")
            
        finally:
            # Reset the archiving flag
            cursor.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES ('archiving_in_progress', 'false')")
            conn.commit()
            conn.close()
            
    except Exception as e:
        logger.error(f"Error during audit log backup: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        backup_audit_logs()
    except Exception as e:
        logger.error(f"Audit backup script failed: {str(e)}")
        sys.exit(1)