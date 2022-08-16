# Dependencies
import ee
import geemap

from dynamic_world.configurations import ForestConfig
# Constants
from dynamic_world.constants import (CLASS_LABELS_DICT, FACTOR_PIXEL_LABEL,
                                     NA_LABEL, OTHER_LABEL, SCALE)
# Errors
from dynamic_world.errors import DateBeforeError
from dynamic_world.utils import get_logger, validate_dates


def single_date_calculation(
        start_date: str,
        end_date: str,
        forest: ForestConfig) -> "dict[str, int]":
    """
    Retrieves the pixel counts of the area defined in a proyect
    (see dynamic_world.configurations.py)
    using the classification defined by Google's Dynamic Wold
    (https://www.nature.com/articles/s41597-022-01307-4)
    To retrieve the current status of a pixel we use the mode
    (typically nulls are associated to clouds) between start_date and end_date.
    Each pixel is 10x10m.
    Args:
        start_date: a string with format YYYY-mm-dd
        end_date: a string with format YYYY-mm-dd, must be after start_date
        proyect: a ForestConfig (see mrv.configurations.py) object
    Returns:
        a {string : int} dictionary with the following format
        (some keys could not be present):
            {'NA': 1,
            'bare': 1,
            'built': 1,
            'crops': 1,
            'flooded_vegetation': 1,
            'grass': 1,
            'shrub_and_scrub': 1,
            'snow_and_ice': 1,
            'trees': 1,
            'water': 1}
    """
    validate_dates([start_date, end_date])

    # Loading geojson object as ee.FeatureCollection
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

    dw = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1').filterDate(
        start_date, end_date).filterBounds(
        borders)  # Returns ee.ImageCollection

    # Reducing using the mode (polling)
    classification = dw.select('label')
    dw_composite = classification.reduce(ee.Reducer.mode()).clip(borders)

    # Extract pixel counts
    countStats = dw_composite.reduceRegion(
        geometry=borders,
        reducer=ee.Reducer.frequencyHistogram().unweighted(),
        scale=SCALE,  # IMPORTANT!!!! each pixel is 10m x 10m
        maxPixels=1e10)

    counts = ee.Dictionary(countStats.get('label_mode'))

    # Rename using propper classLabels (not 0-8)
    old_keys = counts.keys().getInfo()
    counts_formatted = counts.rename(
        old_keys,
        [CLASS_LABELS_DICT.get(key) for key in old_keys])

    return counts_formatted.getInfo()


def co2_factor_calculation(
        pixel_counts: "dict[str, int]",
        forest: ForestConfig) -> float:
    """
    Calulates the Co2 Tons. absorbed by a forest with a
    specific landcover distribution.
    Each pixel has an associated weight depending on the class
    (forest >> built, for example)
    and we multiply by the number of squares of each class.
    IMPORTANT: each square must represent a 10m x 10m area
    FOR NA's: we assume they distribute just like the pixels
    which we have information about.
    For example, if available pixels contain 40% forest,
    we suppose NA's also have 40% forest.
    Args:
        pixel_counts: a dictionary containing the counts of each category
        forest: a ForestConfig object (containing a co2_factor_info dictionary).
            The keys in this dictionary should map to the keys in pixel_counts
            (except for 'other' and 'factor_pixel').
    Returns:
        a float representing total CO2 tons
    """
    pixel_counts_copy = pixel_counts.copy()

    if NA_LABEL not in pixel_counts_copy.keys():
        pixel_counts_copy[NA_LABEL] = 0

    metric = forest.co2_factor_info.copy()

    totalCO2 = 0

    factorPixel = metric[FACTOR_PIXEL_LABEL]

    notNACount = sum(pixel_counts_copy.values()) - pixel_counts_copy[NA_LABEL]

    #  First we remove the NA assuming they
    # distribute just like the pixels for which we have info
    for notNAKey in set(pixel_counts_copy.keys()).difference([NA_LABEL]):
        pixel_counts_copy[notNAKey] += pixel_counts_copy[
            NA_LABEL] * pixel_counts_copy[notNAKey] / notNACount

    for commonKey in set(metric.keys()).intersection(pixel_counts_copy.keys()) :
        totalCO2 += pixel_counts_copy[commonKey] * metric[commonKey] / factorPixel

    # We apply the metric for 'other' keys
    for otherKey in set(pixel_counts_copy.keys()).difference(
            list(metric.keys()) + [NA_LABEL]):
        totalCO2 += pixel_counts_copy[otherKey] * metric[OTHER_LABEL] / factorPixel

    return totalCO2
