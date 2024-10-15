"""Testes unitários para o módulo event_generator/main."""

from unittest.mock import ANY, MagicMock, patch

from event_generator import main

main.AWS_KEY_ID = "aaa"
main.AWS_SECRET = "bbb"
main.LOCALSTACK_URL = "localstack"
main.LOCALSTACK_PORT = "4566"
main.S3_BUCKET_NAME = "pools-info"
main.S3_FILE_NAME = "spark_events.json"


@patch("boto3.session.Session")
def test_get_s3_client(mock_session: MagicMock) -> None:
    """Testa o método get_s3_client()."""

    result = main.get_s3_client()

    # Testa a chamada `boto3.session.Session()``
    mock_session.assert_called_once()

    mock_session.return_value.client.assert_called_once_with(
        service_name="s3",
        aws_access_key_id=main.AWS_KEY_ID,
        aws_secret_access_key=main.AWS_SECRET,
        endpoint_url=f"http://{main.LOCALSTACK_URL}:{main.LOCALSTACK_PORT}",
    )

    assert result == mock_session.return_value.client.return_value


def test_s3_append_data() -> None:
    """Testa o método s3_append_data()."""
    mock_s3_client = MagicMock()
    main.s3_append_data(
        s3_client=mock_s3_client,
        data='{"xpto":"xyz"}',
    )

    mock_s3_client.put_object.assert_called_once_with(
        Body=ANY,
        Bucket=main.S3_BUCKET_NAME,
        Key=main.S3_FILE_NAME,
    )


@patch("event_generator.main.s3_append_data")
def test_send_random_data(mock_s3_append_data: MagicMock) -> None:
    """Testa o método send_random_data()."""
    mock_s3_client = MagicMock()
    main.send_random_data(mock_s3_client)

    mock_s3_append_data.assert_called_once_with(s3_client=mock_s3_client, data=ANY)
