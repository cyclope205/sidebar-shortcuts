"""Tests for the internal-target extraction (_target_path)."""
from __future__ import annotations

from custom_components.sidebar_shortcuts import _target_path


def test_target_path_plain_path():
    assert _target_path("/lovelace/xceed") == "/lovelace/xceed"


def test_target_path_with_query():
    assert _target_path("/config/integrations?domain=hue") == "/config/integrations?domain=hue"


def test_target_path_with_fragment():
    assert _target_path("/lovelace#section") == "/lovelace#section"


def test_target_path_with_query_and_fragment():
    assert _target_path("/search?q=light#top") == "/search?q=light#top"


def test_target_path_strips_scheme_and_host():
    assert _target_path("http://192.168.0.38:8123/lovelace/xceed") == "/lovelace/xceed"
    assert _target_path("https://example.duckdns.org/config") == "/config"


def test_target_path_external_url_keeps_only_path():
    # Discarding the host on purpose: the redirect is always same-origin,
    # so a pasted external URL's path/query/hash is all that is kept here.
    # Whether to redirect internally or open externally is decided
    # elsewhere (_navigate in the JS module), based on the *original* URL.
    assert _target_path("https://www.google.fr") == "/"


def test_target_path_empty_path_defaults_to_root():
    assert _target_path("http://192.168.0.38:8123") == "/"
