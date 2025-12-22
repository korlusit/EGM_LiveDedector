import sys
import cv2
import os
import numpy as np
import time
from insightface.app import FaceAnalysis
from numpy.linalg import norm
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QMessageBox, QFrame, QComboBox, QInputDialog)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, QThread, pyqtSignal

SIMILARITY_THRESHOLD = 0.50
DET_SIZE = (640, 640)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_DIR = os.path.join(BASE_DIR, "CAMS", "Users")

if not os.path.exists(USERS_DIR):
    os.makedirs(USERS_DIR)

PROFESSIONAL_THEME = """
QWidget { background-color: #050505; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
QFrame#MainFrame { background-color: #121212; border: 1px solid #222; border-radius: 12px; padding: 20px; }
QLabel#VideoLabel { background-color: #000; border: 2px solid #333; border-radius: 8px; }
QLabel#StatusLabel { font-size: 24px; font-weight: bold; padding: 10px; }
QPushButton { background-color: #c0392b; color: white; border-radius: 6px; padding: 12px; font-weight: bold; border: none; min-width: 120px; }
QPushButton:hover { background-color: #e74c3c; }
QComboBox { background-color: #222; color: white; padding: 8px; border: 1px solid #555; border-radius: 5px; min-width: 150px; }
QComboBox:hover { border: 1px solid #0a84ff; }
"""

class LoginWorker(QThread):
    change_pixmap = pyqtSignal(QImage)
    status_signal = pyqtSignal(str, str)
    finished = pyqtSignal()
    
    def __init__(self, camera_source=0):
        super().__init__()
        self.running = True
        self.users = {}
        self.reload_db = True
        self.camera_source = camera_source

    def run(self):
        providers = ['CUDAExecutionProvider', 'DmlExecutionProvider', 'CPUExecutionProvider']
        app = FaceAnalysis(name='buffalo_l', providers=providers)
        app.prepare(ctx_id=0, det_size=DET_SIZE)
        
        src = self.camera_source
        if isinstance(src, str) and src.isdigit():
             src = int(src)
             
        cap = cv2.VideoCapture(src)
        if isinstance(src, int):
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        
        prev_time = 0
        
        while self.running:
            if self.reload_db:
                self.load_users(app)
                print(f"DEBUG: Loaded users: {len(self.users)}")
                for k, v in self.users.items():
                    print(f"DEBUG: User {k} has {len(v)} embeddings")
                self.reload_db = False

            ret, frame = cap.read()
            if not ret or frame is None:
                self.status_signal.emit("Kamera Açılamadı", "red")
                time.sleep(1)
                if isinstance(src, str):
                    cap.release()
                    time.sleep(1)
                    cap = cv2.VideoCapture(src)
                continue
            
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time) if prev_time > 0 else 0
            prev_time = curr_time

            cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if frame.shape[1] > 1280:
                frame = cv2.resize(frame, (1280, 720))

            try:
                faces = app.get(frame)
            except:
                faces = []

            status_text = "Yüz Aranıyor..."
            status_color = "#f39c12"
            found_user = None

            for face in faces:
                bbox = face.bbox.astype(int)
                max_score = 0
                match_name = "Bilinmiyor"
                
                for uname, uembs in self.users.items():
                    for emb in uembs:
                        sim = np.dot(face.embedding, emb) / (norm(face.embedding) * norm(emb))
                        if sim > max_score:
                            max_score = sim
                            if sim > SIMILARITY_THRESHOLD:
                                match_name = uname
                
                color = (0, 0, 255)
                if match_name != "Bilinmiyor":
                    color = (0, 255, 0)
                    found_user = match_name
                
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
                cv2.putText(frame, match_name, (bbox[0], bbox[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            if found_user:
                status_text = f"GİRİŞ BAŞARILI: {found_user}"
                status_color = "#27ae60"
            elif faces:
                status_text = "YETKİSİZ KULLANICI"
                status_color = "#c0392b"

            self.status_signal.emit(status_text, status_color)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888).copy()
            self.change_pixmap.emit(qt_img)

        cap.release()
        self.finished.emit()

    def load_users(self, app):
        self.users = {}
        if not os.path.exists(USERS_DIR): return
        
        items = os.listdir(USERS_DIR)
        
        for item in items:
            path = os.path.join(USERS_DIR, item)
            
            def read_image_unicode(file_path):
                try:
                    with open(file_path, "rb") as f:
                        data = f.read()
                    data_arr = np.frombuffer(data, dtype=np.uint8)
                    return cv2.imdecode(data_arr, cv2.IMREAD_COLOR)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    return None

            if os.path.isdir(path):
                name = item
                if name not in self.users: self.users[name] = []
                for img_file in os.listdir(path):
                    if img_file.lower().endswith(('.jpg', '.png', '.jpeg')):
                        img = read_image_unicode(os.path.join(path, img_file))
                        if img is not None:
                            faces = app.get(img)
                            if faces: self.users[name].append(faces[0].embedding)
            elif os.path.isfile(path) and item.lower().endswith(('.jpg', '.png', '.jpeg')):
                name = item.split('_')[0]
                img = read_image_unicode(path)
                if img is not None:
                    faces = app.get(img)
                    if faces:
                        if name not in self.users: self.users[name] = []
                        self.users[name].append(faces[0].embedding)

    def stop(self):
        self.running = False
        self.wait()

class LoginApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EGM GÜVENLİ GİRİŞ (TR SUPPORT)")
        self.setStyleSheet(PROFESSIONAL_THEME)
        self.resize(800, 700)
        self.worker = None
        self.available_cams = self.check_cameras()
        self.init_ui()
        self.start_camera(0) 

    def check_cameras(self):
        cams = []
        for i in range(5):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if not cap.isOpened():
                cap = cv2.VideoCapture(i)
            
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    cams.append(i)
                cap.release()
        return cams

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        frame = QFrame(); frame.setObjectName("MainFrame"); layout = QVBoxLayout(frame)
        
        title = QLabel("YÜZ TANIMA SİSTEMİ"); title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #3498db; margin-bottom: 10px;")
        layout.addWidget(title)
        
        h_cam = QHBoxLayout()
        h_cam.addWidget(QLabel("Kaynak:"))
        self.combo_cam = QComboBox()
        for i in self.available_cams:
            self.combo_cam.addItem(f"Kamera {i}", i)
        self.combo_cam.addItem("IP Kamera (URL)", "ip")
            
        self.combo_cam.currentIndexChanged.connect(self.change_camera)
        h_cam.addWidget(self.combo_cam)
        h_cam.addStretch()
        layout.addLayout(h_cam)
        
        self.vid_lbl = QLabel("Başlatılıyor..."); self.vid_lbl.setObjectName("VideoLabel")
        self.vid_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter); self.vid_lbl.setFixedHeight(480)
        layout.addWidget(self.vid_lbl)
        
        self.lbl_status = QLabel("BEKLENİYOR..."); self.lbl_status.setObjectName("StatusLabel")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_status)
        
        btn_layout = QHBoxLayout()
        btn_close = QPushButton("KAPAT"); btn_close.clicked.connect(self.close)
        btn_layout.addStretch(); btn_layout.addWidget(btn_close); btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        main_layout.addWidget(frame)

    def change_camera(self, idx):
        data = self.combo_cam.currentData()
        if data == "ip":
            url, ok = QInputDialog.getText(self, "IP Kamera", "RTSP/HTTP Bağlantı Adresi Giriniz:\n(Örn: http://192.168.1.20:8080/video)")
            if ok and url:
                self.stop_camera()
                self.start_camera(url)
            else:
                self.combo_cam.setCurrentIndex(0) 
        else:
            self.stop_camera()
            self.start_camera(data)

    def start_camera(self, cam_idx):
        if self.worker is not None: return
        self.worker = LoginWorker(cam_idx)
        self.worker.change_pixmap.connect(self.update_image)
        self.worker.status_signal.connect(self.update_status)
        self.worker.start()

    def stop_camera(self):
        if self.worker:
            self.worker.stop()
            self.worker = None

    def update_image(self, img):
        self.vid_lbl.setPixmap(QPixmap.fromImage(img).scaled(
            self.vid_lbl.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def update_status(self, text, color_name):
        self.lbl_status.setText(text)
        self.lbl_status.setStyleSheet(f"color: {color_name};")

    def closeEvent(self, event):
        self.stop_camera()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginApp()
    window.show()
    sys.exit(app.exec())
