from PyQt6 import QtCore, QtGui, QtWidgets
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 850)
        MainWindow.setStyleSheet("""
/* --- ULTRA MODERN DARK THEME --- */
QMainWindow {
    background-color: #121212;
    color: #ffffff;
}

/* --- LOGO AREA --- */
QLabel#labelImagePlace {
    background-color: transparent;
    border: none;
}

/* --- SIDEBAR FRAME --- */
QFrame#sidebarFrame {
    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1a1a1a, stop:1 #2d2d2d);
    border-right: 1px solid #333333;
}
    border-right: 1px solid #444444;
}

    color: #4da3ff;
    font-family: 'Segoe UI', sans-serif;
    font-weight: 800;
    font-size: 22px;
    letter-spacing: 1px;
    margin-top: 15px;
    margin-bottom: 20px;
}

/* Sidebar Butonları */
QPushButton.sidebarBtn {
    background-color: transparent;
    color: #e0e0e0;
    text-align: left;
    padding: 12px 25px;
    border: none;
    border-radius: 12px;
    font-size: 15px;
    font-weight: 600;
    margin: 4px 15px;
}

QPushButton.sidebarBtn:hover {
    background-color: #333333;
    color: #4da3ff;
    padding-left: 30px; /* Hafif kayma efekti */
}

QPushButton.sidebarBtn:pressed {
    background-color: #444444;
    color: #8ab4f8;
}

/* --- ANA İÇERİK ALANI --- */
    background-color: #2b2b2b;
}

/* Bölüm Başlıkları */
QLabel.pageHeader {
    font-size: 28px;
    font-weight: bold;
    color: #e0e0e0;
    margin-bottom: 20px;
}

/* --- KART TASARIMLARI (WATERMARK İKONLU) --- */
QFrame.cardFrame {
    background-color: #3d3d3d;
    border-radius: 20px;
    border: 1px solid #555555;
    /* İkonlar aşağıda ID bazlı tanımlanacak */
}

QFrame.cardFrame:hover {
    background-color: #444444;
    border: 1px solid #4da3ff;
    margin-top: -5px; /* Yukarı kalkma efekti */
}

QLabel.cardTitle {
    font-size: 24px;
    font-weight: 800;
    color: #ffffff;
    background: transparent;
}

QLabel.cardDesc {
    color: #aaaaaa;
    font-size: 14px;
    background: transparent;
    margin-top: 10px;
}

QPushButton.cardActionBtn {
    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #1A73E8, stop:1 #287AE6);
    color: white;
    border-radius: 10px;
    font-weight: bold;
    font-size: 14px;
    padding: 12px;
    border: none;
    margin-top: 20px;
}

QPushButton.cardActionBtn:hover {
    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #1557B0, stop:1 #174EA6);
}

/* --- KARTLARA ÖZEL WATERMARK İKONLARI --- 
   Not: Bu URL'ler örnek amaçlıdır. Gerçek projede yerel dosyalar (.qrc) kullanmak daha iyidir.
   background-size: 120px; ile ikon boyutu ayarlanıyor, sağ üstte duruyor.
*/
    background-image: url('https://cdn-icons-png.flaticon.com/512/2554/2554933.png');
    background-repeat: no-repeat;
    background-position: right 20px top 20px;
    background-size: 140px;
}

    background-image: url('https://cdn-icons-png.flaticon.com/512/921/921586.png');
    background-repeat: no-repeat;
    background-position: right 20px top 20px;
    background-size: 140px;
}

    background-image: url('https://cdn-icons-png.flaticon.com/512/2991/2991108.png');
    background-repeat: no-repeat;
    background-position: right 20px top 20px;
    background-size: 140px;
}

/* --- PROFİL VE ADMIN FORMLARI --- */
QFrame.dataCard {
    background-color: #3d3d3d;
    border-radius: 15px;
    padding: 30px;
}

QLabel.formLabel {
    font-size: 16px;
    font-weight: 600;
    color: #aaaaaa;
}

QLabel.formData {
    font-size: 18px;
    color: #ffffff;
    font-weight: 500;
    padding: 5px;
    border-bottom: 1px solid #E0E0E0;
}

QLineEdit.adminInput {
    background-color: #444444;
    border: 2px solid transparent;
    border-radius: 8px;
    padding: 12px;
    font-size: 16px;
    color: #ffffff;
}

QLineEdit.adminInput:focus {
    border: 2px solid #4da3ff;
    background-color: #505050;
}

QPushButton.saveBtn {
    background-color: #34A853;
    color: white;
    font-size: 16px;
    font-weight: bold;
    padding: 15px;
    border-radius: 10px;
}
QPushButton.saveBtn:hover { background-color: #2D8E47; }

/* Ayarlar Renk Butonları */
QPushButton.colorBtn {
    padding: 20px;
    border-radius: 15px;
    font-size: 16px;
    font-weight: bold;
    background-color: #3d3d3d;
    color: #ffffff;
    border: 2px solid #555555;
    text-align: center;
}
""")
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.mainLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setObjectName("mainLayout")
        self.sidebarFrame = QtWidgets.QFrame(parent=self.centralwidget)
        self.sidebarFrame.setMinimumSize(QtCore.QSize(280, 0))
        self.sidebarFrame.setMaximumSize(QtCore.QSize(280, 16777215))
        self.sidebarFrame.setObjectName("sidebarFrame")
        self.sidebarLayout = QtWidgets.QVBoxLayout(self.sidebarFrame)
        self.sidebarLayout.setContentsMargins(-1, 40, -1, 30)
        self.sidebarLayout.setSpacing(15)
        self.sidebarLayout.setObjectName("sidebarLayout")
        self.labelImagePlace = QtWidgets.QLabel(parent=self.sidebarFrame)
        self.labelImagePlace.setMinimumSize(QtCore.QSize(0, 180))
        self.labelImagePlace.setStyleSheet("background-color: transparent; border: none;")
        self.labelImagePlace.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.labelImagePlace.setObjectName("labelImagePlace")
        self.sidebarLayout.addWidget(self.labelImagePlace)
        self.labelTitle = QtWidgets.QLabel(parent=self.sidebarFrame)
        self.labelTitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.labelTitle.setObjectName("labelTitle")
        self.sidebarLayout.addWidget(self.labelTitle)
        spacerItem = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        self.sidebarLayout.addItem(spacerItem)
        self.btnAnaSayfa = QtWidgets.QPushButton(parent=self.sidebarFrame)
        self.btnAnaSayfa.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btnAnaSayfa.setObjectName("btnAnaSayfa")
        self.sidebarLayout.addWidget(self.btnAnaSayfa)
        self.btnProfil = QtWidgets.QPushButton(parent=self.sidebarFrame)
        self.btnProfil.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btnProfil.setObjectName("btnProfil")
        self.sidebarLayout.addWidget(self.btnProfil)
        self.btnAdmin = QtWidgets.QPushButton(parent=self.sidebarFrame)
        self.btnAdmin.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btnAdmin.setObjectName("btnAdmin")
        self.sidebarLayout.addWidget(self.btnAdmin)
        self.btnAyarlar = QtWidgets.QPushButton(parent=self.sidebarFrame)
        self.btnAyarlar.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btnAyarlar.setObjectName("btnAyarlar")
        self.sidebarLayout.addWidget(self.btnAyarlar)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.sidebarLayout.addItem(spacerItem1)
        self.labelVersion = QtWidgets.QLabel(parent=self.sidebarFrame)
        self.labelVersion.setStyleSheet("color: #CCCCCC; font-size: 12px;")
        self.labelVersion.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.labelVersion.setObjectName("labelVersion")
        self.sidebarLayout.addWidget(self.labelVersion)
        self.mainLayout.addWidget(self.sidebarFrame)
        self.mainContentWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.mainContentWidget.setObjectName("mainContentWidget")
        self.contentLayout = QtWidgets.QVBoxLayout(self.mainContentWidget)
        self.contentLayout.setContentsMargins(40, 40, 40, 40)
        self.contentLayout.setObjectName("contentLayout")
        self.mainStack = QtWidgets.QStackedWidget(parent=self.mainContentWidget)
        self.mainStack.setObjectName("mainStack")
        self.pageHome = QtWidgets.QWidget()
        self.pageHome.setObjectName("pageHome")
        self.verticalLayout_Home = QtWidgets.QVBoxLayout(self.pageHome)
        self.verticalLayout_Home.setSpacing(30)
        self.verticalLayout_Home.setObjectName("verticalLayout_Home")
        self.label_2 = QtWidgets.QLabel(parent=self.pageHome)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_Home.addWidget(self.label_2)
        self.cardsContainer = QtWidgets.QWidget(parent=self.pageHome)
        self.cardsContainer.setObjectName("cardsContainer")
        self.gridLayout = QtWidgets.QGridLayout(self.cardsContainer)
        self.gridLayout.setSpacing(30)
        self.gridLayout.setObjectName("gridLayout")
        self.cardPTS = QtWidgets.QFrame(parent=self.cardsContainer)
        self.cardPTS.setMinimumSize(QtCore.QSize(0, 240))
        self.cardPTS.setObjectName("cardPTS")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.cardPTS)
        self.verticalLayout_4.setContentsMargins(30, 30, 30, 30)
        self.verticalLayout_4.setSpacing(15)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_4 = QtWidgets.QLabel(parent=self.cardPTS)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_4.addWidget(self.label_4)
        self.label_7 = QtWidgets.QLabel(parent=self.cardPTS)
        self.label_7.setWordWrap(True)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_4.addWidget(self.label_7)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_4.addItem(spacerItem2)
        self.btnOpenPTS = QtWidgets.QPushButton(parent=self.cardPTS)
        self.btnOpenPTS.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btnOpenPTS.setObjectName("btnOpenPTS")
        self.verticalLayout_4.addWidget(self.btnOpenPTS)
        self.gridLayout.addWidget(self.cardPTS, 0, 0, 1, 1)
        self.cardGBT = QtWidgets.QFrame(parent=self.cardsContainer)
        self.cardGBT.setMinimumSize(QtCore.QSize(0, 240))
        self.cardGBT.setObjectName("cardGBT")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.cardGBT)
        self.verticalLayout_5.setContentsMargins(30, 30, 30, 30)
        self.verticalLayout_5.setSpacing(15)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_5 = QtWidgets.QLabel(parent=self.cardGBT)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_5.addWidget(self.label_5)
        self.label_8 = QtWidgets.QLabel(parent=self.cardGBT)
        self.label_8.setWordWrap(True)
        self.label_8.setObjectName("label_8")
        self.verticalLayout_5.addWidget(self.label_8)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_5.addItem(spacerItem3)
        self.btnOpenGBT = QtWidgets.QPushButton(parent=self.cardGBT)
        self.btnOpenGBT.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btnOpenGBT.setObjectName("btnOpenGBT")
        self.verticalLayout_5.addWidget(self.btnOpenGBT)
        self.gridLayout.addWidget(self.cardGBT, 0, 1, 1, 1)
        self.cardTutanak = QtWidgets.QFrame(parent=self.cardsContainer)
        self.cardTutanak.setMinimumSize(QtCore.QSize(0, 240))
        self.cardTutanak.setObjectName("cardTutanak")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.cardTutanak)
        self.verticalLayout_6.setContentsMargins(30, 30, 30, 30)
        self.verticalLayout_6.setSpacing(15)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_6 = QtWidgets.QLabel(parent=self.cardTutanak)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_6.addWidget(self.label_6)
        self.label_9 = QtWidgets.QLabel(parent=self.cardTutanak)
        self.label_9.setWordWrap(True)
        self.label_9.setObjectName("label_9")
        self.verticalLayout_6.addWidget(self.label_9)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_6.addItem(spacerItem4)
        self.btnOpenTutanak = QtWidgets.QPushButton(parent=self.cardTutanak)
        self.btnOpenTutanak.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btnOpenTutanak.setObjectName("btnOpenTutanak")
        self.verticalLayout_6.addWidget(self.btnOpenTutanak)
        self.gridLayout.addWidget(self.cardTutanak, 0, 2, 1, 1)
        self.verticalLayout_Home.addWidget(self.cardsContainer)
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_Home.addItem(spacerItem5)
        self.mainStack.addWidget(self.pageHome)
        self.pageProfile = QtWidgets.QWidget()
        self.pageProfile.setObjectName("pageProfile")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.pageProfile)
        self.verticalLayout_7.setSpacing(30)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.label_3 = QtWidgets.QLabel(parent=self.pageProfile)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_7.addWidget(self.label_3)
        self.profileDataCard = QtWidgets.QFrame(parent=self.pageProfile)
        self.profileDataCard.setObjectName("profileDataCard")
        self.formLayout = QtWidgets.QFormLayout(self.profileDataCard)
        self.formLayout.setHorizontalSpacing(30)
        self.formLayout.setVerticalSpacing(25)
        self.formLayout.setObjectName("formLayout")
        self.label_10 = QtWidgets.QLabel(parent=self.profileDataCard)
        self.label_10.setObjectName("label_10")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_10)
        self.viewName = QtWidgets.QLabel(parent=self.profileDataCard)
        self.viewName.setObjectName("viewName")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.viewName)
        self.label_11 = QtWidgets.QLabel(parent=self.profileDataCard)
        self.label_11.setObjectName("label_11")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_11)
        self.viewRank = QtWidgets.QLabel(parent=self.profileDataCard)
        self.viewRank.setObjectName("viewRank")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.viewRank)
        self.label_12 = QtWidgets.QLabel(parent=self.profileDataCard)
        self.label_12.setObjectName("label_12")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_12)
        self.viewID = QtWidgets.QLabel(parent=self.profileDataCard)
        self.viewID.setObjectName("viewID")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.viewID)
        self.label_13 = QtWidgets.QLabel(parent=self.profileDataCard)
        self.label_13.setObjectName("label_13")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_13)
        self.viewDuty = QtWidgets.QLabel(parent=self.profileDataCard)
        self.viewDuty.setObjectName("viewDuty")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.viewDuty)
        self.verticalLayout_7.addWidget(self.profileDataCard)
        spacerItem6 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_7.addItem(spacerItem6)
        self.mainStack.addWidget(self.pageProfile)
        self.pageAdmin = QtWidgets.QWidget()
        self.pageAdmin.setObjectName("pageAdmin")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.pageAdmin)
        self.verticalLayout_8.setSpacing(30)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.label_14 = QtWidgets.QLabel(parent=self.pageAdmin)
        self.label_14.setObjectName("label_14")
        self.verticalLayout_8.addWidget(self.label_14)
        self.adminDataCard = QtWidgets.QFrame(parent=self.pageAdmin)
        self.adminDataCard.setObjectName("adminDataCard")
        self.formLayout_2 = QtWidgets.QFormLayout(self.adminDataCard)
        self.formLayout_2.setHorizontalSpacing(30)
        self.formLayout_2.setVerticalSpacing(25)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_15 = QtWidgets.QLabel(parent=self.adminDataCard)
        self.label_15.setObjectName("label_15")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_15)
        self.editName = QtWidgets.QLineEdit(parent=self.adminDataCard)
        self.editName.setObjectName("editName")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.editName)
        self.label_16 = QtWidgets.QLabel(parent=self.adminDataCard)
        self.label_16.setObjectName("label_16")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_16)
        self.editRank = QtWidgets.QLineEdit(parent=self.adminDataCard)
        self.editRank.setObjectName("editRank")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.editRank)
        self.label_17 = QtWidgets.QLabel(parent=self.adminDataCard)
        self.label_17.setObjectName("label_17")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_17)
        self.editID = QtWidgets.QLineEdit(parent=self.adminDataCard)
        self.editID.setObjectName("editID")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.editID)
        self.label_18 = QtWidgets.QLabel(parent=self.adminDataCard)
        self.label_18.setObjectName("label_18")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_18)
        self.editDuty = QtWidgets.QLineEdit(parent=self.adminDataCard)
        self.editDuty.setObjectName("editDuty")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.editDuty)
        self.btnSaveData = QtWidgets.QPushButton(parent=self.adminDataCard)
        self.btnSaveData.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btnSaveData.setObjectName("btnSaveData")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.ItemRole.FieldRole, self.btnSaveData)
        self.verticalLayout_8.addWidget(self.adminDataCard)
        spacerItem7 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_8.addItem(spacerItem7)
        self.mainStack.addWidget(self.pageAdmin)
        self.pageSettings = QtWidgets.QWidget()
        self.pageSettings.setObjectName("pageSettings")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.pageSettings)
        self.verticalLayout_9.setSpacing(30)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.label_19 = QtWidgets.QLabel(parent=self.pageSettings)
        self.label_19.setObjectName("label_19")
        self.verticalLayout_9.addWidget(self.label_19)
        self.widget = QtWidgets.QWidget(parent=self.pageSettings)
        self.widget.setObjectName("widget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setSpacing(30)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.btnColorSidebar = QtWidgets.QPushButton(parent=self.widget)
        self.btnColorSidebar.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btnColorSidebar.setObjectName("btnColorSidebar")
        self.horizontalLayout_2.addWidget(self.btnColorSidebar)
        self.btnColorBg = QtWidgets.QPushButton(parent=self.widget)
        self.btnColorBg.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.btnColorBg.setObjectName("btnColorBg")
        self.horizontalLayout_2.addWidget(self.btnColorBg)
        self.verticalLayout_9.addWidget(self.widget)
        spacerItem8 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_9.addItem(spacerItem8)
        self.mainStack.addWidget(self.pageSettings)
        self.contentLayout.addWidget(self.mainStack)
        self.mainLayout.addWidget(self.mainContentWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        self.mainStack.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "EGM CANLI TAKİP"))
        self.labelImagePlace.setText(_translate("MainWindow", "RESİM ALANI"))
        self.labelTitle.setText(_translate("MainWindow", "EGM CANLI TAKİP"))
        self.btnAnaSayfa.setProperty("class", _translate("MainWindow", "sidebarBtn"))
        self.btnAnaSayfa.setText(_translate("MainWindow", "  Ana Ekran"))
        self.btnProfil.setProperty("class", _translate("MainWindow", "sidebarBtn"))
        self.btnProfil.setText(_translate("MainWindow", "  Profil Bilgileri"))
        self.btnAdmin.setProperty("class", _translate("MainWindow", "sidebarBtn"))
        self.btnAdmin.setText(_translate("MainWindow", "  Admin Paneli"))
        self.btnAyarlar.setProperty("class", _translate("MainWindow", "sidebarBtn"))
        self.btnAyarlar.setText(_translate("MainWindow", "  Sistem Ayarları"))
        self.labelVersion.setText(_translate("MainWindow", ""))
        self.label_2.setProperty("class", _translate("MainWindow", "pageHeader"))
        self.label_2.setText(_translate("MainWindow", "Uygulama Merkezi"))
        self.cardPTS.setProperty("class", _translate("MainWindow", "cardFrame"))
        self.label_4.setProperty("class", _translate("MainWindow", "cardTitle"))
        self.label_4.setText(_translate("MainWindow", "PTS SORGU"))
        self.label_7.setProperty("class", _translate("MainWindow", "cardDesc"))
        self.label_7.setText(_translate("MainWindow", "Plaka Tanıma Sistemi üzerinden anlık araç sorgulama ve takip."))
        self.btnOpenPTS.setProperty("class", _translate("MainWindow", "cardActionBtn"))
        self.btnOpenPTS.setText(_translate("MainWindow", "SİSTEMİ BAŞLAT"))
        self.cardGBT.setProperty("class", _translate("MainWindow", "cardFrame"))
        self.label_5.setProperty("class", _translate("MainWindow", "cardTitle"))
        self.label_5.setText(_translate("MainWindow", "GBT KONTROL"))
        self.label_8.setProperty("class", _translate("MainWindow", "cardDesc"))
        self.label_8.setText(_translate("MainWindow", "Merkezi veritabanı üzerinden detaylı şahıs ve kimlik sorgusu."))
        self.btnOpenGBT.setProperty("class", _translate("MainWindow", "cardActionBtn"))
        self.btnOpenGBT.setText(_translate("MainWindow", "SORGULA"))
        self.cardTutanak.setProperty("class", _translate("MainWindow", "cardFrame"))
        self.label_6.setProperty("class", _translate("MainWindow", "cardTitle"))
        self.label_6.setText(_translate("MainWindow", "DİJİTAL TUTANAK"))
        self.label_9.setProperty("class", _translate("MainWindow", "cardDesc"))
        self.label_9.setText(_translate("MainWindow", "Olay yeri ve ifade tutanaklarını dijital ortamda oluşturun ve arşivleyin."))
        self.btnOpenTutanak.setProperty("class", _translate("MainWindow", "cardActionBtn"))
        self.btnOpenTutanak.setText(_translate("MainWindow", "OLUŞTUR"))
        self.label_3.setProperty("class", _translate("MainWindow", "pageHeader"))
        self.label_3.setText(_translate("MainWindow", "Personel Kimlik Kartı"))
        self.profileDataCard.setProperty("class", _translate("MainWindow", "dataCard"))
        self.label_10.setProperty("class", _translate("MainWindow", "formLabel"))
        self.label_10.setText(_translate("MainWindow", "Ad Soyad:"))
        self.viewName.setProperty("class", _translate("MainWindow", "formData"))
        self.viewName.setText(_translate("MainWindow", "Yükleniyor..."))
        self.label_11.setProperty("class", _translate("MainWindow", "formLabel"))
        self.label_11.setText(_translate("MainWindow", "Rütbe:"))
        self.viewRank.setProperty("class", _translate("MainWindow", "formData"))
        self.viewRank.setText(_translate("MainWindow", "Yükleniyor..."))
        self.label_12.setProperty("class", _translate("MainWindow", "formLabel"))
        self.label_12.setText(_translate("MainWindow", "Sicil No:"))
        self.viewID.setProperty("class", _translate("MainWindow", "formData"))
        self.viewID.setText(_translate("MainWindow", "Yükleniyor..."))
        self.label_13.setProperty("class", _translate("MainWindow", "formLabel"))
        self.label_13.setText(_translate("MainWindow", "Görev Yeri:"))
        self.viewDuty.setProperty("class", _translate("MainWindow", "formData"))
        self.viewDuty.setText(_translate("MainWindow", "Yükleniyor..."))
        self.label_14.setProperty("class", _translate("MainWindow", "pageHeader"))
        self.label_14.setText(_translate("MainWindow", "Personel Veri Yönetimi (Admin)"))
        self.adminDataCard.setProperty("class", _translate("MainWindow", "dataCard"))
        self.label_15.setProperty("class", _translate("MainWindow", "formLabel"))
        self.label_15.setText(_translate("MainWindow", "Ad Soyad:"))
        self.editName.setProperty("class", _translate("MainWindow", "adminInput"))
        self.editName.setPlaceholderText(_translate("MainWindow", "Personel adını giriniz"))
        self.label_16.setProperty("class", _translate("MainWindow", "formLabel"))
        self.label_16.setText(_translate("MainWindow", "Rütbe:"))
        self.editRank.setProperty("class", _translate("MainWindow", "adminInput"))
        self.editRank.setPlaceholderText(_translate("MainWindow", "Güncel rütbe"))
        self.label_17.setProperty("class", _translate("MainWindow", "formLabel"))
        self.label_17.setText(_translate("MainWindow", "Sicil No:"))
        self.editID.setProperty("class", _translate("MainWindow", "adminInput"))
        self.editID.setPlaceholderText(_translate("MainWindow", "Sicil numarası"))
        self.label_18.setProperty("class", _translate("MainWindow", "formLabel"))
        self.label_18.setText(_translate("MainWindow", "Görev Yeri:"))
        self.editDuty.setProperty("class", _translate("MainWindow", "adminInput"))
        self.editDuty.setPlaceholderText(_translate("MainWindow", "Bağlı olduğu birim"))
        self.btnSaveData.setProperty("class", _translate("MainWindow", "saveBtn"))
        self.btnSaveData.setText(_translate("MainWindow", "VERİLERİ GÜNCELLE VE KAYDET"))
        self.label_19.setProperty("class", _translate("MainWindow", "pageHeader"))
        self.label_19.setText(_translate("MainWindow", "Sistem Tema Ayarları"))
        self.btnColorSidebar.setProperty("class", _translate("MainWindow", "colorBtn"))
        self.btnColorSidebar.setText(_translate("MainWindow", "Sol Menü Rengini Değiştir"))
        self.btnColorBg.setProperty("class", _translate("MainWindow", "colorBtn"))
        self.btnColorBg.setText(_translate("MainWindow", "Ana Arka Plan Rengini Değiştir"))
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
