from pathlib import Path
import pytest
from app.cli.__main__ import main


@pytest.fixture
def cli_db(tmp_path: Path) -> str:
    db_file = tmp_path / "cli_test.db"
    return str(db_file)


def test_cli_add_and_list(cli_db: str, capsys):
    # Add an item
    ret = main([
        "--db", cli_db,
        "add",
        "--name", "Plasma Relay",
        "--category", "ELECTRONIC",
        "--weight", "2.4",
        "--value", "350",
        "--lat", "37.7749",
        "--lon", "-122.4194",
        "--met-tag", "MAPSEC_SECTOR_9",
    ])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Plasma Relay" in captured.out
    assert "Item successfully registered" in captured.out

    # List items
    ret = main(["--db", cli_db, "list"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Plasma Relay" in captured.out
    assert "ELECTRONIC" in captured.out


def test_cli_spatial_search_and_summary(cli_db: str, capsys):
    # Add two items at different coordinates
    main([
        "--db", cli_db,
        "add",
        "--name", "Local Sensor",
        "--category", "ELECTRONIC",
        "--weight", "1.0",
        "--value", "100",
        "--lat", "37.7749",
        "--lon", "-122.4194",
        "--met-tag", "MAPSEC_LOCAL",
    ])
    main([
        "--db", cli_db,
        "add",
        "--name", "Distant Module",
        "--category", "MECHANICAL",
        "--weight", "10.0",
        "--value", "500",
        "--lat", "40.7128",
        "--lon", "-74.0060",
        "--met-tag", "MAPSEC_NYC",
    ])
    # Flush output from add commands
    capsys.readouterr()

    # Search near SF (within 20 km)
    ret = main([
        "--db", cli_db,
        "search-spatial",
        "--lat", "37.7750",
        "--lon", "-122.4190",
        "--radius-km", "20.0",
    ])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Local Sensor" in captured.out
    assert "Distant Module" not in captured.out

    # Summary
    ret = main(["--db", cli_db, "summary"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "PIKMIN 2 AGGREGATE CATALOG SUMMARY" in captured.out
    assert "Total Registered Items   : 2" in captured.out
