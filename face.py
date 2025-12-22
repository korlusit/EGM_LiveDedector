import sys
import cv2
import os
import shutil
import sqlite3
import numpy as np
import random
import unicodedata
import onnxruntime
from insightface.app import FaceAnalysis
from numpy.linalg import norm
from PIL import Image, ImageDraw, ImageFont 

from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QTextEdit, QListWidget, QListWidgetItem,
                             QFrame, QSizePolicy, QFileDialog, QMessageBox, 
                             QComboBox, QRadioButton, QButtonGroup, QDialog, QSlider,
                             QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView)
from PyQt6.QtGui import QImage, QPixmap, QIcon, QImageReader
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMutex, QSize

SIMILARITY_THRESHOLD = 0.45
DET_SIZE = (640, 640)
DB_PATH = "egm_database.db"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PERSONS_DIR = os.path.join(BASE_DIR, "CAMS", "Persons") 
FACECAM_DIR = os.path.join(BASE_DIR, "CAMS", "FaceCam")

if not os.path.exists(PERSONS_DIR): os.makedirs(PERSONS_DIR)
if not os.path.exists(FACECAM_DIR): os.makedirs(FACECAM_DIR)

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
    c.execute("""CREATE TABLE IF NOT EXISTS persons (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, full_name TEXT,
        is_criminal INTEGER, crime_type TEXT, description TEXT)""")
    conn.commit(); conn.close()

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

QListWidget {
    background-color: #121212;
    color: #e0e0e0;
    border: 1px solid #333;
    border-radius: 6px;
    padding: 5px;
}
QListWidget::item {
    border-bottom: 1px solid #222;
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
    def get_person_info(self, name):
        self.mutex.lock(); info = None
        try:
            conn = sqlite3.connect(self.db_path); c = conn.cursor()
            c.execute("SELECT full_name, is_criminal, crime_type, description FROM persons WHERE name=?", (name.lower(),))
            r = c.fetchone(); conn.close()
            if r: 
                info = {"name": name, "full_name": r[0], "is_criminal": bool(r[1]), "crime_type": r[2], "description": r[3]}
        except: pass
        self.mutex.unlock(); return info

    def get_all_persons(self):
        self.mutex.lock(); data = []
        try:
            conn = sqlite3.connect(self.db_path); c = conn.cursor()
            c.execute("SELECT name, full_name, crime_type, description FROM persons")
            data = c.fetchall(); conn.close()
        except: pass
        self.mutex.unlock(); return data

    def delete_person(self, name):
        self.mutex.lock()
        try:
            conn = sqlite3.connect(self.db_path); c = conn.cursor()
            c.execute("DELETE FROM persons WHERE name=?", (name,))
            conn.commit(); conn.close()
            # Delete associated images
            for f in os.listdir(PERSONS_DIR):
                if f.startswith(name + "_"):
                    try: os.remove(os.path.join(PERSONS_DIR, f))
                    except: pass
        except: pass
        self.mutex.unlock()

class RecordsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("KAYITLARI YONET")
        self.resize(800, 600)
        self.setStyleSheet(PROFESSIONAL_THEME)
        self.db = DatabaseHandler(DB_PATH)
        self.init_ui()

    def init_ui(self):
        l = QVBoxLayout(self)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Sistem ID", "Ad Soyad", "Suc Tipi", "Aciklama"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        l.addWidget(self.table)
        
        btn_del = QPushButton("SECILI KAYDI SIL")
        btn_del.clicked.connect(self.delete_rec)
        btn_del.setStyleSheet("background-color: #dc3545;")
        l.addWidget(btn_del)
        
        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        data = self.db.get_all_persons()
        for i, row in enumerate(data):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(row[0]))
            self.table.setItem(i, 1, QTableWidgetItem(row[1]))
            self.table.setItem(i, 2, QTableWidgetItem(row[2]))
            self.table.setItem(i, 3, QTableWidgetItem(row[3]))

    def delete_rec(self):
        r = self.table.currentRow()
        if r < 0: return
        name = self.table.item(r, 0).text()
        res = QMessageBox.question(self, "Onay", f"{name} kaydini silmek istediginize emin misiniz?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if res == QMessageBox.StandardButton.Yes:
            self.db.delete_person(name)
            self.load_data()
            QMessageBox.information(self, "Bilgi", "Kayit silindi.")

class AdminDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("EGM VERI GIRISI") 
        self.resize(600, 700)
        self.setStyleSheet(PROFESSIONAL_THEME)
        self.selected_files = []
        self.init_ui()

    def init_ui(self):
        l = QVBoxLayout(self)
        l.addWidget(QLabel("Ad Soyad:")); self.inp_fn = QTextEdit(); self.inp_fn.setFixedHeight(30); l.addWidget(self.inp_fn)
        # Sistem ID alani kaldirildi, otomatik uretilecek.
        
        self.r_crim = QRadioButton("SUCLU"); self.r_inno = QRadioButton("TEMIZ"); self.r_inno.setChecked(True)
        l.addWidget(self.r_crim); l.addWidget(self.r_inno)
        
        self.combo = QComboBox(); self.combo.addItems(["Yok", "Hirsizlik", "Gasp", "Teror", "Diger"]); self.combo.setEditable(True); l.addWidget(self.combo)
        self.inp_desc = QTextEdit(); self.inp_desc.setFixedHeight(60); l.addWidget(self.inp_desc)
        
        self.lbl_cnt = QLabel("0 Secildi"); l.addWidget(self.lbl_cnt)
        btn_sel = QPushButton("FOTO SEC"); btn_sel.clicked.connect(self.sel_phot); l.addWidget(btn_sel)
        btn_sav = QPushButton("KAYDET"); btn_sav.clicked.connect(self.save); l.addWidget(btn_sav)

    def normalize_chars(self, text):
        # Basit Turkce karakter donusumu
        replacements = {
            'ğ': 'g', 'Ğ': 'g', 'ü': 'u', 'Ü': 'u', 'ş': 's', 'Ş': 's',
            'ı': 'i', 'İ': 'i', 'ö': 'o', 'Ö': 'o', 'ç': 'c', 'Ç': 'c'
        }
        for tr, en in replacements.items():
            text = text.replace(tr, en)
        
        # ASCII disindaki karakterleri temizle ve kucuk harfe cevir
        text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
        return "".join([c if c.isalnum() else "_" for c in text]).lower()

    def save(self):
        fn = self.inp_fn.toPlainText().strip()
        if not fn:
            QMessageBox.warning(self, "Eksik Bilgi", "Lutfen Ad Soyad giriniz."); return
        if not self.selected_files:
            QMessageBox.warning(self, "Eksik Bilgi", "Lutfen en az bir fotograf seciniz."); return

        # Otomatik ID Olusturma
        base_id = self.normalize_chars(fn)
        rand_suffix = random.randint(1000, 9999)
        sn = f"{base_id}_{rand_suffix}"

        isc = 1 if self.r_crim.isChecked() else 0
        
        try:
            for i, fp in enumerate(self.selected_files):
                shutil.copy(fp, os.path.join(PERSONS_DIR, f"{sn}_{i+1}{os.path.splitext(fp)[1]}"))
            
            conn = sqlite3.connect(DB_PATH); c = conn.cursor()
            # Onceki kaydi silmeye gerek yok cunku ID unikal uretiliyor
            c.execute("INSERT INTO persons (name, full_name, is_criminal, crime_type, description) VALUES (?,?,?,?,?)",
                      (sn, fn, isc, self.combo.currentText(), self.inp_desc.toPlainText()))
            conn.commit(); conn.close(); 
            QMessageBox.information(self, "Basarili", f"Kayit eklendi.\nSistem ID: {sn}")
            self.accept()
        except Exception as e: QMessageBox.critical(self, "Hata", str(e))

    def sel_phot(self):
        fs, _ = QFileDialog.getOpenFileNames(self, "Sec", "", "Resimler (*.jpg *.png)")
        if fs: self.selected_files = fs; self.lbl_cnt.setText(f"{len(fs)} Secildi")



class VideoWorker(QThread):
    change_pixmap = pyqtSignal(QImage)
    person_found = pyqtSignal(dict) 
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
        self.kb = {}
        self.reload = False

    def toggle_pause(self): self.paused = not self.paused; return self.paused
    def set_seek(self, frame): self.seek_req = frame
    def trigger_reload(self): self.reload = True
    def kill(self): self.running = False; self.wait()

    def run(self):
        self.log_msg.emit(f"Baslatiliyor: {os.path.basename(self.vpath)}")
        try:
            providers = ['DmlExecutionProvider', 'CPUExecutionProvider']
            app = FaceAnalysis(name='buffalo_l', providers=providers)
            app.prepare(ctx_id=0, det_size=DET_SIZE)
            self.load_db(app)
            
            cap = cv2.VideoCapture(self.vpath)
            if not cap.isOpened():
                self.log_msg.emit("HATA: Video dosyasi acilamadi!"); self.finished.emit(); return

            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.duration_set.emit(total)

            while self.running:
                if self.seek_req != -1:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, self.seek_req)
                    ret, frame = cap.read()
                    if ret: self.process(frame, app, cap.get(cv2.CAP_PROP_POS_FRAMES))
                    self.seek_req = -1
                    if self.paused: self.msleep(50); continue 

                if self.paused: self.msleep(50); continue
                if self.reload: self.load_db(app); self.reload = False
                
                ret, frame = cap.read()
                if not ret: self.log_msg.emit("Video Bitti."); self.running = False; break
                
                self.process(frame, app, cap.get(cv2.CAP_PROP_POS_FRAMES))

            cap.release(); self.finished.emit()
        except Exception as e: self.log_msg.emit(f"HATA: {e}"); self.finished.emit()

    def process(self, frame, app, pos):
        self.position_changed.emit(int(pos))
        try: faces = app.get(frame)
        except: faces = []

        for face in faces:
            bbox = face.bbox.astype(int)
            name, best = "unknown", -1.0
            for pn, embs in self.kb.items():
                for e in embs:
                    sim = np.dot(face.embedding, e) / (norm(face.embedding) * norm(e))
                    if sim > best and sim > SIMILARITY_THRESHOLD: name, best = pn, sim
            
            is_crim, dname = False, "TANIMSIZ"
            info = {"name": name, "full_name": name, "is_criminal": False, "crime_type": "Bilinmiyor", "description": ""}
            
            if name != "unknown":
                db_info = self.db.get_person_info(name)
                if db_info: 
                    info = db_info
                    dname, is_crim = info['full_name'], info['is_criminal']
                else:
                    dname = name
                
                self.person_found.emit(info)

            color = (0, 0, 255) if is_crim else (0, 255, 0)
            
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            label = f"SUCLU %{int(best*100)}" if is_crim else dname
            if label:
                cv2.rectangle(frame, (bbox[0], bbox[1]-30), (bbox[0]+200, bbox[1]), color, -1)
                frame = put_text_utf8(frame, label, (bbox[0]+5, bbox[1]-25), (255,255,255))

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888).copy()
        self.change_pixmap.emit(qt_img)

    def load_db(self, app):
        self.kb = {}
        if not os.path.exists(PERSONS_DIR): return
        for f in os.listdir(PERSONS_DIR):
            if f.lower().endswith(('.jpg', '.png', '.jpeg')):
                # ID format: name_surname_id_counter.ext (e.g. ahmet_calik_1234_1.jpg)
                # We need to remove the last part (counter) and extension to get the ID
                base_name = os.path.splitext(f)[0]
                parts = base_name.split('_')
                if len(parts) > 1:
                    rn = "_".join(parts[:-1]).lower()
                else:
                    rn = base_name.lower()

                img = cv2.imread(os.path.join(PERSONS_DIR, f))
                if img is not None:
                    faces = app.get(img)
                    if faces:
                        if rn not in self.kb: self.kb[rn] = []
                        self.kb[rn].append(faces[0].embedding)

class GBTApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EGM AKILLI GBT SISTEMI (MULTI-DETECT)")
        self.resize(1500, 950)
        self.setStyleSheet(PROFESSIONAL_THEME)
        self.curr_vid = None
        self.is_dragging = False
        self.worker = None 
        self.detected_ids = set()
        self.video_dir = FACECAM_DIR
        self.init_ui()
        self.load_files()

    def init_ui(self):
        layout = QHBoxLayout(self)
        
        left_frame = QFrame(); left_frame.setObjectName("LeftPanel"); left_frame.setFixedWidth(280)
        left = QVBoxLayout(left_frame)
        
        btn_adm = QPushButton("ADMIN PANELI"); btn_adm.clicked.connect(self.open_admin); btn_adm.setFixedHeight(50); btn_adm.setObjectName("AdminBtn")
        left.addWidget(btn_adm)
        
        btn_recs = QPushButton("KAYITLARI YONET"); btn_recs.clicked.connect(self.open_records); btn_recs.setFixedHeight(40); btn_recs.setStyleSheet("background-color: #555;")
        left.addWidget(btn_recs)
        
        # Klasör Seçimi
        f_lay = QHBoxLayout()
        self.lbl_path = QLabel("Varsayılan Klasör"); self.lbl_path.setStyleSheet("color:gray; font-size:10px;")
        btn_dir = QPushButton("KLASÖR SEÇ"); btn_dir.clicked.connect(self.select_folder)
        btn_dir.setStyleSheet("background-color:#444; font-size:11px; padding: 5px;")
        f_lay.addWidget(btn_dir)
        left.addLayout(f_lay); left.addWidget(self.lbl_path)

        left.addWidget(QLabel("KAYITLAR"))
        self.vlist = QListWidget(); self.vlist.itemClicked.connect(self.sel_vid); left.addWidget(self.vlist)
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
        right.addWidget(QLabel("ANLIK TESPITLER"))
        
        self.det_list = QListWidget()
        self.det_list.setIconSize(QSize(80, 80))
        right.addWidget(self.det_list)
        
        btn_clr = QPushButton("LISTEYI TEMIZLE")
        btn_clr.clicked.connect(self.clear_detections)
        right.addWidget(btn_clr)

        layout.addWidget(right_frame)

    def select_folder(self):
        d = QFileDialog.getExistingDirectory(self, "Video Klasörü Seç", self.video_dir)
        if d:
            self.video_dir = d
            self.lbl_path.setText(os.path.basename(d))
            self.load_files()

    def load_files(self):
        self.vlist.clear()
        if not os.path.exists(self.video_dir): os.makedirs(self.video_dir)
        fs = [f for f in os.listdir(self.video_dir) if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.wmv'))]
        for f in fs: self.vlist.addItem(f)

    def sel_vid(self, item): 
        self.curr_vid = os.path.join(self.video_dir, item.text())
        self.btn_play.setEnabled(True)
        self.clear_detections()

    def toggle(self):
        if not self.worker or not self.worker.isRunning():
            self.worker = VideoWorker(self.curr_vid)
            self.worker.change_pixmap.connect(self.upd_img)
            self.worker.person_found.connect(self.add_detection)
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

    def add_detection(self, info):
        pid = info['name']
        if pid in self.detected_ids: return 
        
        self.detected_ids.add(pid)
        
        reg_img_path = None
        for f in os.listdir(PERSONS_DIR):
            if f.startswith(pid + "_") and f.lower().endswith(('jpg','png','jpeg')):
                reg_img_path = os.path.join(PERSONS_DIR, f)
                break
        
        icon = QIcon()
        if reg_img_path:
            reader = QImageReader(reg_img_path)
            reader.setAutoTransform(True)
            img = reader.read()
            if not img.isNull():
                icon = QIcon(QPixmap.fromImage(img))
            else:
                icon = QIcon(reg_img_path)
        
        item_text = f"{info['full_name']}\n{info['crime_type']}\n{info['description']}"
        if info['is_criminal']:
            item_text = f"[SUCLU] {item_text}"
        else:
            item_text = f"[TEMIZ] {item_text}"
            
        item = QListWidgetItem(icon, item_text)
        item.setFont(self.font())
        
        item.setBackground(QColor("#350000") if info['is_criminal'] else QColor("#002200"))
        item.setForeground(QColor("white"))
        
        self.det_list.insertItem(0, item)

    def clear_detections(self):
        self.det_list.clear()
        self.detected_ids.clear()

    def set_dur(self, tot):
        self.slider.setRange(0, tot)
        m, s = divmod(tot // 30, 60); self.lbl_tot.setText(f"{m:02d}:{s:02d}")

    def upd_pos(self, cur):
        if not self.is_dragging:
            self.slider.blockSignals(True); self.slider.setValue(cur); self.slider.blockSignals(False)
            m, s = divmod(cur // 30, 60); self.lbl_cur.setText(f"{m:02d}:{s:02d}")

    def on_press(self): self.is_dragging = True
    def on_move(self):
        if self.is_dragging and self.worker: self.worker.set_seek(self.slider.value())
    def on_release(self): self.is_dragging = False

    def open_admin(self):
        if self.worker and self.worker.isRunning():
            self.worker.paused = True; self.btn_play.setText("OYNAT")
        if AdminDialog(self).exec() and self.worker: self.worker.trigger_reload()

    def open_records(self):
        RecordsDialog(self).exec()
        if self.worker: self.worker.trigger_reload()

    def stop(self): 
        if self.worker: self.worker.kill()
    
    def on_fin(self):
        self.btn_play.setText("OYNAT"); self.btn_play.setEnabled(True); self.btn_stop.setEnabled(False)
        self.slider.setValue(0); self.slider.setEnabled(False); self.vid_lbl.setText("Bitti")

    def upd_img(self, im): self.vid_lbl.setPixmap(QPixmap.fromImage(im).scaled(self.vid_lbl.size(), Qt.AspectRatioMode.KeepAspectRatio))
    def log(self, t): self.log_box.append(f">> {t}")

if __name__ == "__main__":
    from PyQt6.QtGui import QColor 
    app = QApplication(sys.argv)
    window = GBTApp()
    window.show()
    sys.exit(app.exec())