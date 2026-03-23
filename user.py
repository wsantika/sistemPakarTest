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

# 1. Fungsi untuk LOGIN (Mengecek Nama DAN Umur harus cocok)
def get_user_for_login(name, age):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True, buffered=True)
    cursor.execute("SELECT * FROM users WHERE name = %s AND age = %s", (name, age))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

# 2. Fungsi untuk CEK NAMA SAJA (Digunakan untuk Update/Register)
def get_user_by_name(name):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True, buffered=True)
    cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def register_user(name, gender, age):
    conn = connect_db()
    cursor = conn.cursor(buffered=True)
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
    cursor = conn.cursor(buffered=True)
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
    
    # Menambahkan input umur dengan placeholder sesuai idemu
    login_age = st.number_input("Umur", min_value=1, max_value=120, value=10, placeholder="Umur saat ini", key="input_login_age")
    
    if st.button("Login", key="btn_login"):
        if not login_name or login_age is None:
            st.error("Nama dan Umur wajib diisi!")
        else:
            # Cek kecocokan nama dan umur
            exact_user = get_user_for_login(login_name, login_age)
            
            if exact_user:
                st.success("Login berhasil! Mengalihkan...")
                st.session_state.user_id = exact_user["id"]
                st.switch_page("pages/app.py")
            else:
                # Jika tidak cocok, kita cek apakah namanya sebenarnya ada di database
                name_only_user = get_user_by_name(login_name)
                if name_only_user:
                    st.warning("Umur tidak cocok dengan data sebelumnya! Jika umur Anda bertambah, silakan perbarui data di tab 'Register / Update'.")
                else:
                    st.error("Akun belum terdaftar. Silakan pindah ke tab 'Register / Update' untuk mendaftar.")

# --- BAGIAN REGISTER / UPDATE ---
with tab_register:
    st.subheader("Buat Akun Baru / Perbarui Data")
    reg_name = st.text_input("Nama Lengkap", key="input_reg_name")
    reg_gender = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"], key="input_reg_gender")
    
    # Di sini tetap kita beri value default agar user tidak bingung saat mendaftar
    reg_age = st.number_input("Umur", min_value=1, max_value=120, value=10, key="input_reg_age")

    if st.button("Simpan & Masuk", key="btn_register"):
        if not reg_name:
            st.error("Nama wajib diisi!")
        else:
            cek_user = get_user_by_name(reg_name)
            
            if cek_user:
                update_user(reg_name, reg_gender, reg_age)
                st.success(f"Data umur/gender milik {reg_name} berhasil diperbarui! Mengalihkan...")
                st.session_state.user_id = cek_user["id"] 
                st.switch_page("pages/app.py")
            else:
                user_id = register_user(reg_name, reg_gender, reg_age)
                st.success("Registrasi berhasil! Mengalihkan...")
                st.session_state.user_id = user_id
                st.switch_page("pages/app.py")