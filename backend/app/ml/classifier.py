"""Domain classifier using pre-trained ML model.

TODO: Train and export model in Phase 3 (ml_training/).
Currently provides a placeholder that returns 0.0 (benign) for all domains.
"""
import os
from typing import Optional
import numpy as np
from app.core.logging import logger
from app.config import settings


class DomainClassifier:
    """Singleton classifier that loads a trained model at startup."""
    _instance: Optional["DomainClassifier"] = None
    _model = None
    _is_loaded = False

    def __init__(self):
        self._load_model()

    def _load_model(self) -> None:
        """Load the trained model from disk."""
        model_path = settings.ml_model_path
        if os.path.exists(model_path):
            try:
                import joblib
                self._model = joblib.load(model_path)
                self._is_loaded = True
                logger.info(f"ML model loaded from {model_path}")
            except Exception as e:
                logger.warning(f"Failed to load ML model: {e}")
                self._is_loaded = False
        else:
            logger.warning(
                f"ML model not found at {model_path}. "
                "Running without ML classification. "
                "Train a model using ml_training/ scripts."
            )
            self._is_loaded = False

    @classmethod
    def get_instance(cls) -> Optional["DomainClassifier"]:
        """Get or create the singleton classifier instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance if cls._instance._is_loaded else None

    def predict_score(self, domain: str) -> float:
        """Predict the maliciousness score for a domain (0.0 = benign, 1.0 = malicious)."""
        if not self._is_loaded or self._model is None:
            return 0.0
        
        from app.ml.features import extract_features
        features = extract_features(domain)
        features_array = np.array([features])
        
        try:
            probas = self._model.predict_proba(features_array)
            # Return probability of malicious class (index 1)
            return float(probas[0][1])
        except Exception as e:
            logger.error(f"ML prediction error for {domain}: {e}")
            return 0.0

    def predict_batch(self, domains: list[str]) -> list[float]:
        """Predict scores for multiple domains."""
        if not self._is_loaded or self._model is None:
            return [0.0] * len(domains)
        
        from app.ml.features import extract_features
        features_list = [extract_features(d) for d in domains]
        features_array = np.array(features_list)
        
        try:
            probas = self._model.predict_proba(features_array)
            return [float(p[1]) for p in probas]
        except Exception as e:
            logger.error(f"ML batch prediction error: {e}")
            return [0.0] * len(domains)
