"""
schemas.py — Contrats de données de l'API DataProphet
Doc de référence : https://docs.pydantic.dev/latest/concepts/fields/
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


# ─────────────────────────────────────────────────────────────────────────────
# Enum : labels lisibles pour la prédiction
# ─────────────────────────────────────────────────────────────────────────────
class ChurnLabel(str, Enum):
    """Label métier retourné à l'équipe commerciale."""
    FAIBLE_RISQUE  = "Faible risque de churn"
    RISQUE_MOYEN   = "Risque moyen de churn"
    RISQUE_ELEVE   = "Risque élevé de churn"


# ─────────────────────────────────────────────────────────────────────────────
# Modèle d'entrée — features du client
# ─────────────────────────────────────────────────────────────────────────────
class CustomerFeatures(BaseModel):
    """
    Données d'entrée pour la prédiction de churn.

    Toutes les contraintes sont validées automatiquement par Pydantic ;
    une erreur 422 est renvoyée au client si une valeur est hors-limite.

    Référence contraintes : https://docs.pydantic.dev/latest/concepts/fields/
    """

    # ── Données contractuelles ────────────────────────────────────────────────
    anciennete_mois: int = Field(
        ...,
        ge=0, le=600,
        description="Ancienneté du client en mois (0–600)",
        examples=[24],
    )
    nb_produits: int = Field(
        ...,
        ge=1, le=10,
        description="Nombre de produits souscrits (1–10)",
        examples=[2],
    )
    montant_mensuel: float = Field(
        ...,
        gt=0.0, le=10_000.0,
        description="Montant moyen mensuel en € (>0 et ≤ 10 000)",
        examples=[89.99],
    )

    # ── Comportement ─────────────────────────────────────────────────────────
    nb_appels_support: int = Field(
        default=0,
        ge=0, le=100,
        description="Nombre d'appels au support sur les 12 derniers mois",
        examples=[3],
    )
    score_satisfaction: float = Field(
        ...,
        ge=0.0, le=10.0,
        description="Score de satisfaction (0.0–10.0)",
        examples=[7.5],
    )

    # ── Données sociodémographiques ───────────────────────────────────────────
    age: int = Field(
        ...,
        ge=18, le=120,
        description="Âge du client (18–120 ans)",
        examples=[35],
    )

    # ── Validateur custom : cohérence métier ─────────────────────────────────
    @field_validator("score_satisfaction")
    @classmethod
    def score_arrondi(cls, v: float) -> float:
        """Arrondit le score à 1 décimale pour éviter les valeurs parasites."""
        return round(v, 1)

    @model_validator(mode="after")
    def coherence_anciennete_produits(self) -> CustomerFeatures:
        """
        Un client avec 0 mois d'ancienneté ne peut pas avoir plusieurs produits.
        Règle métier : ancienneté >= (nb_produits - 1) * 3 mois minimum.
        """
        minimum = (self.nb_produits - 1) * 3
        if self.anciennete_mois < minimum:
            raise ValueError(
                f"Incohérence : {self.nb_produits} produits requiert au moins "
                f"{minimum} mois d'ancienneté (reçu : {self.anciennete_mois})."
            )
        return self

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "anciennete_mois": 24,
                    "nb_produits": 2,
                    "montant_mensuel": 89.99,
                    "nb_appels_support": 3,
                    "score_satisfaction": 7.5,
                    "age": 35,
                }
            ]
        }
    }


# ─────────────────────────────────────────────────────────────────────────────
# Modèle de sortie — réponse de l'API
# ─────────────────────────────────────────────────────────────────────────────
class PredictionResponse(BaseModel):
    """
    Réponse retournée par POST /api/predict.

    Contient à la fois la valeur numérique brute du modèle
    et un label lisible pour l'équipe commerciale.
    """

    prediction: float = Field(
        ...,
        ge=0.0, le=1.0,
        description="Score de risque de churn entre 0 (nul) et 1 (certain)",
    )
    label: ChurnLabel = Field(
        ...,
        description="Interprétation lisible du score pour l'équipe commerciale",
    )
    confiance: float = Field(
        ...,
        ge=0.0, le=1.0,
        description="Niveau de confiance du modèle dans sa prédiction (0–1)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prediction": 0.73,
                    "label": "Risque élevé de churn",
                    "confiance": 0.91,
                }
            ]
        }
    }