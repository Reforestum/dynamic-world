import base64
import datetime
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import List

import ee

from dynamic_world.constants import LOGGER_NAME
from dynamic_world.errors import DateBadFormatError, ForestNotFoundError


def initialize_ee():
    """
    Initializes Earth Engine service using an encrypted
    GEE service account
    """

    with tempfile.NamedTemporaryFile(suffix=".json", mode="w") as tmpfile:

        # Decode base64 secret and load as dict to make sure is json compatible
        service_account_dict = json.loads(
            base64.b64decode(os.environ["SERVICE_ACCOUNT"])
        )
        with open(tmpfile.name, "w") as file:
            json.dump(service_account_dict, file)

        credentials = ee.ServiceAccountCredentials(
            service_account_dict["client_email"],
            tmpfile.name,
        )
    ee.Initialize(credentials)


def validate_forest_names(forests: List[str], base_directory: str):
    """
    Check forests correspond to valid directories inside base_directory folder
    Args:
        forests: list of strings containing forests names,
        they should correspond to an existing directory
    """
    for forest_name in forests:
        forest_path = Path(os.path.join(base_directory, forest_name))
        if not forest_path.exists():
            raise ForestNotFoundError(forest_name)


def validate_dates(dates: List[str]):
    """
    Check if list of dates has YYYY-mm-dd format
    Args:
        forests: list of strings representing dates in YYYY-mm-dd format
    """
    for date in dates:
        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError as exc:
            raise DateBadFormatError() from exc


def get_logger() -> logging.Logger:
    """
    If the logger is not set-up, configure it. Otherwise return it
    """
    logger = logging.getLogger(LOGGER_NAME)

    if not logger.hasHandlers():  # logger is not setup
        logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(
            logging.Formatter(
                "%(pathname)s: %(lineno)d at %(asctime)s -"
                " [%(name)s][%(levelname)s]: %(message)s"
            )
        )

        logger.addHandler(handler)

    return logger
