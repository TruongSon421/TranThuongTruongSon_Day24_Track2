from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern

from .gliner_recognizer import GLiNERRecognizer


def build_vietnamese_analyzer() -> AnalyzerEngine:
    # CCCD: 9-12 digits (Vietnamese ID)
    cccd_pattern = Pattern(
        name="cccd_pattern",
        regex=r"\d{9,12}",
        score=0.9
    )
    cccd_recognizer = PatternRecognizer(
        supported_entity="VN_CCCD",
        patterns=[cccd_pattern]
    )

    # Phone: 9-10 digits starting with 9 (Vietnamese mobile, without leading 0)
    phone_recognizer = PatternRecognizer(
        supported_entity="VN_PHONE",
        patterns=[Pattern(
            name="vn_phone",
            regex=r"9\d{8,9}",
            score=0.85
        )]
    )

    # Vietnamese names: common surname patterns followed by name
    # Common surnames: Nguyễn, Trần, Lê, Phạm, Hoàng/Huỳnh, Đặng, Bùi, etc.
    vn_name_pattern = Pattern(
        name="vn_name_pattern",
        regex=r"(Nguyễn|Trần|Lê|Phạm|Hoàng|Huỳnh|Đặng|Bùi|Vũ|Mai|Trương|Trịnh|Ngô|Đỗ|Dương|Tạ|Phan|Lý|Hồ|Châu|Văn|Thanh|Tấn|Hải|Hiếu|Bảo|Minhoạt|Cô|Yến|Hạnh|Ông|Bác|Ngọc|Hương)",
        score=0.7
    )
    vn_name_recognizer = PatternRecognizer(
        supported_entity="VN_PERSON",
        patterns=[vn_name_pattern]
    )

    # Use default analyzer with English support
    analyzer = AnalyzerEngine()

    analyzer.registry.add_recognizer(cccd_recognizer)
    analyzer.registry.add_recognizer(phone_recognizer)
    analyzer.registry.add_recognizer(vn_name_recognizer)
    analyzer.registry.add_recognizer(GLiNERRecognizer())

    return analyzer


def detect_pii(text: str, analyzer: AnalyzerEngine) -> list:
    results = analyzer.analyze(
        text=text,
        language="en",
        entities=["PERSON", "EMAIL_ADDRESS", "VN_CCCD", "VN_PHONE", "VN_PERSON",
                  "LOCATION", "ORGANIZATION"]
    )
    return results
