"""Config flow for Sidebar Shortcuts.

One config entry = one shortcut. Adding another shortcut means adding
another instance of this integration (Settings -> Devices & services ->
Add integration -> Sidebar Shortcuts).
"""
from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import CONF_ICON, CONF_NAME, CONF_URL, DEFAULT_ICON, DOMAIN


def _validate_url(url: str) -> None:
    """Raise ValueError if the URL is not a valid absolute http(s) URL."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("invalid_url")


def _schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, "")): str,
            vol.Required(CONF_URL, default=defaults.get(CONF_URL, "")): str,
            vol.Optional(
                CONF_ICON, default=defaults.get(CONF_ICON, DEFAULT_ICON)
            ): selector.IconSelector(
                selector.IconSelectorConfig(placeholder=DEFAULT_ICON)
            ),
        }
    )


class SidebarShortcutsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for a single sidebar shortcut."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            name = user_input[CONF_NAME].strip()
            url = user_input[CONF_URL].strip()
            icon = (user_input.get(CONF_ICON) or DEFAULT_ICON).strip() or DEFAULT_ICON

            try:
                _validate_url(url)
            except ValueError:
                errors["base"] = "invalid_url"
            else:
                await self.async_set_unique_id(f"{name.lower()}::{url}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=name,
                    data={CONF_NAME: name, CONF_URL: url, CONF_ICON: icon},
                )

        return self.async_show_form(
            step_id="user", data_schema=_schema(user_input), errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> SidebarShortcutsOptionsFlow:
        return SidebarShortcutsOptionsFlow()


class SidebarShortcutsOptionsFlow(config_entries.OptionsFlow):
    """Let the user edit an existing shortcut's name/URL/icon."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        entry = self.config_entry

        if user_input is not None:
            name = user_input[CONF_NAME].strip()
            url = user_input[CONF_URL].strip()
            icon = (user_input.get(CONF_ICON) or DEFAULT_ICON).strip() or DEFAULT_ICON

            try:
                _validate_url(url)
            except ValueError:
                errors["base"] = "invalid_url"
            else:
                self.hass.config_entries.async_update_entry(
                    entry,
                    title=name,
                    data={CONF_NAME: name, CONF_URL: url, CONF_ICON: icon},
                )
                return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=_schema(user_input or dict(entry.data)),
            errors=errors,
        )
