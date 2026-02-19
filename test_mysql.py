import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # kosong kalau default Laragon
        database="sistem_pakar_pencernaan"
    )

    print("Koneksi berhasil!")
    conn.close()

except Exception as e:
    print("Error:", e)
