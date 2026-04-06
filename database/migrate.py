import os
import mysql.connector
from dotenv import load_dotenv

# Load variabel dari file .env
load_dotenv()

def migrate():
    print("Mulai proses migrasi database...")
    
    # Koneksi awal ke MySQL (tanpa pilih database dulu)
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )
    cursor = conn.cursor()

    # 1. Buat Database jika belum ada
    db_name = os.getenv("DB_NAME")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    print(f"✔️ Database '{db_name}' siap.")
    
    # Gunakan database tersebut
    cursor.execute(f"USE {db_name}")

    # 2. Query Pembuatan Tabel (Sesuai ERD)
    tabel_queries = {
        "users": """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                gender ENUM('Laki-laki', 'Perempuan') NOT NULL,
                age INT NOT NULL,
                consent BOOLEAN NOT NULL DEFAULT 1
            )
        """,
        "penyakit": """
            CREATE TABLE IF NOT EXISTS penyakit (
                id INT AUTO_INCREMENT PRIMARY KEY,
                kode_penyakit VARCHAR(10) UNIQUE NOT NULL,
                nama_penyakit VARCHAR(100) NOT NULL,
                deskripsi TEXT,
                saran TEXT,
                pencegahan TEXT,
                referensi TEXT
            )
        """,
        "gejala": """
            CREATE TABLE IF NOT EXISTS gejala (
                id INT AUTO_INCREMENT PRIMARY KEY,
                kode_gejala VARCHAR(10) UNIQUE NOT NULL,
                nama_gejala VARCHAR(255) NOT NULL
            )
        """,
        "rules_cf": """
            CREATE TABLE IF NOT EXISTS rules_cf (
                id INT AUTO_INCREMENT PRIMARY KEY,
                kode_penyakit VARCHAR(10) NOT NULL,
                kode_gejala VARCHAR(10) NOT NULL,
                nilai_cf FLOAT NOT NULL,
                FOREIGN KEY (kode_penyakit) REFERENCES penyakit(kode_penyakit) ON DELETE CASCADE,
                FOREIGN KEY (kode_gejala) REFERENCES gejala(kode_gejala) ON DELETE CASCADE
            )
        """,
        "diagnosa": """
            CREATE TABLE IF NOT EXISTS diagnosa (
                id_diagnosa INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                penyakit VARCHAR(100) NOT NULL,
                nilai_cf FLOAT NOT NULL,
                tanggal DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """,
        "detail_diagnosa": """
            CREATE TABLE IF NOT EXISTS detail_diagnosa (
                id_detail INT AUTO_INCREMENT PRIMARY KEY,
                id_diagnosa INT NOT NULL,
                kode_gejala VARCHAR(10) NOT NULL,
                FOREIGN KEY (id_diagnosa) REFERENCES diagnosa(id_diagnosa) ON DELETE CASCADE
            )
        """
    }

    # Eksekusi pembuatan masing-masing tabel
    for nama_tabel, query in tabel_queries.items():
        try:
            cursor.execute(query)
            print(f"✔️ Tabel '{nama_tabel}' berhasil di-migrate.")
        except Exception as e:
            print(f"❌ Gagal membuat tabel '{nama_tabel}': {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print("🎉 Migrasi selesai!")

if __name__ == "__main__":
    migrate()