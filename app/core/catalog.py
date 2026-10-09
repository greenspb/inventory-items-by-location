"""Categorized Inventory Array & Spatial Cataloging Engine.

Implements the Pikmin 2 categorized array indexing pattern combined with
Pokémon Emerald spatial bounding and radial queries.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from app.core.models import InventoryItem, SpatialCoordinates


class CategorizedInventoryArray:
    """A cataloging engine inspired by Pikmin 2's categorized array memory layout.

    In Pikmin 2, carryable objects and treasures were segregated into dedicated,
    categorized arrays (e.g. PelletConfigList, Treasure series) for optimal cache
    locality and rapid physical evaluation (weight and value).

    This class maintains synchronized categorized arrays alongside spatial lookups
    derived from Pokémon Emerald's metLocation indexing.
    """

    def __init__(self) -> None:
        # Primary lookup table by item_id
        self._item_registry: Dict[str, InventoryItem] = {}
        # Categorized array partitions: Category -> List[InventoryItem]
        self._category_arrays: Dict[str, List[InventoryItem]] = defaultdict(list)

    def insert(self, item: InventoryItem) -> None:
        """Inserts or updates an item into the registry and categorized partition array."""
        if item.item_id in self._item_registry:
            self.remove(item.item_id)

        self._item_registry[item.item_id] = item
        self._category_arrays[item.physical_attrs.category].append(item)

    def remove(self, item_id: str) -> Optional[InventoryItem]:
        """Removes an item from the registry and its categorized array."""
        item = self._item_registry.pop(item_id, None)
        if item is not None:
            cat_list = self._category_arrays[item.physical_attrs.category]
            self._category_arrays[item.physical_attrs.category] = [
                i for i in cat_list if i.item_id != item_id
            ]
        return item

    def get(self, item_id: str) -> Optional[InventoryItem]:
        """Fetches an item by unique ID."""
        return self._item_registry.get(item_id)

    def clear(self) -> None:
        """Clears all indexed items."""
        self._item_registry.clear()
        self._category_arrays.clear()

    def get_category_array(self, category: str) -> List[InventoryItem]:
        """Returns the contiguous array of items belonging to a given category."""
        return list(self._category_arrays.get(category, []))

    def categories(self) -> List[str]:
        """Lists all active categories in the inventory."""
        return sorted([k for k, v in self._category_arrays.items() if len(v) > 0])

    def all_items(self) -> List[InventoryItem]:
        """Returns all items currently in the registry."""
        return list(self._item_registry.values())

    def __len__(self) -> int:
        return len(self._item_registry)

    def filter_items(
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
        """Filters items across physical attributes and spatial provenance metadata."""
        # Fast partition selection if category is provided
        if category and category != "ALL":
            candidate_pool = self.get_category_array(category)
        else:
            candidate_pool = self.all_items()

        results: List[InventoryItem] = []
        for item in candidate_pool:
            phys = item.physical_attrs
            meta = item.spatial_meta

            # Weight filter (Pikmin carrier capacity threshold)
            if min_weight is not None and phys.weight < min_weight:
                continue
            if max_weight is not None and phys.weight > max_weight:
                continue

            # Value filter (Pikmin Poko appraisal)
            if min_value is not None and phys.value < min_value:
                continue
            if max_value is not None and phys.value > max_value:
                continue

            # Provenance origin filter (Pokémon Emerald metGame equivalent)
            if origin_source and origin_source != "ALL":
                if meta.origin_source.lower() != origin_source.lower():
                    continue

            # Location tag filter (Pokémon Emerald metLocation / MAPSEC equivalent)
            if met_location_tag and met_location_tag.strip():
                if met_location_tag.lower() not in meta.met_location_tag.lower():
                    continue

            # General text search (name, notes, custodian)
            if search_query and search_query.strip():
                q = search_query.lower()
                matches_name = q in item.name.lower()
                matches_notes = q in item.notes.lower()
                matches_custodian = q in meta.custodian_id.lower()
                matches_loc = q in meta.met_location_tag.lower()
                if not (matches_name or matches_notes or matches_custodian or matches_loc):
                    continue

            results.append(item)

        return results

    def filter_by_spatial_radius(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        category: Optional[str] = None,
    ) -> List[Tuple[InventoryItem, float]]:
        """Finds items within a geographic radius, returning pairs of (item, distance_km) sorted by distance.

        Implements the Pokémon Emerald spatial encounter resolver logic.
        """
        center = SpatialCoordinates(latitude=center_lat, longitude=center_lon)
        candidates = self.get_category_array(category) if (category and category != "ALL") else self.all_items()

        within: List[Tuple[InventoryItem, float]] = []
        for item in candidates:
            dist = center.distance_to_km(item.spatial_meta.coordinates)
            if dist <= radius_km:
                within.append((item, dist))

        within.sort(key=lambda pair: pair[1])
        return within

    def aggregate_summary(self) -> Dict[str, any]:
        """Calculates Pikmin-style aggregates: total weight (carry load) and Pokos (total value)."""
        total_weight = sum(item.physical_attrs.weight for item in self._item_registry.values())
        total_value = sum(item.physical_attrs.value for item in self._item_registry.values())

        cat_breakdown: Dict[str, Dict[str, float]] = {}
        for cat, items in self._category_arrays.items():
            if not items:
                continue
            cat_breakdown[cat] = {
                "count": len(items),
                "weight_kg": round(sum(i.physical_attrs.weight for i in items), 3),
                "value_pokos": round(sum(i.physical_attrs.value for i in items), 2),
            }

        return {
            "total_items": len(self._item_registry),
            "total_weight_kg": round(total_weight, 3),
            "total_value_pokos": round(total_value, 2),
            "categories": cat_breakdown,
        }
