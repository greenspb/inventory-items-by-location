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
    # Support partial match or exact match
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
