/*
 * Sidebar Shortcuts - redirect panel.
 *
 * Internal targets (same origin as the current Home Assistant page):
 * same principle as the well-known community "panel-redirect.js"
 * (panel_custom + history.replaceState) - rewrites the browser URL in
 * place and tells the Home Assistant frontend to re-render. Because
 * it's a same-origin navigation (not a cross-origin iframe), it works
 * everywhere the Home Assistant app itself is reachable - local
 * network, remote HTTPS access, Nabu Casa, etc. - with none of the
 * mixed-content restrictions an iframe has.
 *
 * External targets (a different origin - another site, a NAS, a
 * router...): opened in a new browser tab instead, exactly like a
 * normal link with target="_blank". None of the iframe limitations
 * (X-Frame-Options, mixed content) apply since the page is never
 * embedded. The sidebar then returns to the previous panel.
 *
 * link_mode ("auto" / "internal" / "external", set per-shortcut in the
 * config flow) overrides the automatic same-origin detection below.
 * Auto-detection compares the shortcut's URL to the CURRENT page's
 * origin at click time, which misclassifies a shortcut whenever Home
 * Assistant is reached from a different address than the one used
 * when the shortcut was configured (local IP vs Nabu Casa vs
 * Tailscale...). link_mode lets the user pin the correct behavior
 * explicitly instead of relying on that guess. Shortcuts created
 * before this field existed have no link_mode in their config, so
 * they fall through to "auto" and keep behaving exactly as before.
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
    const config = this._info.config;
    const url = config.url;
    const linkMode = config.link_mode || "auto";

    let isExternal;
    if (linkMode === "internal") {
      isExternal = false;
    } else if (linkMode === "external") {
      isExternal = true;
    } else {
      isExternal = true;
      try {
        isExternal = new URL(url, window.location.href).origin !== window.location.origin;
      } catch (e) {
        isExternal = true;
      }
    }

    if (isExternal) {
      window.open(url, "_blank", "noopener");
      if (window.history.length > 1) {
        history.back();
      } else {
        history.replaceState(null, "", "/");
        const event = new Event("location-changed", {
          bubbles: true,
          composed: true,
        });
        event.detail = { replace: true };
        this.dispatchEvent(event);
      }
      return;
    }

    history.replaceState(null, "", config.target);
    const event = new Event("location-changed", {
      bubbles: true,
      composed: true,
    });
    event.detail = { replace: true };
    this.dispatchEvent(event);
  }
}

customElements.define("sidebar-shortcut-redirect", SidebarShortcutRedirect);
