# Dependencies
import datetime
from pathlib import Path
from typing import Any, Dict

import geojson
import yaml
from pydantic import BaseModel, validator
from yaml.loader import SafeLoader

# Constants
from dynamic_world.constants import (CLASS_LABELS, FACTOR_PIXEL_LABEL,
                                     FOREST_CONFIG_FILENAME, OTHER_LABEL)
# Errors
from dynamic_world.errors import (DateBadFormatError, KeyNotPresentError,
                                  UndefinedKeyError)


class ForestConfig(BaseModel):
    name: str  # The name of the forest/proyect
    geojson_info: geojson.FeatureCollection  # Geojson object (FeatureCollection)
    co2_factor_info: Dict[
        str, float
    ]  # Dictionary containing info used to calculate ammount of co2 retained
    start_date: str

    @validator("co2_factor_info")
    def co2_factor_must_contain(cls, v):
        """
        Co2 factors must contain one key named 'other' and another one named
        'factor_pixel'. All other keys must be also declaresd in
        dynamic_world.constants.CLASS_LABELS
        """
        if OTHER_LABEL not in v.keys():
            raise KeyNotPresentError("co2_factor", OTHER_LABEL)
        if FACTOR_PIXEL_LABEL not in v.keys():
            raise KeyNotPresentError("co2_factor", FACTOR_PIXEL_LABEL)
        for key in [key for key in v.keys() if key not in [OTHER_LABEL,
                                                           FACTOR_PIXEL_LABEL]]:
            if key not in CLASS_LABELS:
                raise UndefinedKeyError(key, CLASS_LABELS)
        return v

    @validator("start_date")
    def start_date_datetime_format(cls, v):
        """
        Start date must have format YYYY-mm-dd
        """
        try:
            datetime.datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise DateBadFormatError("start_date")
        return v

    def __init__(
        self,
        name: str,
        geojson_path: Path,
        co2_factor: dict,
        start_date: str,
        **data: Any
    ) -> None:

        with open(geojson_path) as geojson_file:
            geojson_info = geojson.load(geojson_file)

        super().__init__(
            name=name,
            geojson_info=geojson_info,
            co2_factor_info=co2_factor,
            start_date=start_date,
            **data
        )


def load_config(directory_path: Path) -> ForestConfig:
    """
    Loads a forest configuration.
    A forest configuration is defined by its name, location as geojson object and
    dictionary used to calculate the ammount of co2 retained
    The forest directory MUST contain a file named in the same way as defined in
    dynamic_world.constants.FOREST_CONFIG_FILENAME,
    this file has to specify the next fields:
        - name: name of the forest/proyect
        - geojson: location of geojson file
        - co2_factor: location of the json file containing the co2
            factor, this json must contain an element with key 'other' (default value)
            and another element with key 'factor_pixel'
        - start_date: date in which the resforestation began, in format YYYY-mm-dd
    Args:
        directory_path: Path of the directory containing the proyect
    Returns:
        ForestConfig object with the configuration loaded
    TODO:
        Add support for shapefiles?
    """

    path = directory_path / FOREST_CONFIG_FILENAME

    with open(path) as yaml_file:
        config_data = yaml.load(yaml_file, Loader=SafeLoader)

    forest_configuration = ForestConfig(
        name=config_data["name"],
        geojson_path=directory_path / config_data["geojson"],
        co2_factor=config_data["co2_factor"],
        start_date=config_data["start_date"]
    )

    return forest_configuration
