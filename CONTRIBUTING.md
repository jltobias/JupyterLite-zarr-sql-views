# Contributing

Open a focused change with a clear data question, source attribution, and the checks you ran.
Use `scripts/make_notebooks.py` as the notebook authoring source, regenerate the notebooks,
and execute them before building the book. Keep code cells short and explain scientific limits.

New real datasets need exact source URLs/IDs, units, CRS, nodata, dates, transformations,
license, and quality masks. Label synthetic, observed, and modeled data at the dataset,
figure, and export levels. Never replace a failed live request with unlabelled invented data.

Run the checks documented in README.md. The browser app uses a bundled, bounded Zarr schema;
supporting additional formats or providers needs an explicit adapter and a reproducible example.
Do not commit access tokens, large raw archives, browser storage, or generated `_site` output.
