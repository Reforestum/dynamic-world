# dynamic-world 🛰️

Wrapper package around [Google's Dynamic World App](https://dynamicworld.app/) [^1], to easily monitor forests and calculate their co2 storage on a near-real time.

[^1]: This dataset is produced for the Dynamic World Project by Google in partnership with National Geographic Society and the World Resources Institute.

## Install

```zsh
pip install dynamic-world
```

An external C library is required as well: [GDAL](https://gdal.org/download.html). The [Dockerfile](./Dockerfile) already has GDAl installed. If working locally, an easy way to install it is by running `conda install -c conda-forge gdal`

## Google Earth Engine authentication

This package runs computation on Earth Engine and needs to be authenticated beforehand. See the [authentication](https://developers.google.com/earth-engine/guides/python_install#authentication) from a Jupyter notebook, or alternatively using a [private key](https://developers.google.com/earth-engine/guides/service_account#use-a-service-account-with-a-private-key) creating a [service account](https://developers.google.com/earth-engine/guides/service_account).


## Usage

Given a Forest (defined as a directory with some configuration files, see bellow), this package retrieves statistics and images of it.
See [Jupyter tutorial](Notebooks/dynamic_world_tutorial.ipynb) for a usage example.

### Forests

Each forest (or "proyect") is defined inside a directory with a given name and 2 files:

1. A forest_config.yml (name is mandatory) which looks like this:

```yaml
# Name of the forest/proyect
name: Sample

# Locations of the geojson file
geojson: './sample.geojson'

# Co2 factor: how many tons of CO2 are stored on average per hectare
co2_factor: {
    'trees': 591.85,
    'grass': 6,
    'bare': 6,
    'crops': 11.5,
    'flooded_vegetation': 6,
    'other': 0,
    'factor_pixel': 100, # Indicates how many pixels are (on average) inside a hectare
  }

# Date in which the reforestation started, in format YYYY-mm-dd
start_date: '2022-01-01'
```

2. A valid geojson file [see](https://geojson.org/) (named as defined in forest_config.yml) that defines the area

Internally, forests are stored as a ForestConfig instance (see dynamic_world.configurations for more details).

### Available calculations

Given a forest and a pair of dates, we download the forest's landcover image, landcover statistics and total CO2 calculation. In other words, we mean the amount of CO2 (measured in tons) that a forest stores (and therefore is not released into the atmosphere if it was burned :D)

The forest image is stored as a [Cloud Optimized Geotiff](https://www.cogeo.org/) file. The expression used for the file-name is the following:

```python
f"{forest.name.replace(' ', '_')}_{start_date}_{end_date}.cog.tif"
```

For [reductions](https://developers.google.com/earth-engine/guides/reducers_intro) we use the Mode (polling). If a very large time interval is specified, recent changes in the forest will be masked by old pixel values. It is encouraged to use the smallest possible time intervals (at least a week is required or there may not be data). However, depending on some factors (such as the amount of clouds), specifying a small time interval may result in many NA (see mrv.calculations documentation for further info on how NA are treated when calculating the co2 factor).

---

# Development notes

We encourage developers to open the repository using [VSCode remote container functionality](https://code.visualstudio.com/docs/remote/containers).

## Secrets

To run the tests, you will need only one secret, which is Earth Engine's [service account](https://developers.google.com/earth-engine/guides/service_account) base64-encoded:

```
SERVICE_ACCOUNT=<very-long-string>
```

The following snippet can be used to base64-encode the `service_account.json` file:
```console
python <<HEREDOC
import base64
with open('service_account.json', 'rb') as file:
    file = file.read()
    base64_encoded_data = base64.b64encode(file)
    base64_message = base64_encoded_data.decode('utf-8')
print(base64_message)
HEREDOC
```

## How to run tests locally

```zsh
# In the root directory of the proyect
pytest

# Run coverage 
pytest --cov mrv --cov-branch --cov-report term-missing --disable-warnings
```

## How to run tests in docker

```zsh
# Build test docker
docker build --tag dw --file Dockerfile --target dev .

# Run lint and tests
docker run dw /bin/bash -c "flake8 && pytest"
```
