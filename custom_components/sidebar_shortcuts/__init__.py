"""The Sidebar Shortcuts integration.

Each config entry represents one sidebar shortcut: a name, an icon and a
URL. Instead of loading the URL in an iframe, the shortcut is registered
as a ``panel_custom`` panel that redirects internally via
``history.replaceState`` - exactly the same principle as the well-known
community ``panel_custom`` + ``panel-redirect.js`` pattern used directly
in ``configuration.yaml``. Because it's a same-origin navigation rather
than a cross-origin iframe, it works from anywhere the Home Assistant
frontend itself is reachable (local network, remote HTTPS, Nabu Casa...),
with none of the mixed-content restrictions an iframe has.

This only works for targets internal to this Home Assistant instance
(dashboards, config pages, etc.) - it cannot reach a different site or
device, same as the native mechanism it mirrors.

All of this is still registered dynamically from Python at runtime
(``panel_custom.async_register_panel``), exactly like the previous
iframe-based version - no YAML is written or required, and no restart
is needed to add/edit/remove a shortcut after the integration itself is
installed.
"""
from __future__ import annotations

import logging
from pathlib import Path
from urllib.parse import urlparse

from homeassistant.components.http import StaticPathConfig
from homeassistant.components.panel_custom import async_register_panel
from homeassistant.components import frontend
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_ICON, CONF_NAME, CONF_URL, DEFAULT_ICON, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = []

STATIC_URL_PATH = "/sidebar_shortcuts_static/sidebar-shortcut-redirect.js"
WEBCOMPONENT_NAME = "sidebar-shortcut-redirect"


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


async def _register_panel(hass: HomeAssistant, path: str, name: str, icon: str, url: str) -> None:
    """Register (or replace) the sidebar panel for one shortcut."""
    target = _target_path(url)
    kwargs = dict(
        webcomponent_name=WEBCOMPONENT_NAME,
        frontend_url_path=path,
        sidebar_title=name,
        sidebar_icon=icon,
        module_url=STATIC_URL_PATH,
        embed_iframe=False,
        require_admin=False,
        config={"target": target},
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

    await _register_panel(hass, path, name, icon, url)

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
