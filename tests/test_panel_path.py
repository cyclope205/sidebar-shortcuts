"""Tests for the per-entry panel path builder (_panel_path)."""
from __future__ import annotations

from custom_components.sidebar_shortcuts import _panel_path


def test_panel_path_is_prefixed_and_unique_per_entry():
    assert _panel_path("01M65FSD7J2EAXMEV9RGR6PRD7") == "shortcut-01M65FSD7J2EAXMEV9RGR6PRD7"
    assert _panel_path("abc") != _panel_path("def")


def test_panel_path_is_deterministic():
    entry_id = "01M65Z93G2C3ZPTRGH5W8P16ZJ"
    assert _panel_path(entry_id) == _panel_path(entry_id)
