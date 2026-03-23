import streamlit as st
import mysql.connector

# --- FUNGSI DATABASE ---
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="sistem_pakar_pencernaan"
    )

# Kembali menggunakan pengecekan berdasarkan NAMA saja
def get_user(name):
    conn = connect_db()
    # Tambahkan buffered=True di sini agar tidak error saat ada data ganda
    cursor = conn.cursor(dictionary=True, buffered=True) 
    cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def register_user(name, gender, age):
    conn = connect_db()
    cursor = conn.cursor(buffered=True) # Tambahkan di sini
    cursor.execute("""
        INSERT INTO users (name, gender, age, consent)
        VALUES (%s, %s, %s, %s)
    """, (name, gender, age, 1))
    conn.commit()
    user_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return user_id

def update_user(name, gender, age):
    conn = connect_db()
    cursor = conn.cursor(buffered=True) # Tambahkan di sini
    cursor.execute("""
        UPDATE users 
        SET gender = %s, age = %s 
        WHERE name = %s
    """, (gender, age, name))
    conn.commit()
    cursor.close()
    conn.close()

# --- TAMPILAN ANTARMUKA (UI) ---
st.title("Sistem Pakar Pencernaan")

tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register / Update"])

# --- BAGIAN LOGIN ---
with tab_login:
    st.subheader("Masuk ke Akun Anda")
    login_name = st.text_input("Nama", key="input_login_name")
    
    # Kolom umur sudah dihilangkan agar login lebih simpel
    if st.button("Login", key="btn_login"):
        if not login_name:
            st.error("Nama wajib diisi!")
        else:
            user = get_user(login_name)
            if user:
                st.success("Login berhasil! Mengalihkan...")
                st.session_state.user_id = user["id"]
                st.switch_page("pages/app.py")
            else:
                st.error("Akun belum terdaftar. Silakan pindah ke tab 'Register / Update' untuk mendaftar.")

# --- BAGIAN REGISTER ---
with tab_register:
    st.subheader("Buat Akun Baru / Perbarui Data")
    reg_name = st.text_input("Nama Lengkap", key="input_reg_name")
    reg_gender = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"], key="input_reg_gender")
    reg_age = st.number_input("Umur", min_value=1, max_value=120, value=20, key="input_reg_age")

    if st.button("Simpan & Masuk", key="btn_register"):
        if not reg_name:
            st.error("Nama wajib diisi!")
        else:
            # Cek apakah nama sudah ada di database
            cek_user = get_user(reg_name)
            
            if cek_user:
                # JIKA NAMA SUDAH ADA: Update data umurnya
                update_user(reg_name, reg_gender, reg_age)
                st.success(f"Data milik {reg_name} berhasil diperbarui! Mengalihkan...")
                # Gunakan ID lama karena datanya cuma di-update
                st.session_state.user_id = cek_user["id"] 
                st.switch_page("pages/app.py")
            else:
                # JIKA NAMA BELUM ADA: Bikin data baru
                user_id = register_user(reg_name, reg_gender, reg_age)
                st.success("Registrasi berhasil! Mengalihkan...")
                st.session_state.user_id = user_id
                st.switch_page("pages/app.py")