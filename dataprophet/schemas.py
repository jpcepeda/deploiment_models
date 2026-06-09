from __future__ import annotations
from pydantic import BaseModel, Field


class CustomerFeatures(BaseModel):
    genre_bota:           str   = Field(..., description="Genre botanique")
    espece:               str   = Field(..., description="Espèce")
    stadededeveloppement: str   = Field(..., description="Stade de développement")
    hauteurarbre:         float = Field(..., gt=0, description="Hauteur en mètres")
    typenature:           str   = Field(..., description="Type de nature")
    latitude:             float = Field(..., ge=-90,  le=90)
    longitude:            float = Field(..., ge=-180, le=180)
'''
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "genre_bota":           "Acer",
                "espece":               "platanoides",
                "stadededeveloppement": "Adulte",
                "hauteurarbre":         8.5,
                "typenature":           "Arbre",
                "latitude":             48.8566,
                "longitude":            2.3522
            }]
        }
    }

'''
class PredictionResponse(BaseModel):
    annee_plantation: int   = Field(..., description="Année de plantation prédite")
    confiance:        float = Field(..., ge=0.0, le=1.0)

    