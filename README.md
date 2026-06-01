# JupyterLite Geospatial Analyses and Maps

A browser-ready, map-first teaching repository for the Periodic Table of Geospatial Analysis:  https://gisgeography.com/spatial-analysis-periodic-table/ 

Citation:  https://gisgeography.com/how-to-cite/    GIS Geography.com:  https://gisgeography.com/about-us/ 

## What changed

- 90 element notebooks plus an index notebook.
- Every notebook includes several mapping examples.
- Local CSV/GeoJSON datasets are bundled for Pyodide/JupyterLite reliability.
- Synthetic shapefiles are included for administrative boundaries, OSM-style places/roads, and health facilities.
- A lightweight `geopackages/` folder is included for organizing teaching layers.
- `images/` and `videos/` folders contain original CC0-style illustrations and a short map-layer video.

## Licensing and source posture

The repository references GADM, OpenStreetMap/Geofabrik, and healthsites.io as realistic data-source workflows, but it does not redistribute their data. The bundled shapefiles are synthetic teaching layers so the repository remains easy to share and run in JupyterLite.

## Deploy

GitHub Pages should be set to **GitHub Actions**. The included workflow stages notebooks, helper modules, data, shapefiles, images, videos, and geopackages before running `jupyter lite build`.
