# src/models/__init__.py
from .fiscal_schemas import (
    CenarioSimulacaoInput,
    BestResponse,
    HTTPErrorModel,
    HTTPValidationErrorModel,
    ValidationErrorDetail,
    VencedorResumo,
    ComparativoRapido
)

__all__ = [
    "CenarioSimulacaoInput",
    "BestResponse",
    "HTTPErrorModel",
    "HTTPValidationErrorModel",
    "ValidationErrorDetail",
    "VencedorResumo",
    "ComparativoRapido"
]