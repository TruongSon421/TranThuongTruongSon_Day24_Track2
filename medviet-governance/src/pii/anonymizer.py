import pandas as pd
from presidio_analyzer.analyzer_engine import RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from faker import Faker
from .detector import build_vietnamese_analyzer, detect_pii

fake = Faker("vi_VN")
Faker.seed(42)

class MedVietAnonymizer:

    def __init__(self):
        self.analyzer = build_vietnamese_analyzer()
        self.anonymizer = AnonymizerEngine()

    def anonymize_text(self, text: str, strategy: str = "replace") -> str:
        results = detect_pii(text, self.analyzer)
        if not results:
            return text

        operators = {}

        if strategy == "replace":
            operators = {
                "PERSON": OperatorConfig("replace",
                          {"new_value": fake.name()}),
                "EMAIL_ADDRESS": OperatorConfig("replace",
                                 {"new_value": fake.email()}),
                "VN_CCCD": OperatorConfig("replace",
                           {"new_value": fake.ssn()}),
                "VN_PHONE": OperatorConfig("replace",
                            {"new_value": fake.phone_number()}),
                "VN_PERSON": OperatorConfig("replace",
                             {"new_value": fake.name()}),
                "LOCATION": OperatorConfig("replace",
                            {"new_value": fake.address()}),
                "ORGANIZATION": OperatorConfig("replace",
                               {"new_value": fake.company()}),
            }
        elif strategy == "mask":
            operators = {
                "PERSON": OperatorConfig("mask",
                          {"chars_to_mask": 0, "masking_char": "*", "from_start": False}),
                "EMAIL_ADDRESS": OperatorConfig("mask",
                                 {"chars_to_mask": 0, "masking_char": "*", "from_start": False}),
                "VN_CCCD": OperatorConfig("mask",
                           {"chars_to_mask": 6, "masking_char": "*", "from_start": False}),
                "VN_PHONE": OperatorConfig("mask",
                            {"chars_to_mask": 4, "masking_char": "*", "from_start": False}),
                "VN_PERSON": OperatorConfig("mask",
                             {"chars_to_mask": 0, "masking_char": "*", "from_start": False}),
                "LOCATION": OperatorConfig("mask",
                            {"chars_to_mask": 0, "masking_char": "*", "from_start": False}),
                "ORGANIZATION": OperatorConfig("mask",
                               {"chars_to_mask": 0, "masking_char": "*", "from_start": False}),
            }
        elif strategy == "hash":
            import hashlib
            operators = {
                "PERSON": OperatorConfig("hash", {"hash_type": "sha256"}),
                "EMAIL_ADDRESS": OperatorConfig("hash", {"hash_type": "sha256"}),
                "VN_CCCD": OperatorConfig("hash", {"hash_type": "sha256"}),
                "VN_PHONE": OperatorConfig("hash", {"hash_type": "sha256"}),
                "VN_PERSON": OperatorConfig("hash", {"hash_type": "sha256"}),
                "LOCATION": OperatorConfig("hash", {"hash_type": "sha256"}),
                "ORGANIZATION": OperatorConfig("hash", {"hash_type": "sha256"}),
            }

        anonymized = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=operators
        )
        return anonymized.text

    def anonymize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df_anon = df.copy()

        # Text columns: use anonymize_text
        for col in ["ho_ten", "dia_chi", "email"]:
            if col in df_anon.columns:
                df_anon[col] = [self.anonymize_text(str(v)) for v in df_anon[col]]

        # CCCD and phone: direct fake replacement
        if "cccd" in df_anon.columns:
            df_anon["cccd"] = [fake.ssn() for _ in range(len(df_anon))]
        if "so_dien_thoai" in df_anon.columns:
            df_anon["so_dien_thoai"] = [fake.phone_number() for _ in range(len(df_anon))]

        # Keep non-PII columns unchanged
        # patient_id, benh, ket_qua_xet_nghiem stay as-is
        return df_anon

    def calculate_detection_rate(self,
                                  original_df: pd.DataFrame,
                                  pii_columns: list) -> float:
        total = 0
        detected = 0

        for col in pii_columns:
            for value in original_df[col].astype(str):
                total += 1
                results = detect_pii(value, self.analyzer)
                if len(results) > 0:
                    detected += 1

        return detected / total if total > 0 else 0.0
