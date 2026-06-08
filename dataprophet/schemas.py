from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator


# ── Labels lisibles pour l'équipe commerciale ─────────────────────────────────
class ChurnLabel(str, Enum):
    FAIBLE_RISQUE = "Faible risque de churn"
    RISQUE_MOYEN  = "Risque moyen de churn"
    RISQUE_ELEVE  = "Risque élevé de churn"


# ── Données d'entrée ──────────────────────────────────────────────────────────
class CustomerFeatures(BaseModel):
    anciennete_mois: int = Field(..., ge=0, le=600)
    nb_produits: int = Field(..., ge=1, le=10)
    montant_mensuel: float = Field(..., gt=0.0, le=10_000.0)
    nb_appels_support: int = Field(default=0, ge=0, le=100)
    score_satisfaction: float = Field(..., ge=0.0, le=10.0)
    age: int = Field(..., ge=18, le=120)

    @field_validator("score_satisfaction")
    @classmethod
    def score_arrondi(cls, v: float) -> float:
        return round(v, 1)

    @model_validator(mode="after")
    def coherence_anciennete_produits(self) -> CustomerFeatures:
        minimum = (self.nb_produits - 1) * 3
        if self.anciennete_mois < minimum:
            raise ValueError(
                f"{self.nb_produits} produits requiert au moins "
                f"{minimum} mois d'ancienneté (reçu : {self.anciennete_mois})."
            )
        return self


# ── Réponse retournée par l'API ───────────────────────────────────────────────
class PredictionResponse(BaseModel):
    prediction: float = Field(..., ge=0.0, le=1.0)
    label: ChurnLabel
    confiance: float = Field(..., ge=0.0, le=1.0)