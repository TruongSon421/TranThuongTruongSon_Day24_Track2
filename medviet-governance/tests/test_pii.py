import pytest
import pandas as pd
from src.pii.anonymizer import MedVietAnonymizer
from src.pii.detector import detect_pii

@pytest.fixture
def anonymizer():
    return MedVietAnonymizer()

@pytest.fixture
def sample_df():
    return pd.read_csv("data/raw/patients_raw.csv").head(50)

class TestPIIDetection:

    def test_cccd_detected(self, anonymizer):
        text = "Bệnh nhân Nguyen Van A, CCCD: 012345678901"
        results = detect_pii(text, anonymizer.analyzer)
        cccd_results = [r for r in results if r.entity_type == "VN_CCCD"]
        assert len(cccd_results) >= 1, "CCCD should be detected"

    def test_phone_detected(self, anonymizer):
        text = "Liên hệ: 0912345678"
        results = detect_pii(text, anonymizer.analyzer)
        phone_results = [r for r in results if r.entity_type == "VN_PHONE"]
        assert len(phone_results) >= 1, "Phone should be detected"

    def test_email_detected(self, anonymizer):
        text = "Email: nguyenvana@gmail.com"
        results = detect_pii(text, anonymizer.analyzer)
        email_results = [r for r in results if r.entity_type == "EMAIL_ADDRESS"]
        assert len(email_results) >= 1, "Email should be detected"

    def test_detection_rate_above_95_percent(self, anonymizer, sample_df):
        """Pipeline phải đạt >95% detection rate."""
        pii_columns = ["ho_ten", "cccd", "so_dien_thoai", "email"]
        rate = anonymizer.calculate_detection_rate(sample_df, pii_columns)
        print(f"\nDetection rate: {rate:.2%}")
        assert rate >= 0.95, f"Detection rate {rate:.2%} < 95%"

class TestAnonymization:

    def test_pii_not_in_output(self, anonymizer, sample_df):
        """Sau anonymization, không còn CCCD gốc trong output."""
        df_anon = anonymizer.anonymize_dataframe(sample_df)
        df_str = df_anon.to_string()
        for original_cccd in sample_df["cccd"]:
            assert str(original_cccd) not in df_str, f"Original CCCD {original_cccd} found in output!"

    def test_non_pii_columns_unchanged(self, anonymizer, sample_df):
        """Cột benh và ket_qua_xet_nghiem phải giữ nguyên."""
        df_anon = anonymizer.anonymize_dataframe(sample_df)
        pd.testing.assert_frame_equal(
            sample_df[["benh", "ket_qua_xet_nghiem"]].reset_index(drop=True),
            df_anon[["benh", "ket_qua_xet_nghiem"]].reset_index(drop=True)
        )
