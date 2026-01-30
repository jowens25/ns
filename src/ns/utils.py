from importlib.resources import files

# Access assets relative to your package
ASSETS_DIR = files('ns').joinpath('assets')
INTROSPECTION_DIR = files('ns').joinpath('introspection')