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

        # Configure colors and typography
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
        # Scrollable container for smaller screens
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
        # Filters toolbar
        filter_box = ttk.Frame(parent)
        filter_box.pack(fill=tk.X, pady=(0, 8))

        # Filter Row 1: Category, Min/Max Weight, Min/Max Value
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

        # Filter Row 2: Spatial Radial Filter (Pokemon met location resolver)
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

        # Update categories in filter combobox
        current_cats = ["ALL"] + self.service.get_categories()
        self.filter_category["values"] = current_cats

    def update_summary_cards(self) -> None:
        summary = self.service.get_summary()
        self.card_total_items.config(text=str(summary["total_items"]))
        self.card_total_weight.config(text=f"{summary['total_weight_kg']} kg")
        self.card_total_pokos.config(text=f"{summary['total_value_pokos']} P")

    def apply_filter(self) -> None:
        # Check if spatial radial search is requested
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

        # Regular multi-attribute filter
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
