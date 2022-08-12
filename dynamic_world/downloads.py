# Dependencies
import os
from pathlib import Path

import ee
import geemap

from dynamic_world.configurations import ForestConfig
# Constants
from dynamic_world.constants import SCALE
# Errors
from dynamic_world.errors import DateBeforeError
from dynamic_world.utils import get_logger, validate_dates


def download_single_date_image(
        start_date: str,
        end_date: str,
        forest: ForestConfig,
        destination_folder: Path) -> str:
    """
    Downloads the image of a forest (representing the status at a specific date)
    into a Cloud Optimized Geotiff file
    Args:
        start_date: a string with format YYYY-mm-dd
        end_date: a string with format YYYY-mm-dd, must be after start_date
        forest: a ForestConfig instance
        destination_folder: the folder where the files are stored
            created if not exists
    Returns:
        a string containing the path to the newly created COG file
    """
    validate_dates([start_date, end_date])

    ee_geojson = geemap.geojson_to_ee(forest.geojson_info)

    # Defining the borders for DW map (must be defined as ee.Geometry)
    borders = ee_geojson.geometry()

    # Can compare this way since both dates are in ISO notation
    if start_date >= end_date:
        raise DateBeforeError("end_date", "start_date")

    # If end_date is before proyect's start_date raise a warning
    if forest.start_date > end_date:
        get_logger().warning("end_date is before proyect's start_date: " +
                             f"{end_date} > {forest.start_date}")

    # Loading DW map and restrict it to dates and borders
    dw = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1').filterDate(
        start_date, end_date).filterBounds(
        borders)  # Returns ee.ImageCollection

    # Reducing using the mode (polling)
    classification = dw.select('label')
    dw_composite = classification.reduce(ee.Reducer.mode()).clip(borders)

    name = forest.name
    destination_folder.mkdir(parents=True, exist_ok=True)
    file_path = destination_folder / Path(
        name.replace(' ', '_') + '_' + start_date + '_' + end_date + '.tif')
    file_path_cog = destination_folder / Path(
        name.replace(' ', '_') + '_' + start_date + '_' + end_date + ".cog" + ".tif")

    geemap.download_ee_image(
        dw_composite,
        file_path,
        scale=SCALE,
        region=borders,
        crs='EPSG:4326')

    get_logger().info(f"Successfully created TIFF file {file_path}")

    # Use GDAL command to create a COG from the TIFF file
    os.system("gdal_translate " +
              str(file_path) +
              " " +
              str(file_path_cog) +
              " -of COG -co COMPRESS=LZW")

    get_logger().info(f"Successfully created COG file {file_path_cog}")

    return file_path_cog
