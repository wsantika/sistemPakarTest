# File: pakar_rules.py

# 1. DICTIONARY GEJALA (Untuk ditampilkan di Checkbox Tab 1)
daftar_gejala = {
    "G01": "Merasa mual",
    "G02": "Tidak nafsu makan",
    "G03": "Kram dan nyeri perut",
    "G04": "Merasa susah tidur",
    "G05": "Perut terasa nyeri dan bengkak",
    "G06": "Nyeri pada hulu hati seperti terbakar",
    "G07": "Feses berwarna pucat/berdarah",
    "G08": "Mudah merasa lelah",
    "G09": "Kulit berkerut dan kering",
    "G10": "Nyeri perut daerah hulu hati/Epigestrum",
    "G11": "Menggigil",
    "G12": "Sakit tenggorokan",
    "G13": "Badan terasa lemas",
    "G14": "Merasa sangat haus",
    "G15": "Tubuh gampang memar",
    "G16": "Buang air besar > 3x seperti cucian beras",
    "G17": "Timbul rasa asam dimulut",
    "G18": "Perut terasa mules",
    "G19": "Bau mulut",
    "G20": "Perut kembung",
    "G21": "Sering bersendawa",
    "G22": "Mengalami muntah",
    "G23": "Sakit perut sebelah kanan bawah",
    "G24": "Mengalami sembelit",
    "G25": "Mengalami demam",
    "G26": "Kram dan nyeri perut (Disentri)",
    "G27": "Diare disertai darah atau lendir > 3x sehari",
    "G28": "Kulit dan mata tampak menguning",
    "G29": "Mulut terasa kering"
}

rules_cf = {
    "Refluks(GERD)": {
        "G01": 0.40, "G22": 0.40, "G12": 0.80, "G04": 0.70, 
        "G19": 0.60, "G06": 0.50
    },
    "Infeksi SaluranPencernaan (Colera)": {
        "G01": 0.40, "G22": 0.40, "G03": 0.50, "G29": 0.80, 
        "G14": 0.40, "G09": 0.70, "G16": 0.85, "G13": 0.50, "G20": 0.60
    },
    "Maag (Dispepsia)": {
        "G06": 0.70, "G01": 0.50, "G22": 0.40, "G21": 0.40, 
        "G02": 0.50, "G10": 0.90, "G17": 0.50
    },
    "Radang Hati (Hepatitis)": {
        "G28": 0.80, "G05": 0.60, "G07": 0.70, "G01": 0.50, 
        "G08": 0.50, "G22": 0.40, "G02": 0.50, "G15": 0.50
    },
    "Radang Usus Buntu (Apendisitis)": {
        "G23": 0.80, "G11": 0.40, "G25": 0.50, "G02": 0.40, 
        "G24": 0.60, "G01": 0.50, "G22": 0.50
    },
    "Gangguan Pencernaan (Disentry)": {
        "G27": 0.90, "G25": 0.50, "G01": 0.40, "G22": 0.40, 
        "G26": 0.50, "G13": 0.60, "G18": 0.70
    }
}