"""
DataProphet — API de prédiction
Référence doc officielle : https://fastapi.tiangolo.com/tutorial/first-steps/
"""

# ── 1. Import ────────────────────────────────────────────────────────────────
from fastapi import FastAPI
import uvicorn
from schemas import CustomerFeatures, PredictionResponse, ChurnLabel
from contextlib import asynccontextmanager



#########################
# ── 1. Lifespan — chargement du modèle ───────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # DÉMARRAGE
    print("⏳ Chargement du modèle...")
    app.state.model = joblib.load("model.joblib")
    app.state.feature_order = [
        "anciennete_mois",
        "nb_produits",
        "montant_mensuel",
        "nb_appels_support",
        "score_satisfaction",
        "age",
    ]
    print("✅ Modèle chargé :", type(app.state.model).__name__)

    yield  # ← l'API accepte des requêtes ici

    # ARRÊT
    del app.state.model
    print("🛑 Modèle libéré")

######################################################



# ── 2. Instanciation de l'application avec titre et description ───────────────
#    Source : https://fastapi.tiangolo.com/tutorial/metadata/
app = FastAPI(
    title="DataProphet — API Prédiction",
    description=(
        "API exposant le modèle de scoring à l'équipe commerciale.\n\n"
        "- **`/health`** : vérifie que le service est actif\n"
        "- **`/predict`** : envoie des features, reçoit une prédiction\n\n"
        "Documentation interactive disponible sur `/docs` (Swagger UI) "
        "et `/redoc` (ReDoc)."
    ),
    version="1.0.0",
)

# ── 3. Route GET /health ──────────────────────────────────────────────────────
#    Source : https://fastapi.tiangolo.com/tutorial/first-steps/#define-a-path-operation
@app.get("/health", tags=["Système"])
def health():
    """
    Vérifie que le service est actif.

    Retourne un JSON `{ "status": "ok", "service": "DataProphet API" }`.
    """
    return {"status": "ok", "service": "DataProphet API"}



###########

# ── 3. POST /api/predict ──────────────────────────────────────────────────────
#    Référence : https://fastapi.tiangolo.com/tutorial/body/
@app.post(
    "/api/predict",
    response_model=PredictionResponse,
    tags=["Prédiction"],
    summary="Prédire le risque de churn d'un client",
)
def predict(customer: CustomerFeatures) -> PredictionResponse:
    """
    Reçoit les **features d'un client** et retourne une **prédiction de churn**.
 
    - Valide automatiquement toutes les contraintes définies dans `CustomerFeatures`
    - Retourne un score numérique **et** un label lisible pour l'équipe commerciale
    - ⚠️ La prédiction est actuellement **factice** — le vrai modèle sera branché
      à l'étape suivante.
    """
 
    # ── Prédiction factice (stub) ─────────────────────────────────────────────
    # Logique simpliste basée sur les features : remplacée par model.predict()
    # à l'étape suivante.
    score_brut = 0.0
 
    # Facteurs haussiers du risque
    if customer.nb_appels_support >= 5:
        score_brut += 0.35
    if customer.score_satisfaction < 5.0:
        score_brut += 0.30
    if customer.anciennete_mois < 6:
        score_brut += 0.20
    if customer.nb_produits == 1:
        score_brut += 0.15
 
    prediction = min(round(score_brut, 2), 1.0)
 
    # Conversion en label lisible
    if prediction < 0.35:
        label = ChurnLabel.FAIBLE_RISQUE
    elif prediction < 0.65:
        label = ChurnLabel.RISQUE_MOYEN
    else:
        label = ChurnLabel.RISQUE_ELEVE
 
    # Confiance factice : haute quand le score est tranché (proche de 0 ou 1)
    confiance = round(1.0 - 2 * abs(prediction - 0.5) + 0.5, 2)
    confiance = min(max(confiance, 0.5), 0.99)
 
    return PredictionResponse(
        prediction=prediction,
        label=label,
        confiance=confiance,
    )
 

############

# ── 4. Lancement avec Uvicorn ─────────────────────────────────────────────────
#    Source : https://fastapi.tiangolo.com/deployment/manually/
#    Commande équivalente en CLI :
#      uvicorn main:app --host 0.0.0.0 --port 8000 --reload
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,   # rechargement automatique à chaque modification du code
    )