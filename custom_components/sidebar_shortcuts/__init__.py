"""The Sidebar Shortcuts integration.

Each config entry represents one sidebar shortcut: a name, an icon and a
URL. The URL is rendered in an iframe registered as a built-in sidebar
panel, exactly like the native ``panel_iframe`` YAML integration, but
added/removed/edited entirely from the UI, with no YAML and no restart.
"""
from __future__ import annotations

import logging

from homeassistant.components import frontend
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_ICON, CONF_NAME, CONF_URL, DEFAULT_ICON, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = []


def _panel_path(entry_id: str) -> str:
    """Build a unique frontend path for this shortcut's panel."""
    return f"shortcut-{entry_id}"


def _register_panel(hass: HomeAssistant, path: str, name: str, icon: str, url: str) -> None:
    """Register (or replace) the sidebar panel for one shortcut."""
    try:
        frontend.async_register_built_in_panel(
            hass,
            component_name="iframe",
            sidebar_title=name,
            sidebar_icon=icon,
            frontend_url_path=path,
            config={"url": url},
            require_admin=False,
        )
    except ValueError:
        # Panel path already registered (e.g. a reload without a clean
        # unload) - remove the stale one and register fresh.
        frontend.async_remove_panel(hass, path)
        frontend.async_register_built_in_panel(
            hass,
            component_name="iframe",
            sidebar_title=name,
            sidebar_icon=icon,
            frontend_url_path=path,
            config={"url": url},
            require_admin=False,
        )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Register this shortcut's sidebar panel."""
    hass.data.setdefault(DOMAIN, {})

    path = _panel_path(entry.entry_id)
    name = entry.data[CONF_NAME]
    url = entry.data[CONF_URL]
    icon = entry.data.get(CONF_ICON, DEFAULT_ICON)

    _register_panel(hass, path, name, icon, url)

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
