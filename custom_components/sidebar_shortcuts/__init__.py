"""The Sidebar Shortcuts integration.

Each config entry represents one sidebar shortcut: a name, an icon and a
URL. Instead of loading the URL in an iframe, the shortcut is registered
as a ``panel_custom`` panel whose frontend component decides, at click
time, how to get there:

- Internal target (same origin as the page the user is currently on):
  redirects in place via ``history.replaceState`` - exactly the same
  principle as the well-known community ``panel_custom`` +
  ``panel-redirect.js`` pattern used directly in ``configuration.yaml``.
  Same-origin navigation, so it works from anywhere the Home Assistant
  frontend itself is reachable (local network, remote HTTPS, Nabu
  Casa...), with none of the mixed-content restrictions an iframe has.
- External target (a different origin - another site, a NAS, a
  router...): opened in a new browser tab, like a normal link. None of
  the iframe limitations (X-Frame-Options, mixed content) apply.

A shortcut's ``link_mode`` (auto / internal / external) overrides this
origin-based auto-detection when set: useful when Home Assistant is
reachable from several different addresses (local IP, Nabu Casa,
Tailscale...) and the automatic same-origin check would misclassify a
page. Absent on every shortcut created before this field existed, so
``entry.data.get(CONF_LINK_MODE, LINK_MODE_AUTO)`` preserves today's
auto-detect behavior for all of them without any migration.

All of this is still registered dynamically from Python at runtime
(``panel_custom.async_register_panel``), exactly like the previous
iframe-based version - no YAML is written or required, and no restart
is needed to add/edit/remove a shortcut after the integration itself is
installed.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from urllib.parse import urlparse

from homeassistant.components.http import StaticPathConfig
from homeassistant.components.panel_custom import async_register_panel
from homeassistant.components import frontend
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_ICON,
    CONF_LINK_MODE,
    CONF_NAME,
    CONF_URL,
    DEFAULT_ICON,
    DOMAIN,
    LINK_MODE_AUTO,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = []

STATIC_URL_PATH = "/sidebar_shortcuts_static/sidebar-shortcut-redirect.js"
WEBCOMPONENT_NAME = "sidebar-shortcut-redirect"


def _manifest_version() -> str:
    """Read this integration's version from its own manifest.json.

    Used to cache-bust the redirect panel's JS module (see
    ``_async_register_static_path``): the static file is served with a
    long-lived ``Cache-Control`` header, so without a version query
    string browsers that already cached an older build would keep
    running stale JS after an update, even past a restart.
    """
    try:
        manifest = json.loads(
            (Path(__file__).parent / "manifest.json").read_text(encoding="utf-8")
        )
        return str(manifest.get("version", "0"))
    except (OSError, ValueError):
        return "0"


MODULE_VERSION = _manifest_version()


def _panel_path(entry_id: str) -> str:
    """Build a unique frontend path for this shortcut's panel."""
    return f"shortcut-{entry_id}"


def _target_path(url: str) -> str:
    """Extract the internal path (+ query/hash) from a pasted URL.

    The redirect is always same-origin, so only the part after the
    host matters - whatever host/protocol the user pasted gets
    discarded on purpose.
    """
    parsed = urlparse(url)
    target = parsed.path or "/"
    if parsed.query:
        target += f"?{parsed.query}"
    if parsed.fragment:
        target += f"#{parsed.fragment}"
    return target


async def _async_register_static_path(hass: HomeAssistant) -> None:
    """Serve the redirect panel's JS module, once per HA run."""
    if hass.data.get(DOMAIN, {}).get("_static_registered"):
        return
    hass.data.setdefault(DOMAIN, {})["_static_registered"] = True

    js_path = str(Path(__file__).parent / "www" / "sidebar-shortcut-redirect.js")
    await hass.http.async_register_static_paths(
        [StaticPathConfig(STATIC_URL_PATH, js_path, True)]
    )


async def _register_panel(
    hass: HomeAssistant,
    path: str,
    name: str,
    icon: str,
    url: str,
    link_mode: str,
) -> None:
    """Register (or replace) the sidebar panel for one shortcut."""
    target = _target_path(url)
    kwargs = dict(
        webcomponent_name=WEBCOMPONENT_NAME,
        frontend_url_path=path,
        sidebar_title=name,
        sidebar_icon=icon,
        module_url=f"{STATIC_URL_PATH}?v={MODULE_VERSION}",
        embed_iframe=False,
        require_admin=False,
        config={"target": target, "url": url, "link_mode": link_mode},
    )
    try:
        await async_register_panel(hass, **kwargs)
    except ValueError:
        # Panel path already registered (e.g. a reload without a clean
        # unload) - remove the stale one and register fresh.
        frontend.async_remove_panel(hass, path)
        await async_register_panel(hass, **kwargs)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Register this shortcut's sidebar panel."""
    hass.data.setdefault(DOMAIN, {})
    await _async_register_static_path(hass)

    path = _panel_path(entry.entry_id)
    name = entry.data[CONF_NAME]
    url = entry.data[CONF_URL]
    icon = entry.data.get(CONF_ICON, DEFAULT_ICON)
    link_mode = entry.data.get(CONF_LINK_MODE, LINK_MODE_AUTO)

    await _register_panel(hass, path, name, icon, url, link_mode)

    hass.data[DOMAIN][entry.entry_id] = path
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when its options (name/url/icon) change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Remove this shortcut's sidebar panel."""
    path = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if path:
        frontend.async_remove_panel(hass, path)
    return True
