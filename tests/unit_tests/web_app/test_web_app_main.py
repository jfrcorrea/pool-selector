"""Testes unitários para o módulo web_app/main."""

from unittest.mock import MagicMock, patch

with patch("web_app.main.utils.setup_duckdb"):
    with patch("web_app.main.FastAPI"):
        from web_app import main


main.S3_BUCKET_NAME = "pools-info"
main.S3_FILE_NAME = "spark_events.json"
main.LOG_LEVEL = "INFO"


@patch("web_app.main.duckdb")
@patch("web_app.main.utils.make_where_clause")
def test_get_pool(mock_make_where_clause: MagicMock, mock_duckdb: MagicMock) -> None:
    """Testa o método get_pool()."""
    mock_make_where_clause.return_value = "WHERE 1 = 1"
    mock_duckdb.sql.return_value.fetchall.return_value = [("xpto",)]
    main.logger = MagicMock()

    result = main.get_pool(instance_types="xyz")

    assert result == {"pool_id": "xpto"}

    mock_make_where_clause.assert_called_once_with(main.logger, "xyz")
    mock_duckdb.sql.return_value.fetchall.assert_called_once()
    mock_duckdb.sql.assert_called_once_with(
        f"""
        WITH cte as (
          SELECT pool_id,
                 COUNT(*) AS qtde,
                 COUNT(*) FILTER(reason = 'SPOT_INSTANCE_TERMINATION') AS qtde_spot_instance_termination
          FROM 's3://{main.S3_BUCKET_NAME}/{main.S3_FILE_NAME}'
          {mock_make_where_clause.return_value}
          GROUP BY pool_id
        )
        SELECT pool_id
        FROM cte
        ORDER BY qtde_spot_instance_termination / qtde
        LIMIT 1;
        """
    )
