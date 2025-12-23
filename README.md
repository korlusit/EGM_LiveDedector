# 🛡️ EGM - Entegre Güvenlik ve Takip Sistemi

![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![GUI](https://img.shields.io/badge/GUI-PyQt6-green)
![AI](https://img.shields.io/badge/AI-YOLOv11%20%7C%20InsightFace%20%7C%20EasyOCR-orange)

## 🎯 Projenin Amacı

Bu proje, emniyet mensuplarının (polislerin) sahada veya merkezde rahatlıkla kullanabileceği, kullanıcı dostu arayüze sahip bir masaüstü uygulaması olarak geliştirilmiştir. Projenin temel amacı, **Suçlu Tespiti** ve **Plaka Tespiti** işlemlerini yapay zeka desteğiyle otomatikleştirerek güvenlik süreçlerini hızlandırmaktır.

Arayüz tasarımı **PyQt6** kütüphanesi kullanılarak gerçekleştirilmiş olup, sistemin bazı bölümleri dinamik Python kodlarıyla, bazı bölümleri ise doğrudan PyQt yapılarıyla optimize edilmiştir.

---

## 🔐 Giriş Sistemi ve Biyometrik Doğrulama

Uygulama, yüksek güvenlik standartları gereği çift aşamalı bir biyometrik doğrulama sistemi kullanır:

1.  **Kayıt Aşaması:** Kullanıcı ilk kez sisteme dahil olurken kamerasını açar, yüzünü sisteme tanıtır ve adını girerek kaydını tamamlar.
2.  **Giriş (Login) Aşaması:** Kayıt işleminden sonraki girişlerde, kullanıcıdan tekrar yüzünü kameraya göstermesi istenir.
3.  **Eşleştirme:** Sistem, giriş yapmaya çalışan kişinin yüzü ile kayıtlı yüzü karşılaştırır. Eşleşme başarılı olursa ana ekrana erişim izni verilir.

---

## 🚀 Ana Modüller ve Uygulamalar

Sistem içerisinde iki temel yapay zeka modülü aktif olarak çalışmaktadır:

### 1. 👤 Yüz Tanıma Uygulaması (GBT Modülü)
Kamera akışındaki yüzleri tarayarak veritabanındaki kayıtlarla karşılaştıran güvenlik modülüdür.
* **Çalışma Prensibi:** Kameralara yansıyan kişiler, önceden sisteme yüklenmiş **suçlu** ve **masum** bireylerin veri setleriyle anlık olarak kıyaslanır.
* **Görsel Uyarı:** Veritabanında suç kaydı olan bir kişi tespit edildiğinde, yüzü **kırmızı kare** içine alınarak operatör uyarılır.
* **Bilgi Paneli:** Tespit edilen suçlunun anlık fotoğrafı ve işlediği suç türü (Örn: Hırsızlık, Firar vb.) sağ taraftaki sidebar bölümünde eş zamanlı olarak listelenir.

### 2. 🚗 Plaka Tanıma Uygulaması (PTS Modülü)
Akan trafik görüntülerinden araç plakalarını tespit edip okuyan modüldür.
* **Görüntü İşleme:** Kameraya yansıyan araçlar tespit edilir ve plaka bölgesi algılanır.
* **Arka Plan İşlemleri:** Algılanan plaka görüntüsü arka planda otomatik olarak **büyütülür ve netleştirilir**.
* **Anlık Takip:** Okunan plaka metni (OCR), sağ sidebar bölümünde anlık olarak gösterilir. Bu sayede ekrandan geçen her aracın plakası operatör tarafından kaçırılmadan takip edilebilir.

---

## 💻 Kullanıcı Arayüzü ve Yönetim

Uygulama, polis memurlarının ihtiyaçlarına göre özelleştirilebilir modüller içerir:

* **Polis Bilgileri:** Kullanıcı, giriş yaptıktan sonra kendi profil bilgilerini görüntüleyebilir.
* **Admin Paneli:** Kullanıcı adı vb. bilgiler buradan değiştirilebilir. Yapılan değişiklikler veritabanına işlenerek hem ana ekranda (Dashboard) hem de profil kısmında **anlık (real-time)** olarak güncellenir.
* **Sistem Ayarları (Kişiselleştirme):** Kullanıcılar, çalışma ortamlarına veya tercihlerine göre uygulamanın sol menü (sidebar) rengini ve ana ekran arka plan rengini değiştirebilirler.

---

## 🛠️ Kullanılan Teknolojiler

| Kütüphane / Araç | Kullanım Alanı |
| :--- | :--- |
| **PyQt6** | Modern ve özelleştirilebilir kullanıcı arayüzü (GUI). |
| **OpenCV** | Kamera akışı yönetimi ve görüntü işleme. |
| **InsightFace** | Yüz tespiti ve biyometrik eşleştirme. |
| **YOLOv11** | Araç ve plaka bölgesi tespiti (Object Detection). |
| **EasyOCR** | Plaka üzerindeki metnin okunması. |
| **SQLite** | Kullanıcı ve log verilerinin tutulması. |

---

## ⚙️ Kurulum ve Çalıştırma

1.  **Repoyu Klonlayın:**
    ```bash
    git clone [https://github.com/KULLANICI_ADINIZ/REPO_ADINIZ.git](https://github.com/KULLANICI_ADINIZ/REPO_ADINIZ.git)
    ```

2.  **Gerekli Kütüphaneleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Uygulamayı Başlatın:**
    ```bash
    python login.py
    ```

---

### ⚠️ Yasal Uyarı
Bu proje eğitim ve akademik sunum amacıyla geliştirilmiş bir simülasyondur. Gerçek Emniyet Genel Müdürlüğü (EGM) verileriyle bir bağlantısı yoktur.