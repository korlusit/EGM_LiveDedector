import sys
import cv2
import os
import shutil
import sqlite3
import numpy as np
import time
import re
import difflib
import threading
from PIL import Image, ImageDraw, ImageFont

from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QTextEdit, QListWidget, 
                             QFrame, QSizePolicy, QFileDialog, QMessageBox, 
                             QComboBox, QRadioButton, QButtonGroup, QDialog, QSlider)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMutex

import torch
from ultralytics import YOLO
import easyocr

CONFIDENCE_YOLO = 0.50
SIMILARITY_THRESHOLD = 0.80
DET_SIZE = (640, 640)
DB_PATH = "egm_plate_database.db"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FACECAM_DIR = os.path.join(BASE_DIR, "CAMS", "PlateCam") 
SNAPSHOTS_DIR = os.path.join(BASE_DIR, "CAMS", "Snapshots")

if not os.path.exists(FACECAM_DIR): os.makedirs(FACECAM_DIR)
if not os.path.exists(SNAPSHOTS_DIR): os.makedirs(SNAPSHOTS_DIR)

def put_text_utf8(img, text, pos, color, font_size=20):
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    try: font = ImageFont.truetype("arial.ttf", font_size)
    except: font = ImageFont.load_default()
    rgb_color = (color[2], color[1], color[0])
    draw.text(pos, text, font=font, fill=rgb_color)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS plates (
        id INTEGER PRIMARY KEY AUTOINCREMENT, plate_number TEXT UNIQUE, 
        owner TEXT, status TEXT, description TEXT)""")
    conn.commit()
    conn.close()

init_db()

PROFESSIONAL_THEME = """
QWidget { background-color: #050505; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }

QFrame#SidePanel, QFrame#LeftPanel { 
    background-color: #121212; 
    border: 1px solid #222; 
    border-radius: 8px; 
    padding: 10px; 
}

QFrame#SidePanel QLabel, QFrame#LeftPanel QLabel {
    color: #e0e0e0;
    font-weight: bold;
}

QLabel#VideoLabel { 
    background-color: #000; 
    border: 2px solid #333; 
    border-radius: 8px; 
}

QLabel#AlertTitle { 
    color: #ff3333; 
    font-weight: bold; 
    font-size: 28px; 
    background-color: transparent;
    padding: 5px;
}

QGroupBox { 
    border: 1px solid #333; 
    margin-top: 10px; 
}

QLineEdit, QTextEdit, QComboBox { 
    background-color: #1a1a1a; 
    border: 1px solid #333; 
    border-radius: 4px;
    padding: 6px; 
    color: white; 
}

QListWidget {
    background-color: #121212;
    color: #e0e0e0;
    border: 1px solid #333;
    border-radius: 6px;
    padding: 5px;
}
QListWidget::item:selected {
    background-color: #0a58ca;
    color: white;
}

QPushButton { 
    background-color: #0a58ca; 
    color: white; 
    border-radius: 6px; 
    padding: 12px; 
    font-weight: bold; 
    font-size: 14px;
    border: none;
}
QPushButton:hover { background-color: #0d6efd; }
QPushButton:pressed { background-color: #084298; }
QPushButton:disabled { background-color: #222; color: #555; }

QPushButton#PlayBtn { background-color: #0a58ca; font-size: 16px; }
QPushButton#StopBtn { background-color: #dc3545; } 
QPushButton#AdminBtn { background-color: #0a58ca; }

QSlider::groove:horizontal { border: 1px solid #333; height: 6px; background: #222; margin: 2px 0; border-radius: 3px; }
QSlider::handle:horizontal { background: #0a58ca; width: 16px; height: 16px; margin: -5px 0; border-radius: 8px; }
"""

class DatabaseHandler:
    def __init__(self, db_path):
        self.db_path = db_path
        self.mutex = QMutex()
    
    def get_plate_info(self, plate):
        self.mutex.lock()
        info = None
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT owner, status, description FROM plates WHERE plate_number=?", (plate,))
            r = c.fetchone()
            conn.close()
            if r: 
                info = {"owner": r[0], "status": r[1], "description": r[2]}
            else:
                info = {"owner": "Bilinmiyor", "status": "TEMIZ", "description": "Kayit yok"}
        except: pass
        self.mutex.unlock()
        return info
    
    def add_wanted_plate(self, plate, owner, status, desc):
        self.mutex.lock()
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO plates (plate_number, owner, status, description) VALUES (?,?,?,?)",
                      (plate, owner, status, desc))
            conn.commit()
            conn.close()
        except: pass
        self.mutex.unlock()

class AdminDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("EGM PLAKA VERI GIRISI")
        self.resize(500, 600)
        self.setStyleSheet(PROFESSIONAL_THEME)
        self.init_ui()

    def init_ui(self):
        l = QVBoxLayout(self)
        
        l.addWidget(QLabel("Plaka No (Örn: 34ABC123):"))
        self.inp_plate = QTextEdit(); self.inp_plate.setFixedHeight(40); l.addWidget(self.inp_plate)
        
        l.addWidget(QLabel("Araç Sahibi / Durum:"))
        self.inp_owner = QTextEdit(); self.inp_owner.setFixedHeight(40); l.addWidget(self.inp_owner)
        
        l.addWidget(QLabel("Durum Seç:"))
        self.combo_status = QComboBox(); self.combo_status.addItems(["CALINTI", "ARANIYOR", "HACIZLI", "TEMIZ"])
        l.addWidget(self.combo_status)
        
        l.addWidget(QLabel("Açıklama:"))
        self.inp_desc = QTextEdit(); self.inp_desc.setFixedHeight(80); l.addWidget(self.inp_desc)
        
        btn_save = QPushButton("KAYDET")
        btn_save.clicked.connect(self.save)
        l.addWidget(btn_save)

    def save(self):
        plate = self.inp_plate.toPlainText().strip().upper()
        owner = self.inp_owner.toPlainText().strip()
        status = self.combo_status.currentText()
        desc = self.inp_desc.toPlainText()
        
        if not plate: return
        
        db = DatabaseHandler(DB_PATH)
        db.add_wanted_plate(plate, owner, status, desc)
        QMessageBox.information(self, "Bilgi", f"{plate} plakasi sisteme kaydedildi.")
        self.accept()

class VideoWorker(QThread):
    change_pixmap = pyqtSignal(QImage)
    plate_found = pyqtSignal(dict, np.ndarray, str) 
    log_msg = pyqtSignal(str)
    finished = pyqtSignal()
    duration_set = pyqtSignal(int)
    position_changed = pyqtSignal(int)
    
    def __init__(self, vpath):
        super().__init__()
        self.vpath = vpath
        self.running = True
        self.paused = False
        self.seek_req = -1
        self.db = DatabaseHandler(DB_PATH)
        self.confirmed_plates = set()
        
        self.active_tracks = {}
        self.frame_count = 0
        
    def toggle_pause(self): self.paused = not self.paused; return self.paused
    def set_seek(self, frame): self.seek_req = frame
    def kill(self): self.running = False; self.wait()

    def run(self):
        self.log_msg.emit(f"Baslatiliyor: {os.path.basename(self.vpath)}")
        try:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.log_msg.emit(f"Islem Birimi: {device.upper()}")
            
            self.yolo = YOLO('yolo11n.pt').to(device)
            try: self.plate_model = YOLO('plate_model.pt').to(device)
            except: self.plate_model = None; self.log_msg.emit("Plaka modeli yok, yedek mod devrede.")
            
            self.reader = easyocr.Reader(['en'], gpu=(device=='cuda'))
            
            cap = cv2.VideoCapture(self.vpath)
            if not cap.isOpened():
                self.log_msg.emit("HATA: Video acilamadi!"); self.finished.emit(); return
            
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.duration_set.emit(total)

            while self.running:
                if self.seek_req != -1:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, self.seek_req)
                    self.seek_req = -1
                
                if self.paused: self.msleep(50); continue

                ret, frame = cap.read()
                if not ret: self.log_msg.emit("Video Bitti."); self.running = False; break
                
                self.process(frame, cap.get(cv2.CAP_PROP_POS_FRAMES))
            
            cap.release(); self.finished.emit()

        except Exception as e:
            self.log_msg.emit(f"HATA: {e}"); self.finished.emit()

    def process(self, frame, pos):
        self.position_changed.emit(int(pos))
        
        results = self.yolo.track(frame, persist=True, conf=0.50, classes=[2, 3, 5, 7], verbose=False)
        
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.int().cpu().tolist()
            ids = results[0].boxes.id.int().cpu().tolist()
            
            for box, obj_id in zip(boxes, ids):
                x1, y1, x2, y2 = box
                w, h = x2 - x1, y2 - y1
                
                if obj_id not in self.active_tracks:
                    self.active_tracks[obj_id] = {"plate": "", "votes": {}, "confirmed": False}
                
                track = self.active_tracks[obj_id]
                
                color = (0, 255, 0) if track["confirmed"] else (0, 255, 255)
                label = track["plate"] if track["confirmed"] else "OKUNUYOR..."
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                if not track["confirmed"] and w > 50 and h > 50:
                    vehicle_crop = self.safe_crop(frame, x1, y1, x2, y2)
                    if vehicle_crop is not None:
                        p_crops = []
                        if self.plate_model:
                            p_res = self.plate_model(vehicle_crop, verbose=False)
                            if len(p_res[0].boxes) > 0:
                                for pb in p_res[0].boxes.xyxy.cpu().tolist():
                                    px1, py1, px2, py2 = map(int, pb)
                                    p_crops.append(self.safe_crop(vehicle_crop, px1, py1, px2, py2, padding=0.1))
                        
                        if not p_crops: 
                            pass 

                        for pc in p_crops:
                            if pc is None: continue
                            gray = cv2.cvtColor(pc, cv2.COLOR_BGR2GRAY)
                            gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                            
                            try:
                                ocr_res = self.reader.readtext(gray, detail=0, allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                                for text in ocr_res:
                                    clean = self.clean_text(text)
                                    if clean:
                                        track["votes"][clean] = track["votes"].get(clean, 0) + 1
                                        if track["votes"][clean] >= 2: 
                                            track["plate"] = clean
                                            track["confirmed"] = True
                                            self.active_tracks[obj_id] = track
                                            
                                            info = self.db.get_plate_info(clean)
                                            self.plate_found.emit(info, vehicle_crop.copy(), clean)
                                            break
                            except: pass

                if label:
                    t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                    cv2.rectangle(frame, (x1, y1-25), (x1+t_size[0], y1), color, -1)
                    cv2.putText(frame, label, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888).copy()
        self.change_pixmap.emit(qt_img)

    def safe_crop(self, img, x1, y1, x2, y2, padding=0):
        h, w = img.shape[:2]
        if padding > 0:
            pw, ph = int((x2-x1)*padding), int((y2-y1)*padding)
            x1, y1 = max(0, x1-pw), max(0, y1-ph)
            x2, y2 = min(w, x2+pw), min(h, y2+ph)
        if x2>x1 and y2>y1: return img[y1:y2, x1:x2]
        return None

    def clean_text(self, text):
        clean = "".join(filter(str.isalnum, text)).upper()
        if len(clean) > 7 and clean.endswith('1'): clean = clean[:-1]
        tr_regex = re.compile(r"^(0[1-9]|[1-7][0-9]|8[0-1])[A-Z]{1,3}\d{2,5}$")
        return clean if tr_regex.match(clean) else None

class PlateApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EGM PLAKA TANIMA SISTEMI (V2 PRO)")
        self.resize(1500, 950)
        self.setStyleSheet(PROFESSIONAL_THEME)
        self.curr_vid = None
        self.is_dragging = False
        self.worker = None 
        self.init_ui()
        self.load_files()

    def init_ui(self):
        layout = QHBoxLayout(self)
        
        left_frame = QFrame()
        left_frame.setObjectName("LeftPanel")
        left = QVBoxLayout(left_frame)
        
        btn_adm = QPushButton("PLAKA VERI GIRISI"); btn_adm.clicked.connect(self.open_admin); btn_adm.setFixedHeight(50); btn_adm.setObjectName("AdminBtn")
        left.addWidget(btn_adm)
        left.addWidget(QLabel("CAMS/PlateCam KLASORU"))
        self.vlist = QListWidget(); self.vlist.setFixedWidth(260); self.vlist.itemClicked.connect(self.sel_vid); left.addWidget(self.vlist)
        btn_ref = QPushButton("Yenile"); btn_ref.clicked.connect(self.load_files); left.addWidget(btn_ref)
        self.log_box = QTextEdit(); self.log_box.setReadOnly(True); self.log_box.setFixedHeight(150); left.addWidget(self.log_box)
        
        layout.addWidget(left_frame)
        
        center = QVBoxLayout()
        self.vid_lbl = QLabel("Sinyal Yok"); self.vid_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter); self.vid_lbl.setObjectName("VideoLabel")
        self.vid_lbl.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        center.addWidget(self.vid_lbl, stretch=5)
        
        s_lay = QHBoxLayout()
        self.lbl_cur = QLabel("00:00")
        self.slider = QSlider(Qt.Orientation.Horizontal); self.slider.setRange(0, 100); self.slider.setEnabled(False)
        self.slider.sliderPressed.connect(self.on_press); self.slider.sliderReleased.connect(self.on_release)
        self.slider.valueChanged.connect(self.on_move)
        self.lbl_tot = QLabel("00:00")
        s_lay.addWidget(self.lbl_cur); s_lay.addWidget(self.slider); s_lay.addWidget(self.lbl_tot)
        center.addLayout(s_lay)

        ctrl = QHBoxLayout()
        self.btn_play = QPushButton("OYNAT"); self.btn_play.clicked.connect(self.toggle); self.btn_play.setEnabled(False); self.btn_play.setObjectName("PlayBtn")
        self.btn_stop = QPushButton("DURDUR"); self.btn_stop.clicked.connect(self.stop); self.btn_stop.setEnabled(False); self.btn_stop.setObjectName("StopBtn")
        ctrl.addWidget(self.btn_play); ctrl.addWidget(self.btn_stop)
        center.addLayout(ctrl)

        layout.addLayout(center, stretch=1)

        right_frame = QFrame(); right_frame.setFixedWidth(380); right_frame.setObjectName("SidePanel")
        right = QVBoxLayout(right_frame)
        
        right.addWidget(QLabel("TESPIT EDILEN PLAKA"))
        self.crim_img = QLabel(); self.crim_img.setFixedSize(320, 200); self.crim_img.setStyleSheet("background:black; border:2px solid #555;")
        self.crim_img.setAlignment(Qt.AlignmentFlag.AlignCenter); right.addWidget(self.crim_img, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_plate = QLabel("-"); self.lbl_plate.setStyleSheet("font-size:32px; font-weight:bold; color: #f39c12;")
        self.lbl_stat = QLabel("DURUM: -"); self.lbl_stat.setObjectName("SafeTitle")
        self.lbl_owner = QLabel("Sahip: -")
        self.txt_desc = QTextEdit(); self.txt_desc.setReadOnly(True)
        
        right.addWidget(self.lbl_plate, alignment=Qt.AlignmentFlag.AlignCenter)
        right.addWidget(self.lbl_stat)
        right.addWidget(self.lbl_owner)
        right.addWidget(self.txt_desc)
        
        right.addWidget(QLabel("Son Tespitler:"))
        self.det_list = QListWidget()
        right.addWidget(self.det_list)

        layout.addWidget(right_frame)

    def load_files(self):
        self.vlist.clear()
        if not os.path.exists(FACECAM_DIR): os.makedirs(FACECAM_DIR)
        valid_exts = ('.mp4', '.mov', '.avi', '.mkv', '.wmv')
        fs = [f for f in os.listdir(FACECAM_DIR) if f.lower().endswith(valid_exts)]
        if not fs: 
            self.log("VIDEO BULUNAMADI! Lutfen su klasore video atin:")
            self.log(f"{FACECAM_DIR}")
        else:
            self.log(f"{len(fs)} video bulundu.")
            for f in fs: self.vlist.addItem(f)

    def sel_vid(self, item): self.curr_vid = os.path.join(FACECAM_DIR, item.text()); self.btn_play.setEnabled(True)

    def toggle(self):
        if not self.worker or not self.worker.isRunning():
            self.worker = VideoWorker(self.curr_vid)
            self.worker.change_pixmap.connect(self.upd_img)
            self.worker.plate_found.connect(self.upd_alert)
            self.worker.log_msg.connect(self.log)
            self.worker.finished.connect(self.on_fin)
            self.worker.duration_set.connect(self.set_dur)
            self.worker.position_changed.connect(self.upd_pos)
            self.worker.start()
            self.btn_stop.setEnabled(True); self.slider.setEnabled(True)
            self.btn_play.setText("DURAKLAT")
        else:
            p = self.worker.toggle_pause()
            self.btn_play.setText("OYNAT" if p else "DURAKLAT")

    def set_dur(self, tot):
        self.slider.setRange(0, tot)
        m, s = divmod(tot // 30, 60); self.lbl_tot.setText(f"{m:02d}:{s:02d}")

    def upd_pos(self, cur):
        if not self.is_dragging:
            self.slider.blockSignals(True); self.slider.setValue(cur); self.slider.blockSignals(False)
            m, s = divmod(cur // 30, 60); self.lbl_cur.setText(f"{m:02d}:{s:02d}")

    def on_press(self): self.is_dragging = True
    def on_move(self):
        if self.is_dragging and self.worker:
            self.worker.set_seek(self.slider.value())
    def on_release(self): self.is_dragging = False

    def open_admin(self):
        if AdminDialog(self).exec(): self.log("Veritabani guncellendi.")

    def stop(self): 
        if self.worker: self.worker.kill()
    
    def on_fin(self):
        self.btn_play.setText("OYNAT"); self.btn_play.setEnabled(True); self.btn_stop.setEnabled(False)
        self.slider.setValue(0); self.slider.setEnabled(False); self.vid_lbl.setText("Bitti")

    def upd_img(self, im): self.vid_lbl.setPixmap(QPixmap.fromImage(im).scaled(self.vid_lbl.size(), Qt.AspectRatioMode.KeepAspectRatio))
    
    def upd_alert(self, inf, im, plate_text):
        rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB); h,w,c = rgb.shape
        self.crim_img.setPixmap(QPixmap.fromImage(QImage(rgb.data,w,h,c*w,QImage.Format.Format_RGB888).copy()).scaled(320,200,Qt.AspectRatioMode.KeepAspectRatio))
        
        self.lbl_plate.setText(plate_text)
        self.lbl_owner.setText(f"Sahip: {inf['owner']}")
        self.lbl_stat.setText(f"DURUM: {inf['status']}")
        self.txt_desc.setText(inf['description'])
        
        is_safe = inf['status'] == "TEMIZ"
        color = "#27ae60" if is_safe else "#c0392b"
        self.lbl_stat.setStyleSheet(f"font-size:18px; font-weight:bold; color: {color};")
        
        self.det_list.insertItem(0, f"{plate_text} - {inf['status']}")

    def log(self, t): self.log_box.append(f">> {t}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlateApp()
    window.show()
    sys.exit(app.exec())