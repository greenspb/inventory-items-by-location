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
