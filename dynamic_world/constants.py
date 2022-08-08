FOREST_CONFIG_FILENAME = 'forest_config.yml'
NA_LABEL = 'NA'
#  See
# https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1
# for labelling reference
CLASS_LABELS_DICT = {
        '0': 'water', '1': 'trees', '2': 'grass',
        '3': 'flooded_vegetation', '4': 'crops',
        '5': 'shrub_and_scrub', '6': 'built',
        '7': 'bare', '8': 'snow_and_ice', 'null': NA_LABEL
}
CLASS_LABELS = list(CLASS_LABELS_DICT.values())
CLASS_LABELS.remove(NA_LABEL)
OTHER_LABEL = 'other'
FACTOR_PIXEL_LABEL = 'factor_pixel'
SCALE = 10
DEFAULT_PROYECTS_DIR = 'forests'
LOGGER_NAME = 'mrv-gnome'
