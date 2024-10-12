"""Declaração das classes de dados."""

from dataclasses import dataclass
from datetime import datetime
import json

# Lista de Status possíveis.
STATUS_LIST = [
    "SUCCEEDED",
    "FAILED",
]

# Lista de valores possíveis para o atributo `reason`.
REASON_LIST = [
    "SPOT_INSTANCE_TERMINATION",
    "TIMED_OUT",
    "SPARK_EXECUTION_ERROR",
]

# Instâncias de exemplo para geração de eventos de teste.
INSTANCE_TYPES = [
    "i3.xlarge",
    "i4g.xlarge",
    "r6a.xlarge",
    "c6a.xlarge",
    "r6a.xlarge",
]

# Lista de zonas de disponibilidade da AWS (AZs) de exemplo
AZS = [
    "us-east-1a",
    "us-east-1b",
    "us-east-1c",
    "us-east-1d",
    "us-east-1e",
]


@dataclass
class SparkEvent:
    """Dados de um Spark Job finalizado."""

    finished_at: str
    job_id: str
    pool_id: str
    status: str
    reason: str

    def __post_init__(self) -> None:
        """Valida os atributos."""

        # Valida o atributo `finished_at`
        datetime.fromisoformat(self.finished_at)

        # Valida o atributo `pool_id`
        assert self.pool_id.startswith("pool-"), "O `pool_id` deve iniciar com 'pool-'"
        assert len(self.pool_id.split("-")) > 2, "O `pool_id` é inválido"

        # Valida o atributo `status`
        assert self.status in STATUS_LIST, f"`{self.status}` é um status inválido"

        # Valida o atributo `reason`
        assert self.reason in REASON_LIST or self.reason == "", f"`{self.reason}` é um reason inválido"

    def to_json(self) -> str:
        """Retorna o evento em formato JSON.

        Returns:
            str: O evento em formato JSON
        """
        return json.dumps(self.__dict__)
