import sys
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QColorDialog, QMessageBox, QGraphicsDropShadowEffect, QPushButton, QVBoxLayout
import subprocess
import os
from egm_ui import Ui_MainWindow
class EGMSistem(QtWidgets.QMainWindow):
    def __init__(self, user_name="Admin"):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.label_4.setText("PLAKA TANIMA SİSTEMİ (PTS)")
        self.ui.label_5.setText("YÜZ TANIMA SİSTEMİ (GBT)")
        self.ui.cardTutanak.hide()
        self.setWindowTitle("EGM CANLI TAKİP")
        display_name = user_name
        if "_" in user_name:
            parts = user_name.split("_")
            if len(parts) >= 2:
                display_name = f"{parts[0].capitalize()} {parts[1].upper()}"
            else:
                display_name = user_name.title()
        self.personel_verisi = {
            "ad": display_name,
            "rutbe": "Polis Memuru", 
            "sicil": f"{QtCore.QTime.currentTime().toString('mmss')}-34", 
            "gorev": "Ankara Emniyet Müdürlüğü"
        }
        self.verileri_arayuze_yukle()
        self.efektleri_uygula()
        self.ui.btnAnaSayfa.clicked.connect(lambda: self.sayfa_degistir(0))
        self.ui.btnProfil.clicked.connect(lambda: self.sayfa_degistir(1))
        self.ui.btnAdmin.clicked.connect(lambda: self.sayfa_degistir(2))
        self.ui.btnAyarlar.clicked.connect(lambda: self.sayfa_degistir(3))
        self.ui.btnSaveData.clicked.connect(self.admin_verileri_kaydet)
        self.ui.btnColorSidebar.clicked.connect(self.sidebar_renk_degistir)
        self.ui.btnColorBg.clicked.connect(self.ana_renk_degistir)
        self.ui.btnOpenPTS.clicked.connect(self.open_pts)
        self.ui.btnOpenGBT.clicked.connect(self.open_gbt)
        self.ui.btnOpenTutanak.clicked.connect(lambda: print("Dijital Tutanak Modülü Yüklendi."))
        try:
            layout = self.ui.sidebarLayout
            index = layout.indexOf(self.ui.btnAdmin)
            self.btnYuzTanitma = QtWidgets.QPushButton(self.ui.sidebarFrame)
            self.btnYuzTanitma.setText("  Yüz Tanıtma")
            self.btnYuzTanitma.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            self.btnYuzTanitma.setProperty("class", "sidebarBtn") 
            self.btnYuzTanitma.setObjectName("btnYuzTanitma")
            self.btnYuzTanitma.clicked.connect(self.open_add_person)
            if index >= 0: layout.insertWidget(index + 1, self.btnYuzTanitma)
            else: layout.addWidget(self.btnYuzTanitma)
            self.ui.sidebarFrame.style().unpolish(self.ui.sidebarFrame)
            self.ui.sidebarFrame.style().polish(self.ui.sidebarFrame)
        except Exception as e:
            print(f"Sidebar buton ekleme hatasi: {e}")
    def open_gbt(self):
        try: 
            flags = 0
            if os.name == 'nt': flags = 0x08000000 
            base_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(base_dir, 'face.py')
            subprocess.Popen([sys.executable, script_path], creationflags=flags)
        except Exception as e: QMessageBox.critical(self, "Hata", str(e))
    def open_pts(self):
        try: 
            flags = 0
            if os.name == 'nt': flags = 0x08000000 
            base_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(base_dir, 'plaka.py')
            subprocess.Popen([sys.executable, script_path], creationflags=flags)
        except Exception as e: QMessageBox.critical(self, "Hata", str(e))
    def open_add_person(self):
        try: 
            flags = 0
            if os.name == 'nt': flags = 0x08000000 
            base_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(base_dir, 'admin_users.py')
            subprocess.Popen([sys.executable, script_path], creationflags=flags)
        except Exception as e: QMessageBox.critical(self, "Hata", str(e))
    def efektleri_uygula(self):
        for card in [self.ui.cardPTS, self.ui.cardGBT, self.ui.cardTutanak, self.ui.profileDataCard, self.ui.adminDataCard]:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setXOffset(0)
            shadow.setYOffset(5)
            shadow.setColor(QtGui.QColor(0, 0, 0, 80))
            card.setGraphicsEffect(shadow)
    def sayfa_degistir(self, index):
        self.ui.mainStack.setCurrentIndex(index)
    def verileri_arayuze_yukle(self):
        self.ui.viewName.setText(self.personel_verisi["ad"])
        self.ui.viewRank.setText(self.personel_verisi["rutbe"])
        self.ui.viewID.setText(self.personel_verisi["sicil"])
        self.ui.viewDuty.setText(self.personel_verisi["gorev"])
        self.ui.editName.setText(self.personel_verisi["ad"])
        self.ui.editRank.setText(self.personel_verisi["rutbe"])
        self.ui.editID.setText(self.personel_verisi["sicil"])
        self.ui.editDuty.setText(self.personel_verisi["gorev"])
    def admin_verileri_kaydet(self):
        yeni_ad = self.ui.editName.text()
        yeni_rutbe = self.ui.editRank.text()
        yeni_sicil = self.ui.editID.text()
        yeni_gorev = self.ui.editDuty.text()
        if not yeni_ad or not yeni_sicil:
            QMessageBox.warning(self, "Eksik Bilgi", "Ad Soyad ve Sicil No alanları boş bırakılamaz!")
            return
        self.personel_verisi["ad"] = yeni_ad
        self.personel_verisi["rutbe"] = yeni_rutbe
        self.personel_verisi["sicil"] = yeni_sicil
        self.personel_verisi["gorev"] = yeni_gorev
        self.verileri_arayuze_yukle()
        QMessageBox.information(self, "Başarılı", "Personel veritabanı başarıyla güncellendi.\nProfil sayfası yenilendi.")
        self.sayfa_degistir(1)
    def sidebar_renk_degistir(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.ui.sidebarFrame.setStyleSheet(f"background-color: {color.name()};")
    def ana_renk_degistir(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.ui.mainContentWidget.setStyleSheet(f"background-color: {color.name()};")
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    font = QtGui.QFont("Segoe UI", 10)
    font.setStyleStrategy(QtGui.QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)
    window = EGMSistem()
    window.show()
    sys.exit(app.exec())