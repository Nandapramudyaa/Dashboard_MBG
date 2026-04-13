import os

# Konten README.md berdasarkan analisis file proyek
readme_content = """# 📊 Dashboard MBG Analytics

**Dashboard MBG (Makan Bergizi Gratis)** adalah aplikasi berbasis web yang dirancang untuk melakukan analisis diskursus publik di media sosial (X/Twitter) terkait program Makan Bergizi Gratis menggunakan algoritma **BERTopic**. Aplikasi ini divisualisasikan menggunakan Streamlit untuk memberikan wawasan mendalam bagi peneliti dan pemangku kepentingan.

## 🚀 Fitur Utama

Aplikasi ini memiliki beberapa modul utama yang dapat diakses melalui sidebar:

* **Executive Summary**: Menampilkan metrik utama seperti total tweet, jumlah kluster topik, skor koherensi model, dan distribusi volume topik (bar & donut chart).
* **Topic Explorer**: Memungkinkan pengguna mengeksplorasi setiap topik secara mendetail melalui *Word Cloud*, bobot kata kunci (*c-TF-IDF*), dan contoh dokumen asli.
* **Trend Analysis**: Visualisasi intensitas pembahasan topik dari waktu ke waktu (berbasis bulan) untuk mengidentifikasi isu yang sedang viral.
* **Model Evaluation**: Evaluasi kualitas topik menggunakan *Lollipop Chart* untuk skor koherensi (c_v) dan *Intertopic Distance Map* (UMAP).
* **Data Preprocessing**: Memberikan transparansi mengenai tahapan pembersihan data dari teks mentah hingga teks final yang siap diproses model.

## 📂 Struktur Folder

``` text
├── .devcontainer/
│   └── devcontainer.json   # Konfigurasi container untuk VS Code
├── my_bertopic_model/      # Folder model BERTopic yang sudah dilatih
├── app.py                  # Script utama aplikasi Streamlit
├── requirements.txt        # Daftar library Python yang dibutuhkan
├── data_hasil_topik.csv    # Dataset hasil pelabelan topik
├── info_topik_lengkap.csv  # Metadata dan skor koherensi per topik
└── trend_waktu_topik.csv   # Data deret waktu untuk analisis tren
```
## 🛠️ Prasyarat
Pastikan Anda telah menginstal Python 3.11 atau versi yang lebih baru. Library utama yang digunakan meliputi:

* **streamlit** & **streamlit-option-menu**
* **bertopic**
* **pandas, numpy, plotly, matplotlib****
* **wordcloud**
* **scikit-learn**

# 📥 Penginstalan
Ikuti langkah-langkah di bawah ini untuk menjalankan dashboard di lingkungan lokal Anda:

## 1. Persiapan Folder
Pastikan semua file data (.csv) dan folder model (my_bertopic_model) berada dalam satu direktori dengan app.py.

## 2. Buat Virtual Environment (Opsional)
``` bash
python -m venv venv
# Aktifkan di Windows:
venv\\Scripts\\activate
# Aktifkan di macOS/Linux:
source venv/bin/activate
```

## 3. Instal Dependencies
Gunakan file requirements.txt untuk menginstal semua library yang diperlukan:
``` bash 
pip install -r requirements.txt
```

## 4. Jalankan Aplikasi
Jalankan perintah berikut untuk membuka dashboard di browser Anda:
``` bash
streamlit run app.py
```
Secara default, aplikasi akan dapat diakses di http://localhost:8501.

# 🐳 Penggunaan dengan Dev Container
Jika Anda menggunakan VS Code atau GitHub Codespaces, Anda dapat menggunakan konfigurasi .devcontainer. Container akan secara otomatis menginstal semua paket dan menjalankan server Streamlit saat diaktifkan.



Peneliti:
* Nanda Pramudya Lestari
* Universitas Tiga Serangkai

Copyright @ 2026 - TSU-Nanda