import sqlite3

DB_PATH = "unified_egm.db"

def fix_schema():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        c.execute("PRAGMA table_info(criminals)")
        cols = [info[1] for info in c.fetchall()]
        
        if 'unique_id' not in cols:
            print("Adding unique_id column (without UNIQUE constraint)...")
            c.execute("ALTER TABLE criminals ADD COLUMN unique_id TEXT")
            conn.commit()
            print("Column 'unique_id' added successfully.")
        else:
            print("Column 'unique_id' already exists.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_schema()
