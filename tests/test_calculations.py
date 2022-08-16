import pytest

from dynamic_world.configurations import load_config
from dynamic_world.calculations import (single_date_calculation,
                                        co2_factor_calculation)
from dynamic_world.utils import initialize_ee

# TODO gives warnings, but I'm pretty sure that it's due to 3rd party libaries,
# maybe supress them?


class TestSingleDateCalculation:

    class TestHappyPaths:
        #  @pytest.mark.skip(reason="Must be executed only in local")
        def test_single_date_calculation_correct(self, directory):

            initialize_ee()

            expected_keys = ['NA', 'bare', 'built', 'crops', 'flooded_vegetation',
                             'grass', 'shrub_and_scrub',
                             'snow_and_ice', 'trees', 'water']

            forest = load_config(directory["cordillera_base_path"])

            counts = single_date_calculation('2022-06-04', '2022-07-04', forest)

            for key in counts.keys():
                assert (
                    key in expected_keys
                )

        @pytest.mark.filterwarnings("ignore:end_date is before")
        def test_single_date_calculation_before_forest_start_date(self, directory):

            initialize_ee()

            expected_keys = ['NA', 'bare', 'built', 'crops', 'flooded_vegetation',
                             'grass', 'shrub_and_scrub',
                             'snow_and_ice', 'trees', 'water']

            forest = load_config(directory["cordillera_base_path"])

            counts = single_date_calculation('2021-01-01', '2021-02-01', forest)

            for key in counts.keys():
                assert (
                    key in expected_keys
                )

    class TestUnhappyPaths:
        def test_date_before_start_date(self, directory):

            initialize_ee()

            with pytest.raises(ValueError):
                forest = load_config(directory["cordillera_base_path"])
                single_date_calculation('2022-06-04', '2000-01-01', forest)


class TestCo2FactorCalculation:

    class TestHappyPaths:
        def test_co2_factor_calculation_correct(self, directory):
            # 1/9 because there is 1 NA and forest proportion is 1/9
            expected_value = 1 + 1/9

            forest = load_config(directory["sample_base_path"])
            pixel_counts = {
                'NA': 1,
                'bare': 1,
                'built': 1,
                'crops': 1,
                'flooded_vegetation': 1,
                'grass': 1,
                'shrub_and_scrub': 1,
                'snow_and_ice': 1,
                'trees': 1,
                'water': 1
            }

            assert co2_factor_calculation(pixel_counts, forest) == expected_value

        def test_co2_factor_calculation_no_na_key(self, directory):
            forest = load_config(directory["sample_base_path"])
            pixel_counts = {
                'bare': 1,
                'built': 1,
                'crops': 1,
                'flooded_vegetation': 1,
                'grass': 1,
                'shrub_and_scrub': 1,
                'snow_and_ice': 1,
                'trees': 1,
                'water': 1
            }
            expected_value = 1

            assert co2_factor_calculation(pixel_counts, forest) == expected_value
