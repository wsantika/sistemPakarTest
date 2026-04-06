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

# Panggil fungsinya, data sekarang berasal murni dari MySQL
daftar_gejala, info_penyakit, rules_cf = load_knowledge_base()

# --- FUNGSI ALGORITMA CERTAINTY FACTOR ---
def hitung_cf(gejala_terpilih):
    cf_gabungan = {penyakit: 0.0 for penyakit in rules_cf.keys()}
    
    tb_m = st.session_state.get('tinggi_badan', 165) / 100
    bb_kg = st.session_state.get('berat_badan', 60)
    bmi = bb_kg / (tb_m * tb_m)
    is_merokok = st.session_state.get('merokok', False)
    is_pedas = st.session_state.get('makan_pedas', False)

    # Injeksi Gaya Hidup (dengan pengecekan nama penyakit untuk keamanan)
    if bmi >= 25.0 and "GERD" in cf_gabungan: 
        cf_gabungan["GERD"] = cf_gabungan["GERD"] + 0.20 * (1 - cf_gabungan["GERD"])
    if is_merokok and "GERD" in cf_gabungan:
        cf_gabungan["GERD"] = cf_gabungan["GERD"] + 0.15 * (1 - cf_gabungan["GERD"])
    if is_pedas:
        if "Gastritis" in cf_gabungan:
            cf_gabungan["Gastritis"] = cf_gabungan["Gastritis"] + 0.25 * (1 - cf_gabungan["Gastritis"])
        if "Diare" in cf_gabungan:
            cf_gabungan["Diare"] = cf_gabungan["Diare"] + 0.15 * (1 - cf_gabungan["Diare"])

    # Kalkulasi Gejala
    for penyakit, rules_pakar in rules_cf.items():
        for kode_gejala in gejala_terpilih:
            if kode_gejala in rules_pakar:
                cf_gejala = rules_pakar[kode_gejala]
                cf_lama = cf_gabungan[penyakit]
                cf_gabungan[penyakit] = cf_lama + cf_gejala * (1 - cf_lama)

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

    # =================================================================
    # LOGIKA BARU: PENGHAPUSAN OTOMATIS (Berjalan real-time)
    # Jika daftar gejala kosong (user meng-uncheck semua), langsung hapus memori
    # =================================================================
    if not selected_gejala:
        if "hasil_diagnosa" in st.session_state:
            del st.session_state["hasil_diagnosa"]
        if "nilai_cf" in st.session_state:
            del st.session_state["nilai_cf"]
        if "gejala_teks" in st.session_state:
            del st.session_state["gejala_teks"]

    st.write("")
    
    # Tombol sekarang hanya fokus untuk memproses diagnosa saja
    if st.button("Analisis Diagnosa", type="primary"):
        if not selected_gejala:
            st.warning("⚠️ Silakan pilih minimal 1 gejala terlebih dahulu.")
        else:
            penyakit_hasil, persentase_hasil = hitung_cf(selected_gejala)

            # --- SIMPAN KE DATABASE ---
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
        if penyakit_user in info_penyakit:
            detail = info_penyakit[penyakit_user]
            
            st.markdown(f"### 🩺 {penyakit_user} (Kepastian: {st.session_state.nilai_cf:.2f}%)")
            st.write("---")
            st.write("**📝 Penjelasan:**")
            st.write(detail["deskripsi"])
            st.write("**💊 Saran Penanganan:**")
            st.warning(detail["saran"])
            st.write("**🛡️ Cara Mencegah:**")
            st.success(detail["pencegahan"])
    else:
        st.info("ℹ️ Anda belum melakukan diagnosa di Tab 1.")

# --- TAB 3: CHATBOT ---
with tabs[2]:
    st.subheader("🤖 Asisten Cerdas Pencernaan")

    if "hasil_diagnosa" in st.session_state:
        st.write("Tanyakan apa saja tentang kondisimu. Chatbot ini mengingat semua percakapan dalam sesi ini.")

        # Bangun konteks untuk system prompt
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

        # Tombol bersihkan chat (pakai key unik per diagnosa agar tidak bentrok)
        chat_key = f"chat_history_{st.session_state.hasil_diagnosa}"
        if chat_key not in st.session_state:
            st.session_state[chat_key] = []

        col_spacer, col_clear = st.columns([5, 1])
        with col_clear:
            if st.button("🗑️ Bersihkan", key="btn_clear_chat"):
                st.session_state[chat_key] = []
                st.rerun()

        st.write("---")

        # Tampilkan semua riwayat percakapan
        for pesan in st.session_state[chat_key]:
            with st.chat_message(pesan["role"]):
                st.markdown(pesan["content"])

        # Input pesan baru
        user_question = st.chat_input("Contoh: Makanan apa yang harus saya hindari?")
        if user_question:
            # Simpan & tampilkan pesan user
            st.session_state[chat_key].append({"role": "user", "content": user_question})
            with st.chat_message("user"):
                st.markdown(user_question)

            # Kirim seluruh riwayat ke Gemini sebagai multi-turn chat
            with st.chat_message("assistant"):
                try:
                    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                    model = genai.GenerativeModel(
                        model_name='gemini-2.5-flash',
                        system_instruction=system_prompt
                    )
                    # Bangun history Gemini dari semua pesan lama (kecuali pesan terakhir yg baru masuk)
                    # PENTING: Gemini pakai role "model" bukan "assistant"
                    history_gemini = [
                        {"role": "model" if p["role"] == "assistant" else "user", "parts": [p["content"]]}
                        for p in st.session_state[chat_key][:-1]  # semua kecuali pesan user terakhir
                    ]
                    chat_session = model.start_chat(history=history_gemini)
                    response = chat_session.send_message(user_question)
                    reply = response.text
                    st.markdown(reply)
                    # Simpan balasan asisten ke riwayat
                    st.session_state[chat_key].append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"❌ Gagal memanggil Gemini API: {e}")
    else:
        st.info("ℹ️ Lakukan diagnosa di Tab 1 terlebih dahulu agar Chatbot mengenali kondisimu.")