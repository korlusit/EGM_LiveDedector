import sqlite3
import uuid

DB_PATH = "unified_egm.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        c.execute("PRAGMA table_info(criminals)")
        cols = [info[1] for info in c.fetchall()]
        
        if 'unique_id' not in cols:
            print("Adding unique_id column...")
            c.execute("ALTER TABLE criminals ADD COLUMN unique_id TEXT UNIQUE")
            print("Column added.")
            
            
            conn.commit()
        else:
            print("unique_id column already exists.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
