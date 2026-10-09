"""Tests for core dataclasses (Pokemon Emerald & Pikmin 2 data models)."""

import pytest
from app.core.models import (
    InventoryItem,
    MetLocationMetadata,
    PhysicalAttributes,
    SpatialCoordinates,
)


def test_spatial_coordinates_distance():
    # San Francisco: ~37.7749, -122.4194
    sf = SpatialCoordinates(latitude=37.7749, longitude=-122.4194)
    # Oakland: ~37.8044, -122.2712 (~13.5 km apart)
    oakland = SpatialCoordinates(latitude=37.8044, longitude=-122.2712)

    dist = sf.distance_to_km(oakland)
    assert 12.0 < dist < 15.0
    assert sf.within_radius_km(oakland, 20.0) is True
    assert sf.within_radius_km(oakland, 10.0) is False


def test_spatial_coordinates_roundtrip_dict():
    coords = SpatialCoordinates(latitude=40.7128, longitude=-74.0060, altitude=15.0, accuracy_meters=2.5)
    d = coords.to_dict()
    reconstructed = SpatialCoordinates.from_dict(d)
    assert reconstructed.latitude == coords.latitude
    assert reconstructed.longitude == coords.longitude
    assert reconstructed.altitude == coords.altitude
    assert reconstructed.accuracy_meters == coords.accuracy_meters


def test_met_location_metadata_pokemon_pattern():
    coords = SpatialCoordinates(latitude=35.6762, longitude=139.6503)
    meta = MetLocationMetadata(
        coordinates=coords,
        met_location_tag="MAPSEC_SILPH_CO_TOWER",
        origin_source="FIELD_DISCOVERY",
        custodian_id="TRAINER_RED",
        containment_type="ULTRA_BALL_POD",
        condition_level=95,
    )
    d = meta.to_dict()
    assert d["met_location_tag"] == "MAPSEC_SILPH_CO_TOWER"
    assert d["origin_source"] == "FIELD_DISCOVERY"
    assert d["custodian_id"] == "TRAINER_RED"

    reconstructed = MetLocationMetadata.from_dict(d)
    assert reconstructed.met_location_tag == meta.met_location_tag
    assert reconstructed.custodian_id == meta.custodian_id
    assert reconstructed.condition_level == 95


def test_physical_attributes_pikmin_pattern():
    attrs = PhysicalAttributes(
        category="MECHANICAL",
        weight=25.5,
        value=850.0,
        dimensions_cm=(30.0, 20.0, 10.0),
        fragility=2,
    )
    assert attrs.volume_cm3 == 6000.0

    d = attrs.to_dict()
    assert d["category"] == "MECHANICAL"
    assert d["weight"] == 25.5
    assert d["value"] == 850.0

    reconstructed = PhysicalAttributes.from_dict(d)
    assert reconstructed.category == "MECHANICAL"
    assert reconstructed.dimensions_cm == (30.0, 20.0, 10.0)


def test_inventory_item_roundtrip():
    coords = SpatialCoordinates(latitude=51.5074, longitude=-0.1278)
    meta = MetLocationMetadata(coordinates=coords, met_location_tag="MAPSEC_LONDON_DEPOT")
    attrs = PhysicalAttributes(category="ARTIFACT", weight=4.2, value=340.0)

    item = InventoryItem(
        name="Ancient Astrolabe",
        spatial_meta=meta,
        physical_attrs=attrs,
        notes="Recovered during excavation",
    )

    d = item.to_dict()
    reconstructed = InventoryItem.from_dict(d)
    assert reconstructed.item_id == item.item_id
    assert reconstructed.name == "Ancient Astrolabe"
    assert reconstructed.physical_attrs.weight == 4.2
    assert reconstructed.spatial_meta.met_location_tag == "MAPSEC_LONDON_DEPOT"
    assert reconstructed.notes == "Recovered during excavation"
