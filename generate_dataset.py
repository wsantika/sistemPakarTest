import pandas as pd
import random

#daftar gejala
symptoms = [
    'nyeri_ulu_hati', 'mual', 'muntah', 'kembung',
    'perih_saat_lapar', 'panas dada', 'asam_naik',
    'diare', 'bab_cair', 'sulit_bab', 'bab_keras',
    'bab_berdarah', 'nafsu_turun', 'bb_turun',
]

#relasi penyakit gejala (knowlage base)
disease_rules ={
    "Gastritis": ["nyeri_ulu_hati", "mual", "perih_saat_lapar", "nafsu_turun"],
    "GERD": ["panas_dada", "asam_naik", "mual", "nyeri_ulu_hati"],
    "Diare": ["diare", "bab_cair", "mual"],
    "Konstipasi": ["sulit_bab", "bab_keras", "kembung"],
    "Tukak_Lambung": ["nyeri_ulu_hati", "bab_berdarah", "bb_turun", "perih_saat_lapar"]
}

data = []

for disease, main_symptoms in disease_rules.items():
    for _ in range(60):
        row = {}
        for symptom in symptoms:
            if symptom in main_symptoms:
                row[symptom] = 1
            else:
                row[symptom] = random.choices([0, 1])

        row['diagnosis'] = disease
        data.append(row)

df = pd.DataFrame(data)

df.to_csv('dataset_pencernaan.csv', index=False)

print("Dataset 'dataset_pencernaan.csv' berhasil dibuat.")
print(df.head())