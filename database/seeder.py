# File: database/seeder.py
import sys
import os
import mysql.connector
from dotenv import load_dotenv

# Menambahkan path folder utama agar bisa membaca file pakar_rules.py & penyakit.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from penyakit import info_penyakit
from pakar_rules import daftar_gejala, rules_cf

load_dotenv()

def seed_database():
    print("Memulai proses Seeding Database...")
    
    # Buka koneksi ke database
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME")
    )
    cursor = conn.cursor()

    # Mapping Kode Penyakit (karena di ERD kita butuh kode_penyakit seperti P01, P02)
    penyakit_kode = {
        "GERD": "P01",
        "Gastritis": "P02",
        "Apendisitis": "P03",
        "Disentri": "P04",
        "Diare": "P05"
    }

    try:
        # 1. Seed Tabel Penyakit
        for nama, detail in info_penyakit.items():
            kode = penyakit_kode.get(nama)
            # Pakai INSERT IGNORE agar tidak error/duplikat kalau file di-run 2 kali
            sql = "INSERT IGNORE INTO penyakit (kode_penyakit, nama_penyakit, deskripsi, saran, pencegahan) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (kode, nama, detail['deskripsi'], detail['saran'], detail['pencegahan']))
        print("✔️ Data Penyakit berhasil di-seed.")

        # 2. Seed Tabel Gejala
        for kode, nama in daftar_gejala.items():
            sql = "INSERT IGNORE INTO gejala (kode_gejala, nama_gejala) VALUES (%s, %s)"
            cursor.execute(sql, (kode, nama))
        print("✔️ Data Gejala berhasil di-seed.")

        # 3. Seed Tabel Rules CF
        for nama_penyakit, gejala_dict in rules_cf.items():
            kode_penyakit = penyakit_kode.get(nama_penyakit)
            for kode_gejala, nilai_cf in gejala_dict.items():
                sql = "INSERT IGNORE INTO rules_cf (kode_penyakit, kode_gejala, nilai_cf) VALUES (%s, %s, %s)"
                cursor.execute(sql, (kode_penyakit, kode_gejala, nilai_cf))
        print("✔️ Data Rules (Bobot Pakar) berhasil di-seed.")

        # Simpan perubahan
        conn.commit()
        print("🎉 Seeding Selesai! Database-mu sekarang sudah secerdas sistem pakar.")

    except Exception as e:
        print(f"❌ Terjadi kesalahan saat seeding: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    seed_database()