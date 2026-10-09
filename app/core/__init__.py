"""Core domain models and legacy decompilation-inspired cataloging engine."""

from app.core.models import (
    InventoryItem,
    MetLocationMetadata,
    PhysicalAttributes,
    SpatialCoordinates,
)
from app.core.catalog import CategorizedInventoryArray
from app.core.decompile_refs import (
    ItemCategoryEnum,
    ProvenanceOriginEnum,
    POKEMON_SUBSTRUCT3_C_REFERENCE,
    PIKMIN_PELLET_CONFIG_C_REFERENCE,
)

__all__ = [
    "InventoryItem",
    "MetLocationMetadata",
    "PhysicalAttributes",
    "SpatialCoordinates",
    "CategorizedInventoryArray",
    "ItemCategoryEnum",
    "ProvenanceOriginEnum",
    "POKEMON_SUBSTRUCT3_C_REFERENCE",
    "PIKMIN_PELLET_CONFIG_C_REFERENCE",
]
