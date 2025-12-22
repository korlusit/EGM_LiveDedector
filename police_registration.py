import sys
import os
import shutil
import numpy as np
import cv2
from insightface.app import FaceAnalysis
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QTextEdit, QComboBox, QPushButton, QMessageBox, QFileDialog, QLineEdit)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt
from database_manager import DatabaseManager
class PoliceRegistrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("YENİ POLİS PERSONEL KAYDI") 
        self.resize(500, 600)
        self.setStyleSheet("""
            QDialog { background-color: 
            QLabel { font-weight: bold; margin-top: 10px; }
            QLineEdit, QComboBox { padding: 8px; background-color: 
            QPushButton { background-color: 
            QPushButton:hover { background-color: 
        """)
        self.selected_file = None
        self.db = DatabaseManager()
        self.init_ui()
    def init_ui(self):
        l = QVBoxLayout(self)
        l.addWidget(QLabel("Ad Soyad:"))
        self.inp_name = QLineEdit()
        l.addWidget(self.inp_name)
        l.addWidget(QLabel("Sicil No:"))
        self.inp_sicil = QLineEdit()
        l.addWidget(self.inp_sicil)
        l.addWidget(QLabel("Rütbe:"))
        self.combo_rank = QComboBox()
        self.combo_rank.addItems(["Polis Memuru", "Komiser Yardımcısı", "Komiser", "Başkomiser", "Emniyet Amiri", "Müdür"])
        self.combo_rank.setEditable(True)
        l.addWidget(self.combo_rank)
        l.addWidget(QLabel("Görev Yeri:"))
        self.inp_unit = QLineEdit()
        self.inp_unit.setText("Genel Hizmet")
        l.addWidget(self.inp_unit)
        self.lbl_photo = QLabel("Fotoğraf Seçilmedi")
        self.lbl_photo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_photo.setStyleSheet("border: 1px dashed 
        self.lbl_photo.setFixedHeight(150)
        l.addWidget(self.lbl_photo)
        btn_sel = QPushButton("FOTOĞRAF SEÇ")
        btn_sel.clicked.connect(self.select_photo)
        l.addWidget(btn_sel)
        btn_save = QPushButton("KAYDET")
        btn_save.clicked.connect(self.save_user)
        btn_save.setStyleSheet("background-color: 
        l.addWidget(btn_save)
    def select_photo(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Fotoğraf Seç", "", "Resimler (*.jpg *.png *.jpeg)")
        if fname:
            self.selected_file = fname
            pix = QPixmap(fname).scaled(self.lbl_photo.width(), self.lbl_photo.height(), Qt.AspectRatioMode.KeepAspectRatio)
            self.lbl_photo.setPixmap(pix)
    def save_user(self):
        name = self.inp_name.text().strip()
        sicil = self.inp_sicil.text().strip()
        rank = self.combo_rank.currentText()
        unit = self.inp_unit.text().strip()
        if not name or not sicil or not self.selected_file:
            QMessageBox.warning(self, "Eksik", "Lütfen Ad, Sicil ve Fotoğraf alanlarını doldurunuz.")
            return
        try:
            app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
            app.prepare(ctx_id=0, det_size=(640, 640))
            img = cv2.imread(self.selected_file)
            if img is None:
                QMessageBox.warning(self, "Hata", "Fotoğraf okunamadı.")
                return 
            faces = app.get(img)
            if not faces:
                QMessageBox.warning(self, "Hata", "Yüz algılanamadı! Lütfen net bir fotoğraf seçin.")
                return 
            embedding = faces[0].embedding
            success, msg = self.db.add_user(sicil, name, rank, unit, embedding)
            if success:
                QMessageBox.information(self, "Başarılı", f"Personel {name} kaydedildi.")
                self.accept()
            else:
                QMessageBox.warning(self, "Hata", msg)
        except Exception as e:
            QMessageBox.critical(self, "Kritik Hata", str(e))
