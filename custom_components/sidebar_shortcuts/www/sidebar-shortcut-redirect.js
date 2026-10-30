/*
 * Sidebar Shortcuts - internal redirect panel.
 *
 * Same principle as the well-known community "panel-redirect.js"
 * (panel_custom + history.replaceState): instead of loading the target
 * in an iframe, this rewrites the browser URL in place and tells the
 * Home Assistant frontend to re-render. Because it's a same-origin
 * navigation (not a cross-origin iframe), it works everywhere the
 * Home Assistant app itself is reachable - local network, remote
 * HTTPS access, Nabu Casa, etc. - with none of the mixed-content
 * restrictions an iframe has.
 *
 * It only works for targets that are internal to this Home Assistant
 * instance (e.g. /lovelace/xxx, /config/integrations). It cannot be
 * used to reach a different origin (another site, a NAS, a router) -
 * the browser blocks cross-origin history.replaceState.
 */
class SidebarShortcutRedirect extends HTMLElement {
  connectedCallback() {
    if (this._info) {
      this._navigate();
    }
  }

  set panel(info) {
    this._info = info;

    if (this.isConnected) {
      this._navigate();
    }
  }

  _navigate() {
    const target = this._info.config.target;
    history.replaceState(null, "", target);
    const event = new Event("location-changed", {
      bubbles: true,
      composed: true,
    });
    event.detail = { replace: true };
    this.dispatchEvent(event);
  }
}

customElements.define("sidebar-shortcut-redirect", SidebarShortcutRedirect);
