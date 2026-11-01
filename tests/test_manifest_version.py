"""Tests for the manifest-version cache-busting helper (_manifest_version).

Covers the fix shipped in v1.2.1/v1.2.2: the redirect panel's JS module is
served with a long-lived Cache-Control header, so its URL must change
whenever the module content changes, or browsers keep serving a stale
cached copy even past a Home Assistant restart.
"""
from __future__ import annotations

import json
from pathlib import Path

from custom_components.sidebar_shortcuts import MODULE_VERSION, STATIC_URL_PATH, _manifest_version


def test_manifest_version_matches_manifest_json():
    manifest_path = (
        Path(__file__).parent.parent
        / "custom_components"
        / "sidebar_shortcuts"
        / "manifest.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert _manifest_version() == manifest["version"]


def test_module_version_is_not_the_fallback():
    # A "0" fallback would mean manifest.json could not be read, which
    # would silently disable the cache-busting this helper exists for.
    assert MODULE_VERSION != "0"


def test_static_url_path_is_versioned_for_cache_busting():
    # _register_panel appends "?v={MODULE_VERSION}" to this base path -
    # guard the base path itself stays a plain, query-free URL.
    assert "?" not in STATIC_URL_PATH
    assert STATIC_URL_PATH.endswith(".js")
