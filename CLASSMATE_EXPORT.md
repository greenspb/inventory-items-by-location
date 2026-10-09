# Location-Based Inventory System: Complete Project Export

> **Project Reference Document**  
> Adapted from classic Game Boy Advance & GameCube decompilations:
> - **Pokémon Emerald (`pret/pokeemerald`)**: Spatial provenance & "Met Location" substructure pattern (`PokemonSubstruct3`).
> - **Pikmin 2 (`projectPiki/pikmin2`)**: Categorized inventory arrays pattern (`PelletConfig` / `TreasureMgr`).

---

## 1. Execution Log & Test Verification

```
[OK] Initialized Python virtual environment (.venv)
[OK] Installed isolated pytest dependency (pytest>=8.0.0)
[OK] Implemented core domain models: SpatialCoordinates, MetLocationMetadata, PhysicalAttributes, InventoryItem
[OK] Implemented Pikmin-style CategorizedInventoryArray cataloging engine with Haversine radial lookup
[OK] Implemented SQLite persistence layer with JSON backup/restore (InventoryRepository)
[OK] Implemented unified business layer (InventoryService)
[OK] Implemented Command Line Interface (app.cli) via argparse
[OK] Implemented Graphical User Interface (app.gui) via Tkinter & ttk
[OK] Implemented foundational test suite (16 tests across models, catalog, repository, CLI, and GUI)
[OK] Verified test suite: 16 passed in 0.42s
```

---

## 2. Architecture & Decompilation Patterns

### A. Pokémon Emerald Pattern: Spatial Provenance & "Met Location"
In `pret/pokeemerald` (`include/pokemon.h`), entity data in storage boxes is divided into 12-byte substructures. Substructure 3 (`PokemonSubstruct3`) encapsulates encounter context and provenance:

```c
struct PokemonSubstruct3 {
    u8 pokerus;
    u8 metLocation;       // MAPSEC_* region map section ID
    u16 metLevel:7;       // Acquisition condition rating (0-100)
    u16 metGame:4;        // Origin version provenance (Ruby, Sapphire, Emerald, etc.)
    u16 pokeball:4;       // Containment apparatus
    u16 otGender:1;       // Trainer metadata
    ...
};
```
* **Python Adaptation**: Refactored into `SpatialCoordinates` (GPS coordinates, elevation, precision radius, and Haversine distance calculations) and `MetLocationMetadata` (binding coordinates, ISO-8601 UTC timestamp, map section tag, acquisition origin, custodian/trainer ID, and container specification).

### B. Pikmin 2 Pattern: Categorized Inventory Arrays & Physical Configs
In `projectPiki/pikmin2` (`plugProjectKandoU/pelletConfig.h`, `TreasureMgr.h`), carryable entities and treasures define strict physical transport and valuation metrics:

```c
struct PelletConfig {
    char*   mName;        // Identifier
    f32     mWeight;      // Minimum Pikmin carrier threshold (mass)
    f32     mMaxWeight;   // Maximum carrying capacity
    u32     mPoko;        // Appraised monetary value upon recovery
    u8      mCategory;    // Treasure series / Pellet color taxon
    f32     mRadius;      // Physical bounding volume
    u8      mDynamics;    // Physical transport dynamics
};
```
* **Python Adaptation**: Refactored into `PhysicalAttributes` (category series, mass in kg, appraised value in Pokos, 3D dimensions, volume, fragility rating) and `CategorizedInventoryArray` (in-memory indexed partitioned arrays by category, providing sub-millisecond filtering and Pikmin-style aggregate carrier weight / Poko valuation summaries).

---

## 3. Directory Structure

```
Antigravity/
├── .venv/                         # Project virtual environment
├── app/
│   ├── __init__.py                # Package root
│   ├── core/
│   │   ├── __init__.py
│   │   ├── models.py              # Modern Dataclasses (SpatialCoordinates, MetLocationMetadata, etc.)
│   │   ├── catalog.py             # CategorizedInventoryArray & Haversine spatial search
│   │   └── decompile_refs.py      # Preserved legacy C struct definitions and memory notes
│   ├── storage/
│   │   ├── __init__.py
│   │   └── repository.py          # SQLite persistence engine with JSON export/import
│   ├── services/
│   │   ├── __init__.py
│   │   └── inventory_service.py   # Unified service layer coordinating storage & catalog
│   ├── cli/
│   │   ├── __init__.py
│   │   └── __main__.py            # CLI entry point: python -m app.cli
│   └── gui/
│       ├── __init__.py
│       └── __main__.py            # GUI entry point: python -m app.gui
├── tests/
│   ├── __init__.py
│   ├── test_models.py             # Dataclass serialization & distance calculation tests
│   ├── test_catalog.py            # Pikmin array partitioning & spatial filter tests
│   ├── test_repository.py         # SQLite CRUD & JSON export/import tests
│   ├── test_cli.py                # Command-line interface argument dispatch tests
│   └── test_gui.py                # Tkinter visual dashboard tests
├── requirements.txt
├── README.md
└── CLASSMATE_EXPORT.md
```

---

## 4. Complete Project Source Code

### `requirements.txt`
```text
# Core application uses Python 3.10+ standard library:
# - dataclasses
# - sqlite3
# - tkinter / ttk
# - argparse
# - math, datetime, uuid, json

# Testing framework:
pytest>=8.0.0
```

---

### `app/core/decompile_refs.py`
```python
"""Legacy Game Decompilation Architectural References and Memory Patterns.

This module documents the exact C struct memory layouts and hardware-constrained
architectural patterns from classic decompilation projects that inspire this system:
1. Pokémon Emerald (pret/pokeemerald) - Spatial provenance and "Met Location" substructures.
2. Pikmin 2 (projectPiki/pikmin2) - Categorized inventory arrays and physical attribute configs.
"""

from dataclasses import dataclass
from typing import Final

# ==============================================================================
# REFERENCE 1: Pokémon Emerald (pret/pokeemerald) - Met Location Substructure
# Source: include/pokemon.h, include/constants/region_map_sections.h
# ==============================================================================
POKEMON_SUBSTRUCT3_C_REFERENCE: Final[str] = """
/* In Pokémon Emerald (Gen 3), BoxPokemon data is split into 4 12-byte substructures.
 * Substructure 3 handles provenance, origin game, and acquisition location:
 */
struct PokemonSubstruct3
{
    u8 pokerus;              // Strain and days remaining
    u8 metLocation;          // Map section ID (MAPSEC_*) where encounter occurred
    u16 metLevel:7;          // Level at encounter (0-100)
    u16 metGame:4;           // Source version: Ruby, Sapphire, Emerald, FRLG, Colosseum
    u16 pokeball:4;          // Apparatus used for capture
    u16 otGender:1;          // Original Trainer gender
    u32 hpIV:5;              // Individual values...
    u32 attackIV:5;
    u32 defenseIV:5;
    u32 speedIV:5;
    u32 spAttackIV:5;
    u32 spDefenseIV:5;
    u32 isEgg:1;             // Provenance flag
    u32 abilityNum:1;
    u32 ribbons;             // Historical achievement flags
};
"""

# ==============================================================================
# REFERENCE 2: Pikmin 2 (projectPiki/pikmin2) - Categorized Pellet & Treasure Config
# Source: plugProjectKandoU/pelletConfig.h, TreasureMgr.h
# ==============================================================================
PIKMIN_PELLET_CONFIG_C_REFERENCE: Final[str] = """
/* In Pikmin 2, carryable objects, pellets, and Otakara (treasures) are defined via
 * static configuration structs that specify physical weight (carrier Pikmin count),
 * monetary value (Pokos), and categorical grouping:
 */
struct PelletConfig
{
    char*   mName;           // Internal identifier / display name
    f32     mWeight;         // Minimum carrying threshold (mass units)
    f32     mMaxWeight;      // Maximum carrier capacity
    u32     mPoko;           // Appraised monetary value upon recovery
    u8      mCategory;       // Category ID: PelletColor / TreasureSeries
    f32     mRadius;         // Bounding collision / physical volume indicator
    u8      mDynamics;       // Physical behavior flags
};

/* The inventory memory layout in GameCube Pikmin 2 manages these items via
 * pre-indexed contiguous arrays (e.g. PelletConfigList, PelletMgr, TreasureMgr),
 * enabling cache-friendly categorization, weight validation, and aggregate value tallying.
 */
"""


@dataclass(frozen=True)
class ProvenanceOriginEnum:
    """Modern enumeration of encounter/provenance origins adapted from metGame."""
    FIELD_DISCOVERY: str = "FIELD_DISCOVERY"
    PROCURED: str = "PROCURED"
    MANUFACTURED: str = "MANUFACTURED"
    DONATED: str = "DONATED"
    SALVAGED: str = "SALVAGED"
    EXCAVATED: str = "EXCAVATED"


@dataclass(frozen=True)
class ItemCategoryEnum:
    """Standardized categories adapted from Pikmin 2 treasure series."""
    MECHANICAL: str = "MECHANICAL"
    ELECTRONIC: str = "ELECTRONIC"
    SPECIMEN: str = "SPECIMEN"
    RAW_MATERIAL: str = "RAW_MATERIAL"
    DOCUMENT: str = "DOCUMENT"
    ARTIFACT: str = "ARTIFACT"
    SURVIVAL_GEAR: str = "SURVIVAL_GEAR"
```

---

### `app/core/models.py`
```python
"""Modern Python Data Models for Location-Based Inventory System.

Refactors legacy Game Boy Advance (Pokémon Emerald) and GameCube (Pikmin 2)
C struct memory architectures into clean, type-safe Python dataclasses.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import datetime
import math
import uuid
from typing import Any, Dict, Optional, Tuple


@dataclass(frozen=True)
class SpatialCoordinates:
    """Represents real-world geographic coordinates with spatial calculation methods.

    Corresponds to the extended spatial metadata derived from Pokémon Emerald's
    mapGroup/mapNum/metLocation grid reference system.
    """
    latitude: float
    longitude: float
    altitude: float = 0.0
    accuracy_meters: float = 1.0

    def distance_to_km(self, other: SpatialCoordinates) -> float:
        """Computes Great-Circle (Haversine) distance between coordinates in kilometers."""
        earth_radius_km = 6371.0

        lat1 = math.radians(self.latitude)
        lon1 = math.radians(self.longitude)
        lat2 = math.radians(other.latitude)
        lon2 = math.radians(other.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (math.sin(dlat / 2.0) ** 2 +
             math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2.0) ** 2)
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return earth_radius_km * c

    def within_radius_km(self, other: SpatialCoordinates, radius_km: float) -> bool:
        """Determines if this coordinate falls within a specified radius of another."""
        return self.distance_to_km(other) <= radius_km

    def to_dict(self) -> Dict[str, Any]:
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "accuracy_meters": self.accuracy_meters,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SpatialCoordinates:
        return cls(
            latitude=float(data["latitude"]),
            longitude=float(data["longitude"]),
            altitude=float(data.get("altitude", 0.0)),
            accuracy_meters=float(data.get("accuracy_meters", 1.0)),
        )


@dataclass
class MetLocationMetadata:
    """Binds spatial coordinates, timestamp, and origin metadata to an item ID.

    Directly adapts the Pokémon Emerald `PokemonSubstruct3` pattern:
    - coordinates + met_location_tag  <->  metLocation (MAPSEC_*) & map coordinates
    - met_timestamp                   <->  RTC encounter timestamp
    - origin_source                   <->  metGame / encounter origin
    - custodian_id                    <->  otId (Original Trainer ID)
    - containment_type                <->  pokeball identifier
    - condition_level                 <->  metLevel (initial acquisition condition)
    """
    coordinates: SpatialCoordinates
    met_location_tag: str
    met_timestamp: str = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    origin_source: str = "FIELD_DISCOVERY"
    custodian_id: str = "SYS_OPERATOR"
    containment_type: str = "STANDARD_CONTAINER"
    condition_level: int = 100  # 1-100 condition metric

    def to_dict(self) -> Dict[str, Any]:
        return {
            "coordinates": self.coordinates.to_dict(),
            "met_location_tag": self.met_location_tag,
            "met_timestamp": self.met_timestamp,
            "origin_source": self.origin_source,
            "custodian_id": self.custodian_id,
            "containment_type": self.containment_type,
            "condition_level": self.condition_level,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MetLocationMetadata:
        return cls(
            coordinates=SpatialCoordinates.from_dict(data["coordinates"]),
            met_location_tag=str(data["met_location_tag"]),
            met_timestamp=str(data.get("met_timestamp", datetime.datetime.now(datetime.timezone.utc).isoformat())),
            origin_source=str(data.get("origin_source", "FIELD_DISCOVERY")),
            custodian_id=str(data.get("custodian_id", "SYS_OPERATOR")),
            containment_type=str(data.get("containment_type", "STANDARD_CONTAINER")),
            condition_level=int(data.get("condition_level", 100)),
        )


@dataclass
class PhysicalAttributes:
    """Encapsulates physical attributes indexed for categorized inventory arrays.

    Directly adapts the Pikmin 2 `PelletConfig` / `TreasureMgr` pattern:
    - category    <->  mCategory (Pellet color / Treasure series)
    - weight      <->  mWeight (Carrying threshold / mass units)
    - value       <->  mPoko (Monetary appraisal value)
    - dimensions  <->  mRadius / bounding volume
    - fragility   <->  Physical transport dynamics
    """
    category: str
    weight: float             # in kilograms
    value: float              # in currency units / Pokos
    dimensions_cm: Tuple[float, float, float] = (10.0, 10.0, 10.0)  # (Length, Width, Height)
    fragility: int = 1        # 1 (Durable) to 5 (Extremely Fragile)

    @property
    def volume_cm3(self) -> float:
        """Calculates approximate cubic volume."""
        return self.dimensions_cm[0] * self.dimensions_cm[1] * self.dimensions_cm[2]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "weight": self.weight,
            "value": self.value,
            "dimensions_cm": list(self.dimensions_cm),
            "fragility": self.fragility,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PhysicalAttributes:
        dims = data.get("dimensions_cm", [10.0, 10.0, 10.0])
        return cls(
            category=str(data["category"]),
            weight=float(data["weight"]),
            value=float(data["value"]),
            dimensions_cm=(float(dims[0]), float(dims[1]), float(dims[2])),
            fragility=int(data.get("fragility", 1)),
        )


@dataclass
class InventoryItem:
    """Core domain entity combining Pokémon Emerald spatial provenance with Pikmin 2 physical attributes."""
    name: str
    spatial_meta: MetLocationMetadata
    physical_attrs: PhysicalAttributes
    item_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_id": self.item_id,
            "name": self.name,
            "spatial_meta": self.spatial_meta.to_dict(),
            "physical_attrs": self.physical_attrs.to_dict(),
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> InventoryItem:
        return cls(
            item_id=str(data.get("item_id", uuid.uuid4())),
            name=str(data["name"]),
            spatial_meta=MetLocationMetadata.from_dict(data["spatial_meta"]),
            physical_attrs=PhysicalAttributes.from_dict(data["physical_attrs"]),
            notes=str(data.get("notes", "")),
        )
```

---

### `app/core/catalog.py`
```python
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
```

---

### `app/storage/repository.py`
```python
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
```

---

### `app/services/inventory_service.py`
```python
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
```

---

### `app/cli/__main__.py`
```python
"""Command Line Interface (CLI) Entry Point for Location-Based Inventory System.

Launchable via:
    python -m app.cli [command] [options]
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from app.services.inventory_service import InventoryService


def format_table(headers: List[str], rows: List[List[str]]) -> str:
    """Formats rows into an aligned terminal table."""
    if not rows:
        return "No records found."
    widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            widths[idx] = max(widths[idx], len(str(val)))

    header_line = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    sep_line = "-+-".join("-" * widths[i] for i in range(len(headers)))
    row_lines = [
        " | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))
        for row in rows
    ]
    return f"{header_line}\n{sep_line}\n" + "\n".join(row_lines)


def handle_add(service: InventoryService, args: argparse.Namespace) -> int:
    item = service.register_item(
        name=args.name,
        category=args.category,
        weight=args.weight,
        value=args.value,
        latitude=args.lat,
        longitude=args.lon,
        met_location_tag=args.met_tag,
        origin_source=args.origin,
        custodian_id=args.custodian,
        containment_type=args.containment,
        notes=args.notes or "",
    )
    print(f"\n[OK] Item successfully registered into categorized inventory!")
    print(f"  Item ID     : {item.item_id}")
    print(f"  Name        : {item.name}")
    print(f"  Category    : {item.physical_attrs.category}")
    print(f"  Weight/Value: {item.physical_attrs.weight} kg | {item.physical_attrs.value} Pokos")
    print(f"  Met Location: {item.spatial_meta.met_location_tag} ({item.spatial_meta.coordinates.latitude:.4f}, {item.spatial_meta.coordinates.longitude:.4f})")
    print(f"  Encounter   : {item.spatial_meta.origin_source} by {item.spatial_meta.custodian_id}\n")
    return 0


def handle_list(service: InventoryService, args: argparse.Namespace) -> int:
    items = service.list_items(
        category=args.category,
        min_weight=args.min_weight,
        max_weight=args.max_weight,
        min_value=args.min_value,
        max_value=args.max_value,
        met_location_tag=args.met_tag,
        search_query=args.query,
    )
    headers = ["ID (Short)", "Name", "Category", "Weight (kg)", "Value (Pokos)", "Met Location", "Coords (Lat, Lon)"]
    rows = []
    for item in items:
        short_id = item.item_id[:8]
        coords = f"{item.spatial_meta.coordinates.latitude:.3f}, {item.spatial_meta.coordinates.longitude:.3f}"
        rows.append([
            short_id,
            item.name,
            item.physical_attrs.category,
            f"{item.physical_attrs.weight:.2f}",
            f"{item.physical_attrs.value:.2f}",
            item.spatial_meta.met_location_tag,
            coords,
        ])
    print(f"\n--- INVENTORY LIST ({len(items)} items) ---")
    print(format_table(headers, rows))
    print()
    return 0


def handle_search_spatial(service: InventoryService, args: argparse.Namespace) -> int:
    results = service.search_nearby(
        center_lat=args.lat,
        center_lon=args.lon,
        radius_km=args.radius_km,
        category=args.category,
    )
    headers = ["Distance (km)", "ID (Short)", "Name", "Category", "Met Tag", "Coords (Lat, Lon)"]
    rows = []
    for item, dist in results:
        coords = f"{item.spatial_meta.coordinates.latitude:.3f}, {item.spatial_meta.coordinates.longitude:.3f}"
        rows.append([
            f"{dist:.2f} km",
            item.item_id[:8],
            item.name,
            item.physical_attrs.category,
            item.spatial_meta.met_location_tag,
            coords,
        ])
    print(f"\n--- SPATIAL SEARCH RESULTS (Center: {args.lat:.4f}, {args.lon:.4f} | Radius: {args.radius_km} km) ---")
    print(format_table(headers, rows))
    print()
    return 0


def handle_inspect(service: InventoryService, args: argparse.Namespace) -> int:
    all_items = service.list_items()
    matched = [i for i in all_items if i.item_id.startswith(args.item_id)]
    if not matched:
        print(f"[ERROR] Item '{args.item_id}' not found.")
        return 1
    item = matched[0]

    print("\n" + "=" * 65)
    print(f" ITEM INSPECTION: {item.name} [{item.item_id}]")
    print("=" * 65)
    print(" [POKÉMON EMERALD PATTERN: Spatial & Origin Substructure]")
    print(f"   Met Location Tag : {item.spatial_meta.met_location_tag}")
    print(f"   Coordinates      : Lat {item.spatial_meta.coordinates.latitude:.6f}, Lon {item.spatial_meta.coordinates.longitude:.6f}, Alt {item.spatial_meta.coordinates.altitude}m")
    print(f"   Met Timestamp    : {item.spatial_meta.met_timestamp}")
    print(f"   Origin Source    : {item.spatial_meta.origin_source}")
    print(f"   Original Trainer : {item.spatial_meta.custodian_id}")
    print(f"   Containment Unit : {item.spatial_meta.containment_type}")
    print(f"   Condition Level  : {item.spatial_meta.condition_level}/100")
    print("-" * 65)
    print(" [PIKMIN 2 PATTERN: Physical Attributes & PelletConfig]")
    print(f"   Category / Series: {item.physical_attrs.category}")
    print(f"   Physical Mass    : {item.physical_attrs.weight} kg")
    print(f"   Appraisal Value  : {item.physical_attrs.value} Pokos")
    print(f"   Dimensions (cm)  : {item.physical_attrs.dimensions_cm[0]} x {item.physical_attrs.dimensions_cm[1]} x {item.physical_attrs.dimensions_cm[2]} cm")
    print(f"   Volume           : {item.physical_attrs.volume_cm3:.1f} cm³")
    print(f"   Fragility Tier   : {item.physical_attrs.fragility} / 5")
    print("-" * 65)
    print(f" Notes: {item.notes or 'None'}")
    print("=" * 65 + "\n")
    return 0


def handle_summary(service: InventoryService, args: argparse.Namespace) -> int:
    summary = service.get_summary()
    print("\n" + "=" * 50)
    print(" PIKMIN 2 AGGREGATE CATALOG SUMMARY")
    print("=" * 50)
    print(f" Total Registered Items   : {summary['total_items']}")
    print(f" Total Carrier Weight Load: {summary['total_weight_kg']} kg")
    print(f" Total Appraised Pokos    : {summary['total_value_pokos']} Pokos")
    print("-" * 50)
    print(" Categorized Array Partitions:")
    for cat, data in summary["categories"].items():
        print(f"   * {cat.ljust(15)}: {str(data['count']).rjust(3)} items | {str(data['weight_kg']).rjust(7)} kg | {str(data['value_pokos']).rjust(8)} Pokos")
    print("=" * 50 + "\n")
    return 0


def handle_delete(service: InventoryService, args: argparse.Namespace) -> int:
    all_items = service.list_items()
    matched = [i for i in all_items if i.item_id.startswith(args.item_id)]
    if not matched:
        print(f"[ERROR] Item '{args.item_id}' not found.")
        return 1
    target = matched[0]
    success = service.delete_item(target.item_id)
    if success:
        print(f"[OK] Item '{target.name}' ({target.item_id}) removed successfully.")
        return 0
    print(f"[ERROR] Failed to remove item '{target.item_id}'.")
    return 1


def handle_export(service: InventoryService, args: argparse.Namespace) -> int:
    service.export_data(args.output)
    print(f"[OK] Inventory exported to {args.output}")
    return 0


def handle_import(service: InventoryService, args: argparse.Namespace) -> int:
    count = service.import_data(args.input)
    print(f"[OK] Successfully imported {count} items from {args.input}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m app.cli",
        description="Location-Based Inventory System (GBA/GCN Legacy Decomp Architecture)",
    )
    parser.add_argument(
        "--db",
        default="inventory.db",
        help="Path to SQLite database file (default: inventory.db)",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: add
    p_add = subparsers.add_parser("add", help="Register a new inventory item")
    p_add.add_argument("--name", required=True, help="Display name of item")
    p_add.add_argument("--category", required=True, help="Pikmin treasure series / category (e.g. MECHANICAL, ELECTRONIC, ARTIFACT)")
    p_add.add_argument("--weight", type=float, required=True, help="Physical mass in kg")
    p_add.add_argument("--value", type=float, required=True, help="Monetary appraisal in Pokos")
    p_add.add_argument("--lat", type=float, required=True, help="Latitude coordinate")
    p_add.add_argument("--lon", type=float, required=True, help="Longitude coordinate")
    p_add.add_argument("--met-tag", required=True, help="Met location tag (MAPSEC_*)")
    p_add.add_argument("--origin", default="FIELD_DISCOVERY", help="Acquisition origin (default: FIELD_DISCOVERY)")
    p_add.add_argument("--custodian", default="OPERATOR_01", help="Handler ID / Trainer ID")
    p_add.add_argument("--containment", default="STANDARD_CONTAINER", help="Packaging / Pokéball equivalent")
    p_add.add_argument("--notes", default="", help="Optional notes")

    # Command: list
    p_list = subparsers.add_parser("list", help="List and filter inventory items")
    p_list.add_argument("--category", default=None, help="Filter by category")
    p_list.add_argument("--min-weight", type=float, default=None, help="Minimum weight (kg)")
    p_list.add_argument("--max-weight", type=float, default=None, help="Maximum weight (kg)")
    p_list.add_argument("--min-value", type=float, default=None, help="Minimum Pokos value")
    p_list.add_argument("--max-value", type=float, default=None, help="Maximum Pokos value")
    p_list.add_argument("--met-tag", default=None, help="Filter by met location tag substring")
    p_list.add_argument("--query", default=None, help="Search name or notes")

    # Command: search-spatial
    p_geo = subparsers.add_parser("search-spatial", help="Search items within radius of coordinates")
    p_geo.add_argument("--lat", type=float, required=True, help="Origin latitude")
    p_geo.add_argument("--lon", type=float, required=True, help="Origin longitude")
    p_geo.add_argument("--radius-km", type=float, default=50.0, help="Search radius in kilometers (default: 50.0)")
    p_geo.add_argument("--category", default=None, help="Optional category filter")

    # Command: inspect
    p_insp = subparsers.add_parser("inspect", help="Inspect legacy memory struct decomposition of an item")
    p_insp.add_argument("item_id", help="Item ID (or prefix)")

    # Command: summary
    subparsers.add_parser("summary", help="Show Pikmin aggregate carrying weight and Poko value stats")

    # Command: delete
    p_del = subparsers.add_parser("delete", help="Delete an item by ID")
    p_del.add_argument("item_id", help="Item ID (or prefix)")

    # Command: export-json
    p_exp = subparsers.add_parser("export-json", help="Export inventory to JSON file")
    p_exp.add_argument("--output", required=True, help="Output JSON file path")

    # Command: import-json
    p_imp = subparsers.add_parser("import-json", help="Import inventory from JSON file")
    p_imp.add_argument("--input", required=True, help="Input JSON file path")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if not args.command:
        parser.print_help()
        return 0

    service = InventoryService(db_path=args.db)

    handlers = {
        "add": handle_add,
        "list": handle_list,
        "search-spatial": handle_search_spatial,
        "inspect": handle_inspect,
        "summary": handle_summary,
        "delete": handle_delete,
        "export-json": handle_export,
        "import-json": handle_import,
    }

    handler = handlers.get(args.command)
    if handler:
        return handler(service, args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
```

---

### `app/gui/__main__.py`
```python
"""Graphical User Interface (GUI) Entry Point for Location-Based Inventory System.

Built with Tkinter / ttk, providing a visual dashboard to log new items,
view spatial coordinate data, and filter categorized inventory arrays.

Launchable via:
    python -m app.gui
"""

from __future__ import annotations

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List, Optional

from app.core.decompile_refs import ItemCategoryEnum, ProvenanceOriginEnum
from app.core.models import InventoryItem
from app.services.inventory_service import InventoryService


class InventoryAppGUI(tk.Tk):
    """Tkinter-based visual dashboard for location-based inventory management."""

    def __init__(self, db_path: str = "inventory.db") -> None:
        super().__init__()
        self.title("Location Inventory System - Decomp Deployed Engine")
        self.geometry("1180x720")
        self.minsize(980, 600)

        # Connect shared business service
        self.service = InventoryService(db_path=db_path)

        self._configure_styles()
        self._build_ui()
        self.refresh_table()
        self.update_summary_cards()

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Treeview.Heading", font=("Helvetica", 9, "bold"))
        style.configure("Treeview", rowheight=24, font=("Helvetica", 9))
        style.configure("Header.TLabel", font=("Helvetica", 14, "bold"))
        style.configure("Subheader.TLabel", font=("Helvetica", 10, "bold"))
        style.configure("CardVal.TLabel", font=("Helvetica", 12, "bold"), foreground="#0052cc")
        style.configure("CardLbl.TLabel", font=("Helvetica", 8))

    def _build_ui(self) -> None:
        # Top Header & Stats Card Banner
        header_frame = ttk.Frame(self, padding=(12, 8))
        header_frame.pack(fill=tk.X, side=tk.TOP)

        title_box = ttk.Frame(header_frame)
        title_box.pack(side=tk.LEFT)
        ttk.Label(
            title_box,
            text="Real-World Spatial Inventory Engine",
            style="Header.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            title_box,
            text="Pokémon Emerald Met-Location Logic x Pikmin 2 Categorized Arrays",
            foreground="#555555",
        ).pack(anchor="w")

        # Stats Cards on Top Right
        stats_frame = ttk.Frame(header_frame)
        stats_frame.pack(side=tk.RIGHT)

        self.card_total_items = self._create_stat_card(stats_frame, "Total Items", "0")
        self.card_total_weight = self._create_stat_card(stats_frame, "Carrier Load (kg)", "0.0")
        self.card_total_pokos = self._create_stat_card(stats_frame, "Appraised Value (Pokos)", "0.0")

        # Main Paned Area (Left: Logging Form, Right: Inventory Dashboard & Filtering)
        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        left_form_frame = ttk.LabelFrame(main_paned, text=" Log New Item (Origin & Physical Specs) ", padding=10)
        main_paned.add(left_form_frame, weight=1)

        right_list_frame = ttk.LabelFrame(main_paned, text=" Inventory Array & Spatial Search ", padding=10)
        main_paned.add(right_list_frame, weight=3)

        self._build_logging_form(left_form_frame)
        self._build_dashboard_view(right_list_frame)

    def _create_stat_card(self, parent: ttk.Frame, label_text: str, default_val: str) -> ttk.Label:
        card = ttk.Frame(parent, relief=tk.RIDGE, padding=(10, 4))
        card.pack(side=tk.LEFT, padx=6)
        val_lbl = ttk.Label(card, text=default_val, style="CardVal.TLabel")
        val_lbl.pack(anchor="center")
        ttk.Label(card, text=label_text, style="CardLbl.TLabel").pack(anchor="center")
        return val_lbl

    def _build_logging_form(self, parent: ttk.Frame) -> None:
        """Constructs form to input items with Pokemon spatial provenance and Pikmin physical attributes."""
        canvas = tk.Canvas(parent, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        form = ttk.Frame(canvas)

        form.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=form, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        row = 0
        ttk.Label(form, text="Item Name:", font=("Helvetica", 9, "bold")).grid(row=row, column=0, sticky="w", pady=2)
        self.entry_name = ttk.Entry(form, width=28)
        self.entry_name.grid(row=row+1, column=0, columnspan=2, sticky="ew", pady=(0, 6))

        row += 2
        ttk.Label(form, text="Category (Pikmin Series):").grid(row=row, column=0, sticky="w", pady=2)
        categories = [
            ItemCategoryEnum.MECHANICAL,
            ItemCategoryEnum.ELECTRONIC,
            ItemCategoryEnum.SPECIMEN,
            ItemCategoryEnum.RAW_MATERIAL,
            ItemCategoryEnum.DOCUMENT,
            ItemCategoryEnum.ARTIFACT,
            ItemCategoryEnum.SURVIVAL_GEAR,
        ]
        self.combo_category = ttk.Combobox(form, values=categories, state="readonly", width=25)
        self.combo_category.set(categories[0])
        self.combo_category.grid(row=row+1, column=0, columnspan=2, sticky="ew", pady=(0, 6))

        row += 2
        ttk.Label(form, text="Mass Weight (kg):").grid(row=row, column=0, sticky="w")
        ttk.Label(form, text="Value (Pokos):").grid(row=row, column=1, sticky="w")
        self.entry_weight = ttk.Entry(form, width=12)
        self.entry_weight.insert(0, "1.5")
        self.entry_weight.grid(row=row+1, column=0, sticky="ew", padx=(0, 4), pady=(0, 6))
        self.entry_value = ttk.Entry(form, width=12)
        self.entry_value.insert(0, "120.0")
        self.entry_value.grid(row=row+1, column=1, sticky="ew", pady=(0, 6))

        row += 2
        ttk.Label(form, text="Met Location Tag (MAPSEC):").grid(row=row, column=0, sticky="w", pady=2)
        self.entry_met_tag = ttk.Entry(form, width=28)
        self.entry_met_tag.insert(0, "MAPSEC_WAREHOUSE_SECTOR_7")
        self.entry_met_tag.grid(row=row+1, column=0, columnspan=2, sticky="ew", pady=(0, 6))

        row += 2
        ttk.Label(form, text="Latitude:").grid(row=row, column=0, sticky="w")
        ttk.Label(form, text="Longitude:").grid(row=row, column=1, sticky="w")
        self.entry_lat = ttk.Entry(form, width=12)
        self.entry_lat.insert(0, "37.7749")
        self.entry_lat.grid(row=row+1, column=0, sticky="ew", padx=(0, 4), pady=(0, 6))
        self.entry_lon = ttk.Entry(form, width=12)
        self.entry_lon.insert(0, "-122.4194")
        self.entry_lon.grid(row=row+1, column=1, sticky="ew", pady=(0, 6))

        row += 2
        ttk.Label(form, text="Origin Source:").grid(row=row, column=0, sticky="w", pady=2)
        origins = [
            ProvenanceOriginEnum.FIELD_DISCOVERY,
            ProvenanceOriginEnum.PROCURED,
            ProvenanceOriginEnum.MANUFACTURED,
            ProvenanceOriginEnum.DONATED,
            ProvenanceOriginEnum.SALVAGED,
            ProvenanceOriginEnum.EXCAVATED,
        ]
        self.combo_origin = ttk.Combobox(form, values=origins, state="readonly", width=25)
        self.combo_origin.set(origins[0])
        self.combo_origin.grid(row=row+1, column=0, columnspan=2, sticky="ew", pady=(0, 6))

        row += 2
        ttk.Label(form, text="Custodian ID:").grid(row=row, column=0, sticky="w")
        ttk.Label(form, text="Containment:").grid(row=row, column=1, sticky="w")
        self.entry_custodian = ttk.Entry(form, width=12)
        self.entry_custodian.insert(0, "TRAINER_01")
        self.entry_custodian.grid(row=row+1, column=0, sticky="ew", padx=(0, 4), pady=(0, 6))
        self.entry_containment = ttk.Entry(form, width=12)
        self.entry_containment.insert(0, "PELLET_HULL")
        self.entry_containment.grid(row=row+1, column=1, sticky="ew", pady=(0, 6))

        row += 2
        ttk.Label(form, text="Item Notes:").grid(row=row, column=0, sticky="w", pady=2)
        self.entry_notes = ttk.Entry(form, width=28)
        self.entry_notes.grid(row=row+1, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        row += 2
        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=6)

        ttk.Button(btn_frame, text="Log Item", command=self._on_register_click).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="Sample Seed Data", command=self._seed_sample_data).pack(fill=tk.X, pady=2)

    def _build_dashboard_view(self, parent: ttk.Frame) -> None:
        """Constructs filter bar and Treeview table."""
        filter_box = ttk.Frame(parent)
        filter_box.pack(fill=tk.X, pady=(0, 8))

        # Filter Row 1: Category, Min/Max Weight, Search query
        r1 = ttk.Frame(filter_box)
        r1.pack(fill=tk.X, pady=2)

        ttk.Label(r1, text="Category:").pack(side=tk.LEFT, padx=(0, 2))
        self.filter_category = ttk.Combobox(r1, values=["ALL"], state="readonly", width=14)
        self.filter_category.set("ALL")
        self.filter_category.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Label(r1, text="Min Wt:").pack(side=tk.LEFT, padx=(0, 2))
        self.filter_min_weight = ttk.Entry(r1, width=5)
        self.filter_min_weight.pack(side=tk.LEFT, padx=(0, 4))

        ttk.Label(r1, text="Max Wt:").pack(side=tk.LEFT, padx=(0, 2))
        self.filter_max_weight = ttk.Entry(r1, width=5)
        self.filter_max_weight.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Label(r1, text="Search:").pack(side=tk.LEFT, padx=(0, 2))
        self.filter_query = ttk.Entry(r1, width=12)
        self.filter_query.pack(side=tk.LEFT, padx=(0, 8))

        # Filter Row 2: Spatial Radial Filter
        r2 = ttk.Frame(filter_box)
        r2.pack(fill=tk.X, pady=4)

        ttk.Label(r2, text="Spatial Filter:").pack(side=tk.LEFT, padx=(0, 4))
        ttk.Label(r2, text="Lat:").pack(side=tk.LEFT)
        self.filter_lat = ttk.Entry(r2, width=8)
        self.filter_lat.pack(side=tk.LEFT, padx=(0, 4))

        ttk.Label(r2, text="Lon:").pack(side=tk.LEFT)
        self.filter_lon = ttk.Entry(r2, width=8)
        self.filter_lon.pack(side=tk.LEFT, padx=(0, 4))

        ttk.Label(r2, text="Radius (km):").pack(side=tk.LEFT)
        self.filter_radius = ttk.Entry(r2, width=5)
        self.filter_radius.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(r2, text="Apply Filter", command=self.apply_filter).pack(side=tk.LEFT, padx=2)
        ttk.Button(r2, text="Reset", command=self.reset_filters).pack(side=tk.LEFT, padx=2)

        # Inventory Table / Treeview
        columns = ("name", "category", "weight", "value", "met_tag", "coords", "origin", "id")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("name", text="Item Name")
        self.tree.heading("category", text="Category")
        self.tree.heading("weight", text="Weight (kg)")
        self.tree.heading("value", text="Value (Pokos)")
        self.tree.heading("met_tag", text="Met Location Tag")
        self.tree.heading("coords", text="Coordinates")
        self.tree.heading("origin", text="Origin")
        self.tree.heading("id", text="Item ID (Short)")

        self.tree.column("name", width=130, anchor="w")
        self.tree.column("category", width=100, anchor="center")
        self.tree.column("weight", width=80, anchor="e")
        self.tree.column("value", width=90, anchor="e")
        self.tree.column("met_tag", width=140, anchor="w")
        self.tree.column("coords", width=120, anchor="center")
        self.tree.column("origin", width=110, anchor="center")
        self.tree.column("id", width=80, anchor="center")

        tree_scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", lambda e: self.inspect_selected())

        # Bottom Action Bar
        actions_bar = ttk.Frame(parent, padding=(0, 6))
        actions_bar.pack(side=tk.BOTTOM, fill=tk.X)

        ttk.Button(actions_bar, text="Inspect Memory Struct", command=self.inspect_selected).pack(side=tk.LEFT, padx=4)
        ttk.Button(actions_bar, text="Delete Item", command=self.delete_selected).pack(side=tk.LEFT, padx=4)
        ttk.Button(actions_bar, text="Refresh", command=self.refresh_table).pack(side=tk.LEFT, padx=4)

        ttk.Button(actions_bar, text="Export JSON", command=self.export_json).pack(side=tk.RIGHT, padx=4)
        ttk.Button(actions_bar, text="Import JSON", command=self.import_json).pack(side=tk.RIGHT, padx=4)

    def _on_register_click(self) -> None:
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showwarning("Validation Error", "Item name is required.")
            return

        try:
            weight = float(self.entry_weight.get().strip())
            value = float(self.entry_value.get().strip())
            lat = float(self.entry_lat.get().strip())
            lon = float(self.entry_lon.get().strip())
        except ValueError:
            messagebox.showerror("Validation Error", "Weight, Value, Latitude, and Longitude must be valid numbers.")
            return

        met_tag = self.entry_met_tag.get().strip()
        category = self.combo_category.get()
        origin = self.combo_origin.get()
        custodian = self.entry_custodian.get().strip()
        containment = self.entry_containment.get().strip()
        notes = self.entry_notes.get().strip()

        item = self.service.register_item(
            name=name,
            category=category,
            weight=weight,
            value=value,
            latitude=lat,
            longitude=lon,
            met_location_tag=met_tag,
            origin_source=origin,
            custodian_id=custodian,
            containment_type=containment,
            notes=notes,
        )

        messagebox.showinfo("Success", f"Item '{item.name}' logged successfully!\nID: {item.item_id[:8]}")
        self.entry_name.delete(0, tk.END)
        self.refresh_table()
        self.update_summary_cards()

    def refresh_table(self, items_to_show: Optional[List[InventoryItem]] = None) -> None:
        """Populates Treeview with current inventory."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        items = items_to_show if items_to_show is not None else self.service.list_items()
        for item in items:
            coords = f"{item.spatial_meta.coordinates.latitude:.3f}, {item.spatial_meta.coordinates.longitude:.3f}"
            self.tree.insert(
                "",
                tk.END,
                iid=item.item_id,
                values=(
                    item.name,
                    item.physical_attrs.category,
                    f"{item.physical_attrs.weight:.2f}",
                    f"{item.physical_attrs.value:.2f}",
                    item.spatial_meta.met_location_tag,
                    coords,
                    item.spatial_meta.origin_source,
                    item.item_id[:8],
                ),
            )

        current_cats = ["ALL"] + self.service.get_categories()
        self.filter_category["values"] = current_cats

    def update_summary_cards(self) -> None:
        summary = self.service.get_summary()
        self.card_total_items.config(text=str(summary["total_items"]))
        self.card_total_weight.config(text=f"{summary['total_weight_kg']} kg")
        self.card_total_pokos.config(text=f"{summary['total_value_pokos']} P")

    def apply_filter(self) -> None:
        lat_txt = self.filter_lat.get().strip()
        lon_txt = self.filter_lon.get().strip()
        rad_txt = self.filter_radius.get().strip()

        if lat_txt and lon_txt and rad_txt:
            try:
                lat = float(lat_txt)
                lon = float(lon_txt)
                radius = float(rad_txt)
                cat = self.filter_category.get()
                spatial_results = self.service.search_nearby(
                    center_lat=lat,
                    center_lon=lon,
                    radius_km=radius,
                    category=cat if cat != "ALL" else None,
                )
                filtered_items = [item for item, _ in spatial_results]
                self.refresh_table(filtered_items)
                return
            except ValueError:
                messagebox.showerror("Filter Error", "Latitude, Longitude, and Radius must be valid numeric values.")
                return

        cat = self.filter_category.get()
        min_w = float(self.filter_min_weight.get()) if self.filter_min_weight.get().strip() else None
        max_w = float(self.filter_max_weight.get()) if self.filter_max_weight.get().strip() else None
        q = self.filter_query.get().strip() or None

        results = self.service.list_items(
            category=cat if cat != "ALL" else None,
            min_weight=min_w,
            max_weight=max_w,
            search_query=q,
        )
        self.refresh_table(results)

    def reset_filters(self) -> None:
        self.filter_category.set("ALL")
        self.filter_min_weight.delete(0, tk.END)
        self.filter_max_weight.delete(0, tk.END)
        self.filter_query.delete(0, tk.END)
        self.filter_lat.delete(0, tk.END)
        self.filter_lon.delete(0, tk.END)
        self.filter_radius.delete(0, tk.END)
        self.refresh_table()

    def delete_selected(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select an item to delete.")
            return

        item_id = selected[0]
        item = self.service.get_item(item_id)
        name = item.name if item else item_id

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{name}'?"):
            self.service.delete_item(item_id)
            self.refresh_table()
            self.update_summary_cards()

    def inspect_selected(self) -> None:
        """Opens a detailed modal showing the legacy decompilation memory architecture."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select an item to inspect.")
            return

        item_id = selected[0]
        item = self.service.get_item(item_id)
        if not item:
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"Legacy Memory Struct Inspection: {item.name}")
        dialog.geometry("640x520")

        txt = tk.Text(dialog, wrap=tk.WORD, font=("Courier New", 10), padx=10, pady=10)
        txt.pack(fill=tk.BOTH, expand=True)

        content = f"""======================================================================
 ITEM IDENTITY
======================================================================
 UUID / Primary Key : {item.item_id}
 Name               : {item.name}
 User Notes         : {item.notes or '(None)'}

======================================================================
 POKÉMON EMERALD PATTERN (PokemonSubstruct3 Met Location Provenance)
======================================================================
 Met Location Tag   : {item.spatial_meta.met_location_tag} (MAPSEC reference)
 Latitude           : {item.spatial_meta.coordinates.latitude:.6f}°
 Longitude          : {item.spatial_meta.coordinates.longitude:.6f}°
 Altitude / Elevation: {item.spatial_meta.coordinates.altitude:.1f} m
 Precision Radius   : {item.spatial_meta.coordinates.accuracy_meters:.1f} m
 Encounter Timestamp: {item.spatial_meta.met_timestamp}
 Origin Game/Source : {item.spatial_meta.origin_source}
 Original Trainer   : {item.spatial_meta.custodian_id}
 Containment Hull   : {item.spatial_meta.containment_type}
 Condition Rating   : {item.spatial_meta.condition_level} / 100

======================================================================
 PIKMIN 2 PATTERN (PelletConfig & Categorized Array Indexing)
======================================================================
 Categorical Series : {item.physical_attrs.category}
 Carrier Mass Weight: {item.physical_attrs.weight} kg (Carrier threshold)
 Appraised Valuation: {item.physical_attrs.value} Pokos
 Physical Dimensions: {item.physical_attrs.dimensions_cm[0]} x {item.physical_attrs.dimensions_cm[1]} x {item.physical_attrs.dimensions_cm[2]} cm
 Computed Volume    : {item.physical_attrs.volume_cm3:.1f} cm³
 Fragility Index    : {item.physical_attrs.fragility} / 5
======================================================================
"""
        txt.insert(tk.END, content)
        txt.configure(state=tk.DISABLED)

    def _seed_sample_data(self) -> None:
        """Seeds demo data illustrating spatial and physical attributes."""
        samples = [
            ("Titanium Turbine Blade", "MECHANICAL", 14.5, 450.0, 37.7749, -122.4194, "MAPSEC_HANGAR_9", "SALVAGED"),
            ("Quantum Gyro Sensor", "ELECTRONIC", 0.4, 820.0, 37.7833, -122.4167, "MAPSEC_LAB_NORTH", "FIELD_DISCOVERY"),
            ("Cryo Crystal Specimen", "SPECIMEN", 2.1, 1200.0, 37.7651, -122.4220, "MAPSEC_VAULT_DEEP", "EXCAVATED"),
            ("Navigational Slate", "ARTIFACT", 5.0, 310.0, 37.8000, -122.4000, "MAPSEC_PIER_BAY", "FIELD_DISCOVERY"),
            ("Emergency Rations Pack", "SURVIVAL_GEAR", 3.2, 85.0, 37.7890, -122.4080, "MAPSEC_BUNKER_3", "PROCURED"),
        ]
        for name, cat, wt, val, lat, lon, tag, orig in samples:
            self.service.register_item(
                name=name,
                category=cat,
                weight=wt,
                value=val,
                latitude=lat,
                longitude=lon,
                met_location_tag=tag,
                origin_source=orig,
                custodian_id="OPERATOR_DEMO",
                notes="Seed demonstration record",
            )
        self.refresh_table()
        self.update_summary_cards()
        messagebox.showinfo("Seeded", "Sample items added successfully across multiple categories and coordinates!")

    def export_json(self) -> None:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Export Inventory as JSON",
        )
        if file_path:
            self.service.export_data(file_path)
            messagebox.showinfo("Exported", f"Successfully saved to {file_path}")

    def import_json(self) -> None:
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            title="Import Inventory from JSON",
        )
        if file_path:
            count = self.service.import_data(file_path)
            self.refresh_table()
            self.update_summary_cards()
            messagebox.showinfo("Imported", f"Successfully imported {count} items!")


def main() -> None:
    db_path = os.environ.get("INVENTORY_DB", "inventory.db")
    app = InventoryAppGUI(db_path=db_path)
    app.mainloop()


if __name__ == "__main__":
    main()
```

---

### `tests/test_models.py`
```python
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
```

---

### `tests/test_catalog.py`
```python
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
        make_item("Gear Assembly", "MECHANICAL", 10.0, 100.0, 37.7749, -122.4194, "MAPSEC_MISSION_BAY", "SALVAGED"),
        make_item("Circuit Board", "ELECTRONIC", 0.5, 250.0, 37.7800, -122.4100, "MAPSEC_SOMA_HUB", "PROCURED"),
        make_item("Heavy Engine", "MECHANICAL", 50.0, 600.0, 37.7720, -122.4200, "MAPSEC_MISSION_BAY", "SALVAGED"),
        make_item("Mineral Core", "SPECIMEN", 3.0, 400.0, 37.7900, -122.4000, "MAPSEC_EMBARCADERO", "FIELD_DISCOVERY"),
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
    mid_weight = populated_catalog.filter_items(min_weight=1.0, max_weight=15.0)
    names = [i.name for i in mid_weight]
    assert "Gear Assembly" in names
    assert "Mineral Core" in names
    assert "Sunken Relic" in names
    assert "Circuit Board" not in names
    assert "Heavy Engine" not in names

    valuable = populated_catalog.filter_items(min_value=400.0)
    val_names = [i.name for i in valuable]
    assert set(val_names) == {"Heavy Engine", "Mineral Core", "Sunken Relic"}


def test_filter_by_spatial_radius(populated_catalog: CategorizedInventoryArray):
    """Validates Pokémon Emerald spatial resolver (radial distance from origin coordinates)."""
    nearby = populated_catalog.filter_by_spatial_radius(
        center_lat=37.7749,
        center_lon=-122.4194,
        radius_km=10.0,
    )
    assert len(nearby) == 4
    assert nearby[0][0].name == "Gear Assembly"
    assert nearby[0][1] < 0.1

    nearby_names = [pair[0].name for pair in nearby]
    assert "Sunken Relic" not in nearby_names


def test_aggregate_summary(populated_catalog: CategorizedInventoryArray):
    """Validates Pikmin 2 aggregate carry load and Poko valuation metrics."""
    summary = populated_catalog.aggregate_summary()
    assert summary["total_items"] == 5
    assert summary["total_weight_kg"] == 78.5
    assert summary["total_value_pokos"] == 2300.0
    assert "MECHANICAL" in summary["categories"]
    assert summary["categories"]["MECHANICAL"]["count"] == 2
    assert summary["categories"]["MECHANICAL"]["weight_kg"] == 60.0
```

---

### `tests/test_repository.py`
```python
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

    db2_path = str(tmp_path / "imported.db")
    repo_fresh = InventoryRepository(db_path=db2_path)
    count = repo_fresh.import_from_json(json_path)
    assert count == 1
    assert repo_fresh.count() == 1
    imported_item = repo_fresh.get(item.item_id)
    assert imported_item is not None
    assert imported_item.name == "Robotic Actuator"
```

---

### `tests/test_cli.py`
```python
"""Tests for CLI interaction and argument dispatch."""

from pathlib import Path
import pytest
from app.cli.__main__ import main


@pytest.fixture
def cli_db(tmp_path: Path) -> str:
    db_file = tmp_path / "cli_test.db"
    return str(db_file)


def test_cli_add_and_list(cli_db: str, capsys):
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

    ret = main(["--db", cli_db, "list"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Plasma Relay" in captured.out
    assert "ELECTRONIC" in captured.out


def test_cli_spatial_search_and_summary(cli_db: str, capsys):
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
```

---

### `tests/test_gui.py`
```python
"""Tests for Tkinter GUI initialization and dashboard actions."""

from pathlib import Path
from unittest.mock import patch
import pytest
from app.gui.__main__ import InventoryAppGUI


@pytest.fixture
def gui_app(tmp_path: Path):
    db_file = tmp_path / "gui_test.db"
    app = InventoryAppGUI(db_path=str(db_file))
    app.withdraw()  # Hide UI during testing
    yield app
    app.destroy()


@patch("app.gui.__main__.messagebox.showinfo")
def test_gui_initialization_and_seeding(mock_showinfo, gui_app: InventoryAppGUI):
    # Check initial empty state
    assert len(gui_app.tree.get_children()) == 0

    # Test seed sample data method
    gui_app._seed_sample_data()

    # Verify table populated with 5 seeded rows
    children = gui_app.tree.get_children()
    assert len(children) == 5

    # Verify summary cards updated
    assert gui_app.card_total_items.cget("text") == "5"

    # Test filter reset
    gui_app.reset_filters()
    assert len(gui_app.tree.get_children()) == 5
```

---

## 5. Setup & Running Instructions

### Virtual Environment Setup
```powershell
# Create virtual environment (if not already created)
python -m venv .venv

# Install pytest
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Running Tests
```powershell
.venv\Scripts\python.exe -m pytest -v
```

### Running the Graphical Dashboard (GUI)
```powershell
.venv\Scripts\python.exe -m app.gui
```

### Running the Command Line Interface (CLI)
```powershell
.venv\Scripts\python.exe -m app.cli --help
```
