# Virtual Painter dengan Gestur Tangan

Sebuah aplikasi real-time yang memungkinkan pengguna untuk menggambar di layar hanya dengan menggunakan gerakan tangan di depan webcam. Proyek ini memanfaatkan **OpenCV** untuk pemrosesan gambar dan **MediaPipe** dari Google untuk deteksi landmark tangan yang akurat.

---

## ✨ Fitur Utama

* **Menggambar Real-Time**: Gambar garis di kanvas virtual hanya dengan menggerakkan jari.
* **Kontrol Berbasis Gestur**:

  * **Mode Menggambar**: Kuas aktif saat jari telunjuk dan jari tengah dirapatkan.
  * **Mode Memilih**: Pilih warna atau penghapus dengan gestur pinch (ibu jari + telunjuk).
* **Palet Warna Interaktif**: Ganti warna kuas (Merah, Hijau, Biru) atau aktifkan penghapus melalui UI di bagian atas layar.
* **Visualisasi Tangan**: Kerangka landmark tangan ditampilkan secara langsung sebagai feedback visual.

---

## 🛠️ Teknologi yang Digunakan

* Python 3.x
* OpenCV (`opencv-python`)
* MediaPipe (`mediapipe`)
* NumPy

---

## ⚙️ Panduan Instalasi dan Penggunaan

### 1. Persiapan Awal

* Pastikan **Python 3.8+** sudah terinstal.
* Clone repositori ini ke komputer Anda:

```bash
git clone https://github.com/ahnafyura/AirDrawing.git
```

### 2. Buat Virtual Environment

Disarankan menggunakan virtual environment agar dependensi terisolasi.

```bash
# Membuat venv
python -m venv venv

# Aktifkan (Windows)
.\venv\Scripts\Activate.ps1

# Aktifkan (macOS/Linux)
source venv/bin/activate
```

### 3. Instal Dependensi

Buat file `requirements.txt` dengan:

```bash
pip freeze > requirements.txt
```

Instal semua library dengan:

```bash
pip install -r requirements.txt
```

### 4. Jalankan Aplikasi

```bash
python virtual_painter_revised.py
```

Aplikasi akan membuka jendela webcam. Kini Anda siap melukis dengan gerakan tangan!

---

## 🖐️ Cara Kerja Kontrol Gestur

* **Menggambar**: Rapatkan jari telunjuk + jari tengah, lalu gerakkan tangan.
* **Memilih Warna/Penghapus**: Lakukan pinch (ibu jari + telunjuk) dan arahkan ke kotak warna di atas layar.
* **Mode Tunggu**: Posisi jari normal → tidak ada aksi.
* **Keluar**: Tekan tombol **`s`** di keyboard.

---

## 📜 Lisensi

Proyek ini dilisensikan di bawah **MIT License**.
