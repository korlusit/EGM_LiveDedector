import sys
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QColorDialog, QMessageBox, QGraphicsDropShadowEffect

# Convert ettiğimiz UI dosyasını import ediyoruz
from egm_ui import Ui_MainWindow

class EGMSistem(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        
        self.setWindowTitle("E.G.M - Entegre Güvenlik Yönetim Sistemi v3.0")
        self.personel_verisi = {
            "ad": "Başkomiser Ali KANDEMİR",
            "rutbe": "Başkomiser (3. Sınıf Emniyet Müdürü)",
            "sicil": "1845-34-A",
            "gorev": "Ankara Asayiş Şube Müdürlüğü"
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

        
        self.ui.btnOpenPTS.clicked.connect(lambda: print("PTS Sistemi Başlatılıyor..."))
        self.ui.btnOpenGBT.clicked.connect(lambda: print("GBT Sorgu Ekranı Açılıyor..."))
        self.ui.btnOpenTutanak.clicked.connect(lambda: print("Dijital Tutanak Modülü Yüklendi."))

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
            self.ui.sidebarFrame.setStyleSheet(f"#sidebarFrame {{ background-color: {color.name()}; border-right: 1px solid #2A2A3A; }}")

    def ana_renk_degistir(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.ui.mainContentWidget.setStyleSheet(f"#mainContentWidget {{ background-color: {color.name()}; }}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    font = QtGui.QFont("Segoe UI", 10)
    font.setStyleStrategy(QtGui.QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)
    
    window = EGMSistem()
    window.show()
    sys.exit(app.exec())