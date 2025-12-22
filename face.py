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
DB_PATH = "unified_egm.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FACECAM_DIR = os.path.join(BASE_DIR, "CAMS", "FaceCam")
if not os.path.exists(FACECAM_DIR): os.makedirs(FACECAM_DIR)
def put_text_utf8(img, text, pos, color, font_size=20):
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    try: font = ImageFont.truetype("arial.ttf", font_size)
    except: font = ImageFont.load_default()
    rgb_color = (color[2], color[1], color[0])
    draw.text(pos, text, font=font, fill=rgb_color)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

PROFESSIONAL_THEME = """
QWidget { background-color: #2D2D2D; color: #E0E0E0; font-family: 'Segoe UI', sans-serif; }
QFrame {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 8px; 
    padding: 10px; 
}
QFrame#LeftPanel, QFrame#SidePanel {
    background-color: #1E1E1E;
}
QLabel {
    color: #E0E0E0;
    font-weight: bold;
}
QLabel#VideoLabel {
    background-color: #000000;
    border: 2px solid #1A73E8;
    border-radius: 8px; 
}
QListWidget {
    background-color: #1E1E1E;
    color: #E0E0E0;
    border: 1px solid #333333;
    border-radius: 6px;
    padding: 5px;
}
QListWidget::item {
    border-bottom: 1px solid #333333;
    padding: 5px;
}
QListWidget::item:selected {
    background-color: #1A73E8;
    color: white;
}
QPushButton { 
    background-color: #333333;
    color: white; 
    border-radius: 6px; 
    padding: 12px; 
    font-weight: bold; 
    font-size: 14px;
    border: 1px solid #555555;
}
QPushButton:hover { background-color: #444444; }
QPushButton:pressed { background-color: #222222; }
QPushButton:disabled { background-color: #555555; color: #888888; }
QPushButton#PlayBtn { background-color: #1A73E8; border: none; }
QPushButton#StopBtn { background-color: #D32F2F; border: none; }
QPushButton#AdminBtn { background-color: #FFA000; color: black; border: none; }
QSlider::groove:horizontal { border: 1px solid #999999; height: 8px; background: #333333; margin: 2px 0; border-radius: 4px; }
QSlider::handle:horizontal { background: #1A73E8; border: 1px solid #1A73E8; width: 18px; height: 18px; margin: -6px 0; border-radius: 9px; }
"""


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
        self.kb = {}
        self.metadata = {} # New metadata storage
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
            unique_name, best = "unknown", -1.0
            
            for pn, embs in self.kb.items():
                for e in embs:
                    sim = np.dot(face.embedding, e) / (norm(face.embedding) * norm(e))
                    if sim > best:
                        if sim > SIMILARITY_THRESHOLD: unique_name, best = pn, sim
            
            is_crim, dname = False, "TANIMSIZ"
            info = {"name": unique_name, "full_name": unique_name, "is_criminal": False, "crime_type": "", "display_photo": None}
            
            if unique_name != "unknown" and unique_name in self.metadata:
                meta = self.metadata[unique_name]
                dname = meta["full_name"]
                is_crim = meta["is_criminal"]
                info = {
                    "name": unique_name,
                    "full_name": dname,
                    "is_criminal": is_crim,
                    "crime_type": "", # No crime type in filename anymore
                    "display_photo": meta["display_photo"]
                }
                
                self.person_found.emit(info)
            
            color = (0, 0, 255) if is_crim else (0, 255, 0)
            
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            label = f"{dname} : {'SUCLU' if is_crim else 'TEMIZ'}" if unique_name != 'unknown' else "TANIMSIZ"
            
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
        self.metadata = {}
        print("DEBUG: Loading faces (Name_Surname_Status_Angle approach)...")
        
        persons_dir = os.path.join(BASE_DIR, "CAMS", "Persons")
        if not os.path.exists(persons_dir): return
        
        file_map = {} # Key: Full Name, Value: List of files
        
        for root, dirs, files in os.walk(persons_dir):
            for file in files:
                if file.lower().endswith(('.jpg', '.png', '.jpeg')):
                    path = os.path.join(root, file)
                    stem = os.path.splitext(file)[0]
                    
                    
                    parts = stem.split('_')
                    
                    
                    if len(parts) >= 3:
                        angle_part = parts[-1] 
                        status_part = parts[-2]
                        
                        if status_part in ['0', '1']:
                            name_parts = parts[:-2]
                            full_name = " ".join(name_parts)
                            is_crim = (status_part == '1')
                            
                            if full_name not in file_map:
                                file_map[full_name] = {"files": [], "is_criminal": is_crim, "display_photo": None}
                            
                            file_map[full_name]["files"].append(path)
                            
                            if angle_part == '0':
                                file_map[full_name]["display_photo"] = path
                        else:
                            pass # Unknown format
                    else:
                        pass # Too short

        for name, data in file_map.items():
            key = name
            self.metadata[key] = {
                "full_name": name,
                "is_criminal": data["is_criminal"],
                "display_photo": data["display_photo"] if data["display_photo"] else (data["files"][0] if data["files"] else None)
            }
            self.kb[key] = []
            
            for fpath in data["files"]:
                try:
                    img_array = np.fromfile(fpath, np.uint8)
                    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    if img is not None:
                         faces = app.get(img)
                         if faces:
                             self.kb[key].append(faces[0].embedding)
                except Exception as e:
                    print(f"Error loading {fpath}: {e}")

        print(f"DEBUG: Total identities loaded: {len(self.kb)}")
class GBTApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EGM CANLI TAKİP")
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
        f_lay = QHBoxLayout()
        self.lbl_path = QLabel("Varsayılan Klasör"); self.lbl_path.setStyleSheet("color:gray; font-size:10px;")
        btn_dir = QPushButton("KLASÖR SEÇ"); btn_dir.clicked.connect(self.select_folder)
        btn_dir.setStyleSheet("background-color: #333333; color: white;")
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
        
        display_photo = info.get('display_photo')
        
        icon = QIcon()
        if display_photo and os.path.exists(display_photo):
            try:
                img_array = np.fromfile(display_photo, np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                if img is not None:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    h, w, ch = img.shape
                    qimg = QImage(img.data, w, h, ch * w, QImage.Format.Format_RGB888)
                    icon = QIcon(QPixmap.fromImage(qimg))
            except: pass
            
        item_text = f"{info['full_name']}"
        if info['is_criminal']:
            item_text = f"[SUCLU] {item_text}"
        else:
            item_text = f"[TEMIZ] {item_text}"
            
        item = QListWidgetItem(icon, item_text)
        item.setFont(self.font())
        item.setBackground(QColor("#B71C1C" if info['is_criminal'] else "#2E7D32"))
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