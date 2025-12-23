import sys
import cv2
import os
import numpy as np
import time
from insightface.app import FaceAnalysis
from numpy.linalg import norm
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QMessageBox, QFrame, QComboBox, QInputDialog, QLineEdit)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from database_manager import DatabaseManager
SIMILARITY_THRESHOLD = 0.40
DET_SIZE = (640, 640)
PROFESSIONAL_THEME = """
QWidget { background-color: #2b2b2b; color: #ffffff; font-family: 'Segoe UI', sans-serif; }
QFrame#MainFrame { background-color: #3d3d3d; border-radius: 15px; border: 1px solid #555555; }
QLabel { color: #ffffff; }
QLabel#VideoLabel { background-color: #000000; border-radius: 10px; border: 2px solid #1A73E8; }
QLabel#StatusLabel { font-size: 16px; font-weight: bold; padding: 10px; }
QPushButton { background-color: #1A73E8; color: white; border-radius: 6px; padding: 10px 20px; font-weight: bold; }
QPushButton:hover { background-color: #1557B0; }
QComboBox { background-color: #3d3d3d; color: #ffffff; border: 1px solid #555555; padding: 5px; border-radius: 4px; }
QComboBox:hover { border: 1px solid #1A73E8; }
QLineEdit { background-color: #3d3d3d; color: #ffffff; border: 1px solid #555555; padding: 8px; border-radius: 4px; }
QLineEdit:focus { border: 1px solid #1A73E8; }
QListWidget { background-color: #3d3d3d; color: #ffffff; border: 1px solid #555555; border-radius: 4px; }
"""
class LoginWorker(QThread):
    change_pixmap = pyqtSignal(QImage)
    status_signal = pyqtSignal(str, str)
    login_success = pyqtSignal(dict) 
    finished = pyqtSignal()

    def __init__(self, camera_source=0):
        super().__init__()
        self.running = True
        self.camera_source = camera_source
        self.users_data = {} 
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

    def run(self):
        providers = ['DmlExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider']
        app = FaceAnalysis(name='buffalo_l', providers=providers)
        app.prepare(ctx_id=0, det_size=DET_SIZE)
        
        src = self.camera_source
        if isinstance(src, str) and src.isdigit():
             src = int(src)
        cap = cv2.VideoCapture(src)
        if isinstance(src, int):
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            
        self.users_data = {}
        users_dir = os.path.join(self.base_dir, "CAMS", "Users")
        
        print("DEBUG: Loading users from CAMS/Users with Unicode Support...")
        if os.path.exists(users_dir):
            for item in os.listdir(users_dir):
                path = os.path.join(users_dir, item)
                img_paths = []
                
                if os.path.isdir(path):
                    for f in os.listdir(path):
                        if f.lower().endswith(('.jpg', '.png', '.jpeg')):
                            img_paths.append(os.path.join(path, f))
                elif os.path.isfile(path) and item.lower().endswith(('.jpg', '.png', '.jpeg')):
                    img_paths.append(path)
                
                for ip in img_paths:
                    try:
                        img_array = np.fromfile(ip, np.uint8)
                        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                        
                        if img is not None:
                            faces_scan = app.get(img)
                            if faces_scan:
                                user_name = item
                                if os.path.isfile(path):
                                    user_name = os.path.splitext(item)[0].replace("_", " ")
                                
                                sicil = f"USER_{user_name}"
                                
                                self.users_data[sicil] = {
                                    'name': user_name,
                                    'rank': 'Personel',
                                    'encoding': faces_scan[0].embedding
                                }
                                print(f"DEBUG: Loaded user: {user_name}")
                    except Exception as e:
                        print(f"DEBUG: Error loading {ip}: {e}")

        print(f"DEBUG: Total users loaded: {len(self.users_data)}")

        while self.running:
            ret, frame = cap.read()
            if not ret or frame is None:
                self.status_signal.emit("Kamera Açılamadı", "red")
                time.sleep(1)
                continue
            
            if frame.shape[1] > 1280:
                frame = cv2.resize(frame, (1280, 720))
                
            try: faces = app.get(frame)
            except: faces = []
            
            status_text = "Yüz Aranıyor..."
            status_color = "orange"
            found_user_data = None
            
            for face in faces:
                bbox = face.bbox.astype(int)
                max_score = 0
                match_sicil = None
                
                for sicil, data in self.users_data.items():
                    db_emb = data['encoding']
                    sim = np.dot(face.embedding, db_emb) / (norm(face.embedding) * norm(db_emb))
                    if sim > max_score:
                        max_score = sim
                        if sim > SIMILARITY_THRESHOLD:
                            match_sicil = sicil
                
                color = (0, 0, 255)
                if match_sicil:
                    user_info = self.users_data[match_sicil]
                    color = (255, 255, 255) 
                    found_user_data = {
                        'sicil': match_sicil,
                        'ad': user_info['name'],
                        'rutbe': user_info['rank']
                    }
                
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)

            if found_user_data:
                status_text = f"Hoşgeldiniz, {found_user_data['ad']}"
                status_color = "#4CAF50"
                self.status_signal.emit(status_text, status_color)
                
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888).copy()
                self.change_pixmap.emit(qt_img)
                
                time.sleep(0.3)
                self.login_success.emit(found_user_data)
                self.running = False
                break
            elif faces:
                status_text = "Tanınmayan Kullanıcı"
                status_color = "#F44336"
            
            self.status_signal.emit(status_text, status_color)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888).copy()
            self.change_pixmap.emit(qt_img)
            
        cap.release()
        self.finished.emit()

    def stop(self):
        self.running = False
        self.wait()
class LoginApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EGM CANLI TAKİP")
        self.setWindowIcon(QtGui.QIcon("logo.png"))
        self.setStyleSheet(PROFESSIONAL_THEME)
        self.resize(900, 750)
        self.worker = None
        self.available_cams = self.check_cameras()
        self.init_ui()
        self.start_camera(0) 
    def check_cameras(self):
        cams = []
        for i in range(3):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if not cap.isOpened(): cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret: cams.append(i)
                cap.release()
        return cams
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        frame = QFrame(); frame.setObjectName("MainFrame"); layout = QVBoxLayout(frame)
        title = QLabel("YÜZ TANIMA & SİCİL GİRİŞ SİSTEMİ"); title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1A73E8;")
        layout.addWidget(title)
        h_cam = QHBoxLayout()
        h_cam.addWidget(QLabel("Kamera Kaynağı:"))
        self.combo_cam = QComboBox()
        for i in self.available_cams:
            self.combo_cam.addItem(f"Kamera {i}", i)
        self.combo_cam.addItem("IP Kamera (URL)", "ip")
        self.combo_cam.currentIndexChanged.connect(self.change_camera)
        h_cam.addWidget(self.combo_cam)
        h_cam.addStretch()
        layout.addLayout(h_cam)
        self.vid_lbl = QLabel("Video Başlatılıyor..."); self.vid_lbl.setObjectName("VideoLabel")
        self.vid_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter); self.vid_lbl.setFixedHeight(480)
        layout.addWidget(self.vid_lbl)
        manual_layout = QHBoxLayout()
        manual_layout.addWidget(QLabel("Manuel Giriş Sicil No:"))
        self.sicil_input = QLineEdit()
        self.sicil_input.setPlaceholderText("Sicil Numaranızı Giriniz...")
        manual_layout.addWidget(self.sicil_input)
        btn_manual = QPushButton("GİRİŞ YAP")
        btn_manual.clicked.connect(self.manual_login)
        btn_manual.setStyleSheet("background-color: #1A73E8; color: white; font-weight: bold;")
        manual_layout.addWidget(btn_manual)
        layout.addLayout(manual_layout)
        self.lbl_status = QLabel("SİSTEM HAZIR"); self.lbl_status.setObjectName("StatusLabel")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_status)
        btn_layout = QHBoxLayout()
        btn_close = QPushButton("ÇIKIŞ"); btn_close.clicked.connect(self.close)
        btn_layout.addStretch(); btn_layout.addWidget(btn_close); btn_layout.addStretch()
        layout.addLayout(btn_layout)
        main_layout.addWidget(frame)
    def change_camera(self, idx):
        data = self.combo_cam.currentData()
        if data == "ip":
            url, ok = QInputDialog.getText(self, "IP Kamera", "RTSP/HTTP Adresi:")
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
        self.worker.login_success.connect(self.on_login_success)
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
    def manual_login(self):
        sicil = self.sicil_input.text().strip()
        if not sicil:
            QMessageBox.warning(self, "Uyarı", "Lütfen sicil numarasını giriniz.")
            return
        db = DatabaseManager()
        user_row = db.get_user_by_sicil(sicil) 
        if user_row:
            user_data = {
                'sicil': user_row[1],
                'ad': user_row[2],
                'rutbe': user_row[3],
                'gorev': user_row[4]
            }
            self.on_login_success(user_data)
        else:
            QMessageBox.critical(self, "Hata", "Bu sicil numarası ile kayıt bulunamadı.")
    def on_login_success(self, user_data):
        self.stop_camera()
        print(f"Login Success: {user_data}")
        self.close()
        from arayuz import EGMSistem
        self.dashboard = EGMSistem(user_data['ad'])
        self.dashboard.show()
    def closeEvent(self, event):
        self.stop_camera()
        event.accept()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginApp()
    window.show()
    sys.exit(app.exec())
