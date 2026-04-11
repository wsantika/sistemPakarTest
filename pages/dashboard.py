import streamlit as st
import sys
import os
import google.generativeai as genai

# --- MENGHUBUNGKAN KE FILE LUAR ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.models import (
    simpan_riwayat_diagnosa, 
    get_semua_gejala, 
    get_info_penyakit, 
    get_rules_cf
)

# --- PENJAGA KEAMANAN HALAMAN ---
if "user_id" not in st.session_state:
    st.warning("Silakan login terlebih dahulu")
    st.switch_page("user.py")
    st.stop()

# --- AMBIL DATA DARI DATABASE (CACHE AGAR CEPAT) ---
@st.cache_data
def load_knowledge_base():
    return get_semua_gejala(), get_info_penyakit(), get_rules_cf()

daftar_gejala, info_penyakit, rules_cf = load_knowledge_base()

# --- FUNGSI ALGORITMA CERTAINTY FACTOR ---
def hitung_cf(gejala_terpilih):
    cf_gabungan = {penyakit: 0.0 for penyakit in rules_cf.keys()}
    
    tb_m = st.session_state.get('tinggi_badan', 165) / 100
    bb_kg = st.session_state.get('berat_badan', 60)
    bmi = bb_kg / (tb_m * tb_m)
    is_merokok = st.session_state.get('merokok', False)
    is_pedas = st.session_state.get('makan_pedas', False)

    # --- PENYESUAIAN NAMA PENYAKIT BERDASARKAN JURNAL TERBARU ---
    if bmi >= 25.0 and "Refluks (GERD)" in cf_gabungan: 
        cf_gabungan["Refluks (GERD)"] = cf_gabungan["Refluks (GERD)"] + 0.20 * (1 - cf_gabungan["Refluks (GERD)"])
    
    if is_merokok and "Refluks (GERD)" in cf_gabungan:
        cf_gabungan["Refluks (GERD)"] = cf_gabungan["Refluks (GERD)"] + 0.15 * (1 - cf_gabungan["Refluks (GERD)"])
    
    if is_pedas:
        if "Maag (Dispepsia)" in cf_gabungan:
            cf_gabungan["Maag (Dispepsia)"] = cf_gabungan["Maag (Dispepsia)"] + 0.25 * (1 - cf_gabungan["Maag (Dispepsia)"])
        if "Gangguan Pencernaan (Disentry)" in cf_gabungan:
            cf_gabungan["Gangguan Pencernaan (Disentry)"] = cf_gabungan["Gangguan Pencernaan (Disentry)"] + 0.15 * (1 - cf_gabungan["Gangguan Pencernaan (Disentry)"])

    # --- PERHITUNGAN CF PAKAR KOMBINASI ---
    for penyakit, rules_pakar in rules_cf.items():
        for kode_gejala in gejala_terpilih:
            if kode_gejala in rules_pakar:
                cf_gejala = rules_pakar[kode_gejala]
                cf_lama = cf_gabungan[penyakit]
                cf_gabungan[penyakit] = cf_lama + cf_gejala * (1 - cf_lama)

    # Mencari penyakit dengan nilai CF tertinggi
    penyakit_tertinggi = max(cf_gabungan, key=cf_gabungan.get)
    persentase_tertinggi = cf_gabungan[penyakit_tertinggi] * 100

    return penyakit_tertinggi, persentase_tertinggi

# --- TAMPILAN UTAMA DASHBOARD ---
col_title, col_logout = st.columns([4, 1])
with col_title:
    st.title("Dashboard Sistem Pakar")
with col_logout:
    st.write("")
    if st.button("Logout"):
        st.session_state.clear()
        st.switch_page("user.py")

tabs = st.tabs(["🩺 Diagnosa", "📚 Informasi Penyakit", "🤖 Chatbot"])

# --- TAB 1: INPUT GEJALA ---
with tabs[0]:
    st.subheader("Pilih Gejala yang Anda Alami")

    selected_gejala = []
    col1, col2 = st.columns(2)
    
    items = list(daftar_gejala.items())
    for i, (kode, nama_gejala) in enumerate(items):
        if i % 2 == 0:
            with col1:
                if st.checkbox(nama_gejala, key=kode):
                    selected_gejala.append(kode)
        else:
            with col2:
                if st.checkbox(nama_gejala, key=kode):
                    selected_gejala.append(kode)

    # Bersihkan state jika tidak ada gejala terpilih
    if not selected_gejala:
        if "hasil_diagnosa" in st.session_state:
            del st.session_state["hasil_diagnosa"]
        if "nilai_cf" in st.session_state:
            del st.session_state["nilai_cf"]
        if "gejala_teks" in st.session_state:
            del st.session_state["gejala_teks"]

    st.write("")
    
    # --- POSISI TOMBOL BAWAH ---
    col_kiri, col_tengah, col_kanan = st.columns([2, 4, 3])
    
    with col_kiri:
        klik_analisis = st.button("Analisis Diagnosa", type="primary", key="btn_analisis_final")

    with col_kanan:
        if selected_gejala:
            def bersihkan_centang():
                for kode in daftar_gejala.keys():
                    if kode in st.session_state:
                        st.session_state[kode] = False 
            st.button("🗑️ Hapus Semua Pilihan", on_click=bersihkan_centang, key="btn_hapus_pilihan")

    # --- TAMPILAN HASIL DIAGNOSA ---
    if klik_analisis:
        if not selected_gejala:
            st.warning("⚠️ Silakan pilih minimal 1 gejala terlebih dahulu.")
        else:
            penyakit_hasil, persentase_hasil = hitung_cf(selected_gejala)

            user_id = st.session_state.user_id
            sukses_simpan = simpan_riwayat_diagnosa(user_id, penyakit_hasil, persentase_hasil, selected_gejala)

            st.session_state.hasil_diagnosa = penyakit_hasil
            st.session_state.nilai_cf = persentase_hasil
            st.session_state.gejala_teks = [daftar_gejala[k] for k in selected_gejala]

            st.success(f"**Hasil Analisis:** Anda terindikasi mengalami **{penyakit_hasil}** dengan tingkat keyakinan **{persentase_hasil:.2f}%**")
            st.info("👉 Silakan buka tab **Informasi Penyakit** dan **Chatbot** di atas untuk pendalaman lebih lanjut.")
            
            if sukses_simpan:
                st.toast('Riwayat diagnosa berhasil disimpan ke database!', icon='✅')
            else:
                st.error('Gagal menyimpan riwayat ke database.')

# --- TAB 2: INFORMASI PENYAKIT ---
with tabs[1]:
    st.subheader("Detail Informasi Penyakit Anda")
    if "hasil_diagnosa" in st.session_state:
        penyakit_user = st.session_state.hasil_diagnosa
        info_penyakit_db = get_info_penyakit() 
        
        if penyakit_user in info_penyakit_db:
            detail = info_penyakit_db[penyakit_user]
            
            st.markdown(f"### 🩺 {penyakit_user} (Kepastian: {st.session_state.nilai_cf:.2f}%)")
            st.write("---")
            st.write("**📝 Penjelasan:**")
            st.write(detail["deskripsi"])
            st.write("**💊 Saran Penanganan:**")
            st.warning(detail["saran"])
            st.write("**🛡️ Cara Mencegah:**")
            st.success(detail["pencegahan"])
            
            st.write("") 
            if "referensi" in detail and detail["referensi"]:
                with st.expander("📚 Lihat Sumber Literatur"):
                    st.markdown(detail["referensi"])
                    
        else:
            st.warning(f"Informasi detail untuk penyakit '{penyakit_user}' belum tersedia.")
    else:
        st.info("ℹ️ Anda belum melakukan diagnosa di Tab 1.")

# --- TAB 3: CHATBOT ---
with tabs[2]:
    st.subheader("🤖 Asisten Cerdas Pencernaan")

    if "hasil_diagnosa" in st.session_state:
        st.write("Tanyakan apa saja tentang kondisimu. Chatbot ini mengingat semua percakapan dalam sesi ini.")

        tb = st.session_state.get('tinggi_badan', 165)
        bb = st.session_state.get('berat_badan', 60)
        bmi_status = "Obesitas/Overweight" if (bb / ((tb/100)**2)) >= 25 else "Normal"
        gaya_hidup = []
        if st.session_state.get('merokok'): gaya_hidup.append("Merokok")
        if st.session_state.get('makan_pedas'): gaya_hidup.append("Suka Makanan Pedas/Asam")
        str_gaya_hidup = ", ".join(gaya_hidup) if gaya_hidup else "Tidak ada kebiasaan berisiko"

        system_prompt = f"""Kamu adalah asisten medis ahli gastroenterologi. 
BERIKUT ADALAH FAKTA MEDIS PASIEN (TIDAK BOLEH DIBANTAH):
1. Hasil Diagnosa CF : {st.session_state.hasil_diagnosa} (Kepastian: {st.session_state.nilai_cf:.2f}%)
2. Gejala Dialami    : {', '.join(st.session_state.gejala_teks)}
3. Status BMI        : {bmi_status} (TB: {tb}cm, BB: {bb}kg)
4. Gaya Hidup Risiko : {str_gaya_hidup}

TUGASMU:
Jawab pertanyaan pasien HANYA dalam konteks diagnosa di atas. Analisis bagaimana Status BMI dan Gaya Hidupnya berkorelasi atau memperparah keluhannya. Jangan mendiagnosa ulang."""

        with st.expander("🔍 Lihat System Prompt (Arsitektur Guardrails)"):
            st.code(system_prompt, language="text")

        chat_key = f"chat_history_{st.session_state.hasil_diagnosa}"
        if chat_key not in st.session_state:
            st.session_state[chat_key] = []

        col_spacer, col_clear = st.columns([5, 1])
        with col_clear:
            if st.button("🗑️ Bersihkan", key="btn_clear_chat"):
                st.session_state[chat_key] = []
                st.rerun()

        st.write("---")

        for pesan in st.session_state[chat_key]:
            with st.chat_message(pesan["role"]):
                st.markdown(pesan["content"])

        user_question = st.chat_input("Contoh: Makanan apa yang harus saya hindari?")
        if user_question:
            st.session_state[chat_key].append({"role": "user", "content": user_question})
            with st.chat_message("user"):
                st.markdown(user_question)

            with st.chat_message("assistant"):
                try:
                    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                    model = genai.GenerativeModel(
                        model_name='gemini-2.5-flash',
                        system_instruction=system_prompt
                    )
                    history_gemini = [
                        {"role": "model" if p["role"] == "assistant" else "user", "parts": [p["content"]]}
                        for p in st.session_state[chat_key][:-1] 
                    ]
                    chat_session = model.start_chat(history=history_gemini)
                    response = chat_session.send_message(user_question)
                    reply = response.text
                    st.markdown(reply)
                    st.session_state[chat_key].append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"❌ Gagal memanggil Gemini API: {e}")
    else:
        st.info("ℹ️ Lakukan diagnosa di Tab 1 terlebih dahulu agar Chatbot mengenali kondisimu.")