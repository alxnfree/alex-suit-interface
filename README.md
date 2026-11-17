# A.L.E.X. — Suit Interface

A single-page interactive 3D suit visualization.

## Features
- Two display modes: cyan/magenta wireframe scan and blue hologram
- Interactive 3D model with rotate, tilt, pan and zoom (Three.js OrbitControls)
- Equipment details for the utility belt and boots
- Project notes saved in the current browser using localStorage
- Optional local browser access gate

## Run locally
Open `index.html` in a local web server (recommended), or use the VS Code Live Server extension. Three.js and OrbitControls load from jsDelivr, so an internet connection is required.

## Publish with GitHub Pages
1. Open the repository Settings.
2. Go to Pages.
3. Under Build and deployment, select Deploy from a branch.
4. Choose `main` and `/ (root)`, then Save.
5. Wait for GitHub Pages to publish the site.

## Important
The password gate is only a convenience barrier stored in this browser. It is not secure authentication and does not protect the source code or site from other visitors. Notes are stored locally in each browser and are not synced to GitHub.
