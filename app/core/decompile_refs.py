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
