# File: pakar_rules.py

# 1. DICTIONARY GEJALA (Untuk ditampilkan di Checkbox Tab 1)
daftar_gejala = {
    "G01": "Nyeri pada ulu hati seperti terbakar",
    "G02": "Perut kembung",
    "G03": "Merasa mual",
    "G04": "Mengalami muntah",
    "G05": "Sakit tenggorokan",
    "G06": "Merasa susah tidur",
    "G07": "Bau mulut",
    "G08": "Nyeri ulu hati / epigastrium (terasa panas/perih)",
    "G09": "Perut kembung dan terasa begah",
    "G10": "Tidak nafsu makan",
    "G11": "Timbul rasa asam di mulut",
    "G12": "Sering bersendawa",
    "G13": "Sakit perut kuadran kanan bawah",
    "G14": "Nyeri perut berpindah dari ulu hati ke kanan bawah",
    "G15": "Demam",
    "G16": "Perut mulas",
    "G17": "Mengalami sembelit",
    "G18": "Menggigil",
    "G19": "Diare disertai darah atau lendir > 3x sehari",
    "G20": "Buang air besar dengan tinja cair / encer",
    "G21": "Badan terasa lemas",
    "G22": "Kram dan nyeri perut",
    "G23": "Sakit / Nyeri Perut",
    "G24": "Buang air besar dengan tinja sangat cair",
    "G25": "Dehidrasi"
}

# 2. BASIS ATURAN (RULE BASE) & NILAI CF PAKAR DARI LITERATUR
# Format: "Nama Penyakit": {"Kode_Gejala": Nilai_CF}
rules_cf = {
    "GERD": {
        "G01": 0.80,
        "G02": 1.00,
        "G03": 0.70,
        "G04": 0.70,
        "G05": 0.70,
        "G06": 0.55,
        "G07": 0.40
    },
    "Gastritis": {
        "G08": 0.95,
        "G03": 0.65,
        "G04": 0.60,
        "G09": 0.60,
        "G10": 0.45,
        "G11": 0.45,
        "G12": 0.30
    },
    "Apendisitis": {
        "G13": 0.90,
        "G14": 0.80,
        "G15": 0.65,
        "G03": 0.75,
        "G04": 0.65,
        "G16": 0.60,
        "G17": 0.40,
        "G18": 0.30,
        "G10": 0.30
    },
    "Disentri": {
        "G19": 0.95,
        "G20": 0.80,
        "G21": 0.80,
        "G02": 0.90,
        "G22": 0.65,
        "G16": 0.65,
        "G03": 0.60,
        "G04": 0.50,
        "G15": 0.55
    },
    "Diare": {
        "G23": 0.90,
        "G02": 0.80,
        "G24": 0.60,
        "G03": 0.40,
        "G25": 0.20,
        "G04": 0.10
    }
}