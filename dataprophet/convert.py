import pickle
import joblib

# Charger le fichier .pkl
with open("ml1_rf_model.pkl", "rb") as f:
    model = pickle.load(f)

# Sauvegarder en .joblib
joblib.dump(model, "model.joblib")

print("Conversion réussie ✅")
print("Type de l'objet :", type(model))

# Vérification — recharger et tester
model_check = joblib.load("model.joblib")
print("Rechargement OK ✅ :", type(model_check))