import json
from dataclasses import dataclass, field


ALLOWED_METHODS = {"regex", "llm", "manual", "not_found"}


@dataclass
class ExtractedField:
    name: str
    label: str
    value: str | None = None
    confidence: float = 0.0
    method: str = "not_found"
    source_text: str | None = None
    warnings: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.method not in ALLOWED_METHODS:
            allowed_methods = ", ".join(sorted(ALLOWED_METHODS))
            raise ValueError(f"method must be one of: {allowed_methods}")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

        if self.method == "not_found":
            if self.value is not None:
                raise ValueError("not_found fields must have value=None")
            if self.confidence != 0.0:
                raise ValueError("not_found fields must have confidence=0.0")
        elif self.value is None:
            raise ValueError("found fields must have a value; use method='not_found' for missing fields")

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "label": self.label,
            "value": self.value,
            "confidence": self.confidence,
            "method": self.method,
            "source_text": self.source_text,
            "warnings": list(self.warnings),
        }


@dataclass
class ExtractionResult:
    contract_number: ExtractedField
    contract_date: ExtractedField
    period_start: ExtractedField
    period_end: ExtractedField
    insurer_inn: ExtractedField
    policyholder_inn: ExtractedField
    total_insurance_premium: ExtractedField
    total_insured_amount: ExtractedField
    pledge_agreements: list[ExtractedField] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "contract_number": self.contract_number.to_dict(),
            "contract_date": self.contract_date.to_dict(),
            "period_start": self.period_start.to_dict(),
            "period_end": self.period_end.to_dict(),
            "insurer_inn": self.insurer_inn.to_dict(),
            "policyholder_inn": self.policyholder_inn.to_dict(),
            "total_insurance_premium": self.total_insurance_premium.to_dict(),
            "total_insured_amount": self.total_insured_amount.to_dict(),
            "pledge_agreements": [field.to_dict() for field in self.pledge_agreements],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)
