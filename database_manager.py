import sqlite3
import os
import datetime
import numpy as np
import pickle
class DatabaseManager:
    def __init__(self, db_name="unified_egm.db"):
        self.db_name = db_name
        self.init_db()
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sicil_no TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                rank TEXT,
                unit TEXT,
                face_encoding BLOB, 
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS criminals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tc_no TEXT UNIQUE,
                name TEXT NOT NULL,
                crime_type TEXT,
                status TEXT,
                notes TEXT,
                face_encoding BLOB,
                photo_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate_number TEXT UNIQUE NOT NULL,
                owner TEXT,
                status TEXT, 
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    def add_user(self, sicil_no, name, rank, unit, face_encoding):
        """
        face_encoding: numpy array
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            encoding_blob = pickle.dumps(face_encoding)
            cursor.execute('''
                INSERT INTO users (sicil_no, name, rank, unit, face_encoding)
                VALUES (?, ?, ?, ?, ?)
            ''', (sicil_no, name, rank, unit, encoding_blob))
            conn.commit()
            return True, "Kullanıcı başarıyla eklendi."
        except sqlite3.IntegrityError:
            return False, "Bu sicil numarası zaten kayıtlı."
        except Exception as e:
            return False, str(e)
        finally:
            if conn: conn.close()
    def get_all_users_encodings(self):
        """
        Returns a dictionary: {sicil_no: {'name': name, 'encoding': numpy_array}}
        """
        users_data = {}
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT sicil_no, name, face_encoding, rank FROM users")
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            sicil, name, blob, rank = row
            if blob:
                encoding = pickle.loads(blob)
                users_data[sicil] = {
                    'name': name,
                    'rank': rank,
                    'encoding': encoding
                }
        return users_data
    def get_user_by_sicil(self, sicil_no):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE sicil_no=?", (sicil_no,))
        row = cursor.fetchone()
        conn.close()
        return row
    def add_criminal(self, name, crime_type, status, notes, face_encoding=None, photo_path=None, tc_no=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        encoding_blob = pickle.dumps(face_encoding) if face_encoding is not None else None
        cursor.execute('''
            INSERT INTO criminals (name, crime_type, status, notes, face_encoding, photo_path, tc_no)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, crime_type, status, notes, encoding_blob, photo_path, tc_no))
        conn.commit()
        conn.close()
    def get_all_criminals(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM criminals")
        rows = cursor.fetchall()
        conn.close()
        return rows
    def add_plate(self, plate_number, owner, status, notes):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO plates (plate_number, owner, status, notes)
                VALUES (?, ?, ?, ?)
            ''', (plate_number, owner, status, notes))
            conn.commit()
            return True, "Plaka eklendi."
        except sqlite3.IntegrityError:
            return False, "Plaka zaten kayıtlı."
        finally:
            if conn: conn.close()
    def check_plate(self, plate_number):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM plates WHERE plate_number=?", (plate_number,))
        row = cursor.fetchone()
        conn.close()
        return row
