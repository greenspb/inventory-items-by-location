"""Inventory Service Layer.

Orchestrates the CategorizedInventoryArray catalog and InventoryRepository
persistence, acting as the unified controller for both GUI and CLI frontends.
"""

from __future__ import annotations

import datetime
from typing import Dict, List, Optional, Tuple

from app.core.catalog import CategorizedInventoryArray
from app.core.models import (
    InventoryItem,
    MetLocationMetadata,
    PhysicalAttributes,
    SpatialCoordinates,
)
from app.storage.repository import InventoryRepository


class InventoryService:
    """Unified application service coordinating business logic, spatial querying,

    Pikmin categorized arrays, and SQLite persistence.
    """

    def __init__(self, db_path: str = "inventory.db") -> None:
        self.repository = InventoryRepository(db_path)
        self.catalog = CategorizedInventoryArray()
        self.reload_from_storage()

    def reload_from_storage(self) -> None:
        """Loads all persisted items into the in-memory categorized array."""
        self.catalog.clear()
        persisted_items = self.repository.load_all()
        for item in persisted_items:
            self.catalog.insert(item)

    def register_item(
        self,
        name: str,
        category: str,
        weight: float,
        value: float,
        latitude: float,
        longitude: float,
        met_location_tag: str,
        altitude: float = 0.0,
        accuracy_meters: float = 1.0,
        origin_source: str = "FIELD_DISCOVERY",
        custodian_id: str = "OPERATOR_01",
        containment_type: str = "STANDARD_CONTAINER",
        condition_level: int = 100,
        dimensions_cm: Tuple[float, float, float] = (10.0, 10.0, 10.0),
        fragility: int = 1,
        notes: str = "",
        item_id: Optional[str] = None,
        met_timestamp: Optional[str] = None,
    ) -> InventoryItem:
        """Creates, indexes, and persists a new item."""
        coords = SpatialCoordinates(
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
            accuracy_meters=accuracy_meters,
        )

        timestamp = (
            met_timestamp
            if met_timestamp
            else datetime.datetime.now(datetime.timezone.utc).isoformat()
        )

        spatial_meta = MetLocationMetadata(
            coordinates=coords,
            met_location_tag=met_location_tag,
            met_timestamp=timestamp,
            origin_source=origin_source,
            custodian_id=custodian_id,
            containment_type=containment_type,
            condition_level=condition_level,
        )

        physical_attrs = PhysicalAttributes(
            category=category.upper(),
            weight=weight,
            value=value,
            dimensions_cm=dimensions_cm,
            fragility=fragility,
        )

        item = InventoryItem(
            name=name,
            spatial_meta=spatial_meta,
            physical_attrs=physical_attrs,
            notes=notes,
        )
        if item_id:
            item.item_id = item_id

        # Persist and update catalog array
        self.repository.save(item)
        self.catalog.insert(item)
        return item

    def delete_item(self, item_id: str) -> bool:
        """Removes item from both database and catalog array."""
        self.catalog.remove(item_id)
        return self.repository.delete(item_id)

    def get_item(self, item_id: str) -> Optional[InventoryItem]:
        """Fetches item from memory catalog (falls back to repository)."""
        cached = self.catalog.get(item_id)
        if cached:
            return cached
        return self.repository.get(item_id)

    def list_items(
        self,
        category: Optional[str] = None,
        min_weight: Optional[float] = None,
        max_weight: Optional[float] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        origin_source: Optional[str] = None,
        met_location_tag: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> List[InventoryItem]:
        """Queries the indexed catalog array."""
        return self.catalog.filter_items(
            category=category,
            min_weight=min_weight,
            max_weight=max_weight,
            min_value=min_value,
            max_value=max_value,
            origin_source=origin_source,
            met_location_tag=met_location_tag,
            search_query=search_query,
        )

    def search_nearby(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        category: Optional[str] = None,
    ) -> List[Tuple[InventoryItem, float]]:
        """Finds items within a geographic radius in kilometers."""
        return self.catalog.filter_by_spatial_radius(
            center_lat=center_lat,
            center_lon=center_lon,
            radius_km=radius_km,
            category=category,
        )

    def get_summary(self) -> Dict[str, any]:
        """Produces aggregate carrying capacity and Poko appraisal statistics."""
        return self.catalog.aggregate_summary()

    def get_categories(self) -> List[str]:
        """Retrieves list of active categories."""
        return self.catalog.categories()

    def export_data(self, filepath: str) -> None:
        """Exports data to JSON."""
        self.repository.export_to_json(filepath)

    def import_data(self, filepath: str) -> int:
        """Imports data from JSON and updates catalog."""
        count = self.repository.import_from_json(filepath)
        self.reload_from_storage()
        return count
