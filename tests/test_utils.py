import pytest
from dynamic_world.utils import validate_forest_names, validate_dates


class TestValidateForest:
    class TestHappyPaths:
        def test_validate_names(self, directory):
            forests = ["CordilleraAzul"]
            validate_forest_names(forests, directory["base_path_string"])

    class TestUnhappyPaths:
        def test_inexistent_names(self, directory):
            with pytest.raises(FileNotFoundError):
                forests = ["CordilleraAzul", "AAA"]
                validate_forest_names(forests, directory["base_path_string"])


class TestValidateDates:
    class TestHappyPaths:
        def test_validate_dates(self):
            dates = ["2022-01-01"]
            validate_dates(dates)

    class TestUnhappyPaths:
        def test_validate_dates_wrong(self):
            with pytest.raises(ValueError):
                dates = ["2022-01-01", "2022/01/01"]
                validate_dates(dates)
