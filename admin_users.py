import sys
import cv2
import os
import shutil
import numpy as np
import time
import math
from insightface.app import FaceAnalysis
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QListWidget, QFrame, 
                             QLineEdit, QMessageBox, QSplitter, QProgressBar, QComboBox, QInputDialog)
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from database_manager import DatabaseManager
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_DIR = os.path.join(BASE_DIR, "CAMS", "Users")
if not os.path.exists(USERS_DIR): os.makedirs(USERS_DIR)
PROFESSIONAL_THEME = """
QWidget { background-color: #2D2D2D; color: #E0E0E0; font-family: 'Segoe UI', sans-serif; }
QFrame#SideBar { background-color: #1E1E1E; border-right: 1px solid #333333; }
QListWidget { background-color: #1E1E1E; border: none; outline: none; }
QListWidget::item { padding: 8px; border-radius: 6px; color: #E0E0E0; }
QListWidget::item:selected { background-color: #1A73E8; color: white; }
QLabel { color: #E0E0E0; }
QLabel#Header { font-size: 18px; font-weight: bold; padding: 10px; color: #1A73E8; }
QLabel#Instruction { font-size: 16px; font-weight: bold; color: #4CAF50; margin-bottom: 10px; }
QLineEdit { background-color: #333333; border: 1px solid #555555; padding: 8px; border-radius: 4px; color: white; }
QPushButton { background-color: #333333; color: white; border-radius: 6px; padding: 10px; border: 1px solid #555555; }
QPushButton:hover { background-color: #444444; }
QPushButton#PrimaryBtn { background-color: #1A73E8; border: none; font-weight: bold; }
QPushButton#PrimaryBtn:hover { background-color: #1557B0; }
QPushButton#DeleteBtn { background-color: #D32F2F; border: none; }
QPushButton#DeleteBtn:hover { background-color: #B71C1C; }
QProgressBar { border: none; background-color: #333333; height: 10px; border-radius: 5px; text-align: center; }
QProgressBar::chunk { background-color: #4CAF50; border-radius: 5px; }
QComboBox { background-color: #333333; border: 1px solid #555555; padding: 5px; border-radius: 4px; color: white; }
QComboBox:hover { border: 1px solid #1A73E8; }
"""
POSES = [
    ("CENTER", "Yüzünü Merkeze Tut", (-15, 15), (-15, 15)),
    ("RIGHT", "Kafanı Sağa Çevir", (-90, -20), (-25, 25)),
    ("LEFT", "Kafanı Sola Çevir", (20, 90), (-25, 25)),
    ("UP", "Yukarı Bak", (-25, 25), (10, 90)),
    ("DOWN", "Aşağı Bak", (-25, 25), (-90, -5))
]
FRAMES_REQUIRED = 20
VISUAL_RADIUS = 220 
CENTER_TOLERANCE = 250 
def estimate_pose(kps):
    if kps is None or len(kps) < 5: return 0, 0
    lm = kps
    eye_left = lm[0]
    eye_right = lm[1]
    nose = lm[2]
    d_left = norm(nose - eye_left)
    d_right = norm(nose - eye_right)
    yaw_val = (d_left - d_right) / (d_left + d_right + 1e-6) * 150
    eye_c = (eye_left + eye_right) / 2
    mouth_left = lm[3]
    mouth_right = lm[4]
    mouth_c = (mouth_left + mouth_right) / 2
    d_eye_nose = norm(eye_c - nose)
    d_nose_mouth = norm(nose - mouth_c)
    pitch_val = (d_nose_mouth - d_eye_nose) / (d_nose_mouth + d_eye_nose + 1e-6) * 150
    return -yaw_val, pitch_val
def norm(v):
    return math.sqrt(v[0]*v[0] + v[1]*v[1])
class FaceIDWorker(QThread):
    change_pixmap = pyqtSignal(QImage)
    pose_feedback = pyqtSignal(str, float)
    finished_registration = pyqtSignal(bool, str)
    def __init__(self, camera_source=0):
        super().__init__()
        self.running = True
        self.register_mode = False
        self.target_name = None
        self.current_pose_idx = 0
        self.collected_frames = 0
        self.camera_source = camera_source
        self.db = DatabaseManager()
        providers = ['CUDAExecutionProvider', 'DmlExecutionProvider', 'CPUExecutionProvider']
        self.app = FaceAnalysis(name='buffalo_l', providers=providers)
        self.app.prepare(ctx_id=0, det_size=(640, 640))
    def run(self):
        src = self.camera_source
        if isinstance(src, str) and src.isdigit():
             src = int(src)
        cap = cv2.VideoCapture(src)
        if isinstance(src, int):
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        while self.running:
            ret, frame = cap.read()
            if not ret or frame is None:
                self.pose_feedback.emit("Kamera Bağlantısı Yok", 0)
                time.sleep(1)
                if isinstance(src, str):
                    cap.release()
                    time.sleep(1)
                    cap = cv2.VideoCapture(src)
                continue
            if isinstance(src, int):
                frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]
            if w > 1280:
                frame = cv2.resize(frame, (1280, 720))
            vis_frame = frame.copy()
            if self.register_mode:
                self.process_registration(frame, vis_frame)
            else:
                self.process_preview(frame, vis_frame)
            rgb = cv2.cvtColor(vis_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            qt_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888).copy()
            self.change_pixmap.emit(qt_img)
        cap.release()
    def process_preview(self, frame, vis_frame):
        h, w = frame.shape[:2]
        try:
            faces = self.app.get(frame)
            for face in faces:
                bbox = face.bbox.astype(int)
                cv2.rectangle(vis_frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (100, 100, 100), 2)
        except: pass
        cv2.circle(vis_frame, (w//2, h//2), VISUAL_RADIUS, (255, 255, 255), 1)
    def process_registration(self, frame, vis_frame):
        h, w = frame.shape[:2]
        target_pose_name, instruction, yaw_range, pitch_range = POSES[self.current_pose_idx]
        faces = self.app.get(frame)
        if not faces:
            self.pose_feedback.emit("Yüz Bulunamadı", self.get_total_progress())
            cv2.circle(vis_frame, (w//2, h//2), VISUAL_RADIUS, (0, 0, 255), 2)
            return
        face = faces[0]
        bbox = face.bbox.astype(int)
        kps = face.kps
        yaw, pitch = estimate_pose(kps)
        y_ok = yaw_range[0] <= yaw <= yaw_range[1]
        p_ok = pitch_range[0] <= pitch <= pitch_range[1]
        cx = (bbox[0] + bbox[2]) / 2
        cy = (bbox[1] + bbox[3]) / 2
        dist_from_center = math.sqrt((cx - w/2)**2 + (cy - h/2)**2)
        c_ok = dist_from_center < CENTER_TOLERANCE
        color = (0, 0, 255)
        status_msg = instruction
        if not c_ok: status_msg = "Çerçevenin Ortasına Gel"
        elif not y_ok:
            if yaw < yaw_range[0]: status_msg = "Daha Sola Dön"
            if yaw > yaw_range[1]: status_msg = "Daha Sağa Dön"
        elif not p_ok:
            if pitch < pitch_range[0]: status_msg = "Daha Yukarı Bak"
            if pitch > pitch_range[1]: status_msg = "Daha Aşağı Bak"
        valid_pose = c_ok and y_ok and p_ok
        if valid_pose:
            color = (0, 255, 0)
            self.collected_frames += 1
            if self.save_frame(frame):
                prog_ratio = self.collected_frames / FRAMES_REQUIRED
                cv2.ellipse(vis_frame, (w//2, h//2), (VISUAL_RADIUS+10, VISUAL_RADIUS+10), 0, -90, 360 * prog_ratio - 90, (0, 255, 0), 4)
            if self.collected_frames >= FRAMES_REQUIRED:
                self.current_pose_idx += 1
                self.collected_frames = 0
                if self.current_pose_idx >= len(POSES):
                    self.register_mode = False
                    
                    faces = self.app.get(frame)
                    if faces:
                        embedding = faces[0].embedding
                        import random
                        fake_sicil = str(random.randint(10000, 99999))
                        success, msg = self.db.add_user(fake_sicil, self.target_name, "Memur", "Merkez", embedding)
                        if success:
                            print(f"[SUCCESS] User {self.target_name} saved to DB. Sicil: {fake_sicil}")
                            self.finished_registration.emit(True, f"KAYIT BAŞARILI!\nSicil: {fake_sicil}\nVeritabanına eklendi.")
                        else:
                            print(f"[ERROR] DB Save failed: {msg}")
                            self.finished_registration.emit(False, f"Veritabanı Hatası: {msg}")
                    else:
                        print("[ERROR] No face detected in final frame.")
                        self.finished_registration.emit(False, "HATA: Son karede yüz algılanamadı, kayıt yapılamadı!")
                    
                    self.pose_feedback.emit("Bitti", 1.0)
                else:
                    time.sleep(0.5) 
        cv2.circle(vis_frame, (w//2, h//2), VISUAL_RADIUS, color, 2)
        self.pose_feedback.emit(status_msg, self.get_total_progress())
    def get_total_progress(self):
        total_frames = len(POSES) * FRAMES_REQUIRED
        done = 0
        for i in range(self.current_pose_idx): done += FRAMES_REQUIRED
        done += self.collected_frames
        return min(1.0, done / total_frames)
    def save_frame(self, frame):
        if not self.target_name: return False
        try:
             return True
        except Exception as e:
            print(f"Save ERROR: {e}")
        return False
    def start_registration(self, name):
        self.target_name = name
        self.current_pose_idx = 0
        self.collected_frames = 0
        self.register_mode = True
    def stop(self):
        self.running = False
        self.wait()
class AdminApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EGM CANLI TAKİP")
        self.setStyleSheet(PROFESSIONAL_THEME)
        self.resize(1100, 700)
        self.available_cams = self.check_cameras()
        self.worker = None
        self.db = DatabaseManager()
        self.init_ui()
        self.start_camera(0)
        self.load_users()
    def check_cameras(self):
        cams = []
        for i in range(5):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if not cap.isOpened(): cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret: cams.append(i)
                cap.release()
        return cams
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        side = QFrame(); side.setObjectName("SideBar"); side.setFixedWidth(300)
        sl = QVBoxLayout(side)
        sl.addWidget(QLabel("KULLANICILAR", objectName="Header"))
        self.user_list = QListWidget()
        sl.addWidget(self.user_list)
        btn_del = QPushButton("KULLANICIYI SİL"); btn_del.setObjectName("DeleteBtn")
        btn_del.clicked.connect(self.delete_user)
        sl.addWidget(btn_del)
        layout.addWidget(side)
        main = QFrame()
        ml = QVBoxLayout(main)
        ml.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cam_sel_layout = QHBoxLayout()
        cam_sel_layout.addStretch()
        cam_sel_layout.addWidget(QLabel("Kamera Seç:"))
        self.combo_cam = QComboBox()
        for i in self.available_cams:
            self.combo_cam.addItem(f"Kamera {i}", i)
        self.combo_cam.addItem("IP Kamera (URL)", "ip")
        self.combo_cam.currentIndexChanged.connect(self.change_camera)
        cam_sel_layout.addWidget(self.combo_cam)
        cam_sel_layout.addStretch()
        ml.addLayout(cam_sel_layout)
        self.lbl_inst = QLabel("Face ID Hazır", objectName="Instruction")
        self.lbl_inst.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ml.addWidget(self.lbl_inst)
        cam_container = QWidget(); cam_container.setFixedSize(640, 480)
        cam_layout = QVBoxLayout(cam_container); cam_layout.setContentsMargins(0,0,0,0)
        self.cam_lbl = QLabel()
        self.cam_lbl.setFixedSize(640, 480)
        self.cam_lbl.setStyleSheet("background: black;")
        cam_layout.addWidget(self.cam_lbl)
        ml.addWidget(cam_container, alignment=Qt.AlignmentFlag.AlignCenter)
        self.prog = QProgressBar(); self.prog.setFixedWidth(400); self.prog.setTextVisible(False)
        ml.addWidget(self.prog, alignment=Qt.AlignmentFlag.AlignCenter)
        controls = QHBoxLayout()
        self.inp_name = QLineEdit(); self.inp_name.setPlaceholderText("İsim Giriniz...")
        self.inp_name.setFixedWidth(250)
        controls.addWidget(self.inp_name)
        self.btn_start = QPushButton("KURULUMU BAŞLAT"); self.btn_start.setObjectName("PrimaryBtn")
        self.btn_start.clicked.connect(self.start_setup)
        controls.addWidget(self.btn_start)
        ml.addLayout(controls)
        layout.addWidget(main)
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
    def start_camera(self, source):
        if self.worker: return
        self.worker = FaceIDWorker(source)
        self.worker.change_pixmap.connect(self.update_cam)
        self.worker.pose_feedback.connect(self.update_feedback)
        self.worker.finished_registration.connect(self.on_finish)
        self.worker.start()
    def stop_camera(self):
        if self.worker:
            self.worker.stop()
            self.worker = None
    def load_users(self):
        self.user_list.clear()
        users = self.db.get_all_users_encodings()
        for sicil, data in users.items():
            self.user_list.addItem(f"{data['name']} ({sicil})")
    def update_cam(self, img):
        self.cam_lbl.setPixmap(QPixmap.fromImage(img).scaled(
            self.cam_lbl.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    def update_feedback(self, msg, progress):
        self.lbl_inst.setText(msg)
        self.prog.setValue(int(progress * 100))
    def start_setup(self):
        name = self.inp_name.text().strip()
        if not name: QMessageBox.warning(self, "Hata", "İsim giriniz."); return
        self.inp_name.setEnabled(False); self.btn_start.setEnabled(False)
        self.worker.start_registration(name)
    def on_finish(self, success, msg):
        self.inp_name.setEnabled(True); self.btn_start.setEnabled(True)
        self.inp_name.clear(); self.prog.setValue(0)
        self.load_users()
        QMessageBox.information(self, "Bilgi", msg)
    def delete_user(self):
        item = self.user_list.currentItem()
        if item and QMessageBox.question(self, "Sil", "Emin misiniz?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            text = item.text()
            if "(" in text and text.endswith(")"):
                sicil = text.split("(")[-1].replace(")", "")
                QMessageBox.information(self, "Bilgi", "Veritabani silme henuz eklenmedi.")
            self.load_users()
    def closeEvent(self, event):
        self.stop_camera()
        event.accept()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminApp()
    window.show()
    sys.exit(app.exec())
