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
QWidget { background-color: 
QFrame
QLabel
QLabel
QPushButton { background-color: 
QPushButton:hover { background-color: 
QComboBox { background-color: 
QComboBox:hover { border: 1px solid 
QLineEdit { background-color: 
QLineEdit:focus { border: 1px solid 
"""
class LoginWorker(QThread):
    change_pixmap = pyqtSignal(QImage)
    status_signal = pyqtSignal(str, str)
    login_success = pyqtSignal(dict) 
    finished = pyqtSignal()
    def __init__(self, camera_source=0):
        super().__init__()
        self.running = True
        self.db = DatabaseManager()
        self.users_data = {} 
        self.camera_source = camera_source
        self.reload_db = True
    def run(self):
        providers = ['CPUExecutionProvider']
        app = FaceAnalysis(name='buffalo_l', providers=providers)
        app.prepare(ctx_id=0, det_size=DET_SIZE)
        src = self.camera_source
        if isinstance(src, str) and src.isdigit():
             src = int(src)
        cap = cv2.VideoCapture(src)
        if isinstance(src, int):
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        prev_time = 0
        self.users_data = self.db.get_all_users_encodings()
        print(f"DEBUG: Loaded {len(self.users_data)} users from DB.")
        while self.running:
            ret, frame = cap.read()
            if not ret or frame is None:
                self.status_signal.emit("Kamera Açılamadı", "red")
                time.sleep(1)
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
            status_color = "
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
                name_display = "Bilinmiyor"
                if match_sicil:
                    user_info = self.users_data[match_sicil]
                    name_display = user_info['name']
                    color = (0, 255, 0)
                    found_user_data = {
                        'sicil': match_sicil,
                        'ad': user_info['name'],
                        'rutbe': user_info['rank']
                    }
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
                cv2.putText(frame, f"{name_display} ({max_score:.2f})", (bbox[0], bbox[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            if found_user_data:
                status_text = f"GİRİŞ BAŞARILI: {found_user_data['ad']}"
                status_color = "
                self.status_signal.emit(status_text, status_color)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888).copy()
                self.change_pixmap.emit(qt_img)
                time.sleep(0.5)
                self.login_success.emit(found_user_data)
                self.running = False
                break
            elif faces:
                status_text = "YETKİSİZ KULLANICI"
                status_color = "
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
        self.setWindowTitle("EGM GÜVENLİ GİRİŞ (TR SUPPORT)")
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
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: 
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
        btn_manual.setStyleSheet("background-color: 
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
        self.dashboard = EGMSistem(user_data)
        self.dashboard.show()
    def closeEvent(self, event):
        self.stop_camera()
        event.accept()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginApp()
    window.show()
    sys.exit(app.exec())
