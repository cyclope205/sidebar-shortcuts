"""Constants for the Sidebar Shortcuts integration."""

DOMAIN = "sidebar_shortcuts"

CONF_NAME = "name"
CONF_URL = "url"
CONF_ICON = "icon"
CONF_LINK_MODE = "link_mode"

DEFAULT_ICON = "mdi:link-variant"

# How to decide whether a shortcut is internal (same-tab redirect) or
# external (new browser tab). "auto" keeps the pre-existing behavior:
# the frontend compares the shortcut's URL origin to the page's current
# origin at click time. Absent on every shortcut created before this
# field existed, so entry.data.get(CONF_LINK_MODE, LINK_MODE_AUTO)
# preserves today's behavior for all of them without any migration.
LINK_MODE_AUTO = "auto"
LINK_MODE_INTERNAL = "internal"
LINK_MODE_EXTERNAL = "external"
LINK_MODE_OPTIONS = [LINK_MODE_AUTO, LINK_MODE_INTERNAL, LINK_MODE_EXTERNAL]
