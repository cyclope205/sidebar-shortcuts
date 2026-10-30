# 🔗 Sidebar Shortcuts

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/)
[![Version](https://img.shields.io/github/v/release/cyclope205/sidebar-shortcuts)](https://github.com/cyclope205/sidebar-shortcuts/releases)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-03a9f4)](https://www.home-assistant.io/)

**Ajoutez des raccourcis vers n'importe quelle page dans le menu latéral de Home Assistant, sans toucher à `configuration.yaml` et sans redémarrage.**

Donnez un nom, collez une URL, et le raccourci apparaît immédiatement dans la barre latérale, ouvert dans une iframe — exactement comme le fait l'intégration native `panel_iframe`, mais entièrement pilotable depuis l'interface.

---

## Sommaire

- [Installation](#installation)
- [Utilisation](#utilisation)
- [Modifier ou supprimer un raccourci](#modifier-ou-supprimer-un-raccourci)
- [FAQ / dépannage](#faq--dépannage)
- [Crédits & licence](#crédits--licence)

---

## Installation

### Via HACS (recommandé)

1. HACS → menu **⋮** → **Dépôts personnalisés**.
2. Dépôt : `https://github.com/cyclope205/sidebar-shortcuts`. Type : **Intégration**. Cliquez sur **Ajouter**.
3. Recherchez **Sidebar Shortcuts** → **Télécharger**.
4. **Redémarrez** Home Assistant (une seule fois, pour charger l'intégration elle-même).

### Manuelle

Copiez le dossier `custom_components/sidebar_shortcuts` dans `/config/custom_components/`, puis redémarrez Home Assistant.

---

## Utilisation

1. **Paramètres → Appareils et services → Ajouter une intégration → Sidebar Shortcuts.**
2. Renseignez :
   - **Nom** : le texte affiché dans le menu latéral ;
   - **URL** : l'adresse complète de la page (`https://...`) ;
   - **Icône** *(optionnel)* : un nom d'icône [Material Design Icons](https://pictogrammers.com/library/mdi/), par exemple `mdi:silverware-fork-knife`. Par défaut : `mdi:link-variant`.
3. Validez : le raccourci apparaît aussitôt dans la barre latérale, sans redémarrage.

Pour ajouter un autre raccourci, répétez l'opération : **Ajouter une intégration → Sidebar Shortcuts** à nouveau. Chaque raccourci est une entrée indépendante, visible et gérable séparément dans **Paramètres → Appareils et services**.

---

## Modifier ou supprimer un raccourci

- **Modifier** : sur la carte du raccourci concerné (Paramètres → Appareils et services), cliquez sur **Configurer** pour changer le nom, l'URL ou l'icône. Le raccourci se met à jour immédiatement.
- **Supprimer** : menu **⋮** de la carte → **Supprimer**. Le raccourci disparaît aussitôt de la barre latérale.
- **Réorganiser** : comme tout élément de la barre latérale, l'ordre et la visibilité se règlent par glisser-déposer dans **Paramètres → Tableaux de bord → Modifier la barre latérale** (ou le menu utilisateur en haut à gauche).

---

## FAQ / dépannage

**Le raccourci n'apparaît pas après l'ajout.** Rechargez la page (Ctrl + Maj + R). Si ça persiste, vérifiez dans Paramètres → Appareils et services que l'intégration est bien à l'état « chargé ».

**La page cible ne s'affiche pas dans le raccourci (écran blanc).** Certains sites bloquent explicitement leur affichage en iframe (en-tête `X-Frame-Options` ou `Content-Security-Policy: frame-ancestors`). C'est une restriction du site visé, pas de l'intégration — ça concerne aussi bien `panel_iframe` que n'importe quelle iframe. Les pages internes à votre réseau (autres apps, NAS, routeur, etc.) fonctionnent généralement sans problème.

**J'ai plusieurs raccourcis à ajouter, dois-je redémarrer à chaque fois ?** Non. Le redémarrage n'est nécessaire qu'une fois, après l'installation initiale de l'intégration elle-même (pour que Home Assistant découvre le nouveau domaine `sidebar_shortcuts`). Chaque raccourci ajouté ensuite apparaît immédiatement.

**Puis-je limiter un raccourci aux administrateurs ?** Pas encore dans cette version — tous les utilisateurs du foyer voient tous les raccourcis. Ouvrez une issue si ce réglage vous est utile.

---

## Crédits & licence

Code : licence **MIT** — © cyclope205.

S'appuie sur l'API frontend native de Home Assistant (`async_register_built_in_panel`, type `iframe`), la même que celle utilisée en interne par l'intégration `panel_iframe`.
