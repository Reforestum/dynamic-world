# mrv-dynamic-world-app

Work in progress 👷

## Usage

This application allows for remote monitoring of forests based around [Google's Dynamic World App](https://dynamicworld.app/).

### Forests

Each forest (or "proyect") is stored inside a directory with a given name. Inside this directory there must be 2 files:
- a forest_config.yml (name is mandatory) which looks like this:

```yaml
# Name of the forest/proyect
name : Dummy

# Locations of the geojson file and dcitionary with carbon factor/metric
geojson : './dummy.geojson'
carbon_factor : {
    "trees" : 1,
    "other" : 0, # MUST contain this label
    "factor_pixel" : 1 # MUST contain this label
}

# Date in which the reforestation started, in format YYYY-mm-dd
start_date: '2022-01-01'
```

- a valid geojson file [see](https://geojson.org/) (named as defined in forest_config.yml) that defines the area

Internally, forests are stored as a ForestConfig instance (see mrv.configurations for more details).

### Available calculations

Given a forest and a pair of dates, we download the forest image, landcover statistics and carbon factor [^cf_foot] calculation.

[^cf_foot]: by carbon factor we mean the amount of CO2 (measured in tons) that a forest stores (and therefore is not released into the atmosphere :D)

The forest image is stored inside a [Cloud Optimized Geotiff](https://www.cogeo.org/) file. The expression used for the file-name is the following (assuming):

```python
f"{forest.name.replace(' ', '_')}_{start_date}_{end_date}.cog.tif"
```

Statistics and carbon factors are stored inside a geojson named like:

```python
f"{forest.name.replace(' ', '_')}_{start_date}_{end_date}_carbon_factor.json"
```

The resulting file will look like this:

```json
{
    "date": "2022-01-01", 
    "pixel_counts": {
        "NA": 1,
        "bare": 1,
        "built": 1,
        "crops": 1,
        "flooded_vegetation": 1,
        "grass": 1,
        "shrub_and_scrub": 1,
        "snow_and_ice": 1,
        "trees": 1,
        "water": 1
        },
    "carbon_factor": 100.0
}
```

For [reductions](https://developers.google.com/earth-engine/guides/reducers_intro) we use the Mode (polling). If a very large time interval is specified, recent changes in the forest will be masked by old pixel values. It is encouraged to use the smallest possible time intervals (at least a week is required or there may not be data). However, depending on some factors (such as the amount of clouds), specifying a small time interval may result in many NA (see mrv.calculations for further info on how NA are treated when calculating the carbon factor).

### Available command-line options

By default, calculations are made for all the forests inside the directory "./forests/" unless the argument --base-directory is specified and an existing directory is provided.
You can specify only some forests and some dates using the flags --forests and --dates. By default a weekly analysis (on Mondays) is made using a time interval of 6 months.
If an analysis (JSON or TIFF) already exists inside the forest's directory (inside Azure) (only file-names are checked), an analysis won't run again unless the flag --force is specified.
To adjust the length of time intervals used in GEE, a --period argument can be specified, it is 6 months by default.
To adjust the frequency of analysis you can specify a --freq argument, it is weekly on mondays by default.

To see these options in detail, use the --help flag

---

# Development notes

## How to run locally

- to execute exhaustive analysis, run "python run.py"
- to see the available command line options run "python run.py --help"
- to test run 'pytest' in the root directory of the proyect
- to run coverage use 'pytest --cov mrv --cov-branch --cov-report term-missing --disable-warnings'

## How to run in docker

The easiest is to use VScode functionality "Reopen in container" which is quite nicer for development. Alternaitvely:

```zsh
# Build test docker
docker build --tag dw --file Dockerfile --target dev .

# Run lint and tests
docker run dw /bin/bash -c "flake8 && pytest"
```

## Adding dependencies

We use [poetry](https://python-poetry.org/) dependency manager:

- `poetry add --dev azure-storage-blob` to add a depenency to the `main` group 
- `poetry add --dev pytest` to add a depenency to the `dev` group

## Secrets

Keep the decrypted secrets in `.env` file, and the encrypted ones in `encrypted.env` to track them in Github. Similarly the `service_account.json`.

```bash
# Encrypt secrets
sops --encrypt .env > encrypted.env

# Decrypt secrets
sops --decrypt encrypted.env > .env
```

The Google Earth Engine `service_account.json` file is encoded in the secret `SERVICE_ACCOUNT`. Snippet to encode it:

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
