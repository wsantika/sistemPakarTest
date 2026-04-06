# File: database/models.py
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# --- FUNGSI KONEKSI INTI ---
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME")
    )

# --- MODEL UNTUK TABEL USERS ---
def get_user_for_login(name, age):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE name = %s AND age = %s", (name, age))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def get_user_by_name(name):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def register_user(name, gender, age):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, gender, age, consent) VALUES (%s, %s, %s, %s)", (name, gender, age, 1))
    conn.commit()
    user_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return user_id

def update_user(name, gender, age):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET gender = %s, age = %s WHERE name = %s", (gender, age, name))
    conn.commit()
    cursor.close()
    conn.close()

# --- MODEL UNTUK TABEL DIAGNOSA ---
def simpan_riwayat_diagnosa(user_id, penyakit, nilai_cf, gejala_terpilih):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Simpan ke tabel diagnosa
        cursor.execute("INSERT INTO diagnosa (user_id, penyakit, nilai_cf) VALUES (%s, %s, %s)", (user_id, penyakit, nilai_cf))
        id_diagnosa = cursor.lastrowid
        
        # Simpan ke tabel detail_diagnosa
        for kode in gejala_terpilih:
            cursor.execute("INSERT INTO detail_diagnosa (id_diagnosa, kode_gejala) VALUES (%s, %s)", (id_diagnosa, kode))
            
        conn.commit()
        return True
    except Exception as e:
        print(f"Error DB: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# --- MODEL UNTUK KNOWLEDGE BASE (MASTER DATA) ---

def get_semua_gejala():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT kode_gejala, nama_gejala FROM gejala")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    # Ubah menjadi format dictionary: {"G01": "Nyeri...", "G02": "Kembung..."}
    return {row['kode_gejala']: row['nama_gejala'] for row in results}

def get_info_penyakit():
    db = get_connection()  # ← isi ini
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT nama_penyakit, deskripsi, saran, pencegahan, referensi FROM penyakit")
    data = cursor.fetchall()
    
    info = {}
    for row in data:
        info[row['nama_penyakit']] = {
            "deskripsi": row['deskripsi'],
            "saran": row['saran'],
            "pencegahan": row['pencegahan'],
            "referensi": row['referensi']
        }
        
    cursor.close()
    db.close()
    return info
def get_rules_cf():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    # Join tabel rules_cf dan penyakit agar kita mendapatkan "nama_penyakit" (bukan kodenya saja)
    query = """
        SELECT p.nama_penyakit, r.kode_gejala, r.nilai_cf 
        FROM rules_cf r
        JOIN penyakit p ON r.kode_penyakit = p.kode_penyakit
    """
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Ubah menjadi format: {"GERD": {"G01": 0.8, "G02": 1.0}}
    rules = {}
    for row in results:
        penyakit = row['nama_penyakit']
        gejala = row['kode_gejala']
        cf = row['nilai_cf']
        
        if penyakit not in rules:
            rules[penyakit] = {}
        rules[penyakit][gejala] = cf
    return rules