"""Testes unitários para o módulo event_generator/model."""

import pytest

from event_generator import model


class TestSparkEvent:
    """Testes para a classe SparkEvent."""

    def test_to_json(self) -> None:
        """Testes para o método to_json()."""
        spark_event = model.SparkEvent(
            finished_at="2024-08-07T00:04:52.767830",
            job_id="my-job",
            pool_id="pool-r6.xlarge-us-east-1c",
            status="FAILED",
            reason="SPOT_INSTANCE_TERMINATION",
        )

        expected_result = (
            '{"finished_at": "2024-08-07T00:04:52.767830", "job_id": "my-job", "pool_id": "pool-r6.xlarge-us-east-1c",'
            ' "status": "FAILED", "reason": "SPOT_INSTANCE_TERMINATION"}'
        )

        assert spark_event.to_json() == expected_result

    def test___post_init__(self) -> None:
        """Testes para o método __post_init__()."""

        # Testa valor inválido para `finished_at`
        with pytest.raises(ValueError):
            model.SparkEvent(
                finished_at="xpto-08-07T00:04:52.767830",
                job_id="my-job",
                pool_id="pool-r6.xlarge-us-east-1c",
                status="FAILED",
                reason="SPOT_INSTANCE_TERMINATION",
            )

        # Testa `pool_id` inválido
        with pytest.raises(AssertionError, match="O `pool_id` deve iniciar com 'pool-'"):
            model.SparkEvent(
                finished_at="2024-08-07T00:04:52.767830",
                job_id="my-job",
                pool_id="xpto-r6.xlarge-us-east-1c",
                status="FAILED",
                reason="SPOT_INSTANCE_TERMINATION",
            )
        with pytest.raises(AssertionError, match="O `pool_id` é inválido"):
            model.SparkEvent(
                finished_at="2024-08-07T00:04:52.767830",
                job_id="my-job",
                pool_id="pool-xpto",
                status="FAILED",
                reason="SPOT_INSTANCE_TERMINATION",
            )

        # Testa `status` inválido
        with pytest.raises(AssertionError, match="`XPTO` é um status inválido"):
            model.SparkEvent(
                finished_at="2024-08-07T00:04:52.767830",
                job_id="my-job",
                pool_id="pool-r6.xlarge-us-east-1c",
                status="XPTO",
                reason="SPOT_INSTANCE_TERMINATION",
            )

        # Testa `reason` inválido
        with pytest.raises(AssertionError, match="`XPTO` é um reason inválido"):
            model.SparkEvent(
                finished_at="2024-08-07T00:04:52.767830",
                job_id="my-job",
                pool_id="pool-r6.xlarge-us-east-1c",
                status="FAILED",
                reason="XPTO",
            )
