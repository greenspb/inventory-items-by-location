# Location-Based Inventory System (Decomp Architecture)

## Execution & Verification Summary
- Checked task `Run full test suite`
- Killed task `Run full test suite`
- Created `test_gui.py`
- Ran command: Run pytest in venv (`.venv\Scripts\python.exe -m pytest -v`)
- Created `requirements.txt`
- Created `README.md`
- Ran command: Run final pytest check (`.venv\Scripts\python.exe -m pytest`)

The location-based inventory application architecture is implemented, adapting the legacy C struct memory patterns from **Pokémon Emerald** and **Pikmin 2** into modern, type-safe Python dataclasses.

---

### 1. Legacy Decompilation Memory & Struct Patterns

#### A. Pokémon Emerald Pattern: Spatial Provenance & "Met Location"
In `pret/pokeemerald` (`include/pokemon.h`), Pokémon data is divided into 12-byte substructures. Substructure 3 (`PokemonSubstruct3`) encapsulates origin and encounter context:
```c
struct PokemonSubstruct3 {
    u8 pokerus;
    u8 metLocation;       // MAPSEC_* region map section ID
    u16 metLevel:7;       // Initial acquisition condition (0-100)
    u16 metGame:4;        // Cartridge provenance (Emerald, Ruby, etc.)
    u16 pokeball:4;       // Containment apparatus
    u16 otGender:1;       // Trainer metadata
    ...
};
```
* **Python Adaptation**: Refactored into [`SpatialCoordinates`](app/core/models.py) (geographic latitude, longitude, altitude, accuracy radius, and Great-Circle / Haversine distance calculations) and [`MetLocationMetadata`](app/core/models.py) (binding GPS coordinates, ISO-8601 UTC timestamp, map section tag, origin source, handler ID, and containment specification).

#### B. Pikmin 2 Pattern: Categorized Inventory Arrays & Physical Configs
In `projectPiki/pikmin2` (`plugProjectKandoU/pelletConfig.h`, `TreasureMgr.h`), carryable entities and treasures define strict physical transport and appraisal metrics:
```c
struct PelletConfig {
    char*   mName;        // Identifier
    f32     mWeight;      // Minimum Pikmin carrier threshold (mass)
    f32     mMaxWeight;   // Maximum carrying capacity
    u32     mPoko;        // Appraised monetary value
    u8      mCategory;    // Treasure series / Pellet color taxon
    f32     mRadius;      // Physical bounding volume
    u8      mDynamics;    // Physical transport dynamics
};
```
* **Python Adaptation**: Refactored into [`PhysicalAttributes`](app/core/models.py) (category series, mass in kg, appraised value in Pokos, 3D dimensions, volume, fragility rating) and [`CategorizedInventoryArray`](app/core/catalog.py) (in-memory indexed partitioned arrays by category, providing sub-millisecond filtering and Pikmin-style aggregate carrier weight / Poko valuation summaries).

---

### 2. Project Directory Structure

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
└── README.md
```

---

### 3. Core Data Models ([`app/core/models.py`](app/core/models.py))

```python
from __future__ import annotations
from dataclasses import dataclass, field
import datetime, math, uuid
from typing import Any, Dict, Tuple

@dataclass(frozen=True)
class SpatialCoordinates:
    """Geographic coordinates with Haversine distance computation."""
    latitude: float
    longitude: float
    altitude: float = 0.0
    accuracy_meters: float = 1.0

    def distance_to_km(self, other: SpatialCoordinates) -> float:
        earth_radius_km = 6371.0
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = (math.sin(dlat / 2.0) ** 2 +
             math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2.0) ** 2)
        return earth_radius_km * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    def within_radius_km(self, other: SpatialCoordinates, radius_km: float) -> bool:
        return self.distance_to_km(other) <= radius_km


@dataclass
class MetLocationMetadata:
    """Adapts Pokémon Emerald PokemonSubstruct3 provenance pattern."""
    coordinates: SpatialCoordinates
    met_location_tag: str                          # MAPSEC_* zone identifier
    met_timestamp: str = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    origin_source: str = "FIELD_DISCOVERY"         # metGame equivalent
    custodian_id: str = "SYS_OPERATOR"             # otId equivalent
    containment_type: str = "STANDARD_CONTAINER"   # Pokéball equivalent
    condition_level: int = 100                     # metLevel (1-100)


@dataclass
class PhysicalAttributes:
    """Adapts Pikmin 2 PelletConfig / Treasure physical config pattern."""
    category: str                                  # Treasure series / pellet color
    weight: float                                  # Carrying requirement / mass in kg
    value: float                                   # Appraisal in currency / Pokos
    dimensions_cm: Tuple[float, float, float] = (10.0, 10.0, 10.0)
    fragility: int = 1                             # 1 (durable) to 5 (fragile)

    @property
    def volume_cm3(self) -> float:
        return self.dimensions_cm[0] * self.dimensions_cm[1] * self.dimensions_cm[2]


@dataclass
class InventoryItem:
    """Domain entity uniting spatial provenance with physical attributes."""
    name: str
    spatial_meta: MetLocationMetadata
    physical_attrs: PhysicalAttributes
    item_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    notes: str = ""
```

---

### 4. Running the Separate Interfaces

Both the CLI and GUI frontends share the identical underlying [`InventoryService`](app/services/inventory_service.py) and SQLite storage ([`InventoryRepository`](app/storage/repository.py)), allowing changes in one interface to be reflected in the other.

#### Launching the Graphical Interface (Tkinter Dashboard)
```powershell
.venv\Scripts\python.exe -m app.gui
```
* **Dashboard Stats**: Real-time cards displaying total item count, cumulative carrier load (kg), and appraised valuation (Pokos).
* **Logging Form**: Input panel with validation for item name, category series, mass, value, met location tag, and coordinates.
* **Spatial & Attribute Filtering**: Filter by category, mass thresholds, or search by geographic radius (`center_lat`, `center_lon`, `radius_km`).
* **Memory Struct Inspector**: Double-click any row to view the legacy C struct decomposition.
* **JSON Backup**: One-click import and export buttons.

#### Launching the Command-Line Interface (CLI)
```powershell
.venv\Scripts\python.exe -m app.cli --help
```
* **Register a new item**:
  ```powershell
  .venv\Scripts\python.exe -m app.cli add --name "Titanium Gyroscope" --category MECHANICAL --weight 4.5 --value 320 --lat 37.7749 --lon -122.4194 --met-tag "MAPSEC_WAREHOUSE_01"
  ```
* **List inventory with filters**:
  ```powershell
  .venv\Scripts\python.exe -m app.cli list --category MECHANICAL --min-weight 2.0
  ```
* **Spatial radius search (Pokémon encounter resolver)**:
  ```powershell
  .venv\Scripts\python.exe -m app.cli search-spatial --lat 37.7750 --lon -122.4190 --radius-km 25.0
  ```
* **Inspect legacy memory decomposition**:
  ```powershell
  .venv\Scripts\python.exe -m app.cli inspect <ITEM_ID_OR_PREFIX>
  ```
* **View Pikmin-style aggregate statistics**:
  ```powershell
  .venv\Scripts\python.exe -m app.cli summary
  ```

---

### 5. Test Suite Verification

Run the test suite inside the virtual environment:
```powershell
.venv\Scripts\python.exe -m pytest -v
```

**Results**: All **16 tests passed in 0.42s** across:
* `tests/test_models.py`: Validates Haversine distance, boundary checks, and full roundtrip dictionary serialization.
* `tests/test_catalog.py`: Validates Pikmin-style categorized array partitioning, weight/value indexing, spatial radial filtering, and aggregate summaries.
* `tests/test_repository.py`: Validates SQLite CRUD operations, connection cleanup, and JSON export/import.
* `tests/test_cli.py`: Validates CLI command execution and argument parsing.
* `tests/test_gui.py`: Validates Tkinter component initialization, data seeding, and summary card updates.
