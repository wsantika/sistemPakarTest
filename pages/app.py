import streamlit as st
import pickle
import numpy as np
import mysql.connector
import json

if "user_id" not in st.session_state:
    st.warning("Silakan login terlebih dahulu")
    st.stop()

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="sistem_pakar_pencernaan"
    )

if "user_id" not in st.session_state:
    st.warning("Silakan login terlebih dahulu")
    st.stop()

@st.cache_resource
def load_model():
    with open("model_pencernaan.pkl", "rb") as f:
        return pickle.load(f)

model = load_model()

st.title("Dashboard Sistem Pakar")

if st.button("Logout"):
    st.session_state.clear()
    st.switch_page("user.py")

tabs = st.tabs(["Diagnosa", "Informasi Penyakit", "Chatbot"])

# TAB 1
with tabs[0]:
    st.subheader("Pilih Gejala")

    symptoms_labels = [
        "Nyeri ulu hati", "Mual", "Muntah", "Perut kembung",
        "Perih saat lapar", "Panas di dada", "Asam naik",
        "Diare", "BAB cair", "Sulit BAB",
        "BAB keras", "BAB berdarah",
        "Nafsu makan turun", "Berat badan turun"
    ]

    selected = []
    for s in symptoms_labels:
        selected.append(st.checkbox(s))

    if st.button("Diagnosa"):
        input_data = np.array([selected]).astype(int)

        ml_pred = model.predict(input_data)[0]
        ml_prob = np.max(model.predict_proba(input_data)) * 100

        st.success(f"Hasil ML: {ml_pred} ({ml_prob:.2f}%)")

# TAB 2
with tabs[1]:
    st.write("Informasi penyakit akan ditampilkan di sini")

# TAB 3
with tabs[2]:
    st.write("Chatbot akan dikembangkan di sini")
