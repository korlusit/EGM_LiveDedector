import os
import cv2
import pickle
import sqlite3
import numpy as np
from insightface.app import FaceAnalysis
from database_manager import DatabaseManager

def reprocess():
    print("Initializing FaceAnalysis...")
    app = FaceAnalysis(name='buffalo_l', providers=['CUDAExecutionProvider', 'DmlExecutionProvider', 'CPUExecutionProvider'])
    app.prepare(ctx_id=0, det_size=(640, 640))
    
    db = DatabaseManager()
    
    persons_dir = os.path.join("CAMS", "Persons")
    print(f"Scanning {persons_dir} for criminals...")
    if os.path.exists(persons_dir):
        count = 0
        for item in os.listdir(persons_dir):
            path = os.path.join(persons_dir, item)
            name = item
            if os.path.isfile(path):
                name = os.path.splitext(item)[0]
            
            img_path = None
            if os.path.isdir(path):
                for f in os.listdir(path):
                    if f.lower().endswith(('.jpg', '.png', '.jpeg')):
                        img_path = os.path.join(path, f)
                        break
            elif os.path.isfile(path) and item.lower().endswith(('.jpg', '.png', '.jpeg')):
                img_path = path

            if img_path:
                print(f"Processing {name}...")
                img = cv2.imread(img_path)
                if img is None: continue
                
                faces = app.get(img)
                if faces:
                    embedding = faces[0].embedding
                    conn = db.get_connection()
                    c = conn.cursor()
                    c.execute("SELECT id FROM criminals WHERE name=?", (name,))
                    row = c.fetchone()
                    
                    encoding_blob = pickle.dumps(embedding)
                    
                    if row:
                        c.execute("UPDATE criminals SET face_encoding=?, photo_path=? WHERE id=?", (encoding_blob, img_path, row[0]))
                        print(f"Updated criminal: {name}")
                    else:
                        c.execute("INSERT INTO criminals (name, crime_type, status, notes, face_encoding, photo_path) VALUES (?, ?, ?, ?, ?, ?)",
                                  (name, "Bilinmiyor", "Aranıyor", "Otomatik eklendi", encoding_blob, img_path))
                        print(f"Added criminal: {name}")
                    conn.commit()
                    conn.close()
                    count += 1
        print(f"Processed {count} criminals.")

    users_dir = os.path.join("CAMS", "Users")
    print(f"Scanning {users_dir} for users...")
    if os.path.exists(users_dir):
        count = 0
        for item in os.listdir(users_dir):
            path = os.path.join(users_dir, item)
            name = item
            if os.path.isfile(path):
                name = os.path.splitext(item)[0]
                
            img_path = None
            if os.path.isdir(path):
                for f in os.listdir(path):
                    if f.lower().endswith(('.jpg', '.png', '.jpeg')):
                        img_path = os.path.join(path, f)
                        break
            elif os.path.isfile(path) and item.lower().endswith(('.jpg', '.png', '.jpeg')):
                img_path = path
                
            if img_path:
                print(f"Processing User {name}...")
                img = cv2.imread(img_path)
                if img is None: continue
                
                faces = app.get(img)
                if faces:
                    embedding = faces[0].embedding
                    conn = db.get_connection()
                    c = conn.cursor()
                    c.execute("SELECT sicil_no FROM users WHERE name=?", (name,))
                    row = c.fetchone()
                    
                    if row:
                        encoding_blob = pickle.dumps(embedding)
                        c.execute("UPDATE users SET face_encoding=? WHERE sicil_no=?", (encoding_blob, row[0]))
                        print(f"Updated user: {name}")
                    else:
                        sicil = f"POL{np.random.randint(10000,99999)}"
                        db.add_user(sicil, name, "Polis Memuru", "Merkez", embedding)
                        print(f"Added user: {name}")
                    conn.close()
                    count += 1
        print(f"Processed {count} users.")

if __name__ == "__main__":
    reprocess()
