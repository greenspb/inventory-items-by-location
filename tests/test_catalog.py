"""Tests for CategorizedInventoryArray (Pikmin array indexing & Pokemon spatial queries)."""

import pytest
from app.core.catalog import CategorizedInventoryArray
from app.core.models import (
    InventoryItem,
    MetLocationMetadata,
    PhysicalAttributes,
    SpatialCoordinates,
)


def make_item(
    name: str,
    category: str,
    weight: float,
    value: float,
    lat: float,
    lon: float,
    tag: str = "MAPSEC_SECTOR_A",
    origin: str = "FIELD_DISCOVERY",
) -> InventoryItem:
    coords = SpatialCoordinates(latitude=lat, longitude=lon)
    meta = MetLocationMetadata(
        coordinates=coords,
        met_location_tag=tag,
        origin_source=origin,
    )
    attrs = PhysicalAttributes(
        category=category,
        weight=weight,
        value=value,
    )
    return InventoryItem(name=name, spatial_meta=meta, physical_attrs=attrs)


@pytest.fixture
def populated_catalog() -> CategorizedInventoryArray:
    catalog = CategorizedInventoryArray()
    items = [
        # San Francisco area items
        make_item("Gear Assembly", "MECHANICAL", 10.0, 100.0, 37.7749, -122.4194, "MAPSEC_MISSION_BAY", "SALVAGED"),
        make_item("Circuit Board", "ELECTRONIC", 0.5, 250.0, 37.7800, -122.4100, "MAPSEC_SOMA_HUB", "PROCURED"),
        make_item("Heavy Engine", "MECHANICAL", 50.0, 600.0, 37.7720, -122.4200, "MAPSEC_MISSION_BAY", "SALVAGED"),
        make_item("Mineral Core", "SPECIMEN", 3.0, 400.0, 37.7900, -122.4000, "MAPSEC_EMBARCADERO", "FIELD_DISCOVERY"),
        # Los Angeles item (~550 km away)
        make_item("Sunken Relic", "ARTIFACT", 15.0, 950.0, 34.0522, -118.2437, "MAPSEC_LA_HARBOR", "EXCAVATED"),
    ]
    for item in items:
        catalog.insert(item)
    return catalog


def test_categorized_array_partitioning(populated_catalog: CategorizedInventoryArray):
    """Validates that items are properly indexed in Pikmin-style categorized arrays."""
    assert len(populated_catalog) == 5
    mech_items = populated_catalog.get_category_array("MECHANICAL")
    assert len(mech_items) == 2
    assert all(i.physical_attrs.category == "MECHANICAL" for i in mech_items)

    elec_items = populated_catalog.get_category_array("ELECTRONIC")
    assert len(elec_items) == 1
    assert elec_items[0].name == "Circuit Board"

    cats = populated_catalog.categories()
    assert set(cats) == {"MECHANICAL", "ELECTRONIC", "SPECIMEN", "ARTIFACT"}


def test_filter_by_weight_and_value(populated_catalog: CategorizedInventoryArray):
    """Validates physical attribute filtering (Pikmin carrier capacity and Poko appraisal)."""
    # Weight range: 1.0 to 15.0 kg
    mid_weight = populated_catalog.filter_items(min_weight=1.0, max_weight=15.0)
    names = [i.name for i in mid_weight]
    assert "Gear Assembly" in names
    assert "Mineral Core" in names
    assert "Sunken Relic" in names
    assert "Circuit Board" not in names  # weight 0.5
    assert "Heavy Engine" not in names   # weight 50.0

    # Value range: at least 400 Pokos
    valuable = populated_catalog.filter_items(min_value=400.0)
    val_names = [i.name for i in valuable]
    assert set(val_names) == {"Heavy Engine", "Mineral Core", "Sunken Relic"}


def test_filter_by_spatial_radius(populated_catalog: CategorizedInventoryArray):
    """Validates Pokémon Emerald spatial resolver (radial distance from origin coordinates)."""
    # Search within 10 km of downtown SF (37.7749, -122.4194)
    nearby = populated_catalog.filter_by_spatial_radius(
        center_lat=37.7749,
        center_lon=-122.4194,
        radius_km=10.0,
    )
    # The 4 Bay Area items should be returned, sorted by distance
    assert len(nearby) == 4
    # The first item should be "Gear Assembly" (distance ~0 km)
    assert nearby[0][0].name == "Gear Assembly"
    assert nearby[0][1] < 0.1

    # Los Angeles item is > 500 km away and should NOT be in the results
    nearby_names = [pair[0].name for pair in nearby]
    assert "Sunken Relic" not in nearby_names


def test_aggregate_summary(populated_catalog: CategorizedInventoryArray):
    """Validates Pikmin 2 aggregate carry load and Poko valuation metrics."""
    summary = populated_catalog.aggregate_summary()
    assert summary["total_items"] == 5
    # Total weight: 10 + 0.5 + 50 + 3 + 15 = 78.5 kg
    assert summary["total_weight_kg"] == 78.5
    # Total value: 100 + 250 + 600 + 400 + 950 = 2300.0 Pokos
    assert summary["total_value_pokos"] == 2300.0
    assert "MECHANICAL" in summary["categories"]
    assert summary["categories"]["MECHANICAL"]["count"] == 2
    assert summary["categories"]["MECHANICAL"]["weight_kg"] == 60.0
