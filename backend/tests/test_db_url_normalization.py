from app.db.session import _normalized_database_url


def test_postgres_scheme_gets_psycopg_driver():
    assert (
        _normalized_database_url("postgres://user:pw@host/db")
        == "postgresql+psycopg://user:pw@host/db"
    )


def test_postgresql_scheme_gets_psycopg_driver():
    assert (
        _normalized_database_url("postgresql://user:pw@host/db?sslmode=require")
        == "postgresql+psycopg://user:pw@host/db?sslmode=require"
    )


def test_sqlite_url_is_left_untouched():
    assert _normalized_database_url("sqlite:///./saans.db") == "sqlite:///./saans.db"
