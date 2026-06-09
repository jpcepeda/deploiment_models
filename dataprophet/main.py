"""
DataProphet — API de prédiction
Référence doc officielle : https://fastapi.tiangolo.com/tutorial/first-steps/
"""

from contextlib import asynccontextmanager
import joblib
import numpy as np
import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException
from schemas import CustomerFeatures, PredictionResponse


# ── 1. Lifespan — chargement du modèle ───────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # DÉMARRAGE
    print("Chargement du modèle...")
    with open("ml1_rf_model.pkl", "rb") as f:
        app.state.model = joblib.load(f)

    app.state.feature_order = [
        "genre_bota",
        "espece",
        "stadededeveloppement",
        "hauteurarbre",
        "typenature",
        "latitude",
        "longitude",
    ]
    print("Modèle chargé :", type(app.state.model).__name__)

    yield  # ← l'API tourne ici

    # ARRÊT
    del app.state.model
    print("Modèle libéré")


# ── 2. Instanciation ──────────────────────────────────────────────────────────
app = FastAPI(
    title="DataProphet — API Arbres",
    description=(
        "Prédit l'année de plantation d'un arbre "
        "à partir de ses caractéristiques botaniques et géographiques.\n\n"
        "Documentation interactive sur `/docs`."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ── 3. GET /health ────────────────────────────────────────────────────────────
#    Source : https://fastapi.tiangolo.com/tutorial/first-steps/#define-a-path-operation
@app.get("/health", tags=["Système"])
def health():
    model_ok = hasattr(app.state, "model") and app.state.model is not None
    return {
        "status":       "ok" if model_ok else "degraded",
        "service":      "DataProphet Arbres API",
        "model_loaded": model_ok,
    }


# ── 4. POST /api/predict ──────────────────────────────────────────────────────
#    Référence : https://fastapi.tiangolo.com/tutorial/body/
@app.post(
    "/api/predict",
    response_model=PredictionResponse,
    tags=["Prédiction"],
    summary="Prédire l'année de plantation d'un arbre",
)
def predict(arbre: CustomerFeatures) -> PredictionResponse:
    """
    Reçoit les caractéristiques d'un arbre et retourne
    l'année de plantation prédite par le modèle.
    """
    model        = app.state.model
    feature_order = app.state.feature_order

    # ── Pydantic → DataFrame pandas ──────────────────────────────────────────
    data = arbre.model_dump()
    df   = pd.DataFrame([data], columns=feature_order)

    print("Tableau envoyé au modèle :")
    print(df.to_string())

    # ── Appel du modèle ───────────────────────────────────────────────────────
    try:
        prediction = model.predict(df)[0]
        annee      = int(prediction)

        # Confiance via predict_proba si disponible
        if hasattr(model, "predict_proba"):
            probas    = model.predict_proba(df)[0]
            confiance = round(float(probas.max()), 4)
        else:
            confiance = 1.0   # régression : pas de proba

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur du modèle : {str(e)}")

    return PredictionResponse(
        annee_plantation=annee,
        confiance=confiance,
    )


# ── 5. Lancement ──────────────────────────────────────────────────────────────
#    Source : https://fastapi.tiangolo.com/deployment/manually/
#    Commande équivalente en CLI :
#    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,   # rechargement automatique à chaque modification du code

    )

    # Test  http://127.0.0.1:8000/docs