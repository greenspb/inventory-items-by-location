"""Tests for InventoryRepository SQLite persistence and JSON interoperability."""

from pathlib import Path
import pytest
from app.core.models import (
    InventoryItem,
    MetLocationMetadata,
    PhysicalAttributes,
    SpatialCoordinates,
)
from app.storage.repository import InventoryRepository


@pytest.fixture
def temp_db_repo(tmp_path: Path):
    db_file = tmp_path / "test_inventory.db"
    return InventoryRepository(db_path=str(db_file))


def test_repository_save_get_and_count(temp_db_repo: InventoryRepository):
    coords = SpatialCoordinates(latitude=48.8566, longitude=2.3522, altitude=35.0)
    meta = MetLocationMetadata(
        coordinates=coords,
        met_location_tag="MAPSEC_PARIS_LAB",
        origin_source="PROCURED",
        custodian_id="OPERATOR_FR",
    )
    attrs = PhysicalAttributes(category="ELECTRONIC", weight=1.2, value=450.0)
    item = InventoryItem(name="Laser Diode", spatial_meta=meta, physical_attrs=attrs)

    assert temp_db_repo.count() == 0
    temp_db_repo.save(item)
    assert temp_db_repo.count() == 1

    fetched = temp_db_repo.get(item.item_id)
    assert fetched is not None
    assert fetched.name == "Laser Diode"
    assert fetched.physical_attrs.category == "ELECTRONIC"
    assert fetched.physical_attrs.weight == 1.2
    assert fetched.physical_attrs.value == 450.0
    assert fetched.spatial_meta.coordinates.latitude == 48.8566
    assert fetched.spatial_meta.met_location_tag == "MAPSEC_PARIS_LAB"


def test_repository_persistence_across_instances(temp_db_repo: InventoryRepository):
    coords = SpatialCoordinates(latitude=52.5200, longitude=13.4050)
    meta = MetLocationMetadata(coordinates=coords, met_location_tag="MAPSEC_BERLIN")
    attrs = PhysicalAttributes(category="SPECIMEN", weight=8.0, value=720.0)
    item = InventoryItem(name="Fossil Fragment", spatial_meta=meta, physical_attrs=attrs)

    temp_db_repo.save(item)

    # Instantiate a new repository pointing to the same SQLite file
    repo2 = InventoryRepository(db_path=temp_db_repo.db_path)
    all_items = repo2.load_all()
    assert len(all_items) == 1
    assert all_items[0].name == "Fossil Fragment"


def test_repository_delete(temp_db_repo: InventoryRepository):
    coords = SpatialCoordinates(latitude=1.0, longitude=2.0)
    meta = MetLocationMetadata(coordinates=coords, met_location_tag="TAG_X")
    attrs = PhysicalAttributes(category="ARTIFACT", weight=1.0, value=10.0)
    item = InventoryItem(name="Discardable", spatial_meta=meta, physical_attrs=attrs)

    temp_db_repo.save(item)
    assert temp_db_repo.count() == 1

    deleted = temp_db_repo.delete(item.item_id)
    assert deleted is True
    assert temp_db_repo.count() == 0
    assert temp_db_repo.get(item.item_id) is None


def test_repository_json_export_and_import(temp_db_repo: InventoryRepository, tmp_path: Path):
    coords = SpatialCoordinates(latitude=35.6895, longitude=139.6917)
    meta = MetLocationMetadata(coordinates=coords, met_location_tag="MAPSEC_TOKYO_HQ")
    attrs = PhysicalAttributes(category="MECHANICAL", weight=3.5, value=500.0)
    item = InventoryItem(name="Robotic Actuator", spatial_meta=meta, physical_attrs=attrs)
    temp_db_repo.save(item)

    json_path = str(tmp_path / "export.json")
    temp_db_repo.export_to_json(json_path)

    # Import into a fresh repo
    db2_path = str(tmp_path / "imported.db")
    repo_fresh = InventoryRepository(db_path=db2_path)
    count = repo_fresh.import_from_json(json_path)
    assert count == 1
    assert repo_fresh.count() == 1
    imported_item = repo_fresh.get(item.item_id)
    assert imported_item is not None
    assert imported_item.name == "Robotic Actuator"
