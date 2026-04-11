# File: database/seeder.py
import sys
import os
import mysql.connector
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from penyakit import info_penyakit
from pakar_rules import daftar_gejala, rules_cf

load_dotenv()

def seed_database():
    print("Memulai proses Seeding Database...")
    
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", ""),
            database=os.getenv("DB_NAME", "sistem_pakar_pencernaan")
        )
        cursor = conn.cursor()

        # Mapping Kode Penyakit yang 100% sama dengan pakar_rules.py
        penyakit_kode = {
            "Refluks (GERD)": "P01",
            "Infeksi Saluran Pencernaan (Colera)": "P02",
            "Maag (Dispepsia)": "P03",
            "Radang Hati (Hepatitis)": "P04",
            "Radang Usus Buntu (Apendisitis)": "P05",
            "Gangguan Pencernaan (Disentry)": "P06"
        }

        # --- 1. SEED TABEL PENYAKIT (Force Update Nama) ---
        sql_penyakit = """
            INSERT INTO penyakit (kode_penyakit, nama_penyakit, deskripsi, saran, pencegahan, referensi) 
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            nama_penyakit=VALUES(nama_penyakit),
            deskripsi=VALUES(deskripsi), 
            saran=VALUES(saran), 
            pencegahan=VALUES(pencegahan), 
            referensi=VALUES(referensi)
        """
        for nama, detail in info_penyakit.items():
            kode = penyakit_kode.get(nama)
            val = (kode, nama, detail['deskripsi'], detail['saran'], detail['pencegahan'], detail['referensi'])
            cursor.execute(sql_penyakit, val)
        print("✔️ Data Penyakit & Referensi Jurnal berhasil di-seed!")

        # --- 2. SEED TABEL GEJALA (Force Update Gejala) ---
        sql_gejala = """
            INSERT INTO gejala (kode_gejala, nama_gejala) VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE nama_gejala=VALUES(nama_gejala)
        """
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