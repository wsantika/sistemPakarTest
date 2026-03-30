# 🩺 Sistem Pakar Diagnosa Masalah Pencernaan (Neuro-Symbolic AI)

Aplikasi sistem pakar berbasis antarmuka web interaktif (Streamlit) untuk mendiagnosis penyakit saluran pencernaan pada manusia. Sistem ini menggunakan arsitektur **Neuro-Symbolic AI**, yang menggabungkan akurasi matematis algoritma **Certainty Factor (CF)** dengan kemampuan interaktif generatif dari **Context-Aware Large Language Model (LLM)**.

Data kepastian pakar (CF) disintesis secara langsung dari berbagai literatur jurnal ilmiah terakreditasi untuk menjamin validitas hasil diagnosis.

---

## ✨ Fitur Utama

- **Autentikasi Pengguna:** Sistem _Login_ dan _Register_ terintegrasi database.
- **Diagnosa Berbasis Gejala (CF):** Kalkulasi tingkat kepastian penyakit berdasarkan gejala klinis yang dialami pengguna.
- **Integrasi Faktor Risiko:** Penyesuaian nilai _Initial Belief_ menggunakan parameter Gaya Hidup (Skor BMI, Merokok, Makanan Pedas).
- **Riwayat Diagnosa:** Penyimpanan otomatis hasil diagnosis pengguna ke dalam database MySQL.
- **Evidence-Based Information:** Penjelasan penyakit, saran, dan pencegahan yang dilengkapi dengan sitasi dan referensi jurnal medis.
- **Guardrailed LLM Chatbot:** Asisten AI cerdas (Tab 3) yang dibatasi konteksnya (_Prompt Engineering_) agar hanya menjawab sesuai hasil diagnosis dan kondisi gaya hidup pengguna (anti-halusinasi).

---

## 📂 Struktur Direktori Proyek

```text
📁 sp-masalahpencernaan/
│
├── 📁 database/             # Modul untuk interaksi dengan MySQL
│   ├── migrate.py           # Script pembuat database & tabel (mirip artisan migrate)
│   ├── models.py            # Kumpulan fungsi query CRUD
│   └── seeder.py            # Script penyuntik Master Data (Penyakit, Gejala, Aturan Pakar)
│
├── 📁 pages/
│   └── dashboard.py         # Halaman Dasbor Utama (Tab Diagnosa, Info Medis, Chatbot)
│
├── .env                     # Konfigurasi kredensial keamanan database (Abaikan dari Git)
├── user.py                  # Entry point aplikasi (Halaman Login & Register)
└── README.md                # Dokumentasi proyek
```

---

## 🛠️ Persyaratan Sistem (Prerequisites)

Sebelum menjalankan proyek ini, pastikan komputer Anda telah menginstal perangkat lunak berikut:

- **Python** (Versi 3.8 atau lebih baru)
- **MySQL Server** (Bisa menggunakan XAMPP, MAMP, atau Laragon)

---

## 🚀 Panduan Instalasi & Setup

### 1. Clone atau Unduh Repositori

Buka terminal/Command Prompt, lalu arahkan ke direktori tempat Anda ingin menyimpan proyek ini.

```bash
git clone https://github.com/wsantika/sp-masalahpencernaan.git
cd sp-masalahpencernaan
```

### 2. Instalasi Library Python

Instal seluruh dependensi yang dibutuhkan oleh aplikasi:

```bash
pip install streamlit mysql-connector-python python-dotenv numpy pandas
```

### 3. Konfigurasi Environment (`.env`)

Pastikan terdapat file bernama `.env` di folder utama proyek (sejajar dengan file `user.py`). Buka dan sesuaikan dengan kredensial MySQL lokal Anda:

```env
DB_HOST=localhost
DB_USER=root
DB_PASS=
DB_NAME=sistem_pakar_pencernaan
```

> **Catatan:** Kosongkan `DB_PASS` jika Anda menggunakan XAMPP versi default.

### 4. Migrasi Database

Nyalakan modul **MySQL** pada XAMPP/Laragon Anda, lalu jalankan script migrasi untuk membentuk arsitektur tabel di database:

```bash
python database/migrate.py
```

Jika berhasil, terminal akan menampilkan tanda centang (✔️) untuk pembuatan tabel `users`, `penyakit`, `gejala`, `rules_cf`, `diagnosa`, dan `detail_diagnosa`.

### 5. Seeding Master Data

Suntikkan literatur medis, daftar gejala, dan bobot _Certainty Factor_ pakar ke dalam database:

```bash
python database/seeder.py
```

### 6. Jalankan Aplikasi

Setelah database siap, luncurkan aplikasi antarmuka Streamlit:

```bash
streamlit run user.py
```

Aplikasi akan secara otomatis terbuka di browser default Anda (biasanya di `http://localhost:8501`).

---

## 💡 Cara Penggunaan

1. **Daftar/Masuk:** Buka tab Register untuk membuat akun baru. Isi data diri beserta parameter opsional tinggi/berat badan dan gaya hidup.
2. **Pilih Gejala:** Masuk ke tab **Diagnosa**, centang gejala-gejala klinis yang saat ini sedang dirasakan, lalu klik "Analisis Diagnosa".
3. **Baca Literatur:** Buka tab **Informasi Penyakit** untuk membaca detail penyakit, penanganan, pencegahan, dan daftar pustaka jurnal rujukannya.
4. **Tanya Chatbot:** Buka tab **Chatbot** untuk berkonsultasi lebih lanjut dengan Asisten AI terkait hasil diagnosa tersebut.
