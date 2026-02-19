import streamlit as st
import mysql.connector

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


st.title("Login Sistem Pakar")

name = st.text_input("Nama")
gender = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan", "Lainnya"])
age = st.number_input("Umur", min_value=1, max_value=120, value=20)

if st.button("Login / Register"):

    if not name:
        st.error("Nama wajib diisi")
    else:
        user = get_user(name)

        if user:
            st.success("Login berhasil")
            st.session_state.user_id = user["id"]
            st.switch_page("pages/app.py")
        else:
            user_id = register_user(name, gender, age)
            st.success("Registrasi berhasil")
            st.session_state.user_id = user_id
            st.switch_page("pages/app.py")
