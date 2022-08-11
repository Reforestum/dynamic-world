# dynamic-world

Package that allow for remote monitoring of reforested forests based around [Google's Dynamic World App](https://dynamicworld.app/) (see attributions bellow).

## Install

```zsh
pip install dynamic-world
```

## Usage

Given a Forest (defined as a directory with some configuration files, see bellow), this package retrieves statistics and images.
See [Jupyter tutorial](Notebooks/dynamic_world_tutorial.ipynb) for a usage example.

### Forests

Each forest (or "proyect") is stored inside a directory with a given name. Inside this directory there must be 2 files:
- a forest_config.yml (name is mandatory) which looks like this:

```yaml
# Name of the forest/proyect
name : Sample

# Locations of the geojson file and dcitionary with carbon factor/metric
geojson : './sample.geojson'
carbon_factor : {
    "trees" : 1,
    "other" : 0, # MUST contain this label
    "factor_pixel" : 1 # MUST contain this label
}

# Date in which the reforestation started, in format YYYY-mm-dd
start_date: '2022-01-01'
```

- a valid geojson file [see](https://geojson.org/) (named as defined in forest_config.yml) that defines the area

Internally, forests are stored as a ForestConfig instance (see dynamic_world.configurations for more details).

### Available calculations

Given a forest and a pair of dates, we download the forest's landcover image, landcover statistics and carbon factor [^cf_foot] calculation.

[^cf_foot]: by carbon factor we mean the amount of CO2 (measured in tons) that a forest stores (and therefore is not released into the atmosphere :D)

The forest image is stored inside a [Cloud Optimized Geotiff](https://www.cogeo.org/) file. The expression used for the file-name is the following:

```python
f"{forest.name.replace(' ', '_')}_{start_date}_{end_date}.cog.tif"
```

For [reductions](https://developers.google.com/earth-engine/guides/reducers_intro) we use the Mode (polling). If a very large time interval is specified, recent changes in the forest will be masked by old pixel values. It is encouraged to use the smallest possible time intervals (at least a week is required or there may not be data). However, depending on some factors (such as the amount of clouds), specifying a small time interval may result in many NA (see mrv.calculations documentation for further info on how NA are treated when calculating the carbon factor).

---
## Attributions

This dataset is produced for the Dynamic World Project by Google in partnership with National Geographic Society and the World Resources Institute.

---

# Development notes

## How to run tests locally

- to test run 'pytest' in the root directory of the proyect
- to run coverage use 'pytest --cov mrv --cov-branch --cov-report term-missing --disable-warnings'

## How to run tests in docker

The easiest is to use VScode functionality "Reopen in container" which is quite nicer for development. Alternaitvely:

```zsh
# Build test docker
docker build --tag dw --file Dockerfile --target dev .

# Run lint and tests
docker run dw /bin/bash -c "flake8 && pytest"
```