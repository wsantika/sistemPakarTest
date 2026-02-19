import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import pickle

# Load dataset
df = pd.read_csv("dataset_pencernaan.csv")

# Pisahkan fitur dan target
X = df.drop("diagnosis", axis=1)
y = df["diagnosis"]

# Bersihkan data jika ada format seperti "[1]"
for col in X.columns:
    X[col] = X[col].astype(str).str.replace("[", "").str.replace("]", "")
    X[col] = X[col].astype(int)

# Split data (80% training, 20% testing)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Buat model Decision Tree
model = DecisionTreeClassifier()

# Training
model.fit(X_train, y_train)

# Prediksi
y_pred = model.predict(X_test)

# Hitung akurasi
accuracy = accuracy_score(y_test, y_pred)

print("Akurasi Model:", accuracy)

# Simpan model
with open("model_pencernaan.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model berhasil disimpan!")
