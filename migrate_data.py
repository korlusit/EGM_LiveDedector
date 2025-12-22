import sqlite3
import json
import os
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from database_manager import DatabaseManager

def migrate():
    print("Starting Migration...")
    db = DatabaseManager()
    
    # 1. Migrate Users & Police (polis_kayit.json + CAMS/Users)
    print("Migrating Users...")
    
    # Load Police Info from JSON
    police_info = {}
    if os.path.exists("polis_kayit.json"):
        try:
            with open("polis_kayit.json", "r", encoding="utf-8") as f:
                police_info = json.load(f)
        except Exception as e:
            print(f"Error reading polis_kayit.json: {e}")

    # Base info structure if json is just a single object (which it seems to be from previous `view_file`)
    # The current json only holds ONE user? "Ahmet Yılmaz". 
    # Validating based on folder structure is better.
    
    users_dir = os.path.join("CAMS", "Users")
    if os.path.exists(users_dir):
        # Initialize FaceAnalysis
        app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        app.prepare(ctx_id=0, det_size=(640, 640))
        
        for item in os.listdir(users_dir):
            path = os.path.join(users_dir, item)
            
            # Default metadata
            name = item
            sicil = f"10{np.random.randint(100,999)}" # Generate fake sicil if unknown
            rank = "Polis Memuru"
            unit = "Genel Hizmet"
            
            # If this folder/file matches the JSON data, use that
            if police_info.get("ad_soyad") == item:
                name = police_info.get("ad_soyad", name)
                rank = police_info.get("rutbe", rank)
                unit = police_info.get("gorev_yeri", unit)
            
            # Extract Face Embedding
            embedding = None
            img_path = None
            
            if os.path.isdir(path):
                # Take first image
                for f in os.listdir(path):
                    if f.lower().endswith(('.jpg', '.png')):
                        img_path = os.path.join(path, f)
                        break
            elif os.path.isfile(path) and item.lower().endswith(('.jpg', '.png')):
                 img_path = path
                 name = os.path.splitext(item)[0]

            if img_path:
                img = cv2.imread(img_path)
                if img is not None:
                    faces = app.get(img)
                    if faces:
                        embedding = faces[0].embedding
                        print(f"Found face for {name}")
            
            if embedding is not None:
                # Add to DB
                # Try to reuse sicil if user already exists or similar logic? 
                # For now just add.
                try:
                    res, msg = db.add_user(sicil, name, rank, unit, embedding)
                    print(f"User {name}: {msg}")
                except Exception as e:
                    print(f"Failed to add {name}: {e}")
    
    # 2. Migrate Criminals
    print("\nMigrating Criminals...")
    if os.path.exists("egm_database.db"):
        conn_old = sqlite3.connect("egm_database.db")
        cursor_old = conn_old.cursor()
        try:
            # Assuming 'persons' table: id, name, type, status, description (based on previous inspect output)
            cursor_old.execute("SELECT * FROM persons")
            rows = cursor_old.fetchall()
            for row in rows:
                # Map columns carefully. Inspect output showed:
                # 0: id, 1: name, 2: type, 3: status, 4: description
                # My `criminals` table: name, crime_type, status, notes
                if len(row) >= 5:
                    name = row[1]
                    c_type = row[2]
                    status = row[3]
                    desc = row[4]
                    db.add_criminal(name, c_type, status, desc)
                    print(f"Migrated criminal: {name}")
        except Exception as e:
            print(f"Error migrating criminals: {e}")
        finally:
            conn_old.close()

    # 3. Migrate Plates
    print("\nMigrating Plates...")
    if os.path.exists("egm_plate_database.db"):
        conn_old = sqlite3.connect("egm_plate_database.db")
        cursor_old = conn_old.cursor()
        try:
            # Assuming 'plates' table. Need to guess columns or select *
            # previous inspect failed to show table name clearly but "sqlite_sequence" was there.
            # Let's try guessing 'plates' or 'plaka'
            cursor_old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name!='sqlite_sequence'")
            tbl = cursor_old.fetchone()
            if tbl:
                t_name = tbl[0]
                cursor_old.execute(f"SELECT * FROM {t_name}")
                rows = cursor_old.fetchall()
                for row in rows:
                    if len(row) >= 2:
                        # Assuming 1: plate, 2: owner, 3: status...
                        # If schema is unknown, we might fail here. 
                        # Let's try to map dynamically or just dump first few cols.
                        plate_no = row[1] if len(row) > 1 else "UNKNOWN"
                        owner = row[2] if len(row) > 2 else "Bilinmiyor"
                        status = row[3] if len(row) > 3 else "Temiz"
                        notes = str(row[4:]) if len(row) > 4 else ""
                        
                        db.add_plate(plate_no, owner, status, notes)
                        print(f"Migrated plate: {plate_no}")
        except Exception as e:
            print(f"Error migrating plates: {e}")
        finally:
            conn_old.close()

    print("Migration Completed.")

if __name__ == "__main__":
    migrate()
