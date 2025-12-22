import sqlite3
import os

def inspect_db(db_path):
    if not os.path.exists(db_path):
        print(f"File not found: {db_path}")
        return

    print(f"--- Inspecting {db_path} ---")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables: {tables}")
        
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            for col in columns:
                print(col)
            
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            rows = cursor.fetchall()
            print("Sample Data:")
            for row in rows:
                print(row)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

inspect_db("egm_database.db")
inspect_db("egm_plate_database.db")
