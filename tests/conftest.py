import pytest
from pathlib import Path
from typer import Typer


@pytest.fixture
def directory():

    base_path_string = "tests/exampleProyects"
    cordillera_base_path = Path("tests/exampleProyects/CordilleraAzul")
    sample_base_path = Path("tests/exampleProyects/Sample")

    directory = {
        "cordillera_base_path": cordillera_base_path,
        "cordillera_geojson": cordillera_base_path / "cordillera_azul_4326.geojson",
        "cordillera_co2_factor":
            cordillera_base_path / "cordillera_azul_co2_factor.json",
        "sample_base_path": sample_base_path,
        "base_path_string": base_path_string
    }

    return directory


@pytest.fixture
def app():
    from dynamic_world.main import main
    app = Typer()
    app.command()(main)

    return app
