from typing import Optional
from presidio_analyzer import RecognizerResult, LocalRecognizer


class GLiNERRecognizer(LocalRecognizer):
    """
    Wraps GLiNER multilingual NER model as a Presidio recognizer.

    GLiNER handles:
      - Vietnamese person names (PERSON)
      - Locations, organizations, and other entities
      - Multilingual inputs without language-specific models

    Usage:
        analyzer.registry.add_recognizer(GLiNERRecognizer())
        # then in detect_pii(), include "VN_PERSON", "PERSON", etc.
    """

    ENTITIES = ["FIRST_NAME", "LAST_NAME", "EMAIL", "PHONE", "ID", "ADDRESS", "LOCATION", "ORGANIZATION"]
    MODEL_NAME = "nvidia/gliner-PII"
    MAX_TOKEN = 128

    def __init__(self):
        self._model = None
        super().__init__(
            supported_entities=self.ENTITIES,
            supported_language="en",
        )

    @property
    def model(self):
        if self._model is None:
            import torch
            from gliner import GLiNER

            device = "cuda" if torch.cuda.is_available() else "cpu"
            self._model = GLiNER.from_pretrained(self.MODEL_NAME)
            if device == "cuda":
                self._model.model.to(device)
        return self._model

    def load(self) -> None:
        _ = self.model

    def _map_entity(self, label: str) -> str:
        """
        Map nvidia/gliner-PII entity labels to Presidio-compatible types.
        """
        mapping = {
            "FIRST_NAME": "PERSON",
            "LAST_NAME": "PERSON",
            "EMAIL": "EMAIL_ADDRESS",
            "PHONE": "VN_PHONE",
            "ID": "VN_CCCD",
            "ADDRESS": "LOCATION",
        }
        return mapping.get(label, label)

    def analyze(
        self,
        text: str,
        entities: Optional[list] = None,
        nlp_artifacts=None,
        language: str = "en",
    ) -> list[RecognizerResult]:
        if entities is None:
            entities = self.ENTITIES

        active_entities = [e for e in entities if e in self.ENTITIES]
        if not active_entities:
            return []

        preds = self.model.predict_entities(
            text, active_entities, threshold=0.5, max_tokens=self.MAX_TOKEN
        )

        results = []
        for pred in preds:
            mapped_type = self._map_entity(pred["label"])
            results.append(
                RecognizerResult(
                    entity_type=mapped_type,
                    start=pred["start"],
                    end=pred["end"],
                    score=float(pred["score"]),
                )
            )
        return results

    def validate_entity_confidence(
        self, recognizer_result: RecognizerResult, entity: str, confidence: float
    ) -> bool:
        return recognizer_result.score >= 0.5
