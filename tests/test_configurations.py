from pathlib import Path
from dynamic_world.configurations import load_config
import geojson
import pytest


class TestLoadConfig:
    class TestHappyPaths:
        def test_load_config_correct(self, directory):
            with open(directory["cordillera_geojson"]) as geojson_file:
                geojson_object = geojson.load(geojson_file)

            expected_info = {
                "name": "Cordillera Azul",
                "geojson_info": geojson_object,
                "co2_factor_info": {
                    "trees" : 591.85,
                    "grass" : 6,
                    "bare" : 6,
                    "crops" : 11.5,
                    "flooded_vegetation" : 6,
                    "other" : 0,
                    "factor_pixel" : 100
                },
            }

            forest_config = load_config(directory["cordillera_base_path"])

            for key, value in expected_info.items():
                assert hasattr(
                    forest_config, key
                )  # Expect to have attribute named like key
                assert (
                    getattr(forest_config, key) == value
                )  # Expect actual attribute to match expected value

    class TestUnhappyPaths:
        def test_load_config_missing_yaml(self):
            with pytest.raises(FileNotFoundError):
                load_config(Path("tests/exampleProyects/Invalid/NoYaml"))

        def test_load_config_missing_geojson(self):
            with pytest.raises(FileNotFoundError):
                load_config(Path("tests/exampleProyects/Invalid/NoGeojson"))

        def test_load_config_missing_co2_factor(self):
            with pytest.raises(KeyError):
                load_config(Path("tests/exampleProyects/Invalid/NoCo2Factor"))

        def test_load_config_co2_factor_missing_other_key(self):
            with pytest.raises(ValueError):
                load_config(Path("tests/exampleProyects/Invalid/NoOtherKey"))

        def test_load_config_co2_factor_missing_factor_pixel_key(self):
            with pytest.raises(ValueError):
                load_config(Path("tests/exampleProyects/Invalid/NoFactorPixelKey"))

        def test_load_config_invalid_start_date(self):
            with pytest.raises(ValueError):
                load_config(Path("tests/exampleProyects/Invalid/BadDate"))

        def test_load_config_invalid_co2_factor_label(self):
            with pytest.raises(ValueError):
                load_config(Path("tests/exampleProyects/Invalid/BadCo2FactorLabel"))
