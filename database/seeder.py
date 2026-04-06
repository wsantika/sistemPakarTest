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
    
    try:
        # Buka koneksi ke database
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", ""),
            database=os.getenv("DB_NAME", "sistem_pakar_pencernaan")
        )
        cursor = conn.cursor()

        # Mapping Kode Penyakit agar sesuai urutan (P01 - P05)
        penyakit_kode = {
            "GERD": "P01",
            "Gastritis": "P02",
            "Apendisitis": "P03",
            "Disentri": "P04",
            "Diare": "P05"
        }

        # --- 1. SEED TABEL PENYAKIT ---
        # Menggunakan INSERT ON DUPLICATE KEY UPDATE agar data lama tertimpa dengan otomatis
        sql_penyakit = """
            INSERT INTO penyakit (kode_penyakit, nama_penyakit, deskripsi, saran, pencegahan, referensi) 
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            deskripsi=VALUES(deskripsi), saran=VALUES(saran), pencegahan=VALUES(pencegahan), referensi=VALUES(referensi)
        """
        
        # Looping membaca format dictionary dari file penyakit.py
        for nama, detail in info_penyakit.items():
            kode = penyakit_kode.get(nama)
            val = (kode, nama, detail['deskripsi'], detail['saran'], detail['pencegahan'], detail['referensi'])
            cursor.execute(sql_penyakit, val)
            
        print("✔️ Data Penyakit & Referensi Jurnal berhasil di-seed!")

        # --- 2. SEED TABEL GEJALA ---
        sql_gejala = "INSERT IGNORE INTO gejala (kode_gejala, nama_gejala) VALUES (%s, %s)"
        for kode, nama in daftar_gejala.items():
            cursor.execute(sql_gejala, (kode, nama))
        print("✔️ Data Gejala berhasil di-seed!")

        # --- 3. SEED TABEL RULES CF ---
        sql_rules = "INSERT IGNORE INTO rules_cf (kode_penyakit, kode_gejala, nilai_cf) VALUES (%s, %s, %s)"
        for nama_penyakit, gejala_dict in rules_cf.items():
            kode_penyakit = penyakit_kode.get(nama_penyakit)
            for kode_gejala, nilai_cf in gejala_dict.items():
                cursor.execute(sql_rules, (kode_penyakit, kode_gejala, nilai_cf))
        print("✔️ Data Rules (Bobot Pakar) berhasil di-seed!")

        # Simpan perubahan permanen ke database
        conn.commit()
        print("🎉 SEEDING SUKSES! Database kamu sudah sinkron dengan data terbaru.")

    except Exception as e:
        print(f"❌ Terjadi kesalahan saat seeding: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    seed_database()