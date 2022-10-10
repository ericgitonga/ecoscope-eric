import geopandas as gpd
import geopandas.testing
import numpy as np
import pandas as pd
import pandas.testing
import pytest
import ecoscope


def test_speed_geoseries(movbank_relocations):
    trajectory = ecoscope.base.Trajectory.from_relocations(movbank_relocations)
    sdf = ecoscope.analysis.speed.SpeedDataFrame.from_trajectory(trajectory)
    assert all(~sdf.geometry.is_empty)
    assert all(~sdf.geometry.isna())
