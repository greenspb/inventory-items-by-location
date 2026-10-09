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
