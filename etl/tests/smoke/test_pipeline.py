from pathlib import Path

import pytest


def test_default_source_is_relative_to_the_repository(monkeypatch, tmp_path):
    from pipeline import parse_args

    monkeypatch.delenv("TAXI_DATA_DIR", raising=False)
    monkeypatch.chdir(tmp_path)
    config = parse_args([])

    repository = Path(__file__).resolve().parents[3]
    assert config.month == "2024-01"
    assert config.source == repository / "data/raw/yellow_taxi/yellow_tripdata_2024-01.parquet"
    assert config.download is True


def test_data_directory_and_explicit_local_source(monkeypatch, tmp_path):
    from pipeline import parse_args

    data_dir = tmp_path / "configured"
    monkeypatch.setenv("TAXI_DATA_DIR", str(data_dir))
    config = parse_args(["--month", "2024-02"])
    assert config.source == data_dir / "raw/yellow_taxi/yellow_tripdata_2024-02.parquet"

    override = tmp_path / "override"
    fixture = tmp_path / "fixture.parquet"
    config = parse_args(["--data-dir", str(override), "--source", str(fixture)])
    assert config.data_dir == override
    assert config.source == fixture
    assert config.download is False


@pytest.mark.parametrize("month", ["2024-13", "2024-1", "../2024-01"])
def test_invalid_month_has_a_cli_error(month, capsys):
    from pipeline import parse_args

    with pytest.raises(SystemExit) as error:
        parse_args(["--month", month])

    assert error.value.code == 2
    assert "YYYY-MM" in capsys.readouterr().err
