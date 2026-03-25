import streamlit as st
import pickle
import numpy as np
import mysql.connector
import json
import sys
import os

# --- MENGHUBUNGKAN KE FILE penyakit.py ---
# Karena penyakit.py ada di folder luar (bukan di dalam pages), kita perlu baris ini
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from penyakit import info_penyakit

# --- PENJAGA KEAMANAN HALAMAN ---
if "user_id" not in st.session_state:
    st.warning("Silakan login terlebih dahulu")
    st.switch_page("user.py") # Lempar balik ke login jika belum
    st.stop()

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="sistem_pakar_pencernaan"
    )

@st.cache_resource
def load_model():
    with open("model_pencernaan.pkl", "rb") as f:
        return pickle.load(f)

model = load_model()

# --- TAMPILAN UTAMA ---
# Tombol logout ditaruh di atas pojok kanan pakai kolom biar rapi
col_title, col_logout = st.columns([4, 1])
with col_title:
    st.title("Dashboard Sistem Pakar")
with col_logout:
    st.write("") # Spasi kosong
    if st.button("Logout"):
        st.session_state.clear()
        st.switch_page("user.py")

tabs = st.tabs(["🩺 Diagnosa", "📚 Informasi Penyakit", "🤖 Chatbot"])

# --- TAB 1: DIAGNOSA ---
with tabs[0]:
    st.subheader("Pilih Gejala yang Anda Alami")

    symptoms_labels = [
        "Nyeri ulu hati", "Mual", "Muntah", "Perut kembung",
        "Perih saat lapar", "Panas di dada", "Asam naik",
        "Diare", "BAB cair", "Sulit BAB",
        "BAB keras", "BAB berdarah",
        "Nafsu makan turun", "Berat badan turun"
    ]

    selected = []
    col_gejala1, col_gejala2 = st.columns(2)
    for i, s in enumerate(symptoms_labels):
        if i % 2 == 0:
            with col_gejala1:
                selected.append(st.checkbox(s))
        else:
            with col_gejala2:
                selected.append(st.checkbox(s))

    st.write("")
    if st.button("Analisis Diagnosa", type="primary"):
        input_data = np.array([selected]).astype(int)

        ml_pred = model.predict(input_data)[0]
        ml_prob = np.max(model.predict_proba(input_data)) * 100

        # SIMPAN HASIL DIAGNOSA KE SESSION STATE AGAR BISA DIBACA OLEH TAB 2
        st.session_state.hasil_diagnosa = ml_pred

        st.success(f"**Hasil Analisis:** Anda terindikasi mengalami **{ml_pred}** dengan tingkat keyakinan **{ml_prob:.2f}%**")
        st.info("👉 Silakan buka tab **Informasi Penyakit** di atas untuk membaca penjelasan, saran, dan cara pencegahannya.")

# --- TAB 2: INFORMASI PENYAKIT (FOKUS 1 PENYAKIT SAJA) ---
with tabs[1]:
    st.subheader("Detail Informasi Penyakit Anda")
    
    # Cek apakah user sudah melakukan diagnosa sebelumnya
    if "hasil_diagnosa" in st.session_state:
        penyakit_user = st.session_state.hasil_diagnosa
        
        if penyakit_user in info_penyakit:
            detail = info_penyakit[penyakit_user]
            
            st.markdown(f"### 🩺 {penyakit_user}")
            st.write("---")
            
            st.write("**📝 Penjelasan:**")
            st.write(detail["deskripsi"])
            
            st.write("")
            st.write("**💊 Saran Penanganan:**")
            st.warning(detail["saran"])
            
            st.write("")
            st.write("**🛡️ Cara Mencegah:**")
            st.success(detail["pencegahan"])
        else:
            st.error("Detail informasi untuk penyakit ini belum tersedia di database kami.")
    else:
        # Tampilan jika user langsung klik Tab 2 sebelum diagnosa
        st.info("ℹ️ Anda belum melakukan diagnosa. Silakan kembali ke tab **Diagnosa** dan periksa gejala Anda terlebih dahulu untuk melihat informasi penyakit di sini.")

# --- TAB 3: CHATBOT ---
with tabs[2]:
    st.subheader("Asisten Cerdas Pencernaan")
    st.write("Chatbot akan dikembangkan di sini nanti.")