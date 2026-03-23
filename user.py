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

def get_user(name):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def register_user(name, gender, age):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (name, gender, age, consent)
        VALUES (%s, %s, %s, %s)
    """, (name, gender, age, 1))
    conn.commit()
    user_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return user_id

# --- TAMPILAN ANTARMUKA (UI) ---
st.title("Sistem Pakar Pencernaan")

# Membuat 2 Tab untuk memisahkan Login dan Register
tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

# --- BAGIAN LOGIN ---
with tab_login:
    st.subheader("Masuk ke Akun Anda")
    # Tambahkan parameter 'key' agar tidak bentrok dengan input di tab sebelah
    login_name = st.text_input("Nama", key="input_login_name")
    
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
                st.error("Akun belum terdaftar. Silakan pindah ke tab 'Register' untuk mendaftar.")

# --- BAGIAN REGISTER ---
with tab_register:
    st.subheader("Buat Akun Baru")
    reg_name = st.text_input("Nama Lengkap", key="input_reg_name")
    reg_gender = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"], key="input_reg_gender")
    reg_age = st.number_input("Umur", min_value=1, max_value=120, value=20, key="input_reg_age")

    if st.button("Register", key="btn_register"):
        if not reg_name:
            st.error("Nama wajib diisi!")
        else:
            # Cek dulu apakah nama sudah dipakai orang lain
            cek_user = get_user(reg_name)
            if cek_user:
                st.warning("Nama sudah terdaftar! Silakan pindah ke tab 'Login' untuk masuk.")
            else:
                # Jika nama belum ada, masukkan data baru ke database
                user_id = register_user(reg_name, reg_gender, reg_age)
                st.success("Registrasi berhasil! Mengalihkan...")
                st.session_state.user_id = user_id
                st.switch_page("pages/app.py")