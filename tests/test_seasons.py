import geopandas as gpd
import plotly.graph_objects as go
import pytest

import ecoscope

if not pytest.earthengine:
    pytest.skip(
        "Skipping tests because connection to Earth Engine is not available.",
        allow_module_level=True,
    )


def test_seasons():
    gdf = gpd.read_file("tests/sample_data/vector/AOI_sites.gpkg").to_crs(4326)

    aoi = gdf.geometry.iat[0]

    # Extract the standardized NDVI ndvi_vals within the AOI
    ndvi_vals = ecoscope.analysis.seasons.std_ndvi_vals(aoi, start="2010-01-01", end="2021-01-01")

    # Calculate the seasonal transition point
    cuts = ecoscope.analysis.seasons.val_cuts(ndvi_vals, 2)

    # Determine the seasonal time windows
    windows = ecoscope.analysis.seasons.seasonal_windows(ndvi_vals, cuts, season_labels=["dry", "wet"])

    ecoscope.plotting.plot_seasonal_dist(ndvi_vals["NDVI"], cuts)
    ecoscope.plotting.plot.add_seasons(go.Figure(), windows)

    assert len(windows) > 0
