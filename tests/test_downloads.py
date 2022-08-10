from pathlib import Path
from dynamic_world.configurations import load_config
from dynamic_world.downloads import download_single_date_image
import pytest
from dynamic_world.utils import initialize_ee


class TestDownloadSingleDateImage:

    class TestHappyPaths:
        def test_download_single_date_image_correct(self, directory):

            initialize_ee()

            forest = load_config(directory["sample_base_path"])

            file_path = download_single_date_image(
                '2021-07-05',
                '2022-07-05',
                forest,
                Path("tests/exampleProyects/Sample/2022-07-05"))

            path_string = ("tests/exampleProyects/Sample/2022-07-05/" +
                           "Sample_2021-07-05_2022-07-05.cog.tif")

            # Check returned path is correct
            assert file_path == Path(path_string)

            # Check COG file exists in directory
            path = Path(file_path)
            assert path.is_file()

            # Check TIFF file exists in directory TODO maybe remove ???
            path_tif = Path(path_string.replace('.cog', ''))
            assert path_tif.is_file()

        @pytest.mark.filterwarnings("ignore:end_date is before")
        def test_download_single_date_image_before_forest_start_date(self, directory):

            initialize_ee()

            forest = load_config(directory["sample_base_path"])

            file_path = download_single_date_image(
                '2017-01-01',
                '2018-02-01',
                forest,
                Path("tests/exampleProyects/Sample/2018-02-01"))

            path_string = ("tests/exampleProyects/Sample/2018-02-01/" +
                           "Sample_2017-01-01_2018-02-01.cog.tif")

            # Check returned path is correct
            assert file_path == Path(path_string)

            # Check COG file exists in directory
            path = Path(file_path)
            assert path.is_file()

            # Check TIFF file exists in directory TODO maybe remove ???
            path_tif = Path(path_string.replace('.cog', ''))
            assert path_tif.is_file()

    class TestUnhappyPaths:
        def test_date_before_start_date(self, directory):

            initialize_ee()

            with pytest.raises(ValueError):
                forest = load_config(directory["cordillera_base_path"])
                download_single_date_image(
                    '2000-02-01',
                    '2000-01-02',
                    forest,
                    Path("tests/exampleProyects/CordilleraAzul/"))
