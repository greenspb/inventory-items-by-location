"""Persistence Layer for Location-Based Inventory System.

Provides robust, lightweight local SQLite persistence with JSON backup/export
capabilities, ensuring decoupled persistence accessible by both CLI and GUI interfaces.
"""

from __future__ import annotations

import contextlib
import json
import sqlite3
from typing import List, Optional

from app.core.models import (
    InventoryItem,
    MetLocationMetadata,
    PhysicalAttributes,
    SpatialCoordinates,
)


class InventoryRepository:
    """Manages persistent SQLite storage for InventoryItem entities."""

    def __init__(self, db_path: str = "inventory.db") -> None:
        self.db_path = db_path
        self._init_db()

    @contextlib.contextmanager
    def _connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Initializes database schema with indexing for fast category and spatial queries."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory_items (
                    item_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    weight REAL NOT NULL,
                    value REAL NOT NULL,
                    dim_l REAL NOT NULL DEFAULT 10.0,
                    dim_w REAL NOT NULL DEFAULT 10.0,
                    dim_h REAL NOT NULL DEFAULT 10.0,
                    fragility INTEGER NOT NULL DEFAULT 1,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    altitude REAL NOT NULL DEFAULT 0.0,
                    accuracy_meters REAL NOT NULL DEFAULT 1.0,
                    met_location_tag TEXT NOT NULL,
                    met_timestamp TEXT NOT NULL,
                    origin_source TEXT NOT NULL,
                    custodian_id TEXT NOT NULL,
                    containment_type TEXT NOT NULL,
                    condition_level INTEGER NOT NULL DEFAULT 100,
                    notes TEXT NOT NULL DEFAULT ''
                );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cat ON inventory_items(category);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_loc ON inventory_items(met_location_tag);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_coords ON inventory_items(latitude, longitude);")
            conn.commit()

    def save(self, item: InventoryItem) -> None:
        """Upserts an inventory item into the SQLite database."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO inventory_items (
                    item_id, name, category, weight, value,
                    dim_l, dim_w, dim_h, fragility,
                    latitude, longitude, altitude, accuracy_meters,
                    met_location_tag, met_timestamp, origin_source,
                    custodian_id, containment_type, condition_level, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(item_id) DO UPDATE SET
                    name = excluded.name,
                    category = excluded.category,
                    weight = excluded.weight,
                    value = excluded.value,
                    dim_l = excluded.dim_l,
                    dim_w = excluded.dim_w,
                    dim_h = excluded.dim_h,
                    fragility = excluded.fragility,
                    latitude = excluded.latitude,
                    longitude = excluded.longitude,
                    altitude = excluded.altitude,
                    accuracy_meters = excluded.accuracy_meters,
                    met_location_tag = excluded.met_location_tag,
                    met_timestamp = excluded.met_timestamp,
                    origin_source = excluded.origin_source,
                    custodian_id = excluded.custodian_id,
                    containment_type = excluded.containment_type,
                    condition_level = excluded.condition_level,
                    notes = excluded.notes;
            """, (
                item.item_id,
                item.name,
                item.physical_attrs.category,
                item.physical_attrs.weight,
                item.physical_attrs.value,
                item.physical_attrs.dimensions_cm[0],
                item.physical_attrs.dimensions_cm[1],
                item.physical_attrs.dimensions_cm[2],
                item.physical_attrs.fragility,
                item.spatial_meta.coordinates.latitude,
                item.spatial_meta.coordinates.longitude,
                item.spatial_meta.coordinates.altitude,
                item.spatial_meta.coordinates.accuracy_meters,
                item.spatial_meta.met_location_tag,
                item.spatial_meta.met_timestamp,
                item.spatial_meta.origin_source,
                item.spatial_meta.custodian_id,
                item.spatial_meta.containment_type,
                item.spatial_meta.condition_level,
                item.notes,
            ))
            conn.commit()

    def get(self, item_id: str) -> Optional[InventoryItem]:
        """Retrieves a single item by ID."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM inventory_items WHERE item_id = ?", (item_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_item(row)

    def delete(self, item_id: str) -> bool:
        """Deletes an item by ID. Returns True if an item was deleted."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM inventory_items WHERE item_id = ?", (item_id,))
            conn.commit()
            return cursor.rowcount > 0

    def load_all(self) -> List[InventoryItem]:
        """Loads all inventory items from the database."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM inventory_items ORDER BY name ASC")
            rows = cursor.fetchall()
            return [self._row_to_item(r) for r in rows]

    def count(self) -> int:
        """Returns total count of stored items."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM inventory_items")
            return int(cursor.fetchone()[0])

    def export_to_json(self, filepath: str) -> None:
        """Exports full database to a JSON file."""
        items = self.load_all()
        data = [i.to_dict() for i in items]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def import_from_json(self, filepath: str) -> int:
        """Imports items from a JSON file. Returns count of imported items."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        imported_count = 0
        for item_dict in data:
            item = InventoryItem.from_dict(item_dict)
            self.save(item)
            imported_count += 1
        return imported_count

    @staticmethod
    def _row_to_item(row: sqlite3.Row) -> InventoryItem:
        coords = SpatialCoordinates(
            latitude=row["latitude"],
            longitude=row["longitude"],
            altitude=row["altitude"],
            accuracy_meters=row["accuracy_meters"],
        )
        spatial_meta = MetLocationMetadata(
            coordinates=coords,
            met_location_tag=row["met_location_tag"],
            met_timestamp=row["met_timestamp"],
            origin_source=row["origin_source"],
            custodian_id=row["custodian_id"],
            containment_type=row["containment_type"],
            condition_level=row["condition_level"],
        )
        physical_attrs = PhysicalAttributes(
            category=row["category"],
            weight=row["weight"],
            value=row["value"],
            dimensions_cm=(row["dim_l"], row["dim_w"], row["dim_h"]),
            fragility=row["fragility"],
        )
        return InventoryItem(
            item_id=row["item_id"],
            name=row["name"],
            spatial_meta=spatial_meta,
            physical_attrs=physical_attrs,
            notes=row["notes"],
        )
